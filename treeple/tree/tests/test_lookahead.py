import numpy as np
import pytest
from numpy.testing import assert_allclose

import treeple.tree._lookahead as lookahead_module
from treeple.ensemble import LookaheadRandomForestClassifier, LookaheadRandomForestRegressor
from treeple.tree import LookaheadDecisionTreeClassifier, LookaheadDecisionTreeRegressor


def _xor_data(repeats=20):
    X = np.asarray([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float64)
    y = np.asarray([0, 1, 1, 0])
    return np.repeat(X, repeats, axis=0), np.repeat(y, repeats)


def test_depth_two_lookahead_fits_xor_when_greedy_cannot_split():
    X, y = _xor_data()

    greedy = LookaheadDecisionTreeClassifier(
        lookahead_depth=1, max_depth=2, max_features=None, random_state=0
    ).fit(X, y)
    lookahead = LookaheadDecisionTreeClassifier(
        lookahead_depth=2, max_depth=2, max_features=None, random_state=0
    ).fit(X, y)

    assert greedy.get_depth() == 0
    assert lookahead.get_depth() == 2
    assert np.mean(lookahead.predict(X) == y) == 1.0


def test_lookahead_classifier_predict_proba_is_normalized():
    X, y = _xor_data()

    clf = LookaheadDecisionTreeClassifier(
        lookahead_depth=2, max_depth=2, max_features=None, random_state=0
    ).fit(X, y)

    proba = clf.predict_proba(X[:4])
    assert proba.shape == (4, 2)
    assert_allclose(proba.sum(axis=1), 1.0)


def test_cython_lookahead_matches_python_fallback():
    if lookahead_module._lookahead_fast is None:
        pytest.skip("Compiled lookahead helper is not available")

    X, y = _xor_data()

    fast = LookaheadDecisionTreeClassifier(
        lookahead_depth=2, max_depth=2, max_features=None, random_state=0
    ).fit(X, y)

    old_fast = lookahead_module._lookahead_fast
    lookahead_module._lookahead_fast = None
    try:
        fallback = LookaheadDecisionTreeClassifier(
            lookahead_depth=2, max_depth=2, max_features=None, random_state=0
        ).fit(X, y)
    finally:
        lookahead_module._lookahead_fast = old_fast

    assert fast.get_depth() == fallback.get_depth()
    assert_allclose(fast.predict_proba(X), fallback.predict_proba(X))
    assert np.array_equal(fast.predict(X), fallback.predict(X))


def test_lookahead_regressor_fits_simple_step_function():
    X = np.arange(12, dtype=np.float64).reshape(-1, 1)
    y = (X[:, 0] >= 6).astype(np.float64)

    reg = LookaheadDecisionTreeRegressor(
        lookahead_depth=1, max_depth=1, max_features=None, random_state=0
    ).fit(X, y)

    assert reg.get_depth() == 1
    assert_allclose(reg.predict([[1.0], [10.0]]), [0.0, 1.0])


def test_lookahead_random_forest_classifier_predicts_probabilities():
    X, y = _xor_data()

    forest = LookaheadRandomForestClassifier(
        n_estimators=5,
        lookahead_depth=2,
        max_depth=2,
        max_features=None,
        bootstrap=True,
        random_state=0,
    ).fit(X, y)

    proba = forest.predict_proba(X[:4])
    assert proba.shape == (4, 2)
    assert_allclose(proba.sum(axis=1), 1.0)
    assert np.mean(forest.predict(X) == y) == 1.0


def test_lookahead_random_forest_regressor_predicts_average():
    X = np.arange(12, dtype=np.float64).reshape(-1, 1)
    y = (X[:, 0] >= 6).astype(np.float64)

    forest = LookaheadRandomForestRegressor(
        n_estimators=3,
        lookahead_depth=1,
        max_depth=1,
        max_features=None,
        bootstrap=False,
        random_state=0,
    ).fit(X, y)

    assert_allclose(forest.predict([[1.0], [10.0]]), [0.0, 1.0])
