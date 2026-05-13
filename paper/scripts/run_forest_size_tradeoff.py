"""Run a small forest-size tradeoff experiment for the AMAI draft.

The main benchmark fixes the forest size and varies lookahead depth. This
secondary experiment asks whether a larger greedy forest can match a smaller
lookahead forest under the same shallow-tree protocol.
"""

from __future__ import annotations

import csv
import os
import time
from pathlib import Path

import numpy as np
from pmlb import fetch_data
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from treeple.ensemble import LookaheadRandomForestClassifier


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tables" / "forest_size_tradeoff.csv"

DATASETS = [
    "iris",
    "wine_recognition",
    "breast_cancer_wisconsin",
    "glass",
    "ecoli",
    "haberman",
    "heart_statlog",
    "diabetes",
    "balance_scale",
    "ionosphere",
    "vehicle",
    "molecular_biology_promoters",
]

GRID = [
    (1, 5),
    (1, 10),
    (1, 25),
    (1, 50),
    (1, 100),
    (2, 1),
    (2, 3),
    (2, 5),
    (2, 10),
]


def _fit_one(dataset: str, lookahead_depth: int, n_estimators: int) -> dict[str, object]:
    X, y = fetch_data(dataset, return_X_y=True)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)

    stratify = y
    _, counts = np.unique(y, return_counts=True)
    if counts.shape[0] <= 1 or counts.min() < 2:
        stratify = None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0, stratify=stratify
    )

    clf = LookaheadRandomForestClassifier(
        n_estimators=n_estimators,
        lookahead_depth=lookahead_depth,
        max_depth=3,
        max_features=None,
        max_split_candidates=None,
        random_state=0,
        bootstrap=True,
        n_jobs=1,
    )
    start = time.perf_counter()
    clf.fit(X_train, y_train)
    fit_time = time.perf_counter() - start
    score = accuracy_score(y_test, clf.predict(X_test))
    return {
        "dataset": dataset,
        "n_samples": X.shape[0],
        "n_features": X.shape[1],
        "lookahead_depth": lookahead_depth,
        "n_estimators": n_estimators,
        "fit_time": fit_time,
        "accuracy": score,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    completed = set()
    if OUT.exists():
        with OUT.open(newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                completed.add(
                    (row["dataset"], int(row["lookahead_depth"]), int(row["n_estimators"]))
                )

    fieldnames = [
        "dataset",
        "n_samples",
        "n_features",
        "lookahead_depth",
        "n_estimators",
        "fit_time",
        "accuracy",
    ]
    write_header = not OUT.exists()
    with OUT.open("a", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for dataset in DATASETS:
            for lookahead_depth, n_estimators in GRID:
                key = (dataset, lookahead_depth, n_estimators)
                if key in completed:
                    continue
                try:
                    row = _fit_one(dataset, lookahead_depth, n_estimators)
                except Exception as exc:
                    print(f"skip {dataset} d={lookahead_depth} t={n_estimators}: {exc}")
                    continue
                writer.writerow(row)
                handle.flush()
                print(
                    dataset,
                    f"d={lookahead_depth}",
                    f"trees={n_estimators}",
                    f"acc={row['accuracy']:.4f}",
                    f"time={row['fit_time']:.3f}s",
                )


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    main()
