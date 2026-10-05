"""Training-only timing checks on prespecified contrasting input types."""

import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"

import json
import time

from run_array_fair_benchmark import (
    OUT, atomic_json, bootstrap_counts, load_data, new_tree, outer_split, tree_seeds,
)


def main():
    rows = []
    for dataset in ("iris", "bupa", "nursery"):
        X, y = load_data(dataset)
        train, _ = outer_split(y, 1000)
        Xtrain, ytrain = X[train], y[train]
        seed = int(tree_seeds(1000, 1)[0])
        weights = bootstrap_counts(len(train), seed)
        for depth in (3, None):
            for horizon in (1, 2, 3):
                params = {"max_depth": depth, "min_samples_leaf": 1, "max_features": None}
                model = new_tree(params, seed, horizon)
                print(f"training-only pilot: {dataset}, D={depth}, k={horizon}", flush=True)
                start = time.perf_counter()
                model.fit(Xtrain, ytrain, sample_weight=weights)
                row = {"dataset": dataset, "max_depth": depth, "horizon": horizon,
                       "fit_time_s": time.perf_counter() - start,
                       "actual_depth": int(model.get_depth()), "n_leaves": int(model.get_n_leaves()),
                       "n_training_rows": len(train), "n_features": X.shape[1]}
                rows.append(row)
                atomic_json(OUT / "training_timing_pilot.json", {
                    "purpose": "training-only timing, no test predictions or scores",
                    "scope_changes_from_pilot": False, "rows": rows})
                print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
