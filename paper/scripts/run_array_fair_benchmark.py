"""Depth-matched, weighted-bootstrap forests with paired training-only selection.

The fair runtime is imported lazily so --self-test needs no compiled scorer.
No accuracy-based screening, fit deadline, or tree serialization is used.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import fcntl
import hashlib
import importlib
from importlib.metadata import version
import inspect
import json
import os
from pathlib import Path
import platform
import tempfile
import time

for _variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_variable] = "1"

import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper/array_revision_fair"
SEEDS = tuple(range(1000, 1005))
DEPTHS = (3, 6, None)
COUNTS = (20, 40, 60, 100, 200)
SELECTION_COUNTS = (20, 40, 60, 100)
HORIZONS = (1, 2, 3)
BANK_SIZE = 200
SELECTION_BANK_SIZE = 100
CHECKPOINT_EVERY = 20
FAMILIES = ("rf", "mixed_k2", "mixed")
INT32_MAX = np.iinfo(np.int32).max
SCHEMA = "array-fair-v1"
Classifier = None


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as handle:
        result = hashlib.sha256()
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            result.update(chunk)
    return result.hexdigest()


def array_hash(value):
    value = np.ascontiguousarray(value)
    digest = hashlib.sha256(canonical({"dtype": value.dtype.str,
                                      "shape": list(value.shape)}).encode())
    digest.update(value.tobytes())
    return digest.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def locked(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def load_runtime():
    global Classifier
    if Classifier is None:
        runtime = importlib.import_module("fair_revision_runtime")
        if Path(runtime.REPO).resolve() != REPO:
            raise RuntimeError("Fair runtime points to a different repository")
        Classifier = runtime.Classifier
    return Classifier


def dataset_metadata():
    with (REPO / "paper/tables/mixed_sighted_dataset_sample.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 57 or len({row["dataset"] for row in rows}) != 57:
        raise ValueError("The frozen dataset list must contain 57 unique datasets")
    return rows


def dataset_names():
    return [row["dataset"] for row in dataset_metadata()]


def load_data(dataset, out=OUT):
    from pmlb import fetch_data

    if dataset not in dataset_names():
        raise ValueError(f"Dataset outside the frozen list: {dataset}")
    cache = Path(out) / ".cache/pmlb"
    with locked(cache / f"{dataset}.lock"):
        frame = fetch_data(dataset, local_cache_dir=str(cache), dropna=False)
    frame = frame.dropna()
    X = np.ascontiguousarray(frame.drop(columns="target"), dtype=np.float32)
    _, y = np.unique(np.asarray(frame["target"]), return_inverse=True)
    y = np.ascontiguousarray(y, dtype=np.int64)
    if not np.isfinite(X).all():
        raise ValueError("Nonfinite float32 predictors; no implicit imputation")
    return X, y


def compositions(include_triple=False):
    # Integer twentieths keep all scheduled counts exact, including T=20.
    result = [(f"pure_k{h}", tuple(20 if k == h else 0 for k in HORIZONS))
              for h in HORIZONS]
    for near, far in ((1, 2), (1, 3), (2, 3)):
        for ticks in (1, 2, 5, 10):
            weights = [0, 0, 0]
            weights[near - 1], weights[far - 1] = 20 - ticks, ticks
            result.append((f"pair_k{near}_k{far}_q{ticks * 5:02d}", tuple(weights)))
    if include_triple:
        result.append(("triple_85_10_05", (17, 2, 1)))
    return tuple(result)


def structural_grid():
    return tuple({"max_depth": depth, "min_samples_leaf": leaf, "max_features": features}
                 for depth in DEPTHS for leaf in (1, 5) for features in ("sqrt", None))


def structural_id(params):
    depth = "None" if params["max_depth"] is None else str(params["max_depth"])
    features = "all" if params["max_features"] is None else params["max_features"]
    return f"D{depth}_L{params['min_samples_leaf']}_F{features}"


def candidate_id(params, count, composition):
    return f"{structural_id(params)}__T{count:03d}__{composition}"


def primary_contrasts():
    contrasts = []
    for depth in (3, None):
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            for horizon in (2, 3):
                contrasts.append({"contrast_id": f"fixed__{structural_id(params)}__k{horizon}_vs_k1",
                                  "stage": "fixed", "params": params,
                                  "left": candidate_id(params, 100, f"pair_k1_k{horizon}_q10"),
                                  "right": candidate_id(params, 100, "pure_k1")})
    for left, right in (("mixed_k2", "rf"), ("mixed", "rf"), ("mixed", "mixed_k2")):
        contrasts.append({"contrast_id": f"tuned__{left}_vs_{right}", "stage": "tuned",
                          "left": left, "right": right})
    return contrasts


def tree_seeds(seed, count=BANK_SIZE):
    if not 1 <= count <= BANK_SIZE:
        raise ValueError("Forest count must be between 1 and 200")
    return np.random.RandomState(seed).randint(INT32_MAX, size=BANK_SIZE)[:count]


def bootstrap_counts(n, tree_seed):
    if n < 1:
        raise ValueError("Bootstrap requires nonempty training data")
    draw = np.random.RandomState(int(tree_seed)).randint(n, size=n)
    return np.bincount(draw, minlength=n).astype(np.float64)


def schedule(seed, count, ticks):
    ticks = tuple(ticks)
    if count not in COUNTS or len(ticks) != 3 or sum(ticks) != 20:
        raise ValueError("Invalid forest count or composition")
    if any(not isinstance(value, (int, np.integer)) or value < 0 for value in ticks):
        raise ValueError("Composition must use nonnegative integer twentieths")
    sizes = [count * value // 20 for value in ticks]
    if any(count * value % 20 for value in ticks):
        raise ValueError("Composition does not give integer tree counts")
    active = [h for h, size in zip(HORIZONS, sizes) if size]
    selected = np.full(count, active[0], dtype=np.int8)
    rng = np.random.RandomState(seed + 130363)
    for start in range(0, count, 20):
        priorities = start + rng.permutation(20)
        offset = 0
        for horizon in active[1:]:
            size = ticks[horizon - 1]
            selected[priorities[offset:offset + size]] = horizon
            offset += size
    if tuple(int(np.sum(selected == h)) for h in HORIZONS) != tuple(sizes):
        raise AssertionError("Disjoint schedule did not preserve composition")
    return selected


def common_params(params, seed):
    return {**params, "criterion": "gini", "min_samples_split": 2,
            "min_weight_fraction_leaf": 0.0, "min_impurity_decrease": 0.0,
            "random_state": int(seed)}


def new_tree(params, seed, horizon):
    common = common_params(params, seed)
    if horizon == 1:
        return DecisionTreeClassifier(**common, ccp_alpha=0.0, splitter="best",
                                      max_leaf_nodes=None, class_weight=None)
    if horizon not in (2, 3):
        raise ValueError(f"Unsupported horizon: {horizon}")
    runtime = load_runtime()
    options = {**common, "lookahead_depth": horizon, "max_split_candidates": None}
    if "ccp_alpha" in inspect.signature(runtime).parameters:
        options["ccp_alpha"] = 0.0
    tree = runtime(**options)
    cart = DecisionTreeClassifier(**common, ccp_alpha=0.0)
    actual = tree.get_params(deep=False)
    for name, value in cart.get_params(deep=False).items():
        if name in actual and actual[name] != value:
            raise AssertionError(f"CART/runtime common parameter mismatch: {name}")
    return tree


def proba(tree, X, n_classes):
    values = np.zeros((len(X), n_classes), dtype=np.float64)
    values[:, np.asarray(tree.classes_, dtype=int)] = tree.predict_proba(X)
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite predicted probabilities")
    return values


def scores(y, values):
    predicted = np.argmax(values, axis=1)
    return {"accuracy": float(accuracy_score(y, predicted)),
            "balanced_accuracy": float(balanced_accuracy_score(y, predicted))}


def make_forest(params, seed, count):
    return RandomForestClassifier(**common_params(params, seed), n_estimators=count,
                                  ccp_alpha=0.0, bootstrap=True, n_jobs=1,
                                  max_samples=None, max_leaf_nodes=None,
                                  class_weight=None, oob_score=False, warm_start=False)


def fit_bank(X, y, Xeval, n_classes, seed, params, horizon, count=BANK_SIZE,
             bank=None, save=None):
    if bank is None:
        bank = {"values": np.full((count, len(Xeval), n_classes), np.nan),
                "fit_s": np.full(count, np.nan), "predict_s": np.full(count, np.nan),
                "depth": np.full(count, -1, dtype=np.int64),
                "leaves": np.full(count, -1, dtype=np.int64),
                "completed_slots": 0, "wall_s": 0.0, "preparation_s": 0.0}
    seeds = tree_seeds(seed, count)
    segment_start = time.perf_counter()
    for slot in range(int(bank["completed_slots"]), count):
        tree_seed = seeds[slot]
        preparation_start = time.perf_counter()
        weights = bootstrap_counts(len(y), tree_seed)
        tree = new_tree(params, tree_seed, horizon)
        bank["preparation_s"] += time.perf_counter() - preparation_start
        fit_start = time.perf_counter()
        tree.fit(X, y, sample_weight=weights)
        bank["fit_s"][slot] = time.perf_counter() - fit_start
        predict_start = time.perf_counter()
        bank["values"][slot] = proba(tree, Xeval, n_classes)
        bank["predict_s"][slot] = time.perf_counter() - predict_start
        bank["depth"][slot] = tree.get_depth()
        bank["leaves"][slot] = tree.get_n_leaves()
        bank["completed_slots"] = slot + 1
        del tree
        if (slot + 1) % CHECKPOINT_EVERY == 0 or slot + 1 == count:
            bank["wall_s"] += time.perf_counter() - segment_start
            if save is not None:
                save(bank)
            segment_start = time.perf_counter()
    return bank


def bank_metadata(bank):
    return {"fit_work_s": float(np.sum(bank["fit_s"])),
            "prediction_work_s": float(np.sum(bank["predict_s"])),
            "bank_wall_s": float(bank["wall_s"]),
            "preparation_wall_s": float(bank["preparation_s"]),
            "mean_actual_depth": float(np.mean(bank["depth"])),
            "fit_s_by_slot": bank["fit_s"].tolist(),
            "predict_s_by_slot": bank["predict_s"].tolist(),
            "actual_depth_by_slot": bank["depth"].tolist(),
            "n_leaves_by_slot": bank["leaves"].tolist()}


def pooled(banks, selected):
    count = len(selected)
    values = np.zeros_like(banks[1]["values"][0])
    fit_work, predict_work, depths, leaves = 0.0, 0.0, [], []
    # Slot order matches sklearn's accumulation order for the greedy prefix.
    for slot, horizon in enumerate(selected):
        bank = banks[int(horizon)]
        values += bank["values"][slot]
        fit_work += float(bank["fit_s"][slot])
        predict_work += float(bank["predict_s"][slot])
        depths.append(int(bank["depth"][slot]))
        leaves.append(int(bank["leaves"][slot]))
    return values / count, {"fit_work_s": fit_work,
                            "prediction_work_s": predict_work,
                            "mean_actual_depth": float(np.mean(depths)),
                            "mean_n_leaves": float(np.mean(leaves))}


def family_accepts(row, family):
    if family == "rf":
        return row["composition_id"] == "pure_k1"
    if family == "mixed_k2":
        return row["composition_twentieths"][2] == 0
    if family == "mixed":
        return True
    raise ValueError(f"Unknown family: {family}")


def curves(banks, y, seed, params, include_triple=False, counts=COUNTS):
    rows = []
    evaluation = {f"{family}_schedule_evaluation_wall_s": 0.0 for family in FAMILIES}
    for count in counts:
        for composition, ticks in compositions(include_triple):
            start = time.perf_counter()
            selected = schedule(seed, count, ticks)
            values, costs = pooled(banks, selected)
            row = {"candidate_id": candidate_id(params, count, composition),
                   "composition_id": composition, "composition_twentieths": list(ticks),
                   "n_estimators": count, "params": params,
                   "horizon_counts": [int(np.sum(selected == h)) for h in HORIZONS],
                   "slot_horizon_sha256": array_hash(selected),
                   "time_kind": "measured_selected_tree_fit_sum", **costs, **scores(y, values)}
            elapsed = time.perf_counter() - start
            row["schedule_evaluation_wall_s"] = elapsed
            for family in FAMILIES:
                if family_accepts(row, family):
                    evaluation[f"{family}_schedule_evaluation_wall_s"] += elapsed
            rows.append(row)
    return rows, evaluation


def inner_splits(y, seed):
    if len(y) < 3:
        raise ValueError("Three-fold fallback requires at least three training samples")
    _, counts = np.unique(y, return_counts=True)
    if len(counts) == 1 or counts.min() < 2:
        cv = KFold(n_splits=3, shuffle=True, random_state=seed + 7)
        kind = "KFold_3_single_or_rare_class"
    else:
        n_splits = min(3, int(counts.min()))
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed + 7)
        kind = f"StratifiedKFold_{n_splits}"
    return list(cv.split(np.zeros((len(y), 1)), y)), kind


def outer_split(y, seed):
    _, counts = np.unique(y, return_counts=True)
    if counts.min() < 2:
        raise ValueError("Outer stratification requires two examples per class")
    return train_test_split(np.arange(len(y), dtype=np.int64), test_size=0.25,
                            stratify=y, random_state=seed)


def choose_candidate(fold_results, family):
    if family not in FAMILIES or not fold_results:
        raise ValueError("Expected a known family and nonempty fold results")
    grouped = {}
    expected_folds = set()
    for block in fold_results:
        fold = block["fold"]
        expected_folds.add(fold)
        for row in block["rows"]:
            if not family_accepts(row, family):
                continue
            grouped.setdefault(row["candidate_id"], {})
            if fold in grouped[row["candidate_id"]]:
                raise ValueError("Duplicate candidate/fold checkpoint")
            grouped[row["candidate_id"]][fold] = row
    candidates = []
    for identity, rows_by_fold in grouped.items():
        if set(rows_by_fold) != expected_folds:
            raise ValueError(f"Incomplete CV candidate: {identity}")
        rows = [rows_by_fold[fold] for fold in sorted(expected_folds)]
        candidate = {key: rows[0][key] for key in
                     ("candidate_id", "composition_id", "composition_twentieths", "params",
                      "n_estimators")}
        candidate["mean_validation_accuracy"] = float(np.mean([r["accuracy"] for r in rows]))
        candidate["mean_validation_fit_work_s"] = float(np.mean([r["fit_work_s"] for r in rows]))
        candidate["n_inner_folds"] = len(rows)
        candidates.append(candidate)
    if not candidates:
        raise ValueError("Empty candidate space")
    return min(candidates, key=lambda row: (-row["mean_validation_accuracy"],
                                           row["mean_validation_fit_work_s"],
                                           row["candidate_id"]))


def source_manifest(include_triple=False):
    runtime = importlib.import_module("fair_revision_runtime")
    paths = {Path(__file__).resolve(), Path(runtime.__file__).resolve(),
             REPO / "paper/array_revision_fair/PROTOCOL.md",
             REPO / "paper/tables/mixed_sighted_dataset_sample.csv",
             REPO / "treeple/tree/_lookahead.py",
             REPO / "treeple/tree/_lookahead_fast.pyx",
             REPO / "paper/array_revision_fair/runtime/_sighted_fast.pyx",
             REPO / "paper/scripts/build_fair_revision_runtime.py"}
    # Capture separately built scorer artifacts without importing treeple.
    for root in (REPO / "paper/array_revision_fair/.cache/runtime",):
        if root.exists():
            paths.update(path for path in root.rglob("*")
                         if path.is_file() and path.suffix in (".so", ".pyd"))
    model_module = inspect.getmodule(load_runtime())
    if model_module is not None and getattr(model_module, "__file__", None):
        paths.add(Path(model_module.__file__).resolve())
    hashes = {}
    for path in sorted(paths):
        key = str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)
        hashes[key] = file_hash(path)
    documentation_hash = hashes.pop("paper/array_revision_fair/PROTOCOL.md")
    protocol = {"schema": SCHEMA, "datasets": dataset_names(), "outer_seeds": list(SEEDS),
                "test_size": 0.25, "counts": list(COUNTS), "horizons": list(HORIZONS),
                "selection_counts": list(SELECTION_COUNTS), "selection_bank_size": SELECTION_BANK_SIZE,
                "selection_families": list(FAMILIES), "checkpoint_every_slots": CHECKPOINT_EVERY,
                "primary_contrasts": primary_contrasts(),
                "fixed_depths": list(DEPTHS), "fixed_leaf": 1, "fixed_max_features": None,
                "fixed_feature_modes": [None, "sqrt"],
                "structural_grid": list(structural_grid()),
                "compositions": [{"id": name, "twentieths": list(ticks)}
                                 for name, ticks in compositions(include_triple)],
                "bootstrap": "RandomState(seed).randint(INT32MAX,200); bincount full-X weights",
                "priorities": "successive RandomState(seed+130363).permutation(20) blocks",
                "shards": "one outer seed per shard; metadata n*p descending task order",
                "missingness": "explicit complete-case rows, raw and used row counts frozen",
                "predictor_dtype": "float32", "criterion": "gini", "min_samples_split": 2,
                "ccp_alpha": 0.0, "inner_cv": "stratified min(3,minclass), ordinary3 rare/single",
                "inner_seed_offset": 7, "tie_break": ["accuracy_desc", "fit_work_asc", "id_asc"],
                "fit_timeout": None, "source_hashes": hashes,
                "python": platform.python_version(), "platform": platform.platform(),
                "numpy": np.__version__, "sklearn": sklearn.__version__,
                "pandas": version("pandas"), "pmlb": version("pmlb")}
    protocol["protocol_fingerprint"] = fingerprint(protocol)
    protocol["documentation_sha256"] = documentation_hash
    return protocol


def guard_manifest(out, manifest):
    path = Path(out) / "protocol.json"
    with locked(Path(out) / ".locks/protocol.lock"):
        if path.exists():
            stored = json.loads(path.read_text())
            if stored["protocol_fingerprint"] != manifest["protocol_fingerprint"]:
                raise RuntimeError("Protocol/source/environment fingerprint changed; use a fresh output root")
        else:
            atomic_json(path, manifest)


def checked_json(path, identity):
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    if result.get("identity") != identity:
        raise RuntimeError(f"Checkpoint identity mismatch: {path}")
    return result


def read_bank(path, identity):
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as archive:
        if str(archive["identity"].item()) != canonical(identity):
            raise RuntimeError(f"Bank cache identity mismatch: {path}")
        bank = {key: archive[key].copy() for key in
                ("values", "fit_s", "predict_s", "depth", "leaves")}
        bank.update({key: float(archive[key].item()) for key in ("wall_s", "preparation_s")})
        bank["completed_slots"] = int(archive["completed_slots"].item())
    count = identity["bank_size"]
    complete = bank["completed_slots"]
    if bank["values"].shape != tuple(identity["probability_shape"]) or not 0 <= complete <= count:
        raise ValueError(f"Malformed bank cache shape/completion: {path}")
    for key in ("fit_s", "predict_s", "depth", "leaves"):
        if bank[key].shape != (count,) or not np.isfinite(bank[key][:complete]).all():
            raise ValueError(f"Malformed bank cache metrics: {path}")
    if (not np.isfinite(bank["values"][:complete]).all()
            or np.any(bank["fit_s"][:complete] < 0) or np.any(bank["predict_s"][:complete] < 0)
            or np.any(bank["depth"][:complete] < 0)
            or np.any(bank["leaves"][:complete] < 1)):
        raise ValueError(f"Malformed completed bank slots: {path}")
    for key in ("wall_s", "preparation_s"):
        if not np.isfinite(bank[key]) or bank[key] < 0:
            raise ValueError(f"Malformed bank wall-time metric: {path}")
    return bank


def save_bank(path, identity, bank):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            np.savez_compressed(handle, identity=canonical(identity), **bank)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def bank_cache(path, identity, X, y, Xeval, n_classes, seed, params, horizon):
    bank = read_bank(path, identity)
    return fit_bank(X, y, Xeval, n_classes, seed, params, horizon,
                    count=identity["bank_size"], bank=bank,
                    save=lambda value: save_bank(path, identity, value))


def structural_block(path, identity, X, y, Xeval, yeval, n_classes, seed, params,
                     include_triple=False, counts=COUNTS):
    stored = checked_json(path, identity)
    if stored is not None:
        return stored
    start = time.perf_counter()
    banks = {}
    bank_size = max(counts)
    for horizon in HORIZONS:
        bank_identity = {**identity, "horizon": horizon, "bank_size": bank_size,
                         "probability_shape": [bank_size, len(Xeval), n_classes],
                         "tree_seed_sha256": array_hash(tree_seeds(seed, bank_size))}
        banks[horizon] = bank_cache(path.with_suffix(f".k{horizon}.npz"), bank_identity,
                                    X, y, Xeval, n_classes, seed, params, horizon)
    rows, evaluation = curves(banks, yeval, seed, params, include_triple, counts)
    metadata = {str(h): bank_metadata(banks[h]) for h in HORIZONS}
    result = {"identity": identity, "rows": rows, "banks": metadata,
              "fold": identity.get("fold"), **evaluation,
              "block_invocation_wall_s": time.perf_counter() - start,
              "block_compute_wall_s": float(sum(banks[h]["wall_s"] for h in HORIZONS)
                                              + evaluation["mixed_schedule_evaluation_wall_s"])}
    atomic_json(path, result)
    return result


def direct_mixed(X, y, Xtest, n_classes, seed, candidate):
    start = time.perf_counter()
    count = candidate["n_estimators"]
    selected = schedule(seed, count, candidate["composition_twentieths"])
    seeds = tree_seeds(seed, count)
    trees, fit_work = [], 0.0
    for slot, horizon in enumerate(selected):
        tree = new_tree(candidate["params"], seeds[slot], int(horizon))
        weights = bootstrap_counts(len(y), seeds[slot])
        fit_start = time.perf_counter()
        tree.fit(X, y, sample_weight=weights)
        fit_work += time.perf_counter() - fit_start
        trees.append(tree)
    fit_wall = time.perf_counter() - start
    prediction_start = time.perf_counter()
    values = np.zeros((len(Xtest), n_classes), dtype=np.float64)
    for tree in trees:
        values += proba(tree, Xtest, n_classes)
    prediction_wall = time.perf_counter() - prediction_start
    return values / count, {"direct_fit_time_s": fit_wall, "refit_tree_fit_work_s": fit_work,
                             "test_prediction_wall_s": prediction_wall,
                             "mean_actual_depth": float(np.mean([t.get_depth() for t in trees])),
                             "mean_n_leaves": float(np.mean([t.get_n_leaves() for t in trees])),
                             "slot_horizon_sha256": array_hash(selected)}


def selection_accounting(blocks):
    result = {}
    for family, horizons in (("rf", (1,)), ("mixed_k2", (1, 2)), ("mixed", HORIZONS)):
        result[family] = {
            "selection_fitting_work_s": float(sum(block["banks"][str(h)]["fit_work_s"]
                                                 for block in blocks for h in horizons)),
            "selection_prediction_work_s": float(sum(block["banks"][str(h)]["prediction_work_s"]
                                                    for block in blocks for h in horizons)),
            "selection_bank_wall_s": float(sum(block["banks"][str(h)]["bank_wall_s"]
                                              for block in blocks for h in horizons)),
            "selection_schedule_evaluation_wall_s": float(sum(
                block[f"{family}_schedule_evaluation_wall_s"] for block in blocks)),
            "selection_time_kind": "measured_fit_work_not_wall_time"}
        result[family]["selection_workflow_wall_s"] = (
            result[family]["selection_bank_wall_s"]
            + result[family]["selection_schedule_evaluation_wall_s"])
    shared = {"shared_k1_fit_work_s": result["rf"]["selection_fitting_work_s"],
              "shared_k1_prediction_work_s": result["rf"]["selection_prediction_work_s"],
              "shared_k1_bank_wall_s": result["rf"]["selection_bank_wall_s"],
              "shared_k1_schedule_wall_s": result["rf"]["selection_schedule_evaluation_wall_s"],
              "shared_k2_fit_work_s": float(sum(block["banks"]["2"]["fit_work_s"] for block in blocks)),
              "physical_selection_fit_work_s": result["mixed"]["selection_fitting_work_s"],
              "physical_selection_compute_wall_s": result["mixed"]["selection_workflow_wall_s"],
              "attribution": "each family charged required horizons; shared k1/k2 physically counted once"}
    return result, shared


def tuned_stage(root, identity, X, y, Xtest, ytest, train_indices, n_classes, seed,
                include_triple=False):
    final_path = root / "tuned.json"
    stored = checked_json(final_path, identity)
    if stored is not None:
        return stored
    splits, cv_kind = inner_splits(y, seed)
    blocks, split_manifest = [], []
    for fold, (train, validation) in enumerate(splits):
        split_identity = {"fold": fold,
                          "inner_train_index_sha256": array_hash(train_indices[train]),
                          "inner_validation_index_sha256": array_hash(train_indices[validation])}
        split_manifest.append(split_identity)
        for params in structural_grid():
            block_identity = {**identity, "stage": "inner_cv", **split_identity,
                              "structural_params": params, "forest_counts": list(SELECTION_COUNTS)}
            path = root / "inner" / f"fold{fold}__{structural_id(params)}.json"
            blocks.append(structural_block(path, block_identity, X[train], y[train],
                                           X[validation], y[validation], n_classes, seed, params,
                                           include_triple, SELECTION_COUNTS))
    selection_path = root / "selection.json"
    selection = checked_json(selection_path, identity)
    if selection is None:
        bookkeeping_start = time.perf_counter()
        accounting, shared = selection_accounting(blocks)
        common_accounting_s = time.perf_counter() - bookkeeping_start
        candidates, family_bookkeeping_s = {}, {}
        for family in FAMILIES:
            family_start = time.perf_counter()
            candidates[family] = choose_candidate(blocks, family)
            family_bookkeeping_s[family] = time.perf_counter() - family_start
        selection = {"identity": identity, "selected": candidates,
                     "inner_cv_kind": cv_kind, "inner_splits": split_manifest,
                     "family_accounting": accounting, "shared_bank_accounting": shared,
                     "selection_common_accounting_wall_s": common_accounting_s,
                     "candidate_selection_wall_s_by_family": family_bookkeeping_s,
                     "selection_bookkeeping_time_kind": "shared_all_families_wall_once_physically",
                     "selection_bookkeeping_wall_s": time.perf_counter() - bookkeeping_start}
        atomic_json(selection_path, selection)
    candidates = selection["selected"]
    accounting = selection["family_accounting"]
    shared = dict(selection["shared_bank_accounting"])
    bookkeeping_s = selection["selection_bookkeeping_wall_s"]
    rows = []
    for family in FAMILIES:
        candidate = candidates[family]
        refit_identity = {**identity, "stage": "selected_refit", "family": family,
                          "candidate": candidate}
        path = root / f"refit_{family}.json"
        row_checkpoint = checked_json(path, refit_identity)
        if row_checkpoint is None:
            if family == "rf":
                start = time.perf_counter()
                model = make_forest(candidate["params"], seed, candidate["n_estimators"])
                model.fit(X, y)
                fit_time = time.perf_counter() - start
                prediction_start = time.perf_counter()
                values = proba(model, Xtest, n_classes)
                costs = {"direct_fit_time_s": fit_time,
                         "test_prediction_wall_s": time.perf_counter() - prediction_start,
                         "mean_actual_depth": float(np.mean([t.get_depth() for t in model.estimators_])),
                         "mean_n_leaves": float(np.mean([t.get_n_leaves() for t in model.estimators_]))}
                del model
            else:
                values, costs = direct_mixed(X, y, Xtest, n_classes, seed, candidate)
            row = {"family": family, "selected": candidate, "refit_model_config": {
                **common_params(candidate["params"], seed), "ccp_alpha": 0.0,
                "n_estimators": candidate["n_estimators"], "bootstrap": True,
                "n_jobs": 1, "composition_twentieths": candidate["composition_twentieths"],
                "estimator": "sklearn.RandomForestClassifier" if family == "rf" else "prepared_weighted_mixture"},
                "time_kind": "direct_wall_clock", **costs, **scores(ytest, values),
                **accounting[family]}
            row["total_fitting_work_s"] = (row["selection_fitting_work_s"]
                                            + costs.get("refit_tree_fit_work_s", costs["direct_fit_time_s"]))
            row["total_fitting_measurement_kind"] = (
                "selection_tree_fit_sum_plus_actual_rf_refit_wall" if family == "rf"
                else "selection_and_refit_tree_fit_sum")
            row["selection_bookkeeping_attributed_wall_s"] = (
                selection["selection_common_accounting_wall_s"]
                + selection["candidate_selection_wall_s_by_family"][family])
            row["total_workflow_wall_s"] = (
                row["selection_workflow_wall_s"] + row["selection_bookkeeping_attributed_wall_s"]
                + row["direct_fit_time_s"] + row["test_prediction_wall_s"])
            row["workflow_time_kind"] = "sum_measured_stage_wall_times_shared_k1_attributed_to_each"
            row_checkpoint = {"identity": refit_identity, "row": row}
            atomic_json(path, row_checkpoint)
        rows.append(row_checkpoint["row"])
    shared["physical_total_workflow_wall_s"] = (shared["physical_selection_compute_wall_s"]
                                               + bookkeeping_s + sum(
        row["direct_fit_time_s"] + row["test_prediction_wall_s"] for row in rows))
    result = {"identity": identity, "inner_cv_kind": cv_kind, "inner_splits": split_manifest,
              "rows": rows, "shared_bank_accounting": shared,
              "selection_bookkeeping_wall_s": bookkeeping_s,
              "selection_common_accounting_wall_s": selection["selection_common_accounting_wall_s"],
              "candidate_selection_wall_s_by_family": selection["candidate_selection_wall_s_by_family"],
              "selection_bookkeeping_time_kind": selection["selection_bookkeeping_time_kind"]}
    atomic_json(final_path, result)
    return result


def fixed_stage(root, identity, X, y, Xtest, ytest, n_classes, seed, depth,
                include_triple=False, max_features=None):
    params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": max_features}
    fixed_identity = {**identity, "stage": "fixed", "structural_params": params,
                      "forest_counts": list(COUNTS)}
    path = root / "fixed" / f"{structural_id(params)}.json"
    stored = checked_json(path, fixed_identity)
    if stored is not None:
        return stored
    single_rows = []
    for horizon in HORIZONS:
        single_identity = {**fixed_identity, "horizon": horizon, "kind": "single_tree"}
        single_path = path.with_name(path.stem + f"__single_k{horizon}.json")
        single = checked_json(single_path, single_identity)
        if single is None:
            tree = new_tree(params, seed, horizon)
            start = time.perf_counter()
            tree.fit(X, y)
            elapsed = time.perf_counter() - start
            prediction_start = time.perf_counter()
            values = proba(tree, Xtest, n_classes)
            row = {"model_id": "cart" if horizon == 1 else f"single_k{horizon}",
                   "n_estimators": 1, "horizon": horizon, "params": common_params(params, seed),
                   "direct_fit_time_s": elapsed, "time_kind": "direct_wall_clock",
                   "test_prediction_wall_s": time.perf_counter() - prediction_start,
                   "actual_depth": int(tree.get_depth()), "n_leaves": int(tree.get_n_leaves()),
                   **scores(ytest, values)}
            single = {"identity": single_identity, "row": row}
            atomic_json(single_path, single)
            del tree
        single_rows.append(single["row"])
    forest_path = path.with_name(path.stem + "__curves.json")
    forests = structural_block(forest_path, fixed_identity, X, y, Xtest, ytest, n_classes,
                               seed, params, include_triple)
    result = {"identity": fixed_identity, "single_trees": single_rows, **{
        key: value for key, value in forests.items() if key != "identity"}}
    atomic_json(path, result)
    return result


def full_result(root, identity):
    path = root / "results.json"
    stored = checked_json(path, identity)
    if stored is not None:
        return stored
    blocks = []
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            expected = {**identity, "stage": "fixed", "structural_params": params,
                        "forest_counts": list(COUNTS)}
            block = checked_json(root / "fixed" / f"{structural_id(params)}.json", expected)
            if block is None:
                return None
            blocks.append(block)
    tuned = checked_json(root / "tuned.json", identity)
    if tuned is None:
        return None
    fixed_rows = {row["candidate_id"]: row for block in blocks for row in block["rows"]}
    tuned_rows = {row["family"]: row for row in tuned["rows"]}
    contrasts = []
    for contrast in primary_contrasts():
        rows = fixed_rows if contrast["stage"] == "fixed" else tuned_rows
        left, right = rows[contrast["left"]], rows[contrast["right"]]
        contrasts.append({**contrast, "left_accuracy": left["accuracy"],
                          "right_accuracy": right["accuracy"],
                          "accuracy_difference": left["accuracy"] - right["accuracy"]})
    result = {"identity": identity, "complete_protocol_task": True, "fixed": blocks,
              "tuned": tuned, "primary_contrasts": contrasts,
              "other_curves_status": "descriptive"}
    atomic_json(path, result)
    return result


def data_identity(dataset, X, y, out):
    import pandas as pd

    source = Path(out) / ".cache/pmlb" / dataset / f"{dataset}.tsv.gz"
    raw = pd.read_csv(source, sep="\t", compression="gzip")
    complete = raw.notna().all(axis=1).to_numpy()
    if int(complete.sum()) != len(y):
        raise ValueError("Raw-source and complete-case training row counts disagree")
    result = {"dataset": dataset, "n_samples": len(y), "n_features": X.shape[1],
              "n_rows_raw": len(raw), "n_rows_used": int(complete.sum()),
              "n_rows_dropped_missing": int((~complete).sum()),
              "missing_by_column": {str(key): int(value) for key, value in raw.isna().sum().items()},
              "used_source_row_index_sha256": array_hash(np.flatnonzero(complete).astype(np.int64)),
              "missingness_policy": "complete_case_all_columns_including_target",
              "n_classes": len(np.unique(y)), "X_float32_sha256": array_hash(X),
              "y_encoded_sha256": array_hash(y),
              "source_tsv_gz_sha256": file_hash(source)}
    path = Path(out) / "data_manifest" / f"{dataset}.json"
    with locked(Path(out) / ".locks" / f"data__{dataset}.lock"):
        if path.exists() and json.loads(path.read_text()) != result:
            raise RuntimeError(f"Dataset changed since checkpoint: {dataset}")
        if not path.exists():
            atomic_json(path, result)
    return result


def evaluate(dataset, seed, out, manifest, stages=("fixed", "tuned"), depths=DEPTHS,
             include_triple=False):
    start = time.perf_counter()
    X, y = load_data(dataset, out)
    data = data_identity(dataset, X, y, out)
    train, test = outer_split(y, seed)
    identity = {"protocol_fingerprint": manifest["protocol_fingerprint"],
                "dataset": dataset, "seed": seed, "data": data,
                "train_index_sha256": array_hash(train), "test_index_sha256": array_hash(test)}
    root = Path(out) / "raw" / manifest["protocol_fingerprint"] / dataset / f"s{seed}"
    results = {}
    with locked(Path(out) / ".locks" / f"{dataset}__s{seed}.lock"):
        split_path = root / "split.json"
        if checked_json(split_path, identity) is None:
            atomic_json(split_path, {"identity": identity, "outer_train_indices": train.tolist(),
                                     "outer_test_indices": test.tolist()})
        Xtrain, ytrain, Xtest, ytest = X[train], y[train], X[test], y[test]
        n_classes = data["n_classes"]
        if "fixed" in stages:
            for depth in depths:
                for features in (None, "sqrt"):
                    label = "all" if features is None else features
                    results[f"fixed_D{depth}_F{label}"] = fixed_stage(
                        root, identity, Xtrain, ytrain, Xtest, ytest, n_classes, seed, depth,
                        include_triple, features)
        if "tuned" in stages:
            results["tuned"] = tuned_stage(root, identity, Xtrain, ytrain, Xtest, ytest,
                                            train, n_classes, seed, include_triple)
        full_result(root, identity)
        # A scope-specific completion marker cannot masquerade as a full run.
        scope = {"stages": list(stages), "fixed_depths": list(depths) if "fixed" in stages else []}
        atomic_json(root / f"complete__{fingerprint(scope)[:16]}.json", {
            "identity": identity, "scope": scope, "invocation_wall_s": time.perf_counter() - start,
            "completed_blocks": list(results)})
    return results


def balanced_shards(metadata, seeds=SEEDS, n_shards=5):
    if n_shards != 5 or tuple(seeds) != SEEDS:
        raise ValueError("The approved allocation is five shards, one per outer seed")
    ordered = sorted(metadata, key=lambda row: (-int(row["n_samples"]) * int(row["n_features"]),
                                                row["dataset"]))
    shards = [[(row["dataset"], seed) for row in ordered] for seed in SEEDS]
    cost = sum(int(row["n_samples"]) * int(row["n_features"]) for row in metadata)
    loads = [cost] * n_shards
    return shards, loads


def self_test():
    all_compositions = compositions(True)
    assert len(compositions()) == 15 and len(all_compositions) == 16
    assert len(structural_grid()) == 12
    for seed in SEEDS:
        expected = np.random.RandomState(seed).randint(INT32_MAX, size=200)
        np.testing.assert_array_equal(tree_seeds(seed), expected)
        np.testing.assert_array_equal(tree_seeds(seed, 20), expected[:20])
        for tree_seed in expected[:3]:
            draw = np.random.RandomState(int(tree_seed)).randint(17, size=17)
            np.testing.assert_array_equal(bootstrap_counts(17, tree_seed), np.bincount(draw, minlength=17))
        for count in COUNTS:
            for _, ticks in all_compositions:
                selected = schedule(seed, count, ticks)
                assert len(selected) == count
                assert tuple(int(np.sum(selected == h)) for h in HORIZONS) == tuple(count * t // 20 for t in ticks)
                np.testing.assert_array_equal(selected, schedule(seed, count, ticks))
                np.testing.assert_array_equal(selected, schedule(seed, 200, ticks)[:count])
                for start in range(0, count, 20):
                    assert tuple(int(np.sum(selected[start:start + 20] == h)) for h in HORIZONS) == ticks
            for near, far in ((1, 2), (1, 3), (2, 3)):
                previous = set()
                for ticks in (1, 2, 5, 10):
                    weights = [0, 0, 0]
                    weights[near - 1], weights[far - 1] = 20 - ticks, ticks
                    positions = set(np.flatnonzero(schedule(seed, count, weights) == far))
                    assert previous <= positions
                    previous = positions
    banks = {h: {"values": np.full((200, 2, 2), h, dtype=float),
                 "fit_s": np.arange(200, dtype=float) + h,
                 "predict_s": np.ones(200), "depth": np.full(200, h),
                 "leaves": np.full(200, h + 1)} for h in HORIZONS}
    selected = schedule(1000, 20, (17, 2, 1))
    values, costs = pooled(banks, selected)
    np.testing.assert_allclose(values, np.full((2, 2), 1.2))
    assert costs["fit_work_s"] == sum(slot + int(h) for slot, h in enumerate(selected))
    params = structural_grid()[0]
    rows, _ = curves(banks, np.array([0, 1]), 1000, params)
    assert len(rows) == 75
    folds = [{"fold": fold, "rows": [dict(row, accuracy=0.5) for row in rows]} for fold in range(2)]
    assert choose_candidate(folds, "rf")["composition_id"] == "pure_k1"
    assert choose_candidate(folds, "mixed_k2")["composition_twentieths"][2] == 0
    assert choose_candidate(folds, "mixed")["n_estimators"] == 20
    cv_rows, _ = curves(banks, np.array([0, 1]), 1000, params, counts=SELECTION_COUNTS)
    assert len(cv_rows) == 60
    assert sum(family_accepts(row, "rf") for row in cv_rows) == 4
    assert sum(family_accepts(row, "mixed_k2") for row in cv_rows) == 24
    assert len(primary_contrasts()) == 11
    tie_rows = [dict(row, accuracy=0.5, fit_work_s=1.0) for row in rows]
    winner = choose_candidate([{"fold": 0, "rows": tie_rows}], "mixed")
    assert winner["candidate_id"] == min(row["candidate_id"] for row in tie_rows)
    for labels, expected in ((np.array([0, 0, 1, 1]), 2),
                             (np.array([0, 0, 0, 1]), 3), (np.zeros(6, dtype=int), 3),
                             (np.array([0, 0, 0, 2, 2, 2]), 3),
                             (np.array([0, 0, 1, 1, 2]), 3)):
        splits, _ = inner_splits(labels, 1000)
        assert len(splits) == expected
        for train, validation in splits:
            assert not set(train) & set(validation)
    shards, _ = balanced_shards(dataset_metadata())
    tasks = [task for shard in shards for task in shard]
    assert len(tasks) == 285 and len(set(tasks)) == 285
    assert [len(shard) for shard in shards] == [57] * 5
    assert balanced_shards(dataset_metadata())[0] == shards
    for index, shard in enumerate(shards):
        assert {seed for _, seed in shard} == {1000 + index}
        assert {name for name, _ in shard} == set(dataset_names())
    with tempfile.TemporaryDirectory(prefix="array-fair-unit-") as directory:
        path = Path(directory) / "checkpoint.json"
        identity = {"protocol": "test"}
        atomic_json(path, {"identity": identity, "rows": rows})
        assert checked_json(path, identity)["rows"] == rows
        try:
            checked_json(path, {"protocol": "other"})
        except RuntimeError:
            pass
        else:
            raise AssertionError("Resume accepted incompatible identity")
        test_bank = {**banks[1], "completed_slots": 20, "wall_s": 1.0, "preparation_s": 0.1}
        bank_identity = {"protocol_fingerprint": "test", "bank_size": 200,
                         "probability_shape": [200, 2, 2]}
        bank_path = Path(directory) / "bank.npz"
        save_bank(bank_path, bank_identity, test_bank)
        loaded = read_bank(bank_path, bank_identity)
        assert loaded["completed_slots"] == 20
        np.testing.assert_array_equal(loaded["values"], test_bank["values"])
        assert not list(Path(directory).glob("*.tmp*"))
        guard_manifest(Path(directory), {"protocol_fingerprint": "test", "documentation_sha256": "a"})
        guard_manifest(Path(directory), {"protocol_fingerprint": "test", "documentation_sha256": "b"})
        try:
            guard_manifest(Path(directory), {"protocol_fingerprint": "different"})
        except RuntimeError:
            pass
        else:
            raise AssertionError("Resume accepted changed protocol")
        root = Path(directory) / "full"
        assert full_result(root, identity) is None
        for depth in DEPTHS:
            for features in (None, "sqrt"):
                params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
                block_identity = {**identity, "stage": "fixed", "structural_params": params,
                                  "forest_counts": list(COUNTS)}
                block_rows, _ = curves(banks, np.array([0, 1]), 1000, params)
                atomic_json(root / "fixed" / f"{structural_id(params)}.json",
                            {"identity": block_identity, "rows": block_rows})
        assert full_result(root, identity) is None
        atomic_json(root / "tuned.json", {"identity": identity,
                                          "rows": [{"family": family, "accuracy": 0.5}
                                                   for family in FAMILIES]})
        final = full_result(root, identity)
        assert final["complete_protocol_task"] and len(final["primary_contrasts"]) == 11
    print("Pure-function tests passed", flush=True)


def pilot():
    """Small synthetic integration check, never a dataset/seed production run."""
    load_runtime()
    rng = np.random.RandomState(42)
    X = np.asarray(rng.randint(0, 4, size=(24, 2)), dtype=np.float32)
    y = (X[:, 0].astype(int) % 2 ^ X[:, 1].astype(int) % 2).astype(np.int64)
    train, test = outer_split(y, 1000)
    Xtrain, ytrain, Xtest, ytest = X[train], y[train], X[test], y[test]
    params = {"max_depth": 3, "min_samples_leaf": 1, "max_features": None}
    with tempfile.TemporaryDirectory(prefix="array-fair-pilot-") as directory:
        root = Path(directory)
        identity = {"protocol_fingerprint": "synthetic-pilot", "seed": 1000}
        block = fixed_stage(root, identity, Xtrain, ytrain, Xtest, ytest, 2, 1000, 3, True)
        assert len(block["rows"]) == 80 and len(block["single_trees"]) == 3
        banks = {}
        for horizon in HORIZONS:
            path = root / "fixed" / f"{structural_id(params)}__curves.k{horizon}.npz"
            bank_identity = {**identity, "stage": "fixed", "structural_params": params,
                             "horizon": horizon, "forest_counts": list(COUNTS), "bank_size": 200,
                             "probability_shape": [200, len(Xtest), 2],
                             "tree_seed_sha256": array_hash(tree_seeds(1000))}
            banks[horizon] = read_bank(path, bank_identity)
            assert banks[horizon]["completed_slots"] == 200
        for features in (None, "sqrt"):
            trial = {**params, "max_features": features}
            bank = banks[1] if features is None else fit_bank(Xtrain, ytrain, Xtest, 2, 1000, trial, 1)
            for count in COUNTS:
                forest = make_forest(trial, 1000, count).fit(Xtrain, ytrain)
                values, _ = pooled({1: bank}, np.ones(count, dtype=np.int8))
                np.testing.assert_allclose(values, proba(forest, Xtest, 2), rtol=0, atol=1e-14)
                np.testing.assert_array_equal([t.random_state for t in forest.estimators_], tree_seeds(1000, count))
        composition, ticks = compositions(True)[-1]
        candidate = {"params": params, "n_estimators": 20, "composition_twentieths": ticks,
                     "composition_id": composition}
        direct, _ = direct_mixed(Xtrain, ytrain, Xtest, 2, 1000, candidate)
        expected, _ = pooled(banks, schedule(1000, 20, ticks))
        np.testing.assert_allclose(direct, expected, rtol=0, atol=1e-14)
        reloaded = fixed_stage(root, identity, Xtrain, ytrain, Xtest, ytest, 2, 1000, 3, True)
        assert block == reloaded
        from unittest.mock import patch

        # Pilot fixture narrows structures only; production always uses all 12.
        trial = {"max_depth": 3, "min_samples_leaf": 5, "max_features": "sqrt"}
        with patch(__name__ + ".structural_grid", return_value=(trial,)):
            tuned = tuned_stage(root, identity, Xtrain, ytrain, Xtest, ytest, train, 2, 1000)
        assert {row["family"] for row in tuned["rows"]} == set(FAMILIES)
        assert all(row["selected"]["n_estimators"] <= 100 for row in tuned["rows"])
        with patch(__name__ + ".new_tree", side_effect=AssertionError("Completed checkpoint refit")):
            assert tuned_stage(root, identity, Xtrain, ytrain, Xtest, ytest, train, 2, 1000) == tuned
        partial_identity = {"protocol_fingerprint": "synthetic-pilot", "bank_size": 40,
                            "probability_shape": [40, len(Xtest), 2]}
        partial = {key: banks[1][key][:40].copy() for key in
                   ("values", "fit_s", "predict_s", "depth", "leaves")}
        partial.update(completed_slots=20, wall_s=0.0, preparation_s=0.0)
        partial_path = root / "partial.npz"
        save_bank(partial_path, partial_identity, partial)
        with patch(__name__ + ".new_tree", wraps=new_tree) as constructor:
            resumed = bank_cache(partial_path, partial_identity, Xtrain, ytrain, Xtest, 2,
                                 1000, params, 1)
            assert constructor.call_count == 20
        np.testing.assert_allclose(resumed["values"], banks[1]["values"][:40], rtol=0, atol=1e-14)
        assert read_bank(partial_path, partial_identity)["completed_slots"] == 40
    print("Pilot passed: RF prefix equivalence, k1/k2/k3, three tuned refits, partial-bank resume", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--n-shards", type=int, choices=(5,), default=5)
    parser.add_argument("--datasets", nargs="+")
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    parser.add_argument("--depths", nargs="+", choices=("3", "6", "None"), default=("3", "6", "None"))
    parser.add_argument("--stage", choices=("fixed", "tune", "both"), default="both")
    parser.add_argument("--include-triple", action="store_true")
    parser.add_argument("--cache-banks", action="store_true", default=True,
                        help="Bank checkpoints are always enabled; this flag is accepted for explicitness")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return
    if args.pilot:
        pilot()
        return
    if args.n_shards < 1 or not 0 <= args.shard_index < args.n_shards:
        parser.error("Require 0 <= shard-index < n-shards")
    if not set(args.seeds) <= set(SEEDS) or len(set(args.seeds)) != len(args.seeds):
        parser.error("Seeds must be unique members of 1000..1004")
    names = args.datasets or dataset_names()
    if not set(names) <= set(dataset_names()) or len(set(names)) != len(names):
        parser.error("Datasets must be unique members of the frozen 57-dataset list")
    depths = tuple(None if depth == "None" else int(depth) for depth in args.depths)
    stages = ("fixed", "tuned") if args.stage == "both" else (("fixed",) if args.stage == "fixed" else ("tuned",))
    if len(set(depths)) != len(depths):
        parser.error("Depths must not contain duplicates")
    if args.out.resolve().is_relative_to((REPO / "paper/array_revision").resolve()):
        parser.error("The older array_revision output must not be modified")
    shards, loads = balanced_shards(dataset_metadata(), SEEDS, args.n_shards)
    tasks = [task for task in shards[args.shard_index] if task[0] in names and task[1] in args.seeds]
    if args.dry_run:
        print(json.dumps({"shard_index": args.shard_index, "n_shards": args.n_shards,
                          "estimated_loads_n_times_p": loads, "tasks": tasks,
                          "structural_settings": 12, "forest_counts": list(COUNTS),
                          "selection_forest_counts": list(SELECTION_COUNTS), "families": list(FAMILIES),
                          "compositions": len(compositions(args.include_triple)),
                          "fit_timeout": None}, indent=2))
        return
    load_runtime()
    manifest = source_manifest(args.include_triple)
    guard_manifest(args.out, manifest)
    from threadpoolctl import threadpool_info

    run_scope = {"shard_index": args.shard_index, "n_shards": args.n_shards,
                 "datasets": names, "seeds": args.seeds, "stage": args.stage,
                 "fixed_depths": list(depths), "cache_banks": args.cache_banks}
    atomic_json(args.out / "launches" / f"{fingerprint(run_scope)}.json", {
        "protocol_fingerprint": manifest["protocol_fingerprint"], "scope": run_scope,
        "tasks": tasks, "all_shard_tasks": shards, "estimated_loads_n_times_p": loads,
        "threadpools": threadpool_info()})
    for index, (dataset, seed) in enumerate(tasks, 1):
        # Detect source changes during a running shard, not just on restart.
        if source_manifest(args.include_triple)["protocol_fingerprint"] != manifest["protocol_fingerprint"]:
            raise RuntimeError("Sources changed while shard was running; stopping before next task")
        print(f"shard={args.shard_index} task={index}/{len(tasks)} {dataset} seed={seed}", flush=True)
        start = time.perf_counter()
        evaluate(dataset, seed, args.out, manifest, stages, depths, args.include_triple)
        print(f"completed in {time.perf_counter() - start:.3f}s", flush=True)


if __name__ == "__main__":
    main()
