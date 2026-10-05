"""Strict independent validation and paired analysis of the frozen fair run.

No estimator is imported or fitted. Fixed-only and full exports stay separate;
partial cohorts are errors, never an invitation to silently subset results.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "array-fair-matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.stats import wilcoxon
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper/array_revision_fair"
SEEDS = tuple(range(1000, 1005))
DEPTHS = (3, 6, None)
COUNTS = (20, 40, 60, 100, 200)
TUNE_COUNTS = COUNTS[:-1]
FAMILIES = ("rf", "mixed_k2", "mixed")
BOOTSTRAPS = 20000
BOOTSTRAP_SEED = 41
HEX = re.compile(r"^[0-9a-f]{64}$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as handle:
        result = hashlib.sha256()
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            result.update(chunk)
    return result.hexdigest()


def array_hash(value):
    value = np.ascontiguousarray(value)
    result = hashlib.sha256(canonical({"dtype": value.dtype.str, "shape": list(value.shape)}).encode())
    result.update(value.tobytes())
    return result.hexdigest()


def number(value, label, minimum=0, maximum=None):
    require(type(value) in (int, float) and np.isfinite(value), f"Invalid number: {label}")
    require(value >= minimum and (maximum is None or value <= maximum), f"Out of range: {label}")
    return float(value)


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, f"Invalid integer: {label}")
    return value


def equal_number(actual, expected, label):
    number(actual, label)
    require(np.isclose(actual, expected, rtol=1e-10, atol=1e-12), f"Numeric mismatch: {label}")


def read_json(path, identity=None):
    require(Path(path).is_file(), f"Incomplete run; missing {path}")
    with Path(path).open() as handle:
        result = json.load(handle, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    require(isinstance(result, dict), f"JSON object required: {path}")
    if identity is not None:
        require(result.get("identity") == identity, f"Identity mismatch: {path}")
    return result


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def compositions():
    result = [(f"pure_k{h}", [20 if i == h else 0 for i in (1, 2, 3)]) for h in (1, 2, 3)]
    for near, far in ((1, 2), (1, 3), (2, 3)):
        for ticks in (1, 2, 5, 10):
            weights = [0, 0, 0]
            weights[near - 1], weights[far - 1] = 20 - ticks, ticks
            result.append((f"pair_k{near}_k{far}_q{ticks * 5:02d}", weights))
    result.append(("triple_85_10_05", [17, 2, 1]))
    return result


def structures():
    return [{"max_depth": d, "min_samples_leaf": leaf, "max_features": f}
            for d in DEPTHS for leaf in (1, 5) for f in ("sqrt", None)]


def structural_id(params):
    features = "all" if params["max_features"] is None else params["max_features"]
    return f"D{params['max_depth']}_L{params['min_samples_leaf']}_F{features}"


def candidate_id(params, count, composition):
    return f"{structural_id(params)}__T{count:03d}__{composition}"


def primary_specs():
    result = []
    for depth in (3, None):
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            for h in (2, 3):
                result.append({"contrast_id": f"fixed__{structural_id(params)}__k{h}_vs_k1",
                               "stage": "fixed", "params": params,
                               "left": candidate_id(params, 100, f"pair_k1_k{h}_q10"),
                               "right": candidate_id(params, 100, "pure_k1")})
    result.extend({"contrast_id": f"tuned__{a}_vs_{b}", "stage": "tuned", "left": a, "right": b}
                  for a, b in (("mixed_k2", "rf"), ("mixed", "rf"), ("mixed", "mixed_k2")))
    return result


def schedule(seed, count, ticks):
    require(count in COUNTS and len(ticks) == 3 and sum(ticks) == 20, "Invalid schedule")
    for value in ticks:
        integer(value, "composition twentieths")
    base = next(i + 1 for i, value in enumerate(ticks) if value)
    assignment = np.full(count, base, dtype=np.int8)
    rng = np.random.RandomState(seed + 130363)
    for start in range(0, count, 20):
        slots, offset = start + rng.permutation(20), 0
        for h in range(base + 1, 4):
            assignment[slots[offset:offset + ticks[h - 1]]] = h
            offset += ticks[h - 1]
    return assignment


def accepts(row, family):
    return (row["composition_id"] == "pure_k1" if family == "rf" else
            row["composition_twentieths"][2] == 0 if family == "mixed_k2" else family == "mixed")


def family(name):
    for prefix in ("GAMETES", "monk", "led", "parity5", "analcatdata_cyyoung"):
        if name.startswith(prefix):
            return prefix
    return name


def synthetic(name):
    return name.startswith(("GAMETES", "monk", "led", "parity5")) or name in {
        "prnn_synth", "mux6", "corral", "threeOf9", "mofn_3_7_10", "xd6", "tic_tac_toe"}


def ci(values):
    values = np.asarray(values, dtype=float)
    require(values.ndim == 1 and len(values) > 0 and np.isfinite(values).all(), "Invalid CI units")
    draws = np.random.default_rng(BOOTSTRAP_SEED).choice(values, (BOOTSTRAPS, len(values)), replace=True)
    return tuple(float(value) for value in np.quantile(draws.mean(axis=1), (0.025, 0.975)))


def holm(values):
    values = np.asarray(values, dtype=float)
    require(np.isfinite(values).all() and np.all((values >= 0) & (values <= 1)), "Invalid p values")
    order = np.argsort(values, kind="stable")
    result = np.empty_like(values)
    result[order] = np.minimum(1, np.maximum.accumulate((len(values) - np.arange(len(values))) * values[order]))
    return result


def p_value(values):
    values = np.round(np.asarray(values, dtype=float), 12)
    return 1.0 if not np.any(values) else float(wilcoxon(values, zero_method="wilcox",
                                                       alternative="two-sided", method="auto").pvalue)


def check_protocol(out, snapshot=None, check_sources=True):
    protocol = read_json(snapshot if snapshot is not None else out / "protocol.json")
    payload = {key: value for key, value in protocol.items()
               if key not in ("protocol_fingerprint", "documentation_sha256")}
    require(protocol.get("protocol_fingerprint") == digest(payload), "Protocol fingerprint is not self-consistent")
    names = pd.read_csv(REPO / "paper/tables/mixed_sighted_dataset_sample.csv").dataset.tolist()
    expected = {"schema": "array-fair-v1", "datasets": names, "outer_seeds": list(SEEDS),
                "counts": list(COUNTS), "selection_counts": list(TUNE_COUNTS),
                "selection_bank_size": 100, "horizons": [1, 2, 3], "selection_families": list(FAMILIES),
                "fixed_depths": list(DEPTHS), "fixed_leaf": 1, "fixed_feature_modes": [None, "sqrt"],
                "structural_grid": structures(), "primary_contrasts": primary_specs(),
                "compositions": [{"id": key, "twentieths": weights} for key, weights in compositions()],
                "predictor_dtype": "float32", "criterion": "gini", "min_samples_split": 2,
                "ccp_alpha": 0.0, "fit_timeout": None, "test_size": 0.25, "inner_seed_offset": 7,
                "checkpoint_every_slots": 20, "tie_break": ["accuracy_desc", "fit_work_asc", "id_asc"]}
    for key, value in expected.items():
        require(protocol.get(key) == value, f"Frozen protocol mismatch: {key}")
    require({"paper/scripts/run_array_fair_benchmark.py", "paper/scripts/fair_revision_runtime.py",
             "paper/array_revision_fair/runtime/_sighted_fast.pyx", "treeple/tree/_lookahead.py"}
            <= set(protocol.get("source_hashes", {})), "Core frozen source hashes missing")
    require(len(names) == 57 and len(set(names)) == 57, "Expected 57 datasets")
    require(len({family(name) for name in names}) == 48, "Known-family sensitivity must have 48 groups")
    require(sum(not synthetic(name) for name in names) == 38, "Non-synthetic sensitivity must have 38 datasets")
    require(bool(protocol.get("source_hashes")), "Missing source fingerprints")
    for key, value in protocol["source_hashes"].items():
        require(bool(HEX.fullmatch(value)), f"Malformed source hash: {key}")
        if check_sources:
            path = Path(key) if Path(key).is_absolute() else REPO / key
            require(path.is_file() and file_hash(path) == value, f"Frozen implementation hash mismatch: {key}")
    return protocol


def required_paths(out, protocol, fixed_only):
    root = out / "raw" / protocol["protocol_fingerprint"]
    result = []
    for name in protocol["datasets"]:
        for seed in SEEDS:
            task = root / name / f"s{seed}"
            result.append(task / "split.json")
            for depth in DEPTHS:
                for features in (None, "sqrt"):
                    params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
                    result.append(task / "fixed" / f"{structural_id(params)}.json")
            if not fixed_only:
                result.extend(task / file for file in ("tuned.json", "selection.json", "results.json"))
                result.extend(task / f"refit_{fam}.json" for fam in FAMILIES)
    return result


def preflight(out, protocol, fixed_only):
    root = out / "raw" / protocol["protocol_fingerprint"]
    paths = required_paths(out, protocol, fixed_only)
    missing = [path for path in paths if not path.is_file()]
    require(not missing, f"Incomplete {'fixed' if fixed_only else 'full'} run: {len(missing)} missing files; "
            + ", ".join(str(path) for path in missing[:4]))
    require({p.name for p in root.iterdir() if p.is_dir()} == set(protocol["datasets"]), "Unexpected dataset tasks")
    for name in protocol["datasets"]:
        actual = {p.name for p in (root / name).iterdir() if p.is_dir()}
        require(actual == {f"s{s}" for s in SEEDS}, f"Unexpected seed tasks: {name}")


def check_data(out, name):
    metadata = read_json(out / "data_manifest" / f"{name}.json")
    source = out / ".cache/pmlb" / name / f"{name}.tsv.gz"
    require(source.is_file() and file_hash(source) == metadata["source_tsv_gz_sha256"], f"Data-source hash: {name}")
    frame = pd.read_csv(source, sep="\t", compression="gzip")
    mask = frame.notna().all(axis=1).to_numpy()
    complete = frame.loc[mask]
    X = np.ascontiguousarray(complete.drop(columns="target"), dtype=np.float32)
    _, y = np.unique(complete.target.to_numpy(), return_inverse=True)
    y = np.ascontiguousarray(y, dtype=np.int64)
    require(np.isfinite(X).all(), f"Nonfinite predictors: {name}")
    expected = {"dataset": name, "n_samples": len(y), "n_features": X.shape[1],
                "n_classes": len(np.unique(y)), "n_rows_raw": len(frame), "n_rows_used": len(y),
                "n_rows_dropped_missing": int((~mask).sum()), "X_float32_sha256": array_hash(X),
                "y_encoded_sha256": array_hash(y),
                "used_source_row_index_sha256": array_hash(np.flatnonzero(mask).astype(np.int64)),
                "missing_by_column": {str(k): int(v) for k, v in frame.isna().sum().items()},
                "missingness_policy": "complete_case_all_columns_including_target"}
    for key, value in expected.items():
        require(metadata.get(key) == value, f"Data manifest mismatch: {name}/{key}")
    for key in ("n_samples", "n_features", "n_classes", "n_rows_raw", "n_rows_used"):
        integer(metadata[key], f"{name}/{key}", 1)
    return metadata, y


def check_split(path, protocol, metadata, y, seed):
    train, test = train_test_split(np.arange(len(y), dtype=np.int64), test_size=.25,
                                  stratify=y, random_state=seed)
    identity = {"protocol_fingerprint": protocol["protocol_fingerprint"], "dataset": metadata["dataset"],
                "seed": seed, "data": metadata, "train_index_sha256": array_hash(train),
                "test_index_sha256": array_hash(test)}
    split = read_json(path, identity)
    require(split.get("outer_train_indices") == train.tolist() and split.get("outer_test_indices") == test.tolist(),
            f"Unpaired outer split: {path}")
    return identity, train, test


def common_params(params, seed):
    return {**params, "criterion": "gini", "min_samples_split": 2, "min_weight_fraction_leaf": 0.0,
            "min_impurity_decrease": 0.0, "random_state": seed}


def check_params(actual, expected, label):
    require(isinstance(actual, dict) and set(actual) == set(expected), f"Parameter fields: {label}")
    for key, value in expected.items():
        require(actual[key] == value, f"Parameter mismatch {label}/{key}")
        if type(value) is int:
            integer(actual[key], f"{label}/{key}")
        elif type(value) is float:
            number(actual[key], f"{label}/{key}")
        elif type(value) is bool:
            require(type(actual[key]) is bool, f"Boolean parameter type: {label}/{key}")
        elif isinstance(value, list):
            require(isinstance(actual[key], list), f"List parameter type: {label}/{key}")
            for element in actual[key]:
                integer(element, f"{label}/{key}")


def check_bank(path, block_identity, metadata, horizon, y):
    size = max(block_identity["forest_counts"])
    seeds = np.random.RandomState(block_identity["seed"]).randint(np.iinfo(np.int32).max, size=200)[:size]
    expected = {**block_identity, "horizon": horizon, "bank_size": size,
                "probability_shape": [size, len(y), block_identity["data"]["n_classes"]],
                "tree_seed_sha256": array_hash(seeds)}
    require(path.is_file(), f"Incomplete bank; missing {path}")
    with np.load(path, allow_pickle=False) as archive:
        require(json.loads(str(archive["identity"].item())) == expected, f"Bank identity: {path}")
        complete = integer(archive["completed_slots"].item(), "Completed bank slots")
        require(complete == size, f"Pending bank is not complete: {path}")
        bank = {key: archive[key].copy() for key in ("values", "fit_s", "predict_s", "depth", "leaves")}
        bank.update({key: float(archive[key].item()) for key in ("wall_s", "preparation_s")})
    require(bank["values"].shape == tuple(expected["probability_shape"]), f"Probability shape: {path}")
    require(bank["values"].dtype == np.float64, f"Probability precision changed: {path}")
    require(np.isfinite(bank["values"]).all() and np.all(bank["values"] >= -1e-12)
            and np.all(bank["values"] <= 1 + 1e-12), f"Invalid probabilities: {path}")
    require(np.allclose(bank["values"].sum(axis=2), 1, rtol=0, atol=1e-12), f"Probability normalization: {path}")
    for key in ("fit_s", "predict_s", "depth", "leaves"):
        array = bank[key]
        require(array.shape == (size,) and np.isfinite(array).all() and np.all(array >= (1 if key == "leaves" else 0)),
                f"Invalid slot metric {key}: {path}")
        if key in ("depth", "leaves"):
            require(np.issubdtype(array.dtype, np.integer), f"Noninteger tree metric: {path}")
    depth = block_identity["structural_params"]["max_depth"]
    require(depth is None or np.all(bank["depth"] <= depth), f"Depth cap exceeded: {path}")
    for key, source in (("fit_s_by_slot", "fit_s"), ("predict_s_by_slot", "predict_s"),
                        ("actual_depth_by_slot", "depth"), ("n_leaves_by_slot", "leaves")):
        require(metadata.get(key) == bank[source].tolist(), f"JSON/NPZ slot mismatch {key}: {path}")
    for key, expected_value in (("fit_work_s", bank["fit_s"].sum()),
                                ("prediction_work_s", bank["predict_s"].sum()),
                                ("bank_wall_s", bank["wall_s"]), ("preparation_wall_s", bank["preparation_s"]),
                                ("mean_actual_depth", bank["depth"].mean())):
        equal_number(metadata[key], float(expected_value), f"{path}/{key}")
    return bank


def pool(banks, assignment):
    count = len(assignment)
    values = np.zeros_like(banks[1]["values"][0])
    metrics = {"fit_work_s": 0.0, "prediction_work_s": 0.0, "mean_actual_depth": 0.0, "mean_n_leaves": 0.0}
    for slot, h in enumerate(assignment):
        bank = banks[int(h)]
        values += bank["values"][slot]
        metrics["fit_work_s"] += float(bank["fit_s"][slot])
        metrics["prediction_work_s"] += float(bank["predict_s"][slot])
        metrics["mean_actual_depth"] += float(bank["depth"][slot]) / count
        metrics["mean_n_leaves"] += float(bank["leaves"][slot]) / count
    return values / count, metrics


def probability_scores(y, values):
    predicted = values.argmax(axis=1)
    return {"accuracy": float(np.mean(predicted == y)),
            "balanced_accuracy": float(np.mean([np.mean(predicted[y == c] == c) for c in np.unique(y)]))}


def check_block(path, expected_identity, y, single_trees=False):
    block = read_json(path, expected_identity)
    params, seed = expected_identity["structural_params"], expected_identity["seed"]
    check_params(block["identity"]["structural_params"], params, "Structural identity")
    counts = expected_identity["forest_counts"]
    require(params in structures(), f"Structural grid: {path}")
    for key in ("min_samples_leaf",):
        integer(params[key], key, 1)
    require(set(block.get("banks", {})) == {"1", "2", "3"}, f"Missing horizon metadata: {path}")
    banks = {h: check_bank(path.with_name(path.stem + "__curves").with_suffix(f".k{h}.npz")
                           if single_trees else path.with_suffix(f".k{h}.npz"),
                           expected_identity, block["banks"][str(h)], h, y) for h in (1, 2, 3)}
    expected_rows = {candidate_id(params, count, name): (count, name, weights)
                     for count in counts for name, weights in compositions()}
    rows = block.get("rows", [])
    require(len(rows) == len(expected_rows) and len({r.get("candidate_id") for r in rows}) == len(rows),
            f"Incomplete/duplicate forest rows: {path}")
    require({r.get("candidate_id") for r in rows} == set(expected_rows), f"Unexpected candidate IDs: {path}")
    evaluation = {fam: 0.0 for fam in FAMILIES}
    for row in rows:
        count, name, weights = expected_rows[row["candidate_id"]]
        require(row.get("params") == params and row.get("composition_id") == name
                and row.get("composition_twentieths") == weights and row.get("n_estimators") == count,
                f"Candidate attributes: {path}/{row['candidate_id']}")
        integer(row["n_estimators"], "n_estimators", 1)
        check_params(row["params"], params, "Forest row")
        for weight in row["composition_twentieths"]:
            integer(weight, "stored composition twentieths")
        for value in row["horizon_counts"]:
            integer(value, "stored horizon count")
        assignment = schedule(seed, count, weights)
        require(row.get("horizon_counts") == [count * w // 20 for w in weights]
                and row.get("slot_horizon_sha256") == array_hash(assignment), f"Composition slots: {path}")
        require(row.get("time_kind") == "measured_selected_tree_fit_sum", f"Mislabelled fixed work: {path}")
        values, metrics = pool(banks, assignment)
        for key, value in {**metrics, **probability_scores(y, values)}.items():
            equal_number(row[key], value, f"{path}/{name}/{key}")
        for key in ("accuracy", "balanced_accuracy"):
            number(row[key], key, maximum=1)
        duration = number(row["schedule_evaluation_wall_s"], "schedule evaluation")
        for fam in FAMILIES:
            if accepts(row, fam):
                evaluation[fam] += duration
    for fam in FAMILIES:
        equal_number(block[f"{fam}_schedule_evaluation_wall_s"], evaluation[fam], "Schedule attribution")
    equal_number(block["block_compute_wall_s"], sum(b["wall_s"] for b in banks.values()) + evaluation["mixed"], "Block wall sum")
    number(block["block_invocation_wall_s"], "Block invocation")
    if single_trees:
        trees = block.get("single_trees", [])
        require(len(trees) == 3 and {r.get("horizon") for r in trees} == {1, 2, 3}, f"Single-tree coverage: {path}")
        for row in trees:
            h = integer(row["horizon"], "horizon", 1)
            require(row.get("model_id") == ("cart" if h == 1 else f"single_k{h}")
                    and row.get("params") == common_params(params, seed) and row.get("n_estimators") == 1,
                    f"Single-tree common parameters: {path}")
            integer(row["n_estimators"], "single n_estimators", 1)
            check_params(row["params"], common_params(params, seed), "Single-tree row")
            actual = integer(row["actual_depth"], "actual depth")
            integer(row["n_leaves"], "leaves", 1)
            require(params["max_depth"] is None or actual <= params["max_depth"], f"Single depth cap: {path}")
            for key in ("accuracy", "balanced_accuracy"):
                number(row[key], key, maximum=1)
            for key in ("direct_fit_time_s", "test_prediction_wall_s"):
                number(row[key], key)
            require(row.get("time_kind") == "direct_wall_clock", f"Single-tree timing: {path}")
            single_identity = {**expected_identity, "horizon": h, "kind": "single_tree"}
            single_path = path.with_name(path.stem + f"__single_k{h}.json")
            require(read_json(single_path, single_identity).get("row") == row, "Single-tree checkpoint mismatch")
    else:
        integer(block.get("fold"), "Fold ID")
        require(block.get("fold") == expected_identity["fold"], f"Fold ID: {path}")
    return block


def cv_splits(y, seed):
    _, counts = np.unique(y, return_counts=True)
    if len(counts) == 1 or counts.min() < 2:
        splitter, kind = KFold(3, shuffle=True, random_state=seed + 7), "KFold_3_single_or_rare_class"
    else:
        folds = min(3, int(counts.min()))
        splitter, kind = StratifiedKFold(folds, shuffle=True, random_state=seed + 7), f"StratifiedKFold_{folds}"
    return list(splitter.split(np.zeros((len(y), 1)), y)), kind


def choose(blocks, fam, n_folds):
    grouped = {}
    for block in blocks:
        for row in block["rows"]:
            if accepts(row, fam):
                grouped.setdefault(row["candidate_id"], {})
                require(block["fold"] not in grouped[row["candidate_id"]], "Duplicate candidate/fold record")
                grouped[row["candidate_id"]][block["fold"]] = row
    require(len(grouped) == {"rf": 48, "mixed_k2": 288, "mixed": 768}[fam], "Selection candidate space")
    candidates = []
    for rows in grouped.values():
        require(set(rows) == set(range(n_folds)), "Incomplete candidate CV folds")
        ordered = [rows[fold] for fold in range(n_folds)]
        candidate = {key: ordered[0][key] for key in
                     ("candidate_id", "composition_id", "composition_twentieths", "params", "n_estimators")}
        candidate.update(mean_validation_accuracy=float(np.mean([r["accuracy"] for r in ordered])),
                         mean_validation_fit_work_s=float(np.mean([r["fit_work_s"] for r in ordered])),
                         n_inner_folds=n_folds)
        candidates.append(candidate)
    return min(candidates, key=lambda r: (-r["mean_validation_accuracy"], r["mean_validation_fit_work_s"], r["candidate_id"]))


def check_tuned(root, identity, train, y):
    tuned = read_json(root / "tuned.json", identity)
    selection = read_json(root / "selection.json", identity)
    splits, kind = cv_splits(y[train], identity["seed"])
    split_manifest, blocks = [], []
    for fold, (inner_train, validation) in enumerate(splits):
        split = {"fold": fold, "inner_train_index_sha256": array_hash(train[inner_train]),
                 "inner_validation_index_sha256": array_hash(train[validation])}
        split_manifest.append(split)
        for params in structures():
            expected = {**identity, "stage": "inner_cv", **split, "structural_params": params,
                        "forest_counts": list(TUNE_COUNTS)}
            path = root / "inner" / f"fold{fold}__{structural_id(params)}.json"
            blocks.append(check_block(path, expected, y[train[validation]]))
    require(tuned.get("inner_cv_kind") == selection.get("inner_cv_kind") == kind, "CV kind")
    require(tuned.get("inner_splits") == selection.get("inner_splits") == split_manifest, "Unpaired CV splits")
    rows = tuned.get("rows", [])
    require(len(rows) == 3 and {r.get("family") for r in rows} == set(FAMILIES), "Three tuned families required")
    candidates = {fam: choose(blocks, fam, len(splits)) for fam in FAMILIES}
    require(selection.get("selected") == candidates, "Locked selection is not the CV winner")
    for fam, candidate in candidates.items():
        check_params(selection["selected"][fam]["params"], candidate["params"], f"Locked {fam} parameters")
        for value in selection["selected"][fam]["composition_twentieths"]:
            integer(value, "Locked composition weights")
    accounting = {}
    for fam, horizons in (("rf", (1,)), ("mixed_k2", (1, 2)), ("mixed", (1, 2, 3))):
        accounting[fam] = {key: float(sum(block["banks"][str(h)][source] for block in blocks for h in horizons))
                           for key, source in (("selection_fitting_work_s", "fit_work_s"),
                                               ("selection_prediction_work_s", "prediction_work_s"),
                                               ("selection_bank_wall_s", "bank_wall_s"))}
        accounting[fam]["selection_schedule_evaluation_wall_s"] = float(sum(
            block[f"{fam}_schedule_evaluation_wall_s"] for block in blocks))
        accounting[fam]["selection_workflow_wall_s"] = (accounting[fam]["selection_bank_wall_s"]
                                                        + accounting[fam]["selection_schedule_evaluation_wall_s"])
        for key, expected in accounting[fam].items():
            equal_number(selection["family_accounting"][fam][key], expected, f"Selection work {fam}/{key}")
        require(selection["family_accounting"][fam].get("selection_time_kind") == "measured_fit_work_not_wall_time",
                "Selection fit work must not be labeled wall time")
    for row in rows:
        fam, candidate = row["family"], candidates[row["family"]]
        require(row.get("selected") == candidate, f"Refit does not use locked candidate: {fam}")
        check_params(row["selected"]["params"], candidate["params"], f"Selected {fam} parameters")
        require(candidate["params"] in structures() and candidate["n_estimators"] in TUNE_COUNTS
                and accepts(candidate, fam), f"Tuned common grid/horizon eligibility: {fam}")
        integer(candidate["n_estimators"], "selected n_estimators", 1)
        expected_config = {**common_params(candidate["params"], identity["seed"]), "ccp_alpha": 0.0,
                           "n_estimators": candidate["n_estimators"], "bootstrap": True, "n_jobs": 1,
                           "composition_twentieths": candidate["composition_twentieths"],
                           "estimator": "sklearn.RandomForestClassifier" if fam == "rf" else "prepared_weighted_mixture"}
        require(row.get("refit_model_config") == expected_config, f"Refit model common attributes: {fam}")
        check_params(row["refit_model_config"], expected_config, f"Refit {fam}")
        for weight in candidate["composition_twentieths"]:
            integer(weight, "Selected composition twentieths")
        refit_identity = {**identity, "stage": "selected_refit", "family": fam, "candidate": candidate}
        require(read_json(root / f"refit_{fam}.json", refit_identity).get("row") == row, "Refit/tuned row mismatch")
        require(row.get("time_kind") == "direct_wall_clock", "Tuned refit must use direct wall time")
        require(row.get("selection_time_kind") == "measured_fit_work_not_wall_time"
                and row.get("workflow_time_kind") == "sum_measured_stage_wall_times_shared_k1_attributed_to_each",
                "Tuned selection/workflow timing labels")
        for key in ("accuracy", "balanced_accuracy"):
            number(row[key], key, maximum=1)
        for key in ("direct_fit_time_s", "test_prediction_wall_s", "selection_bookkeeping_attributed_wall_s",
                    "mean_actual_depth", "mean_n_leaves", "total_workflow_wall_s", "total_fitting_work_s"):
            number(row[key], key)
        cap = candidate["params"]["max_depth"]
        require(cap is None or row["mean_actual_depth"] <= cap, "Tuned depth cap")
        for key, expected in accounting[fam].items():
            equal_number(row[key], expected, f"Tuned selection attribution {fam}/{key}")
        attributed = (selection["selection_common_accounting_wall_s"]
                      + selection["candidate_selection_wall_s_by_family"][fam])
        equal_number(row["selection_bookkeeping_attributed_wall_s"], attributed, "Family bookkeeping")
        equal_number(row["total_workflow_wall_s"], accounting[fam]["selection_workflow_wall_s"] + attributed
                     + row["direct_fit_time_s"] + row["test_prediction_wall_s"], "Family workflow sum")
        refit_work = row["direct_fit_time_s"] if fam == "rf" else row["refit_tree_fit_work_s"]
        equal_number(row["total_fitting_work_s"], accounting[fam]["selection_fitting_work_s"] + refit_work, "Fitting total")
        require(row.get("total_fitting_measurement_kind") == ("selection_tree_fit_sum_plus_actual_rf_refit_wall"
                if fam == "rf" else "selection_and_refit_tree_fit_sum"), "Fit-sum/wall labeling")
        if fam != "rf":
            require(row.get("slot_horizon_sha256") == array_hash(schedule(identity["seed"], candidate["n_estimators"],
                                                                         candidate["composition_twentieths"])), "Refit slots")
    shared = tuned["shared_bank_accounting"]
    expected_shared = {"shared_k1_fit_work_s": accounting["rf"]["selection_fitting_work_s"],
                       "shared_k1_prediction_work_s": accounting["rf"]["selection_prediction_work_s"],
                       "shared_k1_bank_wall_s": accounting["rf"]["selection_bank_wall_s"],
                       "shared_k1_schedule_wall_s": accounting["rf"]["selection_schedule_evaluation_wall_s"],
                       "shared_k2_fit_work_s": sum(b["banks"]["2"]["fit_work_s"] for b in blocks),
                       "physical_selection_fit_work_s": accounting["mixed"]["selection_fitting_work_s"],
                       "physical_selection_compute_wall_s": accounting["mixed"]["selection_workflow_wall_s"]}
    for key, expected in expected_shared.items():
        equal_number(shared[key], expected, key)
        equal_number(selection["shared_bank_accounting"][key], expected, key)
    bookkeeping = number(selection["selection_bookkeeping_wall_s"], "All-family bookkeeping")
    number(selection["selection_common_accounting_wall_s"], "Common selection accounting")
    for fam in FAMILIES:
        number(selection["candidate_selection_wall_s_by_family"][fam], f"Candidate-choice wall {fam}")
    require(bookkeeping + 1e-12 >= selection["selection_common_accounting_wall_s"]
            + sum(selection["candidate_selection_wall_s_by_family"].values()), "Bookkeeping components exceed total")
    require(selection.get("selection_bookkeeping_time_kind") == tuned.get("selection_bookkeeping_time_kind")
            == "shared_all_families_wall_once_physically", "All-family bookkeeping label")
    require(tuned.get("candidate_selection_wall_s_by_family") == selection.get("candidate_selection_wall_s_by_family")
            and tuned.get("selection_common_accounting_wall_s") == selection.get("selection_common_accounting_wall_s"),
            "Bookkeeping checkpoint mismatch")
    equal_number(tuned["selection_bookkeeping_wall_s"], bookkeeping, "Tuned bookkeeping")
    equal_number(shared["physical_total_workflow_wall_s"], expected_shared["physical_selection_compute_wall_s"]
                 + bookkeeping + sum(r["direct_fit_time_s"] + r["test_prediction_wall_s"] for r in rows), "Physical cost once")
    return tuned


def flatten(identity, row, stage, params, model_id):
    record = {**{key: canonical(value) if isinstance(value, (dict, list)) else value for key, value in row.items()},
            "dataset": identity["dataset"], "seed": identity["seed"], "stage": stage,
            "model_id": model_id, "task_depth": str(params["max_depth"]),
            "max_features": "all" if params["max_features"] is None else params["max_features"],
            "min_samples_leaf": params["min_samples_leaf"], "n_classes": identity["data"]["n_classes"],
            "protocol_fingerprint": identity["protocol_fingerprint"],
            "train_index_sha256": identity["train_index_sha256"], "test_index_sha256": identity["test_index_sha256"]}
    if stage == "fixed_tree":
        record.update(mean_actual_depth=row["actual_depth"], mean_n_leaves=row["n_leaves"])
    weights = row.get("composition_twentieths", row.get("selected", {}).get("composition_twentieths"))
    if weights is not None:
        record.update({f"weight_k{h}": weights[h - 1] / 20 for h in (1, 2, 3)})
        record["mean_horizon"] = sum(h * weights[h - 1] / 20 for h in (1, 2, 3))
    if stage == "tuned_forest":
        record["n_estimators"] = row["selected"]["n_estimators"]
        record["selected_depth"] = record["task_depth"]
        record["selected_max_features"] = record["max_features"]
        record["task_depth"], record["max_features"] = "tuned", "selected"
    return record


def load_results(out, fixed_only=False):
    protocol = check_protocol(out)
    preflight(out, protocol, fixed_only)
    fixed, trees, tuned_rows, physical, metadata_rows = [], [], [], [], []
    for index, name in enumerate(protocol["datasets"], 1):
        print(f"validating {index}/57 {name}", flush=True)
        metadata, y = check_data(out, name)
        metadata_rows.append(metadata)
        for seed in SEEDS:
            root = out / "raw" / protocol["protocol_fingerprint"] / name / f"s{seed}"
            identity, train, test = check_split(root / "split.json", protocol, metadata, y, seed)
            blocks = []
            for depth in DEPTHS:
                for features in (None, "sqrt"):
                    params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
                    expected = {**identity, "stage": "fixed", "structural_params": params, "forest_counts": list(COUNTS)}
                    block = check_block(root / "fixed" / f"{structural_id(params)}.json", expected, y[test], True)
                    blocks.append(block)
                    fixed.extend(flatten(identity, row, "fixed_forest", params, row["candidate_id"]) for row in block["rows"])
                    trees.extend(flatten(identity, row, "fixed_tree", params, f"{structural_id(params)}__{row['model_id']}")
                                 for row in block["single_trees"])
            fixed_physical = {"dataset": name, "seed": seed,
                              "physical_fixed_bank_fit_work_s": sum(b["banks"][str(h)]["fit_work_s"] for b in blocks for h in (1, 2, 3)),
                              "physical_fixed_bank_prediction_work_s": sum(b["banks"][str(h)]["prediction_work_s"] for b in blocks for h in (1, 2, 3)),
                              "physical_fixed_bank_wall_s": sum(b["banks"][str(h)]["bank_wall_s"] for b in blocks for h in (1, 2, 3)),
                              "physical_fixed_single_fit_wall_s": sum(r["direct_fit_time_s"] for b in blocks for r in b["single_trees"]),
                              "physical_fixed_single_prediction_wall_s": sum(r["test_prediction_wall_s"] for b in blocks for r in b["single_trees"]),
                              "physical_fixed_stage_wall_s": sum(b["block_compute_wall_s"] + sum(
                                  r["direct_fit_time_s"] + r["test_prediction_wall_s"] for r in b["single_trees"]) for b in blocks)}
            if not fixed_only:
                tuned = check_tuned(root, identity, train, y)
                tuned_rows.extend(flatten(identity, row, "tuned_forest", row["selected"]["params"], row["family"])
                                  for row in tuned["rows"])
                fixed_physical.update({key: value for key, value in tuned["shared_bank_accounting"].items()
                                       if isinstance(value, (int, float))})
                fixed_physical["physical_all_stages_workflow_wall_s"] = (fixed_physical["physical_fixed_stage_wall_s"]
                                                                        + fixed_physical["physical_total_workflow_wall_s"])
                final = read_json(root / "results.json", identity)
                require(final.get("complete_protocol_task") is True and final.get("fixed") == blocks
                        and final.get("tuned") == tuned and final.get("other_curves_status") == "descriptive", "Full task record mismatch")
                contrasts = final.get("primary_contrasts", [])
                require(len(contrasts) == 11, "Literal 11 primary contrasts required")
                lookup_fixed = {row["candidate_id"]: row for block in blocks for row in block["rows"]}
                lookup_tuned = {row["family"]: row for row in tuned["rows"]}
                for actual, spec in zip(contrasts, primary_specs()):
                    require({k: actual.get(k) for k in spec} == spec, "Primary contrast identity")
                    lookup = lookup_fixed if spec["stage"] == "fixed" else lookup_tuned
                    a, b = lookup[spec["left"]]["accuracy"], lookup[spec["right"]]["accuracy"]
                    for key, value in (("left_accuracy", a), ("right_accuracy", b), ("accuracy_difference", a - b)):
                        require(np.isclose(actual[key], value, rtol=0, atol=1e-12), f"Primary contrast value: {key}")
            physical.append(fixed_physical)
    require(len(fixed) == 136800 and len(trees) == 5130, "Fixed export row counts")
    require(fixed_only or len(tuned_rows) == 855, "Tuned export row counts")
    return protocol, pd.DataFrame(fixed), pd.DataFrame(trees), pd.DataFrame(tuned_rows), pd.DataFrame(physical), pd.DataFrame(metadata_rows)


METRICS = ("accuracy", "balanced_accuracy", "fit_work_s", "prediction_work_s", "mean_actual_depth",
           "mean_n_leaves", "direct_fit_time_s", "test_prediction_wall_s", "selection_fitting_work_s",
           "selection_prediction_work_s", "selection_bank_wall_s", "selection_schedule_evaluation_wall_s",
           "selection_workflow_wall_s", "selection_bookkeeping_attributed_wall_s", "total_workflow_wall_s",
           "total_fitting_work_s", "refit_tree_fit_work_s", "n_estimators", "mean_horizon")


def dataset_means(frame):
    parts = []
    for stage, group in frame.groupby("stage", sort=True):
        require(not group.duplicated(["dataset", "seed", "model_id"]).any(), "Duplicate paired repeat")
        for (_, _), repeats in group.groupby(["dataset", "model_id"]):
            require(set(repeats.seed) == set(SEEDS) and len(repeats) == 5, "Five balanced paired repeats required")
        metrics = [key for key in METRICS if key in group and group[key].notna().all()]
        means = group.groupby(["dataset", "model_id"], as_index=False)[metrics].mean()
        attributes = [key for key in ("stage", "task_depth", "max_features", "min_samples_leaf", "composition_id",
                                      "composition_twentieths", "weight_k1", "weight_k2", "weight_k3")
                      if key in group and group[key].notna().all()]
        if stage == "tuned_forest":
            attributes = [key for key in attributes if key not in ("min_samples_leaf", "weight_k1", "weight_k2", "weight_k3")]
        config = group.groupby(["dataset", "model_id"], as_index=False)[attributes].first()
        means = means.merge(config, on=["dataset", "model_id"], validate="one_to_one")
        means["repeats"] = 5
        parts.append(means)
    return pd.concat(parts, ignore_index=True)


def summarize(means):
    summaries = []
    for (stage, identity), group in means.groupby(["stage", "model_id"], sort=True):
        require(group.dataset.nunique() == len(group) == 57, f"Unequal dataset cohort: {identity}")
        row = {"stage": stage, "model_id": identity, "n_datasets": 57, "repeats_per_dataset": 5,
               "aggregation": "repeat_mean_then_equal_dataset_mean"}
        for key in ("task_depth", "max_features", "composition_id", "composition_twentieths"):
            if key in group and group[key].notna().all():
                row[key] = group[key].iloc[0]
        for key in METRICS:
            if key in group and group[key].notna().all():
                row[key] = float(group[key].mean())
                if key.endswith("_s"):
                    row["median_dataset_" + key] = float(group[key].median())
        row["accuracy_ci_low"], row["accuracy_ci_high"] = ci(group.accuracy)
        summaries.append(row)
    return pd.DataFrame(summaries)


def paired(means, left, right, label, primary=False, inferential=False):
    a = means[means.model_id == left].set_index("dataset").sort_index()
    b = means[means.model_id == right].set_index("dataset").sort_index()
    require(len(a) == len(b) == 57 and a.index.equals(b.index) and a.index.is_unique,
            f"Unpaired/full-cohort contrast: {label}")
    delta = a.accuracy - b.accuracy
    low, high = ci(delta)
    row = {"contrast_id": label, "left": left, "right": right,
           "status": "primary_11_family" if inferential else "primary_pending_full_11_family" if primary else "descriptive",
           "n_datasets": 57, "mean_delta": float(delta.mean()), "median_delta": float(delta.median()),
           "ci_low": low, "ci_high": high, "wins": int((delta > 1e-12).sum()),
           "ties": int((delta.abs() <= 1e-12).sum()), "losses": int((delta < -1e-12).sum()),
           "balanced_accuracy_delta": float((a.balanced_accuracy - b.balanced_accuracy).mean()),
           "ci_kind": "paired_dataset_bootstrap_20000_seed41"}
    stage = a.stage.iloc[0]
    require(stage == b.stage.iloc[0], "Cross fixed/tuned comparisons are not allowed")
    cost = "fit_work_s" if stage == "fixed_forest" else "direct_fit_time_s"
    row["comparison_cost_kind"] = "selected_tree_fit_work" if stage == "fixed_forest" else "direct_refit_wall"
    denom = float(b[cost].mean())
    row["ratio_of_mean_fitting_costs"] = float(a[cost].mean()) / denom if denom > 0 else None
    if inferential:
        row["wilcoxon_p"] = p_value(delta)
    deltas = pd.DataFrame({"dataset": delta.index, "contrast_id": label, "delta": delta.to_numpy(),
                           "family_group": [family(name) for name in delta.index],
                           "named_synthetic": [synthetic(name) for name in delta.index]})
    return row, deltas


def comparisons(means, fixed_only):
    primary, descriptive, paired_rows, sensitivities = [], [], [], []
    specs = primary_specs()[:8] if fixed_only else primary_specs()
    for spec in specs:
        row, deltas = paired(means, spec["left"], spec["right"], spec["contrast_id"], True, not fixed_only)
        row["stage"] = spec["stage"]
        primary.append(row)
        paired_rows.append(deltas)
        grouped = deltas.groupby("family_group").delta.mean()
        non_synthetic = deltas.loc[~deltas.named_synthetic, "delta"]
        require(len(grouped) == 48 and len(non_synthetic) == 38, "Sensitivity cohort changed")
        for label, values in (("known_family_groups_48", grouped), ("named_non_synthetic_38", non_synthetic)):
            low, high = ci(values)
            sensitivities.append({"contrast_id": spec["contrast_id"], "sensitivity": label,
                                  "n_units": len(values), "mean_delta": float(values.mean()),
                                  "ci_low": low, "ci_high": high, "status": "prespecified_sensitivity_no_extra_p_family"})
    if not fixed_only:
        require(len(primary) == 11, "Holm requires exactly the frozen 11 contrasts")
        for row, adjusted in zip(primary, holm([row["wilcoxon_p"] for row in primary])):
            row.update(holm_p=float(adjusted), holm_family_size=11)
    primary_pairs = {(spec["left"], spec["right"]) for spec in specs}
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            for count in COUNTS:
                right = candidate_id(params, count, "pure_k1")
                for name, _ in compositions()[1:]:
                    left = candidate_id(params, count, name)
                    if (left, right) not in primary_pairs:
                        row, deltas = paired(means, left, right, f"descriptive__{left}_vs_k1")
                        descriptive.append(row)
                        paired_rows.append(deltas)
            right = f"{structural_id(params)}__cart"
            for h in (2, 3):
                left = f"{structural_id(params)}__single_k{h}"
                row, deltas = paired(means, left, right, f"descriptive__{left}_vs_cart")
                descriptive.append(row)
                paired_rows.append(deltas)
    return pd.DataFrame(primary), pd.DataFrame(descriptive), pd.concat(paired_rows, ignore_index=True), pd.DataFrame(sensitivities)


def physical_summary(physical):
    require(len(physical) == 285 and not physical.duplicated(["dataset", "seed"]).any(), "Physical task cohort")
    for _, group in physical.groupby("dataset"):
        require(set(group.seed) == set(SEEDS), "Physical accounting repeats")
    keys = [key for key in physical if key.endswith("_s")]
    means = physical.groupby("dataset", as_index=False)[keys].mean()
    require(len(means) == 57, "Physical costs must average 57 datasets")
    summary = {key: float(means[key].mean()) for key in keys}
    summary.update(n_datasets=57, repeats_per_dataset=5, accounting="physical_shared_banks_once_not_sum_of_family_attributions")
    return means, summary


COLORS = ("#222222", "#1f77b4", "#d62728", "#2b8c55", "#66a61e", "#c59a00", "#8c6d31",
          "#7b3294", "#a64c9c", "#dc74ab", "#b35806", "#008b8b", "#17a8bd", "#527a9c", "#7f7f7f", "#9d8f11")
MARKERS = ("o", "s", "^", "D", "v")


def curve_label(weights):
    horizon = sum(h * weights[h - 1] / 20 for h in (1, 2, 3))
    return "/".join(str(5 * value) for value in weights) + f"% (h={horizon:.2f})"


def curve_style(index):
    return COLORS[index], "-" if index < 3 or index == 15 else "--" if index < 7 else ":" if index < 11 else "-."


def figure_style():
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
                         "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .6,
                         "pdf.fonttype": 42, "figure.facecolor": "white", "axes.facecolor": "white"})


def check_figure_layout(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    artists = list(fig.legends) + list(fig.texts)
    for axis in fig.axes:
        artists.extend([axis.xaxis.label, axis.yaxis.label, axis.title])
        for axis_object, limits in ((axis.xaxis, axis.get_xlim()), (axis.yaxis, axis.get_ylim())):
            low, high = sorted(limits)
            for tick in axis_object.get_major_ticks() + axis_object.get_minor_ticks():
                if low <= tick.get_loc() <= high:
                    artists.extend([tick.label1, tick.label2])
        artists.extend(axis.texts)
        if axis.get_legend() is not None:
            artists.append(axis.get_legend())
    for artist in artists:
        if not artist.get_visible():
            continue
        box = artist.get_window_extent(renderer)
        require(box.x0 >= bounds.x0 - 1 and box.y0 >= bounds.y0 - 1
                and box.x1 <= bounds.x1 + 1 and box.y1 <= bounds.y1 + 1,
                f"Figure text or legend clipped: {getattr(artist, 'get_text', lambda: 'legend')()}")


def save_figure(fig, path):
    check_figure_layout(fig)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".pdf"))
    fig.savefig(path.with_suffix(".png"), dpi=240)
    plt.close(fig)


def curve_subset(summary, depth, features):
    result = summary[(summary.stage == "fixed_forest") & (summary.task_depth == str(depth))
                     & (summary.max_features == ("all" if features is None else features))]
    require(len(result) == 80 and result.model_id.nunique() == 80, "Figure requires all 16 compositions and five counts")
    require((result.fit_work_s > 0).all(), "Cannot put zero mean fitting work on a logarithmic axis")
    return result


def draw_curve(axis, xs, ys, index, markers=True):
    color, style = curve_style(index)
    axis.plot(xs, ys, color=color, ls=style, lw=1.15, zorder=3 if index < 3 else 2)
    if markers:
        for x, y, marker in zip(xs, ys, MARKERS):
            axis.plot(x, y, marker=marker, color=color, markersize=3.2, ls="none", markeredgewidth=.45)


def plot_curves(summary, path, depth=3, features=None, test_only=False):
    figure_style()
    subset = curve_subset(summary, depth, features)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.5))
    fig.subplots_adjust(left=.09, right=.99, bottom=.33, top=.83, wspace=.26)
    handles = []
    for index, (name, weights) in enumerate(compositions()):
        rows = subset[subset.composition_id == name].set_index("n_estimators").loc[list(COUNTS)]
        draw_curve(axes[0], COUNTS, rows.accuracy, index)
        draw_curve(axes[1], rows.fit_work_s, rows.accuracy, index)
        color, style = curve_style(index)
        handles.append(Line2D([], [], color=color, ls=style, lw=1.3, label=curve_label(weights)))
    axes[0].set_xticks(COUNTS)
    axes[0].set_xlabel("Number of trees T")
    axes[0].set_ylabel("Mean test accuracy")
    axes[0].set_title("(a) Accuracy versus tree count", pad=18)
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Mean measured fitting work (s)")
    axes[1].set_title("(b) Accuracy versus fitting work", pad=18)
    axes[1].axvline(.7, color="0.35", ls="--", lw=.8, zorder=1)
    axes[1].text(.5, 1.025, "0.7 s MEAN-COST reference", transform=axes[1].transAxes,
                 ha="center", fontsize=7, color="0.35")
    for axis in axes:
        axis.grid(color="0.9", lw=.5)
        axis.set_axisbelow(True)
    low, high = float(subset.accuracy.min()), float(subset.accuracy.max())
    margin = max(.004, (high - low) * .12)
    for axis in axes:
        axis.set_ylim(max(0, low - margin), min(1, high + margin))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .015), ncol=4,
               frameon=False, fontsize=7, title="Composition: % k1/k2/k3 (mean horizon h)",
               title_fontsize=7, columnspacing=1.1, handlelength=1.6, handletextpad=.4)
    markers = [Line2D([], [], color="0.25", marker=marker, ls="none", markersize=3.5, label=f"T={count}")
               for count, marker in zip(COUNTS, MARKERS)]
    fig.legend(handles=markers, loc="upper center", bbox_to_anchor=(.5, .955), ncol=5,
               frameon=False, columnspacing=1.6, handletextpad=.3)
    depth_label = "unlimited" if depth is None else str(depth)
    feature_label = "all" if features is None else features
    title = f"Depth {depth_label}; features {feature_label}; 57 datasets, five paired repeats"
    fig.suptitle(("TEST ONLY - synthetic fixture; " if test_only else "") + title, fontsize=8, y=.995)
    save_figure(fig, path)


def plot_pair_facets(summary, path, test_only=False):
    figure_style()
    subset = curve_subset(summary, 3, None)
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 4.5), sharey=True)
    fig.subplots_adjust(left=.09, right=.985, bottom=.42, top=.88, wspace=.16)
    for axis, (near, far) in zip(axes, ((1, 2), (1, 3), (2, 3))):
        handles = []
        for index, (name, weights) in enumerate(compositions()):
            if name not in (f"pure_k{near}", f"pure_k{far}", "triple_85_10_05") and not name.startswith(f"pair_k{near}_k{far}_"):
                continue
            rows = subset[subset.composition_id == name].set_index("n_estimators").loc[list(COUNTS)]
            draw_curve(axis, COUNTS, rows.accuracy, index)
            color, style = curve_style(index)
            handles.append(Line2D([], [], color=color, ls=style, lw=1.2, label=curve_label(weights)))
        axis.set_title(f"Horizons {near} and {far}")
        axis.set_xticks(COUNTS)
        axis.tick_params(axis="x", rotation=45)
        axis.set_xlabel("Number of trees T")
        axis.grid(color="0.9", lw=.5)
        axis.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, -.25),
                    ncol=1, frameon=False, fontsize=7, handlelength=1.5, labelspacing=.45)
    axes[0].set_ylabel("Mean test accuracy")
    fig.suptitle(("TEST ONLY - synthetic fixture; " if test_only else "") + "Depth 3, all features: pair facets", fontsize=8, y=.99)
    save_figure(fig, path)


def plot_tuned(summary, primary, path, test_only=False):
    figure_style()
    target = primary[primary.stage == "tuned"].set_index("contrast_id")
    require(len(target) == 3, "Tuned figure requires all three paired contrasts")
    selected = summary[summary.stage == "tuned_forest"].set_index("model_id").loc[list(FAMILIES)]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.5))
    fig.subplots_adjust(left=.17, right=.99, bottom=.23, top=.88, wspace=.35)
    labels = ("k2-only - RF", "Inclusive - RF", "Inclusive - k2-only")
    colors = ("#25874b", "#b83c3c", "#724694")
    for index, ((_, row), color) in enumerate(zip(target.iterrows(), colors)):
        x, low, high = 100 * row.mean_delta, 100 * row.ci_low, 100 * row.ci_high
        axes[0].errorbar(x, index, xerr=[[x - low], [high - x]], fmt="o", color=color, capsize=3, ms=4)
    axes[0].axvline(0, color="0.5", lw=.7)
    axes[0].set_yticks(range(3), labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Accuracy difference (percentage points)")
    axes[0].set_title("(a) Paired tuned-family differences")
    positions = np.arange(3)
    require((selected.selection_fitting_work_s > 0).all() and (selected.direct_fit_time_s > 0).all(), "Nonpositive tuned plotting costs")
    axes[1].bar(positions - .18, selected.selection_fitting_work_s, width=.32, color="#628eab", label="Selection: tree-fit work")
    axes[1].bar(positions + .18, selected.direct_fit_time_s, width=.32, color="#ce825b", label="Refit: direct wall time")
    axes[1].plot(positions, selected.total_workflow_wall_s, "D", color="0.2", ms=4,
                 label="Sum of measured stage wall times")
    axes[1].set_xticks(positions, ("RF", "k2-only", "Inclusive"))
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Mean time or work (s)")
    axes[1].set_title("(b) Selection work and direct refit time")
    for axis in axes:
        axis.grid(color="0.9", lw=.5)
        axis.set_axisbelow(True)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=7, frameon=False, bbox_to_anchor=(.5, .025))
    fig.suptitle(("TEST ONLY - synthetic fixture; " if test_only else "") + "Training-only tuned families: 57 datasets, five paired repeats", fontsize=8, y=.99)
    save_figure(fig, path)


def atomic_csv(path, frame):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(descriptor, "w") as handle:
            frame.to_csv(handle, index=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def latex_escape(value):
    mapping = {"\\": r"\textbackslash{}", "%": r"\%", "_": r"\_", "&": r"\&", "#": r"\#",
               "$": r"\$", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(mapping.get(char, char) for char in str(value))


def tex_tables(primary, tuning, directory):
    lines = ["% Paired dataset differences; percentage points; fixed-only has no p-values."]
    for row in primary.itertuples():
        p = f"{row.holm_p:.4g}" if hasattr(row, "holm_p") else "--"
        lines.append(f"{latex_escape(row.contrast_id)} & {100 * row.mean_delta:.2f} & "
                     f"[{100 * row.ci_low:.2f}, {100 * row.ci_high:.2f}] & {p}" + r" \\")
    (directory / "table_primary_comparisons.tex").write_text("\n".join(lines) + "\n")
    if tuning is not None:
        lines = ["% Accuracy; balanced accuracy; direct refit wall; selection fitting work; workflow wall."]
        for row in tuning.itertuples():
            lines.append(f"{latex_escape(row.model_id)} & {row.accuracy:.4f} & {row.balanced_accuracy:.4f} & "
                         f"{row.direct_fit_time_s:.3f} & {row.selection_fitting_work_s:.3f} & "
                         f"{row.total_workflow_wall_s:.3f}" + r" \\")
        (directory / "table_tuned_performance.tex").write_text("\n".join(lines) + "\n")


def make_figures(summary, primary, directory, fixed_only):
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            feature = "all" if features is None else features
            filename = "Fig2_main_D3_Fall" if depth == 3 and features is None else f"FigS_curves_D{depth}_F{feature}"
            plot_curves(summary, directory / filename, depth, features)
    plot_pair_facets(summary, directory / "FigS_pair_facets_D3_Fall")
    if not fixed_only:
        plot_tuned(summary, primary, directory / "Fig3_tuned_families")


def export(out, fixed_only=False):
    protocol, fixed, trees, tuned, physical, metadata = load_results(out, fixed_only)
    frames = [fixed, trees] if fixed_only else [fixed, trees, tuned]
    means = dataset_means(pd.concat(frames, ignore_index=True))
    summary = summarize(means)
    primary, descriptive, deltas, sensitivities = comparisons(means, fixed_only)
    directory = out / "analysis" / ("fixed_only" if fixed_only else "full")
    directory.mkdir(parents=True, exist_ok=True)
    outputs = {"fixed_forests.csv": fixed, "fixed_trees.csv": trees, "dataset_means.csv": means,
               "summary.csv": summary, "paired_primary_comparisons.csv": primary,
               "descriptive_paired_comparisons.csv": descriptive, "paired_dataset_deltas.csv": deltas,
               "sensitivities.csv": sensitivities, "dataset_manifest.csv": metadata}
    tuning_table = None
    physical_means, physical_totals = physical_summary(physical)
    outputs.update({"shared_accounting.csv": physical, "physical_cost_dataset_means.csv": physical_means})
    atomic_json(directory / "physical_cost_summary.json", physical_totals)
    if not fixed_only:
        tuning_table = summary[summary.stage == "tuned_forest"].copy()
        outputs.update({"tuned_forests.csv": tuned, "fair_tuning_table.csv": tuning_table})
    for filename, frame in outputs.items():
        atomic_csv(directory / filename, frame)
    atomic_json(directory / "protocol_snapshot.json", protocol)
    make_figures(summary, primary, directory, fixed_only)
    tex_tables(primary, tuning_table, directory)
    audit = {"analysis_schema": "array-fair-analysis-v1", "validated_complete_cohort": True,
             "protocol_fingerprint": protocol["protocol_fingerprint"], "analysis_source_sha256": file_hash(__file__),
             "fixed_only": fixed_only, "datasets": 57, "outer_tasks": 285, "fixed_blocks": 1710,
             "fixed_forest_rows": len(fixed), "fixed_single_rows": len(trees), "tuned_rows": len(tuned),
             "forest_rows_total": len(fixed) + len(tuned), "all_model_rows_total": sum(len(frame) for frame in frames),
             "primary_contrasts": len(primary), "holm_family_size": None if fixed_only else 11,
             "known_family_groups": 48, "named_non_synthetic_datasets": 38,
             "bootstrap_resamples": BOOTSTRAPS, "bootstrap_seed": BOOTSTRAP_SEED,
             "analysis_versions": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
                                   "sklearn": sklearn.__version__, "matplotlib": matplotlib.__version__},
             "all_repeat_counts": 5, "probabilities_and_selected_costs_reconstructed": True,
             "cv_winners_independently_reconstructed": not fixed_only,
             "fixed_only_inference": "pending_full_11_family" if fixed_only else "complete_11_family",
             "missing_or_skipped_tasks": 0, "output_directory": str(directory),
             "summary_rows": len(summary), "dataset_mean_rows": len(means),
             "output_sha256": {name: file_hash(directory / name) for name in
                               [*outputs, "protocol_snapshot.json"]}}
    atomic_json(directory / "validation.json", audit)
    print(json.dumps(audit, indent=2), flush=True)
    return audit


def read_analysis_csv(path):
    frame = pd.read_csv(path, keep_default_na=False)
    numeric = set(METRICS) | {"accuracy_ci_low", "accuracy_ci_high", "repeats", "n_datasets", "repeats_per_dataset",
                             "mean_delta", "median_delta", "ci_low", "ci_high", "wilcoxon_p", "holm_p", "holm_family_size"}
    for key in set(frame) & numeric:
        frame[key] = pd.to_numeric(frame[key].mask(frame[key] == ""), errors="raise")
    return frame


def validate_retained(directory, fixed_only):
    audit = read_json(directory / "validation.json")
    expected = {"analysis_schema": "array-fair-analysis-v1", "validated_complete_cohort": True,
                "fixed_only": fixed_only, "datasets": 57, "outer_tasks": 285, "fixed_blocks": 1710,
                "fixed_forest_rows": 136800, "fixed_single_rows": 5130, "tuned_rows": 0 if fixed_only else 855,
                "forest_rows_total": 136800 if fixed_only else 137655,
                "all_model_rows_total": 141930 if fixed_only else 142785,
                "summary_rows": 498 if fixed_only else 501, "dataset_mean_rows": 28386 if fixed_only else 28557,
                "primary_contrasts": 8 if fixed_only else 11, "holm_family_size": None if fixed_only else 11,
                "all_repeat_counts": 5, "missing_or_skipped_tasks": 0,
                "known_family_groups": 48, "named_non_synthetic_datasets": 38,
                "bootstrap_resamples": 20000, "bootstrap_seed": 41,
                "probabilities_and_selected_costs_reconstructed": True,
                "cv_winners_independently_reconstructed": not fixed_only,
                "fixed_only_inference": "pending_full_11_family" if fixed_only else "complete_11_family"}
    for key, value in expected.items():
        require(audit.get(key) == value, f"Retained analysis scope/count mismatch: {key}")
    files = ["summary.csv", "paired_primary_comparisons.csv", "dataset_means.csv", "dataset_manifest.csv", "protocol_snapshot.json"]
    if not fixed_only:
        files.append("fair_tuning_table.csv")
    for name in files:
        path, expected_hash = directory / name, audit.get("output_sha256", {}).get(name)
        require(isinstance(expected_hash, str) and bool(HEX.fullmatch(expected_hash)) and path.is_file()
                and file_hash(path) == expected_hash, f"Retained output hash mismatch: {name}")
    protocol = check_protocol(directory, directory / "protocol_snapshot.json", check_sources=False)
    require(protocol["protocol_fingerprint"] == audit["protocol_fingerprint"], "Retained protocol fingerprint")
    summary = read_analysis_csv(directory / "summary.csv")
    primary = read_analysis_csv(directory / "paired_primary_comparisons.csv")
    means = read_analysis_csv(directory / "dataset_means.csv")
    metadata = pd.read_csv(directory / "dataset_manifest.csv", keep_default_na=False)
    require(len(metadata) == 57 and set(metadata.dataset) == set(protocol["datasets"]), "Retained metadata cohort")
    metadata_fields = {"n_rows_raw", "n_rows_used", "n_rows_dropped_missing", "n_samples", "n_features", "n_classes",
                       "X_float32_sha256", "y_encoded_sha256", "source_tsv_gz_sha256", "used_source_row_index_sha256"}
    require(metadata_fields <= set(metadata), "Retained data-manifest schema")
    for record in metadata.to_dict("records"):
        for key in ("n_rows_raw", "n_rows_used", "n_samples", "n_features", "n_classes"):
            integer(record[key], f"Retained metadata {key}", 1)
        integer(record["n_rows_dropped_missing"], "Retained dropped rows")
        require(record["n_samples"] == record["n_rows_used"]
                and record["n_rows_raw"] - record["n_rows_used"] == record["n_rows_dropped_missing"],
                "Retained complete-case row accounting")
        for key in ("X_float32_sha256", "y_encoded_sha256", "source_tsv_gz_sha256", "used_source_row_index_sha256"):
            require(isinstance(record[key], str) and bool(HEX.fullmatch(record[key])), "Retained data fingerprint")
    require(len(summary) == expected["summary_rows"] and not summary.model_id.duplicated().any(), "Retained summary row count/IDs")
    require((summary.n_datasets == 57).all() and (summary.repeats_per_dataset == 5).all(), "Retained summary cohort/repeats")
    require(len(means) == expected["dataset_mean_rows"] and not means.duplicated(["dataset", "model_id"]).any(), "Retained dataset mean IDs")
    require(set(means.dataset) == set(protocol["datasets"]) and (means.repeats == 5).all(), "Retained means repeat balance")
    require(set(summary.model_id) == set(means.model_id), "Retained means/summary models")
    for identity, group in means.groupby("model_id"):
        require(len(group) == 57 and set(group.dataset) == set(protocol["datasets"]), f"Retained incomplete model cohort: {identity}")
        row = summary[summary.model_id == identity].iloc[0]
        for key in METRICS:
            if key in group and group[key].notna().all():
                equal_number(float(row[key]), float(group[key].mean()), f"Retained equal-dataset mean {identity}/{key}")
    fixed_expected, tree_expected = set(), set()
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            fixed_expected.update(candidate_id(params, count, name) for count in COUNTS for name, _ in compositions())
            tree_expected.update(f"{structural_id(params)}__{name}" for name in ("cart", "single_k2", "single_k3"))
    for stage, ids in (("fixed_forest", fixed_expected), ("fixed_tree", tree_expected),
                       ("tuned_forest", set() if fixed_only else set(FAMILIES))):
        require(set(summary.loc[summary.stage == stage, "model_id"]) == ids, f"Retained {stage} model space")
    require(set(summary.stage) == ({"fixed_forest", "fixed_tree"} if fixed_only else {"fixed_forest", "fixed_tree", "tuned_forest"}), "Retained stages")
    for key in ("accuracy", "balanced_accuracy"):
        require(np.isfinite(summary[key]).all() and summary[key].between(0, 1).all(), f"Retained {key} bounds")
    for key in METRICS:
        if key in summary:
            values = summary[key].dropna()
            require(np.isfinite(values).all() and (values >= 0).all(), f"Retained invalid metric: {key}")
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            subset = curve_subset(summary, depth, features)
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            for name, weights in compositions():
                rows = subset[subset.composition_id == name]
                require(len(rows) == 5 and set(rows.n_estimators) == set(COUNTS), "Retained five-point composition")
                require(set(rows.model_id) == {candidate_id(params, count, name) for count in COUNTS}, "Retained curve attributes")
                require(all(value == canonical(weights) for value in rows.composition_twentieths), "Retained curve weights")
    specs = primary_specs()[:8] if fixed_only else primary_specs()
    require(len(primary) == len(specs) and primary.contrast_id.tolist() == [spec["contrast_id"] for spec in specs], "Retained primary family")
    require((primary.n_datasets == 57).all(), "Retained primary cohort")
    require(np.isfinite(primary[["mean_delta", "ci_low", "ci_high"]]).all().all()
            and (primary.ci_low <= primary.ci_high).all(), "Retained primary CI schema")
    for row, spec in zip(primary.to_dict("records"), specs):
        require(row["left"] == spec["left"] and row["right"] == spec["right"], "Retained primary pairing")
        units = means[means.model_id == spec["left"]].set_index("dataset").accuracy
        reference = means[means.model_id == spec["right"]].set_index("dataset").accuracy
        require(np.isclose(row["mean_delta"], (units - reference).mean(), atol=1e-12, rtol=0), "Retained paired effect")
    if fixed_only:
        require("wilcoxon_p" not in primary and "holm_p" not in primary, "Fixed-only must not publish partial-family p values")
    else:
        require((primary.holm_family_size == 11).all() and np.allclose(primary.holm_p, holm(primary.wilcoxon_p), rtol=0, atol=1e-12), "Retained 11-member Holm correction")
        tuning = read_analysis_csv(directory / "fair_tuning_table.csv")
        require(len(tuning) == 3 and set(tuning.model_id) == set(FAMILIES), "Retained tuned table")
    return summary, primary, audit


def plot_summaries(out, fixed_only):
    directory = out / "analysis" / ("fixed_only" if fixed_only else "full")
    summary, primary, audit = validate_retained(directory, fixed_only)
    make_figures(summary, primary, directory, fixed_only)
    print(json.dumps({"plot_summaries": True, "fixed_only": fixed_only,
                      "protocol_fingerprint": audit["protocol_fingerprint"], "validated_summary_rows": len(summary),
                      "validated_datasets": 57, "npz_banks_required": False, "output_directory": str(directory)}, indent=2))


def _fixture_block(path, identity, y, single_trees=True):
    """Synthetic schema fixture only: no estimator, benchmark data, or timing."""
    size, params = max(identity["forest_counts"]), identity["structural_params"]
    banks, metadata = {}, {}
    for h in (1, 2, 3):
        probabilities = np.full((size, len(y), 2), .2)
        probabilities[:, np.arange(len(y)), y] = .8
        bank = {"values": probabilities, "fit_s": .001 * h * (1 + np.arange(size) / size),
                "predict_s": np.full(size, .0001), "depth": np.ones(size, dtype=np.int64),
                "leaves": np.full(size, 2, dtype=np.int64), "wall_s": 1.0 * h,
                "preparation_s": .01, "completed_slots": size}
        banks[h] = bank
        seeds = np.random.RandomState(identity["seed"]).randint(np.iinfo(np.int32).max, size=200)[:size]
        bank_identity = {**identity, "horizon": h, "bank_size": size,
                         "probability_shape": [size, len(y), 2], "tree_seed_sha256": array_hash(seeds)}
        bank_path = (path.with_name(path.stem + "__curves").with_suffix(f".k{h}.npz")
                     if single_trees else path.with_suffix(f".k{h}.npz"))
        bank_path.parent.mkdir(parents=True, exist_ok=True)
        with bank_path.open("wb") as handle:
            np.savez_compressed(handle, identity=canonical(bank_identity), **bank)
        metadata[str(h)] = {"fit_work_s": float(bank["fit_s"].sum()),
                            "prediction_work_s": float(bank["predict_s"].sum()),
                            "bank_wall_s": bank["wall_s"], "preparation_wall_s": bank["preparation_s"],
                            "mean_actual_depth": 1.0, "fit_s_by_slot": bank["fit_s"].tolist(),
                            "predict_s_by_slot": bank["predict_s"].tolist(),
                            "actual_depth_by_slot": bank["depth"].tolist(), "n_leaves_by_slot": bank["leaves"].tolist()}
    rows = []
    for count in identity["forest_counts"]:
        for name, weights in compositions():
            assignment = schedule(identity["seed"], count, weights)
            values, metrics = pool(banks, assignment)
            rows.append({"candidate_id": candidate_id(params, count, name), "composition_id": name,
                         "composition_twentieths": weights, "n_estimators": count, "params": params,
                         "horizon_counts": [count * value // 20 for value in weights],
                         "slot_horizon_sha256": array_hash(assignment), "time_kind": "measured_selected_tree_fit_sum",
                         "schedule_evaluation_wall_s": .0001, **metrics, **probability_scores(y, values)})
    evaluation = {f"{fam}_schedule_evaluation_wall_s": sum(r["schedule_evaluation_wall_s"] for r in rows if accepts(r, fam))
                  for fam in FAMILIES}
    block = {"identity": identity, "rows": rows, "banks": metadata, "fold": identity.get("fold"),
             "block_invocation_wall_s": 7.0, "block_compute_wall_s": 6.0 + evaluation["mixed_schedule_evaluation_wall_s"],
             **evaluation}
    if single_trees:
        block["single_trees"] = []
        for h in (1, 2, 3):
            row = {"model_id": "cart" if h == 1 else f"single_k{h}", "horizon": h, "n_estimators": 1,
                   "params": common_params(params, identity["seed"]), "direct_fit_time_s": .001 * h,
                   "test_prediction_wall_s": .0001, "actual_depth": 1, "n_leaves": 2,
                   "time_kind": "direct_wall_clock", "accuracy": 1.0, "balanced_accuracy": 1.0}
            block["single_trees"].append(row)
            atomic_json(path.with_name(path.stem + f"__single_k{h}.json"), {
                "identity": {**identity, "horizon": h, "kind": "single_tree"}, "row": row})
    atomic_json(path, block)
    return block


def _fixture_tuned(root):
    labels = np.array([0, 1] * 12, dtype=np.int64)
    train, test = train_test_split(np.arange(24, dtype=np.int64), test_size=.25, stratify=labels, random_state=1000)
    identity = {"protocol_fingerprint": "f" * 64, "dataset": "TEST_only", "seed": 1000,
                "data": {"n_classes": 2}, "train_index_sha256": array_hash(train), "test_index_sha256": array_hash(test)}
    splits, kind = cv_splits(labels[train], 1000)
    split_manifest, blocks = [], []
    for fold, (inner_train, validation) in enumerate(splits):
        split = {"fold": fold, "inner_train_index_sha256": array_hash(train[inner_train]),
                 "inner_validation_index_sha256": array_hash(train[validation])}
        split_manifest.append(split)
        for params in structures():
            expected = {**identity, "stage": "inner_cv", **split, "structural_params": params, "forest_counts": list(TUNE_COUNTS)}
            blocks.append(_fixture_block(root / "inner" / f"fold{fold}__{structural_id(params)}.json", expected,
                                         labels[train[validation]], False))
    params = {"max_depth": 3, "min_samples_leaf": 1, "max_features": None}
    candidate = {"candidate_id": candidate_id(params, 20, "pure_k1"), "composition_id": "pure_k1",
                 "composition_twentieths": [20, 0, 0], "params": params, "n_estimators": 20,
                 "mean_validation_accuracy": 1.0,
                 "mean_validation_fit_work_s": float(np.sum(.001 * (1 + np.arange(20) / 100))), "n_inner_folds": len(splits)}
    accounting = {}
    for fam, horizons in (("rf", (1,)), ("mixed_k2", (1, 2)), ("mixed", (1, 2, 3))):
        accounting[fam] = {"selection_fitting_work_s": sum(b["banks"][str(h)]["fit_work_s"] for b in blocks for h in horizons),
                           "selection_prediction_work_s": sum(b["banks"][str(h)]["prediction_work_s"] for b in blocks for h in horizons),
                           "selection_bank_wall_s": sum(b["banks"][str(h)]["bank_wall_s"] for b in blocks for h in horizons),
                           "selection_schedule_evaluation_wall_s": sum(b[f"{fam}_schedule_evaluation_wall_s"] for b in blocks),
                           "selection_time_kind": "measured_fit_work_not_wall_time"}
        accounting[fam]["selection_workflow_wall_s"] = accounting[fam]["selection_bank_wall_s"] + accounting[fam]["selection_schedule_evaluation_wall_s"]
    shared = {"shared_k1_fit_work_s": accounting["rf"]["selection_fitting_work_s"],
              "shared_k1_prediction_work_s": accounting["rf"]["selection_prediction_work_s"],
              "shared_k1_bank_wall_s": accounting["rf"]["selection_bank_wall_s"],
              "shared_k1_schedule_wall_s": accounting["rf"]["selection_schedule_evaluation_wall_s"],
              "shared_k2_fit_work_s": sum(b["banks"]["2"]["fit_work_s"] for b in blocks),
              "physical_selection_fit_work_s": accounting["mixed"]["selection_fitting_work_s"],
              "physical_selection_compute_wall_s": accounting["mixed"]["selection_workflow_wall_s"],
              "attribution": "TEST_only_shared_banks"}
    bookkeeping = {"selection_bookkeeping_wall_s": .04, "selection_common_accounting_wall_s": .002,
                   "candidate_selection_wall_s_by_family": {fam: .01 for fam in FAMILIES},
                   "selection_bookkeeping_time_kind": "shared_all_families_wall_once_physically"}
    selection = {"identity": identity, "selected": {fam: candidate for fam in FAMILIES}, "inner_cv_kind": kind,
                 "inner_splits": split_manifest, "family_accounting": accounting, "shared_bank_accounting": shared, **bookkeeping}
    atomic_json(root / "selection.json", selection)
    rows = []
    for index, fam in enumerate(FAMILIES):
        direct_time = .02 + .01 * index
        config = {**common_params(params, 1000), "ccp_alpha": 0.0, "n_estimators": 20, "bootstrap": True,
                  "n_jobs": 1, "composition_twentieths": [20, 0, 0],
                  "estimator": "sklearn.RandomForestClassifier" if fam == "rf" else "prepared_weighted_mixture"}
        row = {"family": fam, "selected": candidate, "refit_model_config": config, "accuracy": 1.0,
               "balanced_accuracy": 1.0, "direct_fit_time_s": direct_time, "test_prediction_wall_s": .001,
               "mean_actual_depth": 1.0, "mean_n_leaves": 2.0, "time_kind": "direct_wall_clock", **accounting[fam],
               "selection_bookkeeping_attributed_wall_s": .012,
               "total_workflow_wall_s": accounting[fam]["selection_workflow_wall_s"] + .012 + direct_time + .001,
               "workflow_time_kind": "sum_measured_stage_wall_times_shared_k1_attributed_to_each"}
        if fam != "rf":
            row["refit_tree_fit_work_s"] = direct_time * .8
            row["slot_horizon_sha256"] = array_hash(np.ones(20, dtype=np.int8))
        row["total_fitting_work_s"] = accounting[fam]["selection_fitting_work_s"] + (direct_time if fam == "rf" else direct_time * .8)
        row["total_fitting_measurement_kind"] = ("selection_tree_fit_sum_plus_actual_rf_refit_wall"
                                                  if fam == "rf" else "selection_and_refit_tree_fit_sum")
        rows.append(row)
        atomic_json(root / f"refit_{fam}.json", {"identity": {**identity, "stage": "selected_refit", "family": fam,
                                                             "candidate": candidate}, "row": row})
    shared_full = {**shared, "physical_total_workflow_wall_s": shared["physical_selection_compute_wall_s"] + .04
                   + sum(row["direct_fit_time_s"] + .001 for row in rows)}
    tuned = {"identity": identity, "inner_cv_kind": kind, "inner_splits": split_manifest, "rows": rows,
             "shared_bank_accounting": shared_full, **bookkeeping}
    atomic_json(root / "tuned.json", tuned)
    return identity, train, labels, tuned


def _expect_failure(call, label):
    try:
        call()
    except (ValueError, KeyError):
        return
    raise AssertionError(f"Invalid fixture was accepted: {label}")


def _qa_summary():
    records = []
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            for index, (name, weights) in enumerate(compositions()):
                for count in COUNTS:
                    horizon = sum(h * weights[h - 1] / 20 for h in (1, 2, 3))
                    accuracy = .72 + .015 * np.log(count / 20) + .014 * np.sin(index / 3) + .012 * (horizon - 1)
                    cost = count * sum(weights[h - 1] / 20 * (.002, .03, .2)[h - 1] for h in (1, 2, 3))
                    records.append({"stage": "fixed_forest", "model_id": candidate_id(params, count, name),
                                    "task_depth": str(depth), "max_features": "all" if features is None else features,
                                    "composition_id": name, "n_estimators": count, "accuracy": accuracy,
                                    "fit_work_s": cost, "mean_horizon": horizon, "TEST_ONLY": True})
    for index, fam in enumerate(FAMILIES):
        records.append({"stage": "tuned_forest", "model_id": fam, "accuracy": .78 + index * .007,
                        "balanced_accuracy": .77 + index * .006, "direct_fit_time_s": .2 * (index + 1),
                        "selection_fitting_work_s": 10.0 * (index + 1) ** 3,
                        "total_workflow_wall_s": 12.0 * (index + 1) ** 3, "TEST_ONLY": True})
    primary = pd.DataFrame([{**spec, "mean_delta": value, "ci_low": value - .004, "ci_high": value + .004}
                            for spec, value in zip(primary_specs()[8:], (.007, .014, .007))])
    return pd.DataFrame(records), primary


def _fixture_retained(directory, fixed_only, names):
    summary, _ = _qa_summary()
    records = summary.to_dict("records")
    for depth in DEPTHS:
        for features in (None, "sqrt"):
            params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": features}
            for h in (1, 2, 3):
                records.append({"stage": "fixed_tree", "model_id": f"{structural_id(params)}__" + ("cart" if h == 1 else f"single_k{h}"),
                                "task_depth": str(depth), "max_features": "all" if features is None else features,
                                "n_estimators": 1, "accuracy": .7 + .01 * h, "direct_fit_time_s": .01 * h})
    summary = pd.DataFrame(records)
    if fixed_only:
        summary = summary[summary.stage != "tuned_forest"].copy()
    summary["balanced_accuracy"] = summary.accuracy - .01
    summary["n_datasets"], summary["repeats_per_dataset"] = 57, 5
    summary["accuracy_ci_low"], summary["accuracy_ci_high"] = summary.accuracy - .004, summary.accuracy + .004
    for name, weights in compositions():
        summary.loc[summary.composition_id == name, "composition_twentieths"] = canonical(weights)
    means = summary.drop(columns=["n_datasets", "repeats_per_dataset", "accuracy_ci_low", "accuracy_ci_high"]).merge(
        pd.DataFrame({"dataset": names}), how="cross")
    means["repeats"] = 5
    specs = primary_specs()[:8] if fixed_only else primary_specs()
    rows = []
    for spec in specs:
        row, _ = paired(means, spec["left"], spec["right"], spec["contrast_id"], True, not fixed_only)
        rows.append({**row, "stage": spec["stage"]})
    primary = pd.DataFrame(rows)
    if not fixed_only:
        primary["holm_p"], primary["holm_family_size"] = holm(primary.wilcoxon_p), 11
    protocol = {"schema": "array-fair-v1", "datasets": names, "outer_seeds": list(SEEDS),
                "counts": list(COUNTS), "selection_counts": list(TUNE_COUNTS), "selection_bank_size": 100,
                "horizons": [1, 2, 3], "selection_families": list(FAMILIES), "fixed_depths": list(DEPTHS),
                "fixed_leaf": 1, "fixed_feature_modes": [None, "sqrt"], "structural_grid": structures(),
                "primary_contrasts": primary_specs(), "compositions": [{"id": k, "twentieths": w} for k, w in compositions()],
                "predictor_dtype": "float32", "criterion": "gini", "min_samples_split": 2, "ccp_alpha": 0.0,
                "fit_timeout": None, "test_size": .25, "inner_seed_offset": 7, "checkpoint_every_slots": 20,
                "tie_break": ["accuracy_desc", "fit_work_asc", "id_asc"],
                "source_hashes": {name: "0" * 64 for name in ("paper/scripts/run_array_fair_benchmark.py",
                                  "paper/scripts/fair_revision_runtime.py", "paper/array_revision_fair/runtime/_sighted_fast.pyx",
                                  "treeple/tree/_lookahead.py")}}
    protocol["protocol_fingerprint"] = digest(protocol)
    protocol["documentation_sha256"] = "0" * 64
    metadata = pd.DataFrame([{"dataset": name, "n_rows_raw": 24, "n_rows_used": 24, "n_rows_dropped_missing": 0,
                              "n_samples": 24, "n_features": 2, "n_classes": 2, **{key: "a" * 64 for key in
                              ("X_float32_sha256", "y_encoded_sha256", "source_tsv_gz_sha256", "used_source_row_index_sha256")}}
                             for name in names])
    files = {"summary.csv": summary, "paired_primary_comparisons.csv": primary,
             "dataset_means.csv": means, "dataset_manifest.csv": metadata}
    if not fixed_only:
        files["fair_tuning_table.csv"] = summary[summary.stage == "tuned_forest"]
    for name, frame in files.items():
        atomic_csv(directory / name, frame)
    atomic_json(directory / "protocol_snapshot.json", protocol)
    audit = {"analysis_schema": "array-fair-analysis-v1", "validated_complete_cohort": True,
             "fixed_only": fixed_only, "protocol_fingerprint": protocol["protocol_fingerprint"],
             "datasets": 57, "outer_tasks": 285, "fixed_blocks": 1710, "fixed_forest_rows": 136800,
             "fixed_single_rows": 5130, "tuned_rows": 0 if fixed_only else 855,
             "forest_rows_total": 136800 if fixed_only else 137655,
             "all_model_rows_total": 141930 if fixed_only else 142785,
             "summary_rows": len(summary), "dataset_mean_rows": len(means),
             "primary_contrasts": len(specs), "holm_family_size": None if fixed_only else 11,
             "all_repeat_counts": 5, "missing_or_skipped_tasks": 0, "known_family_groups": 48,
             "named_non_synthetic_datasets": 38, "bootstrap_resamples": 20000, "bootstrap_seed": 41,
             "probabilities_and_selected_costs_reconstructed": True,
             "cv_winners_independently_reconstructed": not fixed_only,
             "fixed_only_inference": "pending_full_11_family" if fixed_only else "complete_11_family",
             "TEST_ONLY": True,
             "output_sha256": {name: file_hash(directory / name) for name in [*files, "protocol_snapshot.json"]}}
    atomic_json(directory / "validation.json", audit)
    return audit


def self_test(qa_dir=None):
    require(len(compositions()) == 16 and len(structures()) == 12 and len(primary_specs()) == 11, "Frozen grid counts")
    np.testing.assert_allclose(holm([.01, .04, .03]), [.03, .06, .06])
    require(p_value(np.zeros(57)) == 1, "Zero-difference Wilcoxon")
    require(ci(np.ones(57)) == (1.0, 1.0), "Constant paired bootstrap")
    require(latex_escape("10%_test &") == r"10\%\_test \&", "TeX escaping")
    names = pd.read_csv(REPO / "paper/tables/mixed_sighted_dataset_sample.csv").dataset.tolist()
    require(len({family(name) for name in names}) == 48 and sum(not synthetic(name) for name in names) == 38,
            "Sensitivity definitions")
    for seed in SEEDS:
        for _, weights in compositions():
            full = schedule(seed, 200, weights)
            for count in COUNTS:
                np.testing.assert_array_equal(schedule(seed, count, weights), full[:count])
                for start in range(0, count, 20):
                    require([int(np.sum(full[start:start + 20] == h)) for h in (1, 2, 3)] == weights, "Block fractions")
    for labels, kind in ((np.array([0, 0, 2, 2]), "StratifiedKFold_2"),
                         (np.array([0, 0, 1, 1, 2]), "KFold_3_single_or_rare_class"),
                         (np.zeros(6, dtype=int), "KFold_3_single_or_rare_class")):
        require(cv_splits(labels, 1000)[1] == kind, "Present-class CV rule")
    records = [{"dataset": name, "seed": seed, "stage": "fixed_forest", "model_id": model,
                "accuracy": .7 + offset + seed * .00001, "balanced_accuracy": .69 + offset,
                "fit_work_s": .2 + offset, "mean_actual_depth": 3., "task_depth": "3", "max_features": "all"}
               for name in names for seed in SEEDS for model, offset in (("a", 0.), ("b", .01))]
    frame = pd.DataFrame(records)
    means = dataset_means(frame)
    require(len(means) == 114 and (means.repeats == 5).all(), "Repeat-first dataset means")
    row, deltas = paired(means, "a", "b", "TEST_only")
    require(abs(row["mean_delta"] + .01) < 1e-12 and "wilcoxon_p" not in row, "Descriptive paired CI, no p")
    require(len(deltas) == 57 and len(summarize(means)) == 2, "Equal-dataset summaries")
    _expect_failure(lambda: dataset_means(frame.iloc[1:]), "Missing seed")
    _expect_failure(lambda: summarize(means[means.dataset != names[0]]), "Missing dataset")
    with tempfile.TemporaryDirectory(prefix="TEST_array_fair_analysis_") as directory:
        root = Path(directory)
        _expect_failure(lambda: preflight(root, {"protocol_fingerprint": "f" * 64, "datasets": names}, True), "Incomplete fixed cohort")
        _expect_failure(lambda: preflight(root, {"protocol_fingerprint": "f" * 64, "datasets": names}, False), "Incomplete tuned cohort")
        params = {"max_depth": 3, "min_samples_leaf": 1, "max_features": None}
        identity = {"protocol_fingerprint": "f" * 64, "dataset": "TEST_only", "seed": 1000,
                    "data": {"n_classes": 2}, "stage": "fixed", "structural_params": params,
                    "forest_counts": list(COUNTS)}
        y = np.array([0, 1] * 4, dtype=np.int64)
        path = root / "D3_L1_Fall.json"
        block = _fixture_block(path, identity, y)
        require(check_block(path, identity, y, True) == block, "Complete structural fixture")
        for label, change in (
                ("missing row", lambda b: b["rows"].pop()),
                ("duplicate row", lambda b: b["rows"].__setitem__(1, copy.deepcopy(b["rows"][0]))),
                ("wrong score", lambda b: b["rows"][0].__setitem__("accuracy", .5)),
                ("wrong selected cost", lambda b: b["rows"][0].__setitem__("fit_work_s", 99.)),
                ("wrong weights", lambda b: b["rows"][3].__setitem__("composition_twentieths", [18, 2, 0])),
                ("negative time", lambda b: b["rows"][0].__setitem__("schedule_evaluation_wall_s", -1.)),
                ("wrong feature mode", lambda b: b["rows"][0]["params"].__setitem__("max_features", "sqrt")),
                ("wrong protocol", lambda b: b["identity"].__setitem__("protocol_fingerprint", "e" * 64))):
            broken = copy.deepcopy(block)
            change(broken)
            atomic_json(path, broken)
            _expect_failure(lambda: check_block(path, identity, y, True), label)
        atomic_json(path, block)
        bank_path = path.with_name(path.stem + "__curves").with_suffix(".k3.npz")
        with np.load(bank_path, allow_pickle=False) as archive:
            bank = {key: archive[key].copy() for key in archive.files}
        bank["completed_slots"] = np.asarray(20)
        with bank_path.open("wb") as handle:
            np.savez_compressed(handle, **bank)
        _expect_failure(lambda: check_block(path, identity, y, True), "Pending k3 bank")
        _fixture_block(path, identity, y)
        cv_blocks = []
        for fold in range(2):
            for structure in structures():
                rows = []
                for original in block["rows"]:
                    if original["n_estimators"] in TUNE_COUNTS:
                        row = copy.deepcopy(original)
                        row.update(params=structure, candidate_id=candidate_id(structure, row["n_estimators"], row["composition_id"]))
                        rows.append(row)
                cv_blocks.append({"fold": fold, "rows": rows})
        for fam in FAMILIES:
            selected = choose(cv_blocks, fam, 2)
            require(selected["n_estimators"] == 20 and selected["composition_id"] == "pure_k1", "Independent winner/tie rule")
        require(not accepts({"composition_id": "pure_k3", "composition_twentieths": [0, 0, 20]}, "mixed_k2"), "k2 family excludes k3")
        for block in cv_blocks:
            for row in block["rows"]:
                row["accuracy"] = .7 + .05 * sum(h * row["composition_twentieths"][h - 1] / 20 for h in (1, 2, 3))
        require(choose(cv_blocks, "mixed_k2", 2)["composition_id"] == "pure_k2"
                and choose(cv_blocks, "mixed", 2)["composition_id"] == "pure_k3", "Different family eligibility winners")
        full_root = root / "tuned_fixture"
        task_identity, train, labels, tuned = _fixture_tuned(full_root)
        require(check_tuned(full_root, task_identity, train, labels) == tuned, "Full independent tuned audit fixture")
        broken = copy.deepcopy(tuned)
        broken["shared_bank_accounting"]["physical_total_workflow_wall_s"] *= 2
        atomic_json(full_root / "tuned.json", broken)
        _expect_failure(lambda: check_tuned(full_root, task_identity, train, labels), "Double-counted physical costs")
        atomic_json(full_root / "tuned.json", tuned)
        missing_refit = full_root / "refit_mixed_k2.json"
        missing_refit.unlink()
        _expect_failure(lambda: check_tuned(full_root, task_identity, train, labels), "Missing one tuned family refit")
        for fixed_only in (True, False):
            retained = root / ("retained_fixed_TEST" if fixed_only else "retained_full_TEST")
            audit = _fixture_retained(retained, fixed_only, names)
            validated_summary, validated_primary, _ = validate_retained(retained, fixed_only)
            require(len(validated_summary) == (498 if fixed_only else 501), "Retained summary count")
            require(len(validated_primary) == (8 if fixed_only else 11), "Retained primary count")
            _expect_failure(lambda: validate_retained(retained, not fixed_only), "Wrong fixed/full retrieval mode")
            data = read_analysis_csv(retained / "summary.csv")
            data.loc[0, "accuracy"] += .01
            atomic_csv(retained / "summary.csv", data)
            _expect_failure(lambda: validate_retained(retained, fixed_only), "Changed retained summary hash")
            _fixture_retained(retained, fixed_only, names)
            incomplete = read_analysis_csv(retained / "dataset_means.csv").iloc[1:]
            atomic_csv(retained / "dataset_means.csv", incomplete)
            audit["output_sha256"]["dataset_means.csv"] = file_hash(retained / "dataset_means.csv")
            atomic_json(retained / "validation.json", audit)
            _expect_failure(lambda: validate_retained(retained, fixed_only), "Incomplete retained cohort even with refreshed hash")
    if qa_dir is not None:
        qa_dir = Path(qa_dir).resolve()
        require(any(qa_dir.is_relative_to(base.resolve()) for base in (Path("/tmp"), Path(tempfile.gettempdir()))),
                "TEST QA outputs must remain under a temporary root")
        summary, primary = _qa_summary()
        for depth in DEPTHS:
            for features in (None, "sqrt"):
                plot_curves(summary, qa_dir / f"TEST_curves_D{depth}_F{features}", depth, features, True)
        plot_pair_facets(summary, qa_dir / "TEST_pair_facets", True)
        plot_tuned(summary, primary, qa_dir / "TEST_tuned_families", True)
        print(f"TEST-only figure QA: {qa_dir}", flush=True)
    print("Analyzer tests passed: completeness, bank reconstruction, costs, pairing, Holm and CV selection", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT, help="Frozen fair input root; never an older-run output")
    parser.add_argument("--fixed-only", action="store_true")
    parser.add_argument("--plot-summaries", action="store_true", help="Verify retained CSV hashes/schema and regenerate figures without NPZ banks")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--qa-dir", type=Path, help="Only with --self-test; labeled TEST-only synthetic figures under /tmp")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test(args.qa_dir)
        return
    if args.qa_dir is not None:
        parser.error("--qa-dir requires --self-test")
    if args.out.resolve().is_relative_to((REPO / "paper/array_revision").resolve()):
        parser.error("Never read/export the older array_revision run as a fair run")
    if args.plot_summaries:
        plot_summaries(args.out.resolve(), args.fixed_only)
    else:
        export(args.out.resolve(), args.fixed_only)


if __name__ == "__main__":
    main()
