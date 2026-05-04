"""Lookahead decision trees for non-greedy split selection."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral, Real

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.utils import check_random_state
from sklearn.utils._param_validation import Interval, StrOptions
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import _check_sample_weight, check_is_fitted, validate_data


@dataclass
class _LookaheadNode:
    """A fitted binary tree node."""

    prediction: np.ndarray | float | int
    impurity: float
    n_node_samples: int
    weighted_n_node_samples: float
    value: np.ndarray | float
    feature: int = -2
    threshold: float = np.nan
    left: "_LookaheadNode | None" = None
    right: "_LookaheadNode | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None or self.right is None


@dataclass
class _SplitCandidate:
    feature: int
    threshold: float
    left_indices: np.ndarray
    right_indices: np.ndarray


@dataclass
class _TreeSummary:
    node_count: int
    max_depth: int
    n_leaves: int


class _BaseLookaheadDecisionTree(BaseEstimator):
    """Shared implementation for axis-aligned lookahead decision trees."""

    _parameter_constraints: dict = {
        "criterion": [StrOptions({"gini", "entropy", "log_loss", "squared_error", "mse"})],
        "lookahead_depth": [Interval(Integral, 1, None, closed="left")],
        "max_depth": [Interval(Integral, 1, None, closed="left"), None],
        "min_samples_split": [
            Interval(Integral, 2, None, closed="left"),
            Interval(Real, 0.0, 1.0, closed="right"),
        ],
        "min_samples_leaf": [
            Interval(Integral, 1, None, closed="left"),
            Interval(Real, 0.0, 1.0, closed="neither"),
        ],
        "min_weight_fraction_leaf": [Interval(Real, 0.0, 0.5, closed="both")],
        "max_features": [
            Interval(Integral, 1, None, closed="left"),
            Interval(Real, 0.0, 1.0, closed="right"),
            StrOptions({"sqrt", "log2"}),
            None,
        ],
        "max_split_candidates": [Interval(Integral, 1, None, closed="left"), None],
        "min_impurity_decrease": [Interval(Real, 0.0, None, closed="left")],
        "random_state": ["random_state"],
    }

    _estimator_type = None

    def __init__(
        self,
        *,
        criterion,
        lookahead_depth=1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features=None,
        max_split_candidates=None,
        min_impurity_decrease=0.0,
        random_state=None,
    ):
        self.criterion = criterion
        self.lookahead_depth = lookahead_depth
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_split_candidates = max_split_candidates
        self.min_impurity_decrease = min_impurity_decrease
        self.random_state = random_state

    def _fit_tree(self, X, y, sample_weight=None):
        X, y = validate_data(self, X, y, dtype=np.float64, ensure_2d=True, y_numeric=False)
        sample_weight = _check_sample_weight(sample_weight, X, dtype=np.float64)

        self._rng = check_random_state(self.random_state)
        self._base_seed = int(self._rng.randint(np.iinfo(np.int32).max))
        self.n_features_in_ = X.shape[1]
        self._X = X
        self._y = y
        self._sample_weight = sample_weight
        self._weighted_n_samples = float(sample_weight.sum())
        self._min_samples_leaf = self._resolve_min_samples_leaf(X.shape[0])
        self._min_samples_split = max(
            self._resolve_min_samples_split(X.shape[0]), 2 * self._min_samples_leaf
        )
        self._min_weight_leaf = self.min_weight_fraction_leaf * self._weighted_n_samples
        self.max_features_ = self._resolve_max_features()
        self._feature_importances = np.zeros(self.n_features_in_, dtype=np.float64)

        indices = np.arange(X.shape[0], dtype=np.intp)
        self.root_ = self._build_node(indices, depth=0)
        self.tree_ = _TreeSummary(
            node_count=self._count_nodes(self.root_),
            max_depth=self.get_depth(),
            n_leaves=self.get_n_leaves(),
        )

        del self._X
        del self._y
        del self._sample_weight
        del self._rng
        return self

    def _resolve_min_samples_leaf(self, n_samples):
        if isinstance(self.min_samples_leaf, Integral):
            return int(self.min_samples_leaf)
        return int(np.ceil(float(self.min_samples_leaf) * n_samples))

    def _resolve_min_samples_split(self, n_samples):
        if isinstance(self.min_samples_split, Integral):
            return int(self.min_samples_split)
        return int(np.ceil(float(self.min_samples_split) * n_samples))

    def _resolve_max_features(self):
        if self.max_features is None:
            return self.n_features_in_
        if self.max_features == "sqrt":
            return max(1, int(np.sqrt(self.n_features_in_)))
        if self.max_features == "log2":
            return max(1, int(np.log2(self.n_features_in_)))
        if isinstance(self.max_features, Integral):
            return min(int(self.max_features), self.n_features_in_)
        return max(1, int(float(self.max_features) * self.n_features_in_))

    def _build_node(self, indices, depth):
        impurity = self._impurity(indices)
        weighted_n_node_samples = self._weight_sum(indices)
        node = _LookaheadNode(
            prediction=self._node_prediction(indices),
            impurity=impurity,
            n_node_samples=indices.shape[0],
            weighted_n_node_samples=weighted_n_node_samples,
            value=self._node_value(indices),
        )

        split, terminal_score = self._best_lookahead_split(
            indices, depth=depth, lookahead_depth=self.lookahead_depth
        )
        if split is None:
            return node

        node_score = weighted_n_node_samples * impurity
        impurity_decrease = (node_score - terminal_score) / weighted_n_node_samples
        weighted_decrease = weighted_n_node_samples / self._weighted_n_samples * impurity_decrease
        if weighted_decrease < self.min_impurity_decrease:
            return node

        node.feature = split.feature
        node.threshold = split.threshold
        node.left = self._build_node(split.left_indices, depth + 1)
        node.right = self._build_node(split.right_indices, depth + 1)

        children_score = (
            node.left.weighted_n_node_samples * node.left.impurity
            + node.right.weighted_n_node_samples * node.right.impurity
        )
        self._feature_importances[node.feature] += max(node_score - children_score, 0.0)
        return node

    def _best_lookahead_split(self, indices, depth, lookahead_depth):
        node_score = self._weight_sum(indices) * self._impurity(indices)
        if self._is_terminal(indices, depth):
            return None, node_score

        best_split = None
        best_score = node_score

        for split in self._candidate_splits(indices, depth):
            if lookahead_depth <= 1 or self._is_terminal_after_split(depth):
                score = self._leaf_score(split.left_indices) + self._leaf_score(split.right_indices)
            else:
                _, left_score = self._best_lookahead_split(
                    split.left_indices, depth + 1, lookahead_depth - 1
                )
                _, right_score = self._best_lookahead_split(
                    split.right_indices, depth + 1, lookahead_depth - 1
                )
                score = left_score + right_score

            if score < best_score - 1e-12:
                best_score = score
                best_split = split

        return best_split, best_score

    def _is_terminal(self, indices, depth):
        if self.max_depth is not None and depth >= self.max_depth:
            return True
        if indices.shape[0] < self._min_samples_split:
            return True
        if self._weight_sum(indices) <= 0.0:
            return True
        return self._impurity(indices) <= 1e-12

    def _is_terminal_after_split(self, depth):
        return self.max_depth is not None and depth + 1 >= self.max_depth

    def _candidate_splits(self, indices, depth):
        features = self._node_features(indices, depth)
        X_node = self._X[indices]

        for feature in features:
            values = X_node[:, feature]
            order = np.argsort(values, kind="mergesort")
            sorted_values = values[order]
            diffs = sorted_values[:-1] < sorted_values[1:]
            positions = np.flatnonzero(diffs) + 1
            if positions.size == 0:
                continue

            left_counts = positions
            right_counts = indices.shape[0] - positions
            valid = (left_counts >= self._min_samples_leaf) & (
                right_counts >= self._min_samples_leaf
            )
            positions = positions[valid]
            if positions.size == 0:
                continue

            if self.max_split_candidates is not None and positions.size > self.max_split_candidates:
                select = np.linspace(
                    0, positions.size - 1, num=int(self.max_split_candidates), dtype=np.intp
                )
                positions = positions[select]

            thresholds = (sorted_values[positions - 1] + sorted_values[positions]) / 2.0
            for threshold in thresholds:
                left_mask = values <= threshold
                right_mask = ~left_mask
                left_indices = indices[left_mask]
                right_indices = indices[right_mask]
                if not self._valid_partition(left_indices, right_indices):
                    continue
                yield _SplitCandidate(
                    feature=int(feature),
                    threshold=float(threshold),
                    left_indices=left_indices,
                    right_indices=right_indices,
                )

    def _node_features(self, indices, depth):
        if self.max_features_ == self.n_features_in_:
            return np.arange(self.n_features_in_, dtype=np.intp)

        rng = np.random.RandomState(self._node_seed(indices, depth))
        return rng.choice(self.n_features_in_, size=self.max_features_, replace=False)

    def _node_seed(self, indices, depth):
        # A deterministic per-node seed keeps lookahead scoring independent of
        # candidate enumeration order while preserving random feature subsets.
        weighted_sum = int(np.sum((indices.astype(np.uint64) + 1) * 2654435761) % 2**32)
        return int((self._base_seed + 1000003 * depth + weighted_sum) % 2**32)

    def _valid_partition(self, left_indices, right_indices):
        if left_indices.shape[0] < self._min_samples_leaf:
            return False
        if right_indices.shape[0] < self._min_samples_leaf:
            return False
        if self._weight_sum(left_indices) < self._min_weight_leaf:
            return False
        if self._weight_sum(right_indices) < self._min_weight_leaf:
            return False
        return True

    def _leaf_score(self, indices):
        return self._weight_sum(indices) * self._impurity(indices)

    def _weight_sum(self, indices):
        return float(self._sample_weight[indices].sum())

    def _predict_nodes(self, X):
        check_is_fitted(self, "root_")
        X = validate_data(self, X, dtype=np.float64, reset=False)
        return [self._apply_one(row) for row in X]

    def _apply_one(self, row):
        node = self.root_
        while not node.is_leaf:
            if row[node.feature] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node

    def get_depth(self):
        """Return the depth of the fitted tree."""
        check_is_fitted(self, "root_")
        return self._node_depth(self.root_)

    def get_n_leaves(self):
        """Return the number of leaves of the fitted tree."""
        check_is_fitted(self, "root_")
        return self._count_leaves(self.root_)

    @property
    def feature_importances_(self):
        """Return impurity-based feature importances for the fitted tree."""
        check_is_fitted(self, "root_")
        normalizer = self._feature_importances.sum()
        if normalizer <= 0.0:
            return self._feature_importances.copy()
        return self._feature_importances / normalizer

    def _node_depth(self, node):
        if node.is_leaf:
            return 0
        return 1 + max(self._node_depth(node.left), self._node_depth(node.right))

    def _count_leaves(self, node):
        if node.is_leaf:
            return 1
        return self._count_leaves(node.left) + self._count_leaves(node.right)

    def _count_nodes(self, node):
        if node.is_leaf:
            return 1
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)


class LookaheadDecisionTreeClassifier(ClassifierMixin, _BaseLookaheadDecisionTree):
    """Axis-aligned decision tree classifier with multi-generation split scoring.

    ``lookahead_depth=1`` recovers greedy split scoring: each node chooses the
    split with the largest immediate impurity decrease. Larger values score each
    candidate root split by the best terminal impurity reachable after growing a
    complete lookahead subtree of that many split generations.
    """

    _parameter_constraints: dict = {
        **_BaseLookaheadDecisionTree._parameter_constraints,
        "criterion": [StrOptions({"gini", "entropy", "log_loss"})],
        "class_weight": [dict, StrOptions({"balanced"}), None],
    }

    def __init__(
        self,
        *,
        criterion="gini",
        lookahead_depth=1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features=None,
        max_split_candidates=None,
        min_impurity_decrease=0.0,
        class_weight=None,
        random_state=None,
    ):
        super().__init__(
            criterion=criterion,
            lookahead_depth=lookahead_depth,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_split_candidates=max_split_candidates,
            min_impurity_decrease=min_impurity_decrease,
            random_state=random_state,
        )
        self.class_weight = class_weight

    def fit(self, X, y, sample_weight=None):
        """Build a lookahead decision tree classifier from the training set."""
        self._validate_params()
        check_classification_targets(y)
        y = np.asarray(y)
        self.classes_, encoded_y = np.unique(y, return_inverse=True)
        self.n_classes_ = self.classes_.shape[0]
        if sample_weight is not None:
            sample_weight = np.asarray(sample_weight, dtype=np.float64)
        if self.class_weight is not None:
            class_weight = compute_sample_weight(self.class_weight, y)
            sample_weight = class_weight if sample_weight is None else sample_weight * class_weight
        return self._fit_tree(X, encoded_y, sample_weight=sample_weight)

    def predict(self, X):
        """Predict class labels for samples in X."""
        nodes = self._predict_nodes(X)
        encoded = np.asarray([node.prediction for node in nodes], dtype=np.intp)
        return self.classes_[encoded]

    def predict_proba(self, X):
        """Predict class probabilities for samples in X."""
        nodes = self._predict_nodes(X)
        return np.vstack([node.value for node in nodes])

    def _impurity(self, indices):
        proba = self._class_proba(indices)
        nonzero = proba > 0.0
        if self.criterion == "gini":
            return float(1.0 - np.dot(proba, proba))
        return float(-np.dot(proba[nonzero], np.log2(proba[nonzero])))

    def _node_prediction(self, indices):
        return int(np.argmax(self._class_counts(indices)))

    def _node_value(self, indices):
        return self._class_proba(indices)

    def _class_counts(self, indices):
        return np.bincount(
            self._y[indices], weights=self._sample_weight[indices], minlength=self.n_classes_
        ).astype(np.float64)

    def _class_proba(self, indices):
        counts = self._class_counts(indices)
        total = counts.sum()
        if total <= 0.0:
            return np.full(self.n_classes_, 1.0 / self.n_classes_)
        return counts / total


class LookaheadDecisionTreeRegressor(RegressorMixin, _BaseLookaheadDecisionTree):
    """Axis-aligned decision tree regressor with multi-generation split scoring."""

    _parameter_constraints: dict = {
        **_BaseLookaheadDecisionTree._parameter_constraints,
        "criterion": [StrOptions({"squared_error", "mse"})],
    }

    def __init__(
        self,
        *,
        criterion="squared_error",
        lookahead_depth=1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features=None,
        max_split_candidates=None,
        min_impurity_decrease=0.0,
        random_state=None,
    ):
        super().__init__(
            criterion=criterion,
            lookahead_depth=lookahead_depth,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_split_candidates=max_split_candidates,
            min_impurity_decrease=min_impurity_decrease,
            random_state=random_state,
        )

    def fit(self, X, y, sample_weight=None):
        """Build a lookahead decision tree regressor from the training set."""
        self._validate_params()
        y = np.asarray(y, dtype=np.float64)
        return self._fit_tree(X, y, sample_weight=sample_weight)

    def predict(self, X):
        """Predict regression target for samples in X."""
        nodes = self._predict_nodes(X)
        return np.asarray([node.prediction for node in nodes], dtype=np.float64)

    def _impurity(self, indices):
        y = self._y[indices]
        weight = self._sample_weight[indices]
        total = weight.sum()
        if total <= 0.0:
            return 0.0
        mean = np.average(y, weights=weight)
        return float(np.average((y - mean) ** 2, weights=weight))

    def _node_prediction(self, indices):
        return float(self._node_value(indices))

    def _node_value(self, indices):
        weight = self._sample_weight[indices]
        total = weight.sum()
        if total <= 0.0:
            return 0.0
        return float(np.average(self._y[indices], weights=weight))
