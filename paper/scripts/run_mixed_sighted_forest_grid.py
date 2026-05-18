"""Run the full Figure 2 k-sighted forest-size grid.

This benchmark is intentionally separate from
``run_mixed_sighted_forest_benchmark.py`` because Figure 2 now evaluates every
integer and mixed k-sighted forest curve over the same forest-size grid:
20, 40, 60, 100, and 200 trees. The script fits one 200-tree forest for each
integer sight depth, then evaluates pure and mixed curves by averaging selected
tree slots from those fitted forests.

No watchdog timeout is used here. The expected workflow is:

python paper/scripts/run_mixed_sighted_forest_grid.py --make-shard-plan
python paper/scripts/run_mixed_sighted_forest_grid.py --shard-index 0 --n-shards 5
...
python paper/scripts/run_mixed_sighted_forest_grid.py --combine-shards --n-shards 5
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
from pmlb import fetch_data
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from treeple.ensemble import LookaheadRandomForestClassifier


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "tables"
DATASET_SAMPLE_PATH = TABLE_DIR / "mixed_sighted_dataset_sample.csv"
PRIOR_RESULT_PATH = TABLE_DIR / "mixed_sighted_forest_results.csv"
SHARD_PLAN_PATH = TABLE_DIR / "mixed_sighted_forest_grid_shards.csv"
COMBINED_RESULT_PATH = TABLE_DIR / "mixed_sighted_forest_grid_results.csv"

PURE_DEPTHS = (1, 2, 3)
TREE_COUNTS = (20, 40, 60, 100, 200)
MAX_ESTIMATORS = max(TREE_COUNTS)


@dataclass(frozen=True)
class CurveSpec:
    curve_id: str
    label: str
    effective_k: float
    proportions: tuple[tuple[int, int], ...]
    display_order: int

    def counts(self, tree_count: int) -> tuple[tuple[int, int], ...]:
        counts = []
        assigned = 0
        for index, (depth, percent) in enumerate(self.proportions):
            if index == len(self.proportions) - 1:
                count = tree_count - assigned
            else:
                if tree_count * percent % 100 != 0:
                    raise ValueError(
                        f"{tree_count} trees cannot exactly realize {percent}%"
                    )
                count = tree_count * percent // 100
                assigned += count
            if count:
                counts.append((depth, count))
        return tuple(counts)


@dataclass(frozen=True)
class Schedule:
    schedule_id: str
    curve_id: str
    curve_label: str
    effective_k: float
    display_order: int
    tree_count: int
    components: tuple[tuple[int, int], ...]


CURVES = (
    CurveSpec("pure_k1", "k=1", 1.00, ((1, 100),), 0),
    CurveSpec("mix_1_95_2_05", "k=1.05 (95/5: 1/2)", 1.05, ((1, 95), (2, 5)), 1),
    CurveSpec("mix_1_90_2_10", "k=1.10 (90/10: 1/2)", 1.10, ((1, 90), (2, 10)), 2),
    CurveSpec("mix_1_95_3_05", "k=1.10 (95/5: 1/3)", 1.10, ((1, 95), (3, 5)), 3),
    CurveSpec("mix_1_75_2_25", "k=1.25 (75/25: 1/2)", 1.25, ((1, 75), (2, 25)), 4),
    CurveSpec("mix_1_50_2_50", "k=1.50 (50/50: 1/2)", 1.50, ((1, 50), (2, 50)), 5),
    CurveSpec("pure_k2", "k=2", 2.00, ((2, 100),), 6),
    CurveSpec("mix_2_95_3_05", "k=2.05 (95/5: 2/3)", 2.05, ((2, 95), (3, 5)), 7),
    CurveSpec("pure_k3", "k=3", 3.00, ((3, 100),), 8),
)

SCHEDULES = tuple(
    Schedule(
        schedule_id=f"{curve.curve_id}_T{tree_count}",
        curve_id=curve.curve_id,
        curve_label=curve.label,
        effective_k=curve.effective_k,
        display_order=curve.display_order,
        tree_count=tree_count,
        components=curve.counts(tree_count),
    )
    for curve in CURVES
    for tree_count in TREE_COUNTS
)

RESULT_FIELDS = [
    "dataset",
    "n_samples",
    "n_features",
    "schedule_id",
    "curve_id",
    "curve_label",
    "display_order",
    "effective_k",
    "tree_count",
    "depth_1_trees",
    "depth_2_trees",
    "depth_3_trees",
    "fit_time_s",
    "accuracy",
]

ERROR_FIELDS = [
    "dataset",
    "error",
]

SHARD_FIELDS = [
    "dataset",
    "shard",
    "estimated_cost_s",
]


def _read_dataset_rows(path: Path) -> list[dict[str, object]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"no datasets found in {path}")
    for row in rows:
        row["n_samples"] = int(row["n_samples"])
        row["n_features"] = int(row["n_features"])
    return rows


def _append_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
        handle.flush()


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_completed(path: Path) -> dict[str, set[str]]:
    completed: dict[str, set[str]] = {}
    if not path.exists():
        return completed
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            completed.setdefault(row["dataset"], set()).add(row["schedule_id"])
    return completed


def _prior_costs(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}

    by_dataset: dict[str, dict[str, float]] = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            by_dataset.setdefault(row["dataset"], {})[row["schedule_id"]] = float(
                row["fit_time_s"]
            )

    k1 = [values["pure_k1_100"] for values in by_dataset.values() if "pure_k1_100" in values]
    k2 = [values["pure_k2_100"] for values in by_dataset.values() if "pure_k2_100" in values]
    k3 = [values["pure_k3_5"] for values in by_dataset.values() if "pure_k3_5" in values]
    fallback = {
        "pure_k1_100": float(np.median(k1)) if k1 else 1.0,
        "pure_k2_100": float(np.median(k2)) if k2 else 10.0,
        "pure_k3_5": float(np.median(k3)) if k3 else 50.0,
    }

    estimates = {}
    for dataset, values in by_dataset.items():
        k1_time = values.get("pure_k1_100", fallback["pure_k1_100"])
        k2_time = values.get("pure_k2_100", fallback["pure_k2_100"])
        k3_time = values.get("pure_k3_5", fallback["pure_k3_5"])
        estimates[dataset] = 2.0 * k1_time + 2.0 * k2_time + 40.0 * k3_time
    return estimates


def _make_shard_plan(dataset_rows: list[dict[str, object]], n_shards: int) -> list[dict[str, object]]:
    prior_costs = _prior_costs(PRIOR_RESULT_PATH)
    default_cost = float(np.median(list(prior_costs.values()))) if prior_costs else 1.0
    work = [
        (row["dataset"], prior_costs.get(row["dataset"], default_cost))
        for row in dataset_rows
    ]
    work.sort(key=lambda item: item[1], reverse=True)

    shard_costs = [0.0] * n_shards
    assignments: dict[str, int] = {}
    for dataset, cost in work:
        shard = min(range(n_shards), key=lambda idx: shard_costs[idx])
        assignments[dataset] = shard
        shard_costs[shard] += cost

    rows = []
    for row in dataset_rows:
        dataset = row["dataset"]
        rows.append(
            {
                "dataset": dataset,
                "shard": assignments[dataset],
                "estimated_cost_s": round(prior_costs.get(dataset, default_cost), 6),
            }
        )
    return rows


def _read_shard_plan(path: Path, n_shards: int) -> list[dict[str, object]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["shard"] = int(row["shard"])
        row["estimated_cost_s"] = float(row["estimated_cost_s"])
    observed = sorted({row["shard"] for row in rows})
    expected = list(range(n_shards))
    if observed != expected:
        raise ValueError(f"shard plan has shards {observed}, expected {expected}")
    return rows


def _load_dataset(dataset: str, cache_dir: str | None):
    X, y = fetch_data(dataset, return_X_y=True, local_cache_dir=cache_dir)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    if X.ndim != 2:
        raise ValueError("X is not two-dimensional")
    classes, counts = np.unique(y, return_counts=True)
    if classes.shape[0] < 2:
        raise ValueError("dataset has fewer than two classes")
    stratify = y if counts.min() >= 2 else None
    return X, y, classes, stratify


def _fit_integer_forests(X_train, y_train, *, n_jobs: int) -> tuple[dict[int, object], dict[int, float]]:
    forests = {}
    fit_times = {}
    for depth in PURE_DEPTHS:
        clf = LookaheadRandomForestClassifier(
            n_estimators=MAX_ESTIMATORS,
            lookahead_depth=depth,
            max_depth=3,
            max_features=None,
            max_split_candidates=None,
            random_state=0,
            bootstrap=True,
            n_jobs=n_jobs,
        )
        start = time.perf_counter()
        clf.fit(X_train, y_train)
        fit_times[depth] = time.perf_counter() - start
        forests[depth] = clf
    return forests, fit_times


def _mean_proba_for_schedule(
    forests: dict[int, object],
    schedule: Schedule,
    X_test: np.ndarray,
    classes: np.ndarray,
) -> np.ndarray:
    proba = np.zeros((X_test.shape[0], classes.shape[0]), dtype=np.float64)
    class_to_index = {label: idx for idx, label in enumerate(classes)}
    n_trees = 0

    for depth, count in schedule.components:
        forest = forests[depth]
        for index in range(count):
            tree = forest.estimators_[index]
            tree_proba = tree.predict_proba(X_test)
            for tree_index, label in enumerate(tree.classes_):
                proba[:, class_to_index[label]] += tree_proba[:, tree_index]
            n_trees += 1

    if n_trees == 0:
        raise ValueError(f"empty schedule: {schedule.schedule_id}")
    return proba / n_trees


def _component_counts(schedule: Schedule) -> dict[int, int]:
    return {depth: count for depth, count in schedule.components}


def _time_for_schedule(fit_times: dict[int, float], schedule: Schedule) -> float:
    total = 0.0
    for depth, count in schedule.components:
        total += fit_times[depth] * count / MAX_ESTIMATORS
    return total


def _evaluate_dataset(dataset: str, *, cache_dir: str | None, n_jobs: int) -> list[dict[str, object]]:
    X, y, classes, stratify = _load_dataset(dataset, cache_dir)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0, stratify=stratify
    )
    forests, fit_times = _fit_integer_forests(X_train, y_train, n_jobs=n_jobs)

    rows: list[dict[str, object]] = []
    for schedule in SCHEDULES:
        proba = _mean_proba_for_schedule(forests, schedule, X_test, classes)
        pred = classes.take(np.argmax(proba, axis=1), axis=0)
        counts = _component_counts(schedule)
        rows.append(
            {
                "dataset": dataset,
                "n_samples": X.shape[0],
                "n_features": X.shape[1],
                "schedule_id": schedule.schedule_id,
                "curve_id": schedule.curve_id,
                "curve_label": schedule.curve_label,
                "display_order": schedule.display_order,
                "effective_k": schedule.effective_k,
                "tree_count": schedule.tree_count,
                "depth_1_trees": counts.get(1, 0),
                "depth_2_trees": counts.get(2, 0),
                "depth_3_trees": counts.get(3, 0),
                "fit_time_s": _time_for_schedule(fit_times, schedule),
                "accuracy": accuracy_score(y_test, pred),
            }
        )
    return rows


def _result_path_for_shard(shard_index: int) -> Path:
    return TABLE_DIR / f"mixed_sighted_forest_grid_shard_{shard_index}.csv"


def _error_path_for_shard(shard_index: int) -> Path:
    return TABLE_DIR / f"mixed_sighted_forest_grid_errors_shard_{shard_index}.csv"


def _run_shard(args: argparse.Namespace) -> None:
    if args.shard_index is None:
        raise ValueError("--shard-index is required unless --make-shard-plan or --combine-shards is used")
    if not SHARD_PLAN_PATH.exists():
        dataset_rows = _read_dataset_rows(args.datasets_file)
        _write_rows(
            SHARD_PLAN_PATH,
            SHARD_FIELDS,
            _make_shard_plan(dataset_rows, args.n_shards),
        )

    plan = _read_shard_plan(SHARD_PLAN_PATH, args.n_shards)
    datasets = [
        row["dataset"]
        for row in plan
        if row["shard"] == args.shard_index
    ]
    out = _result_path_for_shard(args.shard_index)
    err = _error_path_for_shard(args.shard_index)
    completed = _read_completed(out)
    required = {schedule.schedule_id for schedule in SCHEDULES}

    for index, dataset in enumerate(datasets, start=1):
        seen = completed.get(dataset, set())
        if required.issubset(seen):
            print(
                f"shard {args.shard_index}: {dataset} already complete "
                f"({index}/{len(datasets)})",
                flush=True,
            )
            continue

        try:
            rows = _evaluate_dataset(dataset, cache_dir=args.cache_dir, n_jobs=args.n_jobs)
        except Exception as exc:
            _append_rows(
                err,
                ERROR_FIELDS,
                [{"dataset": dataset, "error": f"{type(exc).__name__}: {exc}"}],
            )
            print(
                f"shard {args.shard_index}: error on {dataset}: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )
            continue

        missing = [row for row in rows if row["schedule_id"] not in seen]
        if missing:
            _append_rows(out, RESULT_FIELDS, missing)
        completed[dataset] = required

        pure_200 = {
            row["curve_id"]: row
            for row in rows
            if row["tree_count"] == MAX_ESTIMATORS and row["curve_id"] in {"pure_k1", "pure_k2", "pure_k3"}
        }
        print(
            f"shard {args.shard_index}: {dataset} done ({index}/{len(datasets)}) "
            f"k1={pure_200['pure_k1']['accuracy']:.4f} "
            f"k2={pure_200['pure_k2']['accuracy']:.4f} "
            f"k3={pure_200['pure_k3']['accuracy']:.4f} "
            f"time200=({pure_200['pure_k1']['fit_time_s']:.2f},"
            f"{pure_200['pure_k2']['fit_time_s']:.2f},"
            f"{pure_200['pure_k3']['fit_time_s']:.2f})s",
            flush=True,
        )


def _combine_shards(n_shards: int) -> None:
    rows_by_key: dict[tuple[str, str], dict[str, object]] = {}
    for shard_index in range(n_shards):
        path = _result_path_for_shard(shard_index)
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                key = (row["dataset"], row["schedule_id"])
                rows_by_key[key] = row

    dataset_order = {
        row["dataset"]: index
        for index, row in enumerate(_read_dataset_rows(DATASET_SAMPLE_PATH))
    }
    rows = sorted(
        rows_by_key.values(),
        key=lambda row: (
            dataset_order.get(row["dataset"], 10**9),
            int(row["display_order"]),
            int(row["tree_count"]),
        ),
    )
    _write_rows(COMBINED_RESULT_PATH, RESULT_FIELDS, rows)
    print(f"wrote {len(rows)} rows to {COMBINED_RESULT_PATH}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default="/private/tmp/pmlb_lookahead_cache")
    parser.add_argument("--datasets-file", type=Path, default=DATASET_SAMPLE_PATH)
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--n-shards", type=int, default=5)
    parser.add_argument("--shard-index", type=int, default=None)
    parser.add_argument("--make-shard-plan", action="store_true")
    parser.add_argument("--combine-shards", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.make_shard_plan:
        rows = _make_shard_plan(_read_dataset_rows(args.datasets_file), args.n_shards)
        _write_rows(SHARD_PLAN_PATH, SHARD_FIELDS, rows)
        totals = [0.0] * args.n_shards
        counts = [0] * args.n_shards
        for row in rows:
            totals[int(row["shard"])] += float(row["estimated_cost_s"])
            counts[int(row["shard"])] += 1
        for shard, (count, total) in enumerate(zip(counts, totals)):
            print(f"shard {shard}: {count} datasets, estimated {total:.1f}s")
        return

    if args.combine_shards:
        _combine_shards(args.n_shards)
        return

    _run_shard(args)


if __name__ == "__main__":
    main()
