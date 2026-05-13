"""Run the mixed k-sighted forest benchmark for the AMAI manuscript.

The script fits forests with integer sight depths k=1,2,3 and then evaluates
pure and mixed forests by selecting tree slots from those fitted forests. This
keeps the benchmark reproducible while avoiding duplicate fitting for every
mixture. Mixed-forest fitting times are reported as the sum of the constituent
tree-slot fitting times estimated from the corresponding pure forest fits.
"""

from __future__ import annotations

import argparse
import csv
import multiprocessing as mp
import os
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
from pmlb import classification_dataset_names, fetch_data
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from treeple.ensemble import LookaheadRandomForestClassifier


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "tables"
RESULT_PATH = TABLE_DIR / "mixed_sighted_forest_results.csv"
SAMPLE_PATH = TABLE_DIR / "mixed_sighted_dataset_sample.csv"
SKIP_PATH = TABLE_DIR / "mixed_sighted_forest_skipped.csv"

PURE_DEPTHS = (1, 2, 3)
MAX_ESTIMATORS_BY_DEPTH = {1: 100, 2: 100, 3: 5}
FOREST_SIZE_GRID_BY_DEPTH = {
    1: (5, 10, 25, 50, 100),
    2: (5, 10, 25, 50, 100),
    3: (1, 3, 5),
}


@dataclass(frozen=True)
class Schedule:
    schedule_id: str
    label: str
    effective_k: float
    components: tuple[tuple[int, int], ...]
    kind: str

    @property
    def n_estimators(self) -> int:
        return sum(count for _, count in self.components)


SCHEDULES = [
    *(Schedule(f"pure_k{k}_{n}", f"k={k}, T={n}", float(k), ((k, n),), "pure_size")
      for k in PURE_DEPTHS
      for n in FOREST_SIZE_GRID_BY_DEPTH[k]),
    Schedule("mix_1_95_2_05", "95% k=1 + 5% k=2", 1.05, ((1, 95), (2, 5)), "mixture"),
    Schedule("mix_1_90_2_10", "90% k=1 + 10% k=2", 1.10, ((1, 90), (2, 10)), "mixture"),
    Schedule("mix_1_75_2_25", "75% k=1 + 25% k=2", 1.25, ((1, 75), (2, 25)), "mixture"),
    Schedule("mix_1_50_2_50", "50% k=1 + 50% k=2", 1.50, ((1, 50), (2, 50)), "mixture"),
    Schedule("mix_1_95_3_05", "95% k=1 + 5% k=3", 1.10, ((1, 95), (3, 5)), "mixture"),
    Schedule("mix_2_95_3_05", "95% k=2 + 5% k=3", 2.05, ((2, 95), (3, 5)), "mixture"),
]

RESULT_FIELDS = [
    "dataset",
    "n_samples",
    "n_features",
    "schedule_id",
    "label",
    "kind",
    "effective_k",
    "depth_1_trees",
    "depth_2_trees",
    "depth_3_trees",
    "n_estimators",
    "fit_time_s",
    "accuracy",
]

SAMPLE_FIELDS = [
    "dataset",
    "n_samples",
    "n_features",
    "dimension",
    "n_classes",
]

SKIP_FIELDS = [
    "dataset",
    "reason",
]


def _pmlb_summary_path() -> Path:
    import pmlb

    return Path(pmlb.__file__).resolve().parent / "all_summary_stats.tsv"


def _candidate_datasets(dimension_limit: int) -> list[str]:
    metadata: dict[str, tuple[int, int]] = {}
    with _pmlb_summary_path().open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row.get("task") != "classification":
                continue
            try:
                n_instances = int(row["n_instances"])
                n_features = int(row["n_features"])
            except (TypeError, ValueError):
                continue
            if n_instances * n_features <= dimension_limit:
                metadata[row["dataset"]] = (n_instances, n_features)

    order = {dataset: index for index, dataset in enumerate(classification_dataset_names)}
    return sorted(
        metadata,
        key=lambda dataset: (
            metadata[dataset][1],
            metadata[dataset][0] * metadata[dataset][1],
            metadata[dataset][0],
            order.get(dataset, 10**9),
        ),
    )


