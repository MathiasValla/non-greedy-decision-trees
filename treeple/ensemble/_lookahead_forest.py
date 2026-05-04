"""Random forests built from lookahead decision trees."""

from __future__ import annotations

from numbers import Integral, Real

import numpy as np
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.utils import check_random_state
from sklearn.utils._param_validation import Interval, StrOptions
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.utils.multiclass import check_classification_targets
from sklearn.utils.validation import _check_sample_weight, check_is_fitted, validate_data

from ..tree import LookaheadDecisionTreeClassifier, LookaheadDecisionTreeRegressor


def _parallel_fit_tree(tree, X, y, sample_weight, sample_indices):
    tree.fit(X[sample_indices], y[sample_indices], sample_weight=sample_weight[sample_indices])
    return tree


class _BaseLookaheadRandomForest(BaseEstimator):
    """Shared implementation for forests of lookahead trees."""

    _parameter_constraints: dict = {
        "n_estimators": [Interval(Integral, 1, None, closed="left")],
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
        "bootstrap": ["boolean"],
        "max_samples": [
            Interval(Integral, 1, None, closed="left"),
            Interval(Real, 0.0, 1.0, closed="right"),
            None,
        ],
        "n_jobs": [Integral, None],
        "random_state": ["random_state"],
        "verbose": ["verbose"],
    }

    def __init__(
        self,
        n_estimators=100,
        *,
        criterion,
        lookahead_depth=1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features="sqrt",
        max_split_candidates=None,
        min_impurity_decrease=0.0,
        bootstrap=True,
        max_samples=None,
        n_jobs=None,
        random_state=None,
        verbose=0,
    ):
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.lookahead_depth = lookahead_depth
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_split_candidates = max_split_candidates
        self.min_impurity_decrease = min_impurity_decrease
        self.bootstrap = bootstrap
        self.max_samples = max_samples
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose

    def _fit_forest(self, X, y, sample_weight=None):
        X, y = validate_data(self, X, y, dtype=np.float64, ensure_2d=True, y_numeric=False)
        sample_weight = _check_sample_weight(sample_weight, X, dtype=np.float64)

        rng = check_random_state(self.random_state)
        n_samples_bootstrap = self._get_n_samples_bootstrap(X.shape[0])
        seeds = rng.randint(np.iinfo(np.int32).max, size=self.n_estimators)
        samples = [
            self._draw_sample_indices(rng, X.shape[0], n_samples_bootstrap)
            for _ in range(self.n_estimators)
        ]
        trees = [self._make_tree(seed) for seed in seeds]

        self.estimators_ = Parallel(
            n_jobs=self.n_jobs, verbose=self.verbose, prefer="threads"
        )(
            delayed(_parallel_fit_tree)(tree, X, y, sample_weight, sample_indices)
            for tree, sample_indices in zip(trees, samples)
        )
        self.estimators_samples_ = samples
        self.n_features_in_ = X.shape[1]
        return self

    def _get_n_samples_bootstrap(self, n_samples):
        if self.max_samples is None:
            return n_samples
        if isinstance(self.max_samples, Integral):
            if self.max_samples > n_samples:
                raise ValueError("max_samples must be <= n_samples")
            return int(self.max_samples)
        return max(1, int(round(float(self.max_samples) * n_samples)))

    def _draw_sample_indices(self, rng, n_samples, n_samples_bootstrap):
        if self.bootstrap:
            return rng.randint(0, n_samples, size=n_samples_bootstrap, dtype=np.intp)
        if self.max_samples is None:
            return np.arange(n_samples, dtype=np.intp)
        return rng.choice(n_samples, size=n_samples_bootstrap, replace=False).astype(np.intp)

    @property
    def feature_importances_(self):
        """Return averaged impurity-based feature importances."""
        check_is_fitted(self, "estimators_")
        importances = np.asarray([tree.feature_importances_ for tree in self.estimators_])
        mean_importances = importances.mean(axis=0)
        normalizer = mean_importances.sum()
        if normalizer <= 0.0:
            return mean_importances
        return mean_importances / normalizer


