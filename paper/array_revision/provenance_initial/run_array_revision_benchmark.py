"""Repeated outer holdouts, depth sensitivity, and training-only tuned baselines.

No timeout or accuracy-dependent dataset selection is used. Every task is
checkpointed atomically. Mixed forests replace distinct bootstrap slots; they
never concatenate overlapping prefixes. Costs are measured per constituent
tree, with direct end-to-end checks for the principal shallow comparison.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import time

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
import sklearn
from pmlb import fetch_data
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier

from revision_runtime import REPO, load_classifier

Classifier = load_classifier()
OUT = REPO / "paper/array_revision"
DEPTHS = (3, 6, None)
SEEDS = (1000, 1001, 1002, 1003, 1004)
SCHEDULES = (
    ("greedy20", 20, 0), ("mix05_20", 20, 1),
    ("mix10_20", 20, 2), ("mix25_20", 20, 5),
    ("mix50_20", 20, 10), ("sighted2_20", 20, 20),
    ("greedy100", 100, 0), ("mix05_100", 100, 5),
    ("mix10_100", 100, 10), ("mix25_100", 100, 25),
    ("greedy200", 200, 0),
)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dataset_names():
    with (REPO / "paper/tables/mixed_sighted_dataset_sample.csv").open() as handle:
        return [row["dataset"] for row in csv.DictReader(handle)]


def task_path(dataset, seed, depth):
    return OUT / "raw" / f"{dataset}__s{seed}__D{depth}.json"


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def load_data(dataset):
    # The downloaded PMLB file is a public data artifact, not generated code.
    frame = fetch_data(dataset, local_cache_dir=str(OUT / ".cache/pmlb"))
    X = np.asarray(frame.drop(columns="target"), dtype=np.float64)
    _, y = np.unique(np.asarray(frame["target"]), return_inverse=True)
    if not np.isfinite(X).all():
        raise ValueError("Nonfinite predictors; no implicit imputation is applied")
    return X, y


def proba(tree, X, n_classes):
    values = np.zeros((len(X), n_classes))
    values[:, np.asarray(tree.classes_, dtype=int)] = tree.predict_proba(X)
    return values


def scores(y, values):
    predicted = np.argmax(values, axis=1)
    return {"accuracy": float(accuracy_score(y, predicted)),
            "balanced_accuracy": float(balanced_accuracy_score(y, predicted))}


def bootstrap_slots(n, seed, count=200):
    rng = np.random.RandomState(seed + 104729)
    seeds = rng.randint(np.iinfo(np.int32).max, size=count)
    samples = [np.random.RandomState(int(s)).randint(n, size=n) for s in seeds]
    # A fixed permutation chooses replacement positions independently of labels.
    replacement = np.random.RandomState(seed + 130363).permutation(100)[:25]
    return seeds, samples, replacement


def fitted_tree(X, y, indices, seed, depth, sight):
    start = time.perf_counter()
    tree = Classifier(lookahead_depth=sight, max_depth=depth,
                      max_features=None, random_state=int(seed))
    tree.fit(X[indices], y[indices])
    elapsed = time.perf_counter() - start
    return tree, elapsed


def direct_forest(X, y, Xtest, n_classes, seeds, samples, selected, depth):
    start = time.perf_counter()
    trees = [fitted_tree(X, y, samples[i], seeds[i], depth,
                         2 if i in selected else 1)[0] for i in range(100)]
    elapsed = time.perf_counter() - start
    values = sum(proba(tree, Xtest, n_classes) for tree in trees) / len(trees)
    return values, elapsed


def tune_baselines(X, y, Xtest, ytest, seed):
    minimum = int(np.bincount(y).min())
    if minimum < 2:
        raise ValueError("Training class count cannot support inner stratified CV")
    cv = StratifiedKFold(n_splits=min(3, minimum), shuffle=True, random_state=seed + 7)
    results = []
    models = (
        ("cart_tuned", DecisionTreeClassifier(random_state=seed),
         {"max_depth": [3, 6, None], "min_samples_leaf": [1, 5]}),
        ("rf_tuned", RandomForestClassifier(n_estimators=100, random_state=seed, n_jobs=1),
         {"max_depth": [3, 6, None], "min_samples_leaf": [1, 5],
          "max_features": ["sqrt", None]}),
    )
    for model_id, model, grid in models:
        search = GridSearchCV(model, grid, scoring="accuracy", cv=cv,
                              n_jobs=1, refit=True, error_score="raise")
        start = time.perf_counter()
        search.fit(X, y)
        total_time = time.perf_counter() - start
        values = proba(search.best_estimator_, Xtest, int(max(y.max(), ytest.max())) + 1)
        results.append({"model_id": model_id, "max_depth": "tuned",
                        "n_estimators": 100 if model_id == "rf_tuned" else 1,
                        "fit_time_s": float(search.refit_time_),
                        "selection_fit_time_s": total_time,
                        "time_kind": "direct_wall_clock",
                        "params": search.best_params_, **scores(ytest, values)})
    return results


def evaluate(dataset, seed, depth):
    X, y = load_data(dataset)
    classes, counts = np.unique(y, return_counts=True)
    if counts.min() < 2:
        raise ValueError("Outer stratification requires two examples per class")
    train, test = train_test_split(np.arange(len(y)), test_size=0.25,
                                  stratify=y, random_state=seed)
    Xtrain, ytrain, Xtest, ytest = X[train], y[train], X[test], y[test]
    n_classes = len(classes)
    rows = []
    all_indices = np.arange(len(train))
    for sight in (1, 2):
        tree, elapsed = fitted_tree(Xtrain, ytrain, all_indices, seed, depth, sight)
        rows.append({"model_id": f"tree_k{sight}", "max_depth": str(depth),
                     "n_estimators": 1, "fit_time_s": elapsed,
                     "time_kind": "direct_wall_clock", "realized_depth": tree.get_depth(),
                     "n_leaves": tree.get_n_leaves(),
                     **scores(ytest, proba(tree, Xtest, n_classes))})

    seeds, samples, replacement = bootstrap_slots(len(train), seed)
    greedy_proba, greedy_times, greedy_depths = [], [], []
    for slot in range(200):
        tree, elapsed = fitted_tree(Xtrain, ytrain, samples[slot], seeds[slot], depth, 1)
        greedy_proba.append(proba(tree, Xtest, n_classes))
        greedy_times.append(elapsed)
        greedy_depths.append(tree.get_depth())
    sighted_proba, sighted_times, sighted_depths = {}, {}, {}
    # The first 20 slots support the homogeneous 20-tree comparison; the
    # permuted slots support distinct, nested replacements in 100-tree forests.
    for slot in sorted(set(range(20)) | set(replacement.tolist())):
        tree, elapsed = fitted_tree(Xtrain, ytrain, samples[slot], seeds[slot], depth, 2)
        sighted_proba[slot] = proba(tree, Xtest, n_classes)
        sighted_times[slot] = elapsed
        sighted_depths[slot] = tree.get_depth()

    for model_id, count, n_sighted in SCHEDULES:
        selected = set(range(n_sighted)) if count == 20 else set(replacement[:n_sighted])
        values, elapsed, depths = np.zeros_like(greedy_proba[0]), 0.0, []
        for slot in range(count):
            if slot in selected:
                values += sighted_proba[slot]
                elapsed += sighted_times[slot]
                depths.append(sighted_depths[slot])
            else:
                values += greedy_proba[slot]
                elapsed += greedy_times[slot]
                depths.append(greedy_depths[slot])
        rows.append({"model_id": model_id, "max_depth": str(depth),
                     "n_estimators": count, "n_sighted": n_sighted,
                     "fit_time_s": elapsed, "time_kind": "measured_tree_fit_sum",
                     "realized_depth": float(np.mean(depths)),
                     **scores(ytest, values / count)})

    # Measure the actual standalone forest fits for the main comparison.
    if depth == 3:
        for model_id, selected in (("greedy100", set()),
                                   ("mix10_100", set(replacement[:10]))):
            values, elapsed = direct_forest(Xtrain, ytrain, Xtest, n_classes,
                                           seeds, samples, selected, depth)
            pooled = next(row for row in rows if row["model_id"] == model_id)
            direct_scores = scores(ytest, values)
            if direct_scores != {key: pooled[key] for key in direct_scores}:
                raise AssertionError("Direct and pooled forest predictions disagree")
            pooled["tree_fit_sum_s"] = pooled["fit_time_s"]
            pooled["fit_time_s"] = elapsed
            pooled["time_kind"] = "direct_wall_clock"
        rows.extend(tune_baselines(Xtrain, ytrain, Xtest, ytest, seed))
        dummy = DummyClassifier(strategy="most_frequent").fit(Xtrain, ytrain)
        rows.append({"model_id": "majority", "max_depth": "none",
                     "n_estimators": 0, "fit_time_s": 0.0,
                     "time_kind": "not_compared", **scores(ytest, proba(dummy, Xtest, n_classes))})

    return {"dataset": dataset, "seed": seed, "max_depth": str(depth),
            "n_samples": len(X), "n_features": X.shape[1], "n_classes": n_classes,
            "train_index_sha256": hashlib.sha256(train.tobytes()).hexdigest(),
            "test_index_sha256": hashlib.sha256(test.tobytes()).hexdigest(),
            "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--n-shards", type=int, default=1)
    parser.add_argument("--datasets", nargs="+")
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--depths", nargs="+", default=["3", "6", "None"])
    args = parser.parse_args()
    depths = [None if value == "None" else int(value) for value in args.depths]
    names = args.datasets or dataset_names()
    # A deterministic metadata-only order; no measured accuracy is consulted.
    tasks = [(name, seed, depth) for name in names for seed in args.seeds for depth in depths]
    tasks = tasks[args.shard_index::args.n_shards]
    manifest = {"seeds": list(SEEDS), "max_depths": [3, 6, None],
                "test_size": 0.25, "inner_folds": "min(3, min training class count)",
                "datasets": dataset_names(), "python": platform.python_version(),
                "platform": platform.platform(), "numpy": np.__version__,
                "sklearn": sklearn.__version__,
                "source_hashes": {str(path.relative_to(REPO)): file_hash(path) for path in
                                  (REPO / "treeple/tree/_lookahead.py",
                                   REPO / "treeple/tree/_lookahead_fast.pyx", Path(__file__))}}
    atomic_json(OUT / f"manifest_shard_{args.shard_index}.json", manifest)
    for index, (dataset, seed, depth) in enumerate(tasks, 1):
        path = task_path(dataset, seed, depth)
        if path.exists():
            continue
        start = time.perf_counter()
        print(f"shard={args.shard_index} {index}/{len(tasks)} {dataset} seed={seed} D={depth}", flush=True)
        # Errors are visible and stop the shard; failed datasets are not silently removed.
        value = evaluate(dataset, seed, depth)
        atomic_json(path, value)
        print(f"completed in {time.perf_counter() - start:.2f}s", flush=True)


if __name__ == "__main__":
    main()