def _read_completed(path: Path) -> dict[str, set[str]]:
    completed: dict[str, set[str]] = {}
    if not path.exists():
        return completed
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            completed.setdefault(row["dataset"], set()).add(row["schedule_id"])
    return completed


def _read_sample(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return [row["dataset"] for row in csv.DictReader(handle)]


def _read_skipped(path: Path, *, retry_timeouts: bool = False) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="") as handle:
        skipped = set()
        for row in csv.DictReader(handle):
            if retry_timeouts and "TimeoutError" in row.get("reason", ""):
                continue
            skipped.add(row["dataset"])
        return skipped


def _append_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
        handle.flush()


def _load_dataset(dataset: str, cache_dir: str | None):
    X, y = fetch_data(dataset, return_X_y=True, local_cache_dir=cache_dir)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    if X.ndim != 2:
        raise ValueError("X is not two-dimensional")
    classes, counts = np.unique(y, return_counts=True)
    if classes.shape[0] < 2:
        raise ValueError("dataset has fewer than two classes")
    if counts.min() < 2:
        stratify = None
    else:
        stratify = y
    return X, y, classes, stratify


def _fit_integer_forests(X_train, y_train, *, n_jobs: int) -> tuple[dict[int, object], dict[int, float]]:
    forests = {}
    fit_times = {}
    for depth in PURE_DEPTHS:
        clf = LookaheadRandomForestClassifier(
            n_estimators=MAX_ESTIMATORS_BY_DEPTH[depth],
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


def _slot_indices(schedule: Schedule) -> dict[int, list[int]]:
    indices: dict[int, list[int]] = {}
    starts: dict[int, int] = {}
    for depth, count in schedule.components:
        start = starts.get(depth, 0)
        indices[depth] = list(range(start, start + count))
        starts[depth] = start + count
    return indices


def _mean_proba_for_schedule(
    forests: dict[int, object],
    schedule: Schedule,
    X_test: np.ndarray,
    classes: np.ndarray,
) -> np.ndarray:
    proba = np.zeros((X_test.shape[0], classes.shape[0]), dtype=np.float64)
    class_to_index = {label: idx for idx, label in enumerate(classes)}
    n_trees = 0

    for depth, indices in _slot_indices(schedule).items():
        forest = forests[depth]
        for index in indices:
            tree = forest.estimators_[index]
            tree_proba = tree.predict_proba(X_test)
            for tree_index, label in enumerate(tree.classes_):
                proba[:, class_to_index[label]] += tree_proba[:, tree_index]
            n_trees += 1

    if n_trees == 0:
        raise ValueError(f"empty schedule: {schedule.schedule_id}")
    return proba / n_trees


def _time_for_schedule(fit_times: dict[int, float], schedule: Schedule) -> float:
    total = 0.0
    for depth, count in schedule.components:
        total += fit_times[depth] * count / MAX_ESTIMATORS_BY_DEPTH[depth]
    return total


def _component_counts(schedule: Schedule) -> dict[int, int]:
    return {depth: count for depth, count in schedule.components}


def _evaluate_dataset(dataset: str, *, cache_dir: str | None, n_jobs: int) -> tuple[
    dict[str, object],
    list[dict[str, object]],
]:
    X, y, classes, stratify = _load_dataset(dataset, cache_dir)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0, stratify=stratify
    )
    forests, fit_times = _fit_integer_forests(X_train, y_train, n_jobs=n_jobs)

    sample_row = {
        "dataset": dataset,
        "n_samples": X.shape[0],
        "n_features": X.shape[1],
        "dimension": X.shape[0] * X.shape[1],
        "n_classes": classes.shape[0],
    }

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
                "label": schedule.label,
                "kind": schedule.kind,
                "effective_k": schedule.effective_k,
                "depth_1_trees": counts.get(1, 0),
                "depth_2_trees": counts.get(2, 0),
                "depth_3_trees": counts.get(3, 0),
                "n_estimators": schedule.n_estimators,
                "fit_time_s": _time_for_schedule(fit_times, schedule),
                "accuracy": accuracy_score(y_test, pred),
            }
        )
    return sample_row, rows


