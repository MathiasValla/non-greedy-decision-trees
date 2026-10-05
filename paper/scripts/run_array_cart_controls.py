"""Depth-matched CART controls and mixtures, using the same outer splits/slots."""

from __future__ import annotations

import argparse
import hashlib
import os
import time

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from run_array_revision_benchmark import (
    OUT, SEEDS, atomic_json, bootstrap_slots, dataset_names, fitted_tree,
    load_data, proba, scores,
)


def evaluate(dataset, seed, depth):
    X, y = load_data(dataset)
    train, test = train_test_split(np.arange(len(y)), test_size=.25, stratify=y, random_state=seed)
    Xtrain, ytrain, Xtest, ytest = X[train], y[train], X[test], y[test]
    n_classes = len(np.unique(y))
    start = time.perf_counter()
    tree = DecisionTreeClassifier(max_depth=depth, random_state=seed).fit(Xtrain, ytrain)
    elapsed = time.perf_counter() - start
    rows = [{"model_id": "cart_fixed", "max_depth": str(depth), "n_estimators": 1,
             "fit_time_s": elapsed, "time_kind": "direct_wall_clock",
             "realized_depth": tree.get_depth(), **scores(ytest, proba(tree, Xtest, n_classes))}]
    seeds, samples, replacement = bootstrap_slots(len(train), seed)
    selected = set(replacement[:10])
    trees, times = [], []
    for slot in range(200):
        start = time.perf_counter()
        tree = DecisionTreeClassifier(max_depth=depth, random_state=int(seeds[slot]))
        tree.fit(Xtrain[samples[slot]], ytrain[samples[slot]])
        times.append(time.perf_counter() - start)
        trees.append(tree)
    values = [proba(tree, Xtest, n_classes) for tree in trees]
    for count in (100, 200):
        rows.append({"model_id": f"cart_bag{count}", "max_depth": str(depth),
                     "n_estimators": count, "fit_time_s": sum(times[:count]),
                     "time_kind": "measured_tree_fit_sum",
                     "realized_depth": float(np.mean([t.get_depth() for t in trees[:count]])),
                     **scores(ytest, sum(values[:count]) / count)})

    # Directly fit a standalone heterogeneous forest. Replacement trees use
    # the exact same distinct bootstrap draws as their greedy counterparts.
    start = time.perf_counter()
    mixture = []
    constituent_time = 0.0
    for slot in range(100):
        if slot in selected:
            tree, tree_time = fitted_tree(Xtrain, ytrain, samples[slot], seeds[slot], depth, 2)
        else:
            tree_start = time.perf_counter()
            tree = DecisionTreeClassifier(max_depth=depth, random_state=int(seeds[slot]))
            tree.fit(Xtrain[samples[slot]], ytrain[samples[slot]])
            tree_time = time.perf_counter() - tree_start
        mixture.append(tree)
        constituent_time += tree_time
    elapsed = time.perf_counter() - start
    rows.append({"model_id": "cart_mix10_100", "max_depth": str(depth),
                 "n_estimators": 100, "fit_time_s": elapsed, "time_kind": "direct_wall_clock",
                 "tree_fit_sum_s": constituent_time,
                 "realized_depth": float(np.mean([t.get_depth() for t in mixture])),
                 **scores(ytest, sum(proba(t, Xtest, n_classes) for t in mixture) / 100)})

    start = time.perf_counter()
    forest = RandomForestClassifier(n_estimators=100, max_depth=depth, max_features="sqrt",
                                    random_state=seed, n_jobs=1).fit(Xtrain, ytrain)
    elapsed = time.perf_counter() - start
    rows.append({"model_id": "rf_sqrt_fixed", "max_depth": str(depth), "n_estimators": 100,
                 "fit_time_s": elapsed, "time_kind": "direct_wall_clock",
                 "realized_depth": float(np.mean([t.get_depth() for t in forest.estimators_])),
                 **scores(ytest, proba(forest, Xtest, n_classes))})
    return {"dataset": dataset, "seed": seed, "max_depth": str(depth),
            "n_samples": len(X), "n_features": X.shape[1], "n_classes": n_classes,
            "train_index_sha256": hashlib.sha256(train.tobytes()).hexdigest(),
            "test_index_sha256": hashlib.sha256(test.tobytes()).hexdigest(), "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--n-shards", type=int, default=1)
    parser.add_argument("--datasets", nargs="+")
    args = parser.parse_args()
    from threadpoolctl import threadpool_info
    atomic_json(OUT / f"cart_manifest_shard_{args.shard_index}.json", {
        "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
        "threadpools": threadpool_info(), "seeds": list(SEEDS), "depths": [3, 6, None],
        "datasets": args.datasets or dataset_names(), "n_shards": args.n_shards,
        "shard_index": args.shard_index,
    })
    tasks = [(name, seed, depth) for name in (args.datasets or dataset_names())
             for seed in SEEDS for depth in (3, 6, None)]
    for index, (dataset, seed, depth) in enumerate(tasks[args.shard_index::args.n_shards], 1):
        path = OUT / "raw_cart" / f"{dataset}__s{seed}__D{depth}.json"
        if path.exists():
            continue
        print(f"CART shard={args.shard_index} {index} {dataset} seed={seed} D={depth}", flush=True)
        atomic_json(path, evaluate(dataset, seed, depth))


if __name__ == "__main__":
    main()
