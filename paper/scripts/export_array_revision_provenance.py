"""Fingerprint retained inputs, sources, and training-only CV decisions."""

from __future__ import annotations

import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess

from run_array_revision_benchmark import OUT, REPO, SEEDS, dataset_names, load_data
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inputs, cv = [], []
    for name in dataset_names():
        path = OUT / ".cache/pmlb" / name / f"{name}.tsv.gz"
        X, y = load_data(name)
        inputs.append({
            "dataset": name, "download_sha256": digest(path),
            "X_float64_sha256": hashlib.sha256(X.astype("<f8").tobytes()).hexdigest(),
            "y_int64_sha256": hashlib.sha256(y.astype("<i8").tobytes()).hexdigest(),
            "n_samples": len(y), "n_features": X.shape[1],
            "class_counts": np.bincount(y).tolist(),
        })
        for seed in SEEDS:
            train, _ = train_test_split(np.arange(len(y)), test_size=.25,
                                       stratify=y, random_state=seed)
            minimum = int(np.bincount(y[train]).min())
            kind = "KFold_3_rare_class" if minimum < 2 else f"StratifiedKFold_{min(3, minimum)}"
            task = json.loads((OUT / "raw" / f"{name}__s{seed}__D3.json").read_text())
            for row in task["rows"]:
                if row["model_id"] in ("cart_tuned", "rf_tuned"):
                    if row.get("inner_cv_kind", kind) != kind:
                        raise ValueError(f"CV rule mismatch: {name}, {seed}")
                    cv.append({"dataset": name, "seed": seed, "model_id": row["model_id"],
                               "minimum_training_class_count": minimum, "inner_cv_kind": kind,
                               "rule_reconstructed_from_retained_inputs": "inner_cv_kind" not in row})
    pd.DataFrame(inputs).to_csv(OUT / "input_fingerprints.csv", index=False)
    pd.DataFrame(cv).to_csv(OUT / "inner_cv_manifest.csv", index=False)
    sources = [REPO / "treeple/tree/_lookahead.py", REPO / "treeple/tree/_lookahead_fast.pyx"]
    sources += sorted((REPO / "paper/scripts").glob("*array*.py"))
    sources += [REPO / "paper/scripts" / name for name in
                ("build_revision_runtime.py", "revision_runtime.py")]
    manifest = {
        "python": platform.python_version(), "platform": platform.platform(),
        "machine": platform.machine(),
        "versions": {name: version(name) for name in
                     ("numpy", "scipy", "scikit-learn", "pandas", "matplotlib", "pmlb", "Cython", "setuptools")},
        "source_hashes": {str(path.relative_to(REPO)): digest(path) for path in sources},
        "compiled_scorer_hashes": {path.name: digest(path) for path in
                                  (OUT / ".cache/runtime/revision_tree").glob("*.so")},
        "repository_base_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        "cv_fallback_partitions": sum(row["minimum_training_class_count"] == 1 for row in cv) // 2,
        "source_amendments": "protocol_changes.md",
        "validation": json.loads((OUT / "validation.json").read_text()),
    }
    (OUT / "reproducibility_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Fingerprinted {len(inputs)} inputs; {manifest['cv_fallback_partitions']} singleton-class partitions.")


if __name__ == "__main__":
    main()
