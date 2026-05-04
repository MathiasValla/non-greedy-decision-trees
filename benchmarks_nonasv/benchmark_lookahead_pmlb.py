"""Benchmark lookahead trees and forests on PMLB datasets.

Examples
--------
python benchmarks_nonasv/benchmark_lookahead_pmlb.py
    --task classification
    --datasets iris parity5
    --lookahead-depths 1 2
    --max-depths 2 4
    --estimators tree forest
    --output lookahead_pmlb_results.csv
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split

from treeple.ensemble import LookaheadRandomForestClassifier, LookaheadRandomForestRegressor
from treeple.tree import LookaheadDecisionTreeClassifier, LookaheadDecisionTreeRegressor


def _parse_max_depth(value):
    if value.lower() == "none":
        return None
    return int(value)


def _parse_max_features(value):
    lower = value.lower()
    if lower == "none":
        return None
    if lower in {"sqrt", "log2"}:
        return lower
    try:
        return int(value)
    except ValueError:
        return float(value)


def _parse_optional_int(value):
    if value.lower() == "none":
        return None
    return int(value)


def _dataset_names(task):
    try:
        from pmlb import classification_dataset_names, regression_dataset_names
    except ImportError as exc:
        raise SystemExit(
            "pmlb is required for this benchmark. Install it with `pip install pmlb`."
        ) from exc

    if task == "classification":
        return list(classification_dataset_names)
    return list(regression_dataset_names)


def _fetch_dataset(name):
    try:
        from pmlb import fetch_data
    except ImportError as exc:
        raise SystemExit(
            "pmlb is required for this benchmark. Install it with `pip install pmlb`."
        ) from exc

    X, y = fetch_data(name, return_X_y=True)
    return np.asarray(X, dtype=np.float64), np.asarray(y)


def _make_estimator(args, estimator_name, task, lookahead_depth, max_depth):
    shared = dict(
        lookahead_depth=lookahead_depth,
        max_depth=max_depth,
        min_samples_leaf=args.min_samples_leaf,
        max_features=args.max_features,
        max_split_candidates=args.max_split_candidates,
        random_state=args.random_state,
    )
    if task == "classification":
        if estimator_name == "tree":
            return LookaheadDecisionTreeClassifier(**shared)
        return LookaheadRandomForestClassifier(
            n_estimators=args.n_estimators,
            bootstrap=True,
            n_jobs=args.n_jobs,
            **shared,
        )

    if estimator_name == "tree":
        return LookaheadDecisionTreeRegressor(**shared)
    return LookaheadRandomForestRegressor(
        n_estimators=args.n_estimators,
        bootstrap=True,
        n_jobs=args.n_jobs,
        **shared,
    )


def _evaluate_dataset(name, args, writer):
    X, y = _fetch_dataset(name)
    stratify = None
    if args.task == "classification":
        _, counts = np.unique(y, return_counts=True)
        if counts.shape[0] > 1 and np.min(counts) >= 2:
            stratify = y
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=stratify,
    )

    for estimator_name in args.estimators:
        for lookahead_depth in args.lookahead_depths:
            for max_depth in args.max_depths:
                estimator = _make_estimator(
                    args, estimator_name, args.task, lookahead_depth, max_depth
                )
                fit_start = time.perf_counter()
                estimator.fit(X_train, y_train)
                fit_time = time.perf_counter() - fit_start

                predict_start = time.perf_counter()
                y_pred = estimator.predict(X_test)
                predict_time = time.perf_counter() - predict_start

                if args.task == "classification":
                    score = accuracy_score(y_test, y_pred)
                else:
                    score = r2_score(y_test, y_pred)

                writer.writerow(
                    {
                        "dataset": name,
                        "task": args.task,
                        "estimator": estimator_name,
                        "lookahead_depth": lookahead_depth,
                        "max_depth": "None" if max_depth is None else max_depth,
                        "n_estimators": args.n_estimators if estimator_name == "forest" else 1,
                        "max_features": "None" if args.max_features is None else args.max_features,
                        "max_split_candidates": (
                            "None"
                            if args.max_split_candidates is None
                            else args.max_split_candidates
                        ),
                        "min_samples_leaf": args.min_samples_leaf,
                        "n_train": X_train.shape[0],
                        "n_test": X_test.shape[0],
                        "n_features": X.shape[1],
                        "fit_time": fit_time,
                        "predict_time": predict_time,
                        "score": score,
                    }
                )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--task", choices=["classification", "regression"], required=True)
    parser.add_argument("--datasets", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--estimators", nargs="+", choices=["tree", "forest"], default=["tree", "forest"]
    )
    parser.add_argument("--lookahead-depths", nargs="+", type=int, default=[1, 2])
    parser.add_argument("--max-depths", nargs="+", type=_parse_max_depth, default=[None])
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-features", type=_parse_max_features, default="sqrt")
    parser.add_argument("--max-split-candidates", type=_parse_optional_int, default=64)
    parser.add_argument("--min-samples-leaf", type=int, default=1)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=0)
    parser.add_argument("--n-jobs", type=int, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    datasets = args.datasets if args.datasets else _dataset_names(args.task)
    if args.limit is not None:
        datasets = datasets[: args.limit]

    fieldnames = [
        "dataset",
        "task",
        "estimator",
        "lookahead_depth",
        "max_depth",
        "n_estimators",
        "max_features",
        "max_split_candidates",
        "min_samples_leaf",
        "n_train",
        "n_test",
        "n_features",
        "fit_time",
        "predict_time",
        "score",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for dataset in datasets:
            _evaluate_dataset(dataset, args, writer)


if __name__ == "__main__":
    main()
