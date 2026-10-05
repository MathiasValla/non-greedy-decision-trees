"""Focused checks of the research harness and unchanged split scorer."""

import json
import os
from pathlib import Path

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_info

from run_array_revision_benchmark import Classifier, OUT, bootstrap_slots, proba
import revision_tree._lookahead as implementation


def main():
    X = np.array([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
    y = np.array([0, 1, 1, 0])
    greedy = Classifier(lookahead_depth=1, max_depth=2).fit(X, y)
    farther = Classifier(lookahead_depth=2, max_depth=2).fit(X, y)
    cart = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
    assert greedy.score(X, y) == .5
    assert farther.score(X, y) == cart.score(X, y) == 1
    # XOR exposes the stopping convention; it is not evidence that CART
    # cannot express this interaction at the same final depth.

    rng = np.random.RandomState(31)
    X = rng.randint(5, size=(24, 3)).astype(float)
    y = rng.randint(3, size=24)
    weight = rng.uniform(.1, 2, size=24)
    fast = implementation._lookahead_fast
    for depth, sight in ((2, 3), (6, 2), (None, 2)):
        a = Classifier(lookahead_depth=sight, max_depth=depth).fit(X, y, sample_weight=weight)
        implementation._lookahead_fast = None
        try:
            b = Classifier(lookahead_depth=sight, max_depth=depth).fit(X, y, sample_weight=weight)
        finally:
            implementation._lookahead_fast = fast
        np.testing.assert_allclose(a.predict_proba(X), b.predict_proba(X), atol=1e-12)
        assert a.get_depth() == b.get_depth()

    missing = Classifier(lookahead_depth=2, max_depth=2).fit(X, np.where(y == 1, 2, 0))
    aligned = proba(missing, X, 3)
    np.testing.assert_allclose(aligned[:, 1], 0)
    np.testing.assert_allclose(aligned.sum(axis=1), 1)
    seeds_a, samples_a, replacement_a = bootstrap_slots(24, 1000, count=100)
    seeds_b, samples_b, replacement_b = bootstrap_slots(24, 1000, count=200)
    np.testing.assert_array_equal(seeds_a, seeds_b[:100])
    for a, b in zip(samples_a, samples_b):
        np.testing.assert_array_equal(a, b)
    assert len(set(replacement_a)) == 25
    np.testing.assert_array_equal(replacement_a, replacement_b)

    pools = threadpool_info()
    assert all(pool["num_threads"] == 1 for pool in pools)
    report = {"XOR_stopping_convention_checked": True,
              "weighted_multiclass_Cython_Python_parity": True,
              "depth_clipping_and_unlimited_tree_checked": True,
              "missing_bootstrap_class_alignment": True,
              "size_stable_bootstrap_prefix": True,
              "distinct_replacement_slots": True,
              "native_threadpools": pools}
    (OUT / "harness_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
