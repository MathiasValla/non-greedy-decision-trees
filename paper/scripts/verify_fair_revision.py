"""Pre-run gates for fair stopping, resampling, and exact optimized scores."""

import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"

import json
import hashlib
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from fair_revision_runtime import Classifier, REPO, fast


class Reference(Classifier):
    """Small exhaustive Python oracle with the same candidate policy."""

    def _best_lookahead_split(self, indices, depth, lookahead_depth):
        node_score = self._leaf_score(indices)
        if self._is_terminal(indices, depth):
            return None, node_score
        best, best_score = None, node_score
        for split in self._candidate_splits(indices, depth):
            if lookahead_depth <= 1 or self._is_terminal_after_split(depth):
                score = self._leaf_score(split.left_indices) + self._leaf_score(split.right_indices)
            else:
                _, a = self._best_lookahead_split(split.left_indices, depth + 1, lookahead_depth - 1)
                _, b = self._best_lookahead_split(split.right_indices, depth + 1, lookahead_depth - 1)
                score = a + b
            if score < best_score - 1e-12 or (best is None and score <= node_score + 1e-12):
                best, best_score = split, min(score, node_score)
        return best, best_score


def main():
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
    y = np.array([0, 1, 1, 0])
    for sight in (1, 2, 3):
        model = Classifier(lookahead_depth=sight, max_depth=2).fit(X, y)
        assert np.array_equal(model.predict(X), y), "A feasible zero-gain root must not be pruned"
    nuisance_X = np.asarray([[a, b, noise] for a in (0, 1) for b in (0, 1)
                            for noise in (0, 1)], dtype=np.float32)
    nuisance_y = (nuisance_X[:, 0] != nuisance_X[:, 1]).astype(int)
    nuisance_seed = None
    for seed in range(64):
        cart = DecisionTreeClassifier(max_depth=2, random_state=seed, ccp_alpha=0).fit(nuisance_X, nuisance_y)
        if cart.tree_.feature[0] == 2:
            nuisance_seed = seed
            assert cart.score(nuisance_X, nuisance_y) == .5
            sighted = Classifier(max_depth=2, lookahead_depth=2, random_state=seed).fit(nuisance_X, nuisance_y)
            assert sighted.score(nuisance_X, nuisance_y) == 1
            break
    assert nuisance_seed is not None
    constant_X = np.zeros((16, 4), dtype=np.float32)
    constant_X[:, 3] = np.arange(16)
    constant_y = (constant_X[:, 3] >= 8).astype(int)
    for seed in range(8):
        model = Classifier(lookahead_depth=3, max_depth=1, max_features="sqrt",
                           min_samples_leaf=3, random_state=seed).fit(constant_X, constant_y)
        assert np.array_equal(model.predict(constant_X), constant_y), "Constant features need a feasible-feature fallback"
    rng = np.random.RandomState(71)
    X = rng.randint(0, 5, (24, 4)).astype(np.float32)
    y = rng.randint(0, 3, 24)
    weights = rng.randint(0, 4, 24).astype(float)
    checked = 0
    for depth in (2, 4, None):
        for horizon in (1, 2, 3):
            for features in (None, "sqrt"):
                for leaf in (1, 3):
                    params = dict(max_depth=depth, lookahead_depth=horizon, max_features=features,
                                  min_samples_leaf=leaf, random_state=17)
                    a = Classifier(**params).fit(X, y, sample_weight=weights)
                    b = Reference(**params).fit(X, y, sample_weight=weights)
                    assert np.allclose(a.predict_proba(X), b.predict_proba(X), rtol=0, atol=1e-12), params
                    assert a.get_depth() == b.get_depth(), params
                    checked += 1
    # Prepared weighted CART banks must reproduce the actual library RF,
    # including its random feature draws and zero-weight bootstrap exclusion.
    RF_X = X.copy()
    RF_X[:, :2] = 0
    RF_y = rng.randint(0, 2, len(y))
    RF_y[-1] = 2
    RF_cases = 0
    missing_class_bags = 0
    for depth in (3, 6, None):
        for leaf in (1, 5):
            for features in (None, "sqrt"):
                for forest_seed in (91, 103):
                    params = dict(max_depth=depth, min_samples_leaf=leaf, max_features=features,
                                  criterion="gini", min_samples_split=2, ccp_alpha=0.0)
                    forest = RandomForestClassifier(n_estimators=200, random_state=forest_seed,
                                                    n_jobs=1, **params).fit(RF_X, RF_y)
                    seeds = np.random.RandomState(forest_seed).randint(np.iinfo(np.int32).max, size=200)
                    assert np.array_equal(seeds, [tree.random_state for tree in forest.estimators_])
                    values, library_values = [], []
                    for seed, library_tree in zip(seeds, forest.estimators_):
                        sample = np.random.RandomState(int(seed)).randint(len(RF_y), size=len(RF_y))
                        counts = np.bincount(sample, minlength=len(RF_y))
                        missing_class_bags += int(counts[-1] == 0)
                        tree = DecisionTreeClassifier(random_state=int(seed), **params)
                        tree.fit(RF_X, RF_y, sample_weight=counts)
                        values.append(tree.predict_proba(RF_X))
                        library_values.append(library_tree.predict_proba(RF_X))
                    for count in (20, 40, 60, 100, 200):
                        assert np.allclose(np.mean(values[:count], axis=0),
                                           np.mean(library_values[:count], axis=0), rtol=0, atol=1e-12)
                        RF_cases += 1
                    assert np.allclose(np.mean(values, axis=0), forest.predict_proba(RF_X),
                                       rtol=0, atol=1e-12)
    assert missing_class_bags > 0
    from threadpoolctl import threadpool_info
    pools = threadpool_info()
    assert all(pool["num_threads"] == 1 for pool in pools)
    sources = [Path(__file__), REPO / "paper/scripts/fair_revision_runtime.py",
               REPO / "paper/array_revision_fair/runtime/_sighted_fast.pyx"]
    result = {"zero_gain_xor": True, "constant_feature_fallback_seeds": 8, "optimized_oracle_cases": checked,
              "nuisance_XOR_depth_matched_seed": nuisance_seed,
              "weighted_CART_RF_equivalence": True, "RF_prefix_cases": RF_cases,
              "missing_class_bootstrap_bags": missing_class_bags, "absolute_tolerance": 1e-12,
              "relative_tolerance": 0, "threadpools": pools,
              "source_hashes": {str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sources},
              "compiled_scorer_sha256": hashlib.sha256(Path(fast.__file__).read_bytes()).hexdigest()}
    path = REPO / "paper/array_revision_fair/harness_checks.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