def _dataset_worker(queue, dataset: str, cache_dir: str | None, n_jobs: int) -> None:
    try:
        queue.put(("ok", _evaluate_dataset(dataset, cache_dir=cache_dir, n_jobs=n_jobs)))
    except Exception as exc:
        queue.put(("error", type(exc).__name__, str(exc)))


def _evaluate_dataset_with_timeout(
    dataset: str,
    *,
    cache_dir: str | None,
    n_jobs: int,
    timeout: float | None,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    if timeout is None or timeout <= 0:
        return _evaluate_dataset(dataset, cache_dir=cache_dir, n_jobs=n_jobs)

    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(
        target=_dataset_worker,
        args=(queue, dataset, cache_dir, n_jobs),
        daemon=False,
    )
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"dataset exceeded {timeout:.0f} seconds")

    if queue.empty():
        raise RuntimeError(f"dataset worker exited with code {process.exitcode}")
    status, *payload = queue.get()
    if status == "ok":
        return payload[0]
    error_name, message = payload
    raise RuntimeError(f"{error_name}: {message}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-datasets", type=int, default=67)
    parser.add_argument("--dimension-limit", type=int, default=25000)
    parser.add_argument("--cache-dir", default="/private/tmp/pmlb_lookahead_cache")
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument(
        "--dataset-timeout",
        type=float,
        default=1800.0,
        help="Maximum seconds for one dataset; <=0 disables the watchdog.",
    )
    parser.add_argument("--datasets", nargs="*", default=None)
    parser.add_argument("--out", type=Path, default=RESULT_PATH)
    parser.add_argument("--sample-out", type=Path, default=SAMPLE_PATH)
    parser.add_argument("--skip-out", type=Path, default=SKIP_PATH)
    parser.add_argument("--retry-timeouts", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    schedule_ids = {schedule.schedule_id for schedule in SCHEDULES}
    completed = _read_completed(args.out)
    pinned_sample = _read_sample(args.sample_out)
    skipped = _read_skipped(args.skip_out, retry_timeouts=args.retry_timeouts)
    completed_datasets = [
        dataset for dataset, seen in completed.items() if schedule_ids.issubset(seen)
    ]

    if args.datasets is not None:
        candidates = args.datasets
    elif pinned_sample:
        extra_candidates = [
            dataset
            for dataset in _candidate_datasets(args.dimension_limit)
            if dataset not in pinned_sample
        ]
        candidates = [*pinned_sample, *extra_candidates]
    else:
        candidates = _candidate_datasets(args.dimension_limit)

    completed_set = set(completed_datasets)
    for dataset in candidates:
        if len(completed_set) >= args.target_datasets:
            break
        if dataset in skipped:
            continue
        seen = completed.get(dataset, set())
        if schedule_ids.issubset(seen):
            completed_set.add(dataset)
            continue

        try:
            sample_row, rows = _evaluate_dataset_with_timeout(
                dataset,
                cache_dir=args.cache_dir,
                n_jobs=args.n_jobs,
                timeout=args.dataset_timeout,
            )
        except Exception as exc:
            print(f"skip {dataset}: {type(exc).__name__}: {exc}", flush=True)
            _append_rows(
                args.skip_out,
                SKIP_FIELDS,
                [{"dataset": dataset, "reason": f"{type(exc).__name__}: {exc}"}],
            )
            skipped.add(dataset)
            continue

        missing_rows = [row for row in rows if row["schedule_id"] not in seen]
        if missing_rows:
            _append_rows(args.out, RESULT_FIELDS, missing_rows)
        if dataset not in pinned_sample:
            _append_rows(args.sample_out, SAMPLE_FIELDS, [sample_row])
            pinned_sample.append(dataset)
        completed_set.add(dataset)

        pure_max = {
            row["effective_k"]: row
            for row in rows
            if row["kind"] == "pure_size"
            and row["n_estimators"] == MAX_ESTIMATORS_BY_DEPTH[int(row["effective_k"])]
        }
        print(
            dataset,
            f"done {len(completed_set)}/{args.target_datasets}",
            " ".join(
                f"k={int(k)} acc={pure_max[k]['accuracy']:.4f} "
                f"time={pure_max[k]['fit_time_s']:.2f}s"
                for k in sorted(pure_max)
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