class LookaheadRandomForestClassifier(ClassifierMixin, _BaseLookaheadRandomForest):
    """Random forest classifier using lookahead decision tree base estimators."""

    _parameter_constraints: dict = {
        **_BaseLookaheadRandomForest._parameter_constraints,
        "criterion": [StrOptions({"gini", "entropy", "log_loss"})],
        "class_weight": [
            dict,
            StrOptions({"balanced", "balanced_subsample"}),
            None,
        ],
    }

    def __init__(
        self,
        n_estimators=100,
        *,
        criterion="gini",
        lookahead_depth=1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features="sqrt",
        max_split_candidates=None,
        min_impurity_decrease=0.0,
        bootstrap=True,
        max_samples=None,
        n_jobs=None,
        random_state=None,
        verbose=0,
        class_weight=None,
    ):
        super().__init__(
            n_estimators=n_estimators,
            criterion=criterion,
            lookahead_depth=lookahead_depth,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_split_candidates=max_split_candidates,
            min_impurity_decrease=min_impurity_decrease,
            bootstrap=bootstrap,
            max_samples=max_samples,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
        )
        self.class_weight = class_weight

    def fit(self, X, y, sample_weight=None):
        """Build a forest of lookahead decision tree classifiers."""
        self._validate_params()
        check_classification_targets(y)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        self.n_classes_ = self.classes_.shape[0]
        if sample_weight is not None:
            sample_weight = np.asarray(sample_weight, dtype=np.float64)
        if self.class_weight == "balanced":
            class_weight = compute_sample_weight("balanced", y)
            sample_weight = class_weight if sample_weight is None else sample_weight * class_weight
        return self._fit_forest(X, y, sample_weight=sample_weight)

    def predict_proba(self, X):
        """Predict class probabilities for X."""
        check_is_fitted(self, "estimators_")
        X = validate_data(self, X, dtype=np.float64, reset=False)
        proba = np.zeros((X.shape[0], self.n_classes_), dtype=np.float64)
        class_to_index = {label: index for index, label in enumerate(self.classes_)}

        for tree in self.estimators_:
            tree_proba = tree.predict_proba(X)
            for tree_index, label in enumerate(tree.classes_):
                proba[:, class_to_index[label]] += tree_proba[:, tree_index]

        proba /= len(self.estimators_)
        return proba

    def predict(self, X):
        """Predict class labels for X."""
        proba = self.predict_proba(X)
        return self.classes_.take(np.argmax(proba, axis=1), axis=0)

    def _make_tree(self, seed):
        class_weight = (
            "balanced" if self.class_weight == "balanced_subsample" else self.class_weight
        )
        if self.class_weight == "balanced":
            class_weight = None
        return LookaheadDecisionTreeClassifier(
            criterion=self.criterion,
            lookahead_depth=self.lookahead_depth,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_features=self.max_features,
            max_split_candidates=self.max_split_candidates,
            min_impurity_decrease=self.min_impurity_decrease,
            class_weight=class_weight,
            random_state=int(seed),
        )


class LookaheadRandomForestRegressor(RegressorMixin, _BaseLookaheadRandomForest):
    """Random forest regressor using lookahead decision tree base estimators."""

    _parameter_constraints: dict = {
        **_BaseLookaheadRandomForest._parameter_constraints,
        "criterion": [StrOptions({"squared_error", "mse"})],
    }

    def __init__(
        self,
        n_estimators=100,
        *,
        criterion="squared_error",
        lookahead_depth=1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features="sqrt",
        max_split_candidates=None,
        min_impurity_decrease=0.0,
        bootstrap=True,
        max_samples=None,
        n_jobs=None,
        random_state=None,
        verbose=0,
    ):
        super().__init__(
            n_estimators=n_estimators,
            criterion=criterion,
            lookahead_depth=lookahead_depth,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_split_candidates=max_split_candidates,
            min_impurity_decrease=min_impurity_decrease,
            bootstrap=bootstrap,
            max_samples=max_samples,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
        )

    def fit(self, X, y, sample_weight=None):
        """Build a forest of lookahead decision tree regressors."""
        self._validate_params()
        y = np.asarray(y, dtype=np.float64)
        return self._fit_forest(X, y, sample_weight=sample_weight)

    def predict(self, X):
        """Predict regression target for X."""
        check_is_fitted(self, "estimators_")
        predictions = np.asarray([tree.predict(X) for tree in self.estimators_])
        return predictions.mean(axis=0)

    def _make_tree(self, seed):
        return LookaheadDecisionTreeRegressor(
            criterion=self.criterion,
            lookahead_depth=self.lookahead_depth,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_features=self.max_features,
            max_split_candidates=self.max_split_candidates,
            min_impurity_decrease=self.min_impurity_decrease,
            random_state=int(seed),
        )
