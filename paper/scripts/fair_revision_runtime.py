"""Matched unpruned classifier adapter; legacy results remain untouched."""

import importlib
import importlib.util
from pathlib import Path
import sys
import types

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RUNTIME = REPO / "paper/array_revision_fair/.cache/runtime/fair_tree"
package = types.ModuleType("fair_tree")
package.__path__ = [str(RUNTIME)]
sys.modules.setdefault("fair_tree", package)
spec = importlib.util.spec_from_file_location(
    "fair_tree._lookahead", REPO / "treeple/tree/_lookahead.py"
)
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
fast = importlib.import_module("fair_tree._sighted_fast")


class Classifier(base.LookaheadDecisionTreeClassifier):
    """Unpruned bounded search with zero-gain splits and weighted bootstraps.

    Zero-weight observations are excluded from split/leaf sample counts, as in
    library CART. The inherited parameter resolution still uses training size.
    The default min_impurity_decrease=0 allows a valid zero-gain split; no
    post-fit cost-complexity pruning is applied.
    """

    def _build_node(self, indices, depth):
        if depth == 0:
            indices = np.ascontiguousarray(indices[self._sample_weight[indices] > 0], dtype=np.intp)
        return super()._build_node(indices, depth)

    def _node_features(self, indices, depth):
        if self.max_features_ == self.n_features_in_:
            return np.arange(self.n_features_in_, dtype=np.intp)
        rng = np.random.RandomState(self._node_seed(indices, depth))
        selected = rng.choice(self.n_features_in_, size=self.max_features_, replace=False)
        if any(self._feature_has_partition(indices, feature) for feature in selected):
            return selected
        remainder = np.setdiff1d(np.arange(self.n_features_in_), selected)
        extra = []
        for feature in rng.permutation(remainder):
            extra.append(feature)
            if self._feature_has_partition(indices, feature):
                break
        return np.asarray(list(selected) + extra, dtype=np.intp)

    def _feature_has_partition(self, indices, feature):
        if len(indices) < 2 * self._min_samples_leaf:
            return False
        order = np.argsort(self._X[indices, feature], kind="mergesort")
        values = self._X[indices[order], feature]
        positions = np.flatnonzero(values[:-1] < values[1:]) + 1
        positions = positions[(positions >= self._min_samples_leaf) &
                              (len(indices) - positions >= self._min_samples_leaf)]
        if not len(positions):
            return False
        weights = np.cumsum(self._sample_weight[indices[order]])
        return bool(np.any((weights[positions - 1] >= self._min_weight_leaf) &
                           (weights[-1] - weights[positions - 1] >= self._min_weight_leaf)))

    def _best_lookahead_split_fast(self, indices, depth, lookahead_depth):
        result = fast.best_lookahead_split_classification(
            self._X, self._y.astype(np.intp, copy=False), self._sample_weight,
            np.ascontiguousarray(indices, dtype=np.intp),
            int(lookahead_depth), int(depth),
            -1 if self.max_depth is None else int(self.max_depth),
            int(self._min_samples_split), int(self._min_samples_leaf),
            float(self._min_weight_leaf),
            -1 if self.max_split_candidates is None else int(self.max_split_candidates),
            0 if self.criterion == "gini" else 1, int(self.n_classes_),
            int(self.max_features_), int(self._base_seed), True,
        )
        feature, threshold, left, right, score = result
        if feature < 0:
            return None, score
        # C_h includes stopping. Clamp only the round-trip discrepancy between
        # NumPy and Cython's accumulation of that same upper bound, so a valid
        # zero-gain split is not rejected by the inherited strict gain check.
        score = min(score, self._leaf_score(indices))
        return base._SplitCandidate(feature, threshold, left, right), score


def load_classifier():
    return Classifier
