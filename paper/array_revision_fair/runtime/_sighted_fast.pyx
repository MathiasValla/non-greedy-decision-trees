# cython: boundscheck=False, wraparound=False, initializedcheck=False, nonecheck=False
"""Isolated bounded classification search for the matched forest revision.

The one-generation horizon scores sorted prefixes, not materialized children.
Deeper horizons minimize the two child objectives separately. This module does
not replace treeple's legacy scorer or implement sklearn's random draw order.
"""

import numpy as np
cimport numpy as cnp

from libc.float cimport DBL_EPSILON
from libc.math cimport fabs, floor, isfinite, log
from libc.stdlib cimport free, malloc


ctypedef cnp.intp_t ITYPE_t

cdef double _EPS = 1e-12
cdef double _LOG2 = log(2.0)


cdef double _impurity(double* counts, double weight, int n_classes, int criterion):
    cdef int cls
    cdef double p
    cdef double impurity = 0.0
    if weight <= 0.0:
        return 0.0
    if criterion == 0:
        impurity = 1.0
        for cls in range(n_classes):
            p = counts[cls] / weight
            impurity -= p * p
    else:
        for cls in range(n_classes):
            if counts[cls] > 0.0:
                p = counts[cls] / weight
                impurity -= p * log(p) / _LOG2
    return impurity


cdef double _leaf_score_counts(double* counts, double weight, int n_classes, int criterion):
    # Preserve the legacy separate leaf products rather than a fused multiply-add.
    cdef volatile double score = weight * _impurity(counts, weight, n_classes, criterion)
    return score


cdef double _partition_leaf_score(
    double[:, ::1] X,
    ITYPE_t[::1] y,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    Py_ssize_t feature,
    double threshold,
    double* left_counts,
    double* right_counts,
    int n_classes,
    int criterion,
):
    """Resolve a fractional-weight roundoff tie in legacy accumulation order."""
    cdef Py_ssize_t i, idx
    cdef int cls
    cdef double left_weight = 0.0
    cdef double right_weight = 0.0
    cdef double weight
    for cls in range(n_classes):
        left_counts[cls] = 0.0
        right_counts[cls] = 0.0
    for i in range(indices.shape[0]):
        idx = indices[i]
        cls = <int>y[idx]
        weight = sample_weight[idx]
        if X[idx, feature] <= threshold:
            left_counts[cls] += weight
            left_weight += weight
        else:
            right_counts[cls] += weight
            right_weight += weight
    return (_leaf_score_counts(left_counts, left_weight, n_classes, criterion)
            + _leaf_score_counts(right_counts, right_weight, n_classes, criterion))


cdef tuple _partition_weights(
    double[::1] values,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    double threshold,
):
    cdef Py_ssize_t i
    cdef double left_weight = 0.0
    cdef double right_weight = 0.0
    for i in range(indices.shape[0]):
        if values[i] <= threshold:
            left_weight += sample_weight[indices[i]]
        else:
            right_weight += sample_weight[indices[i]]
    return left_weight, right_weight


cdef object _ordered_features(ITYPE_t[::1] indices, int depth,
                              Py_ssize_t n_features, int max_features,
                              object base_seed):
    cdef object all_features = np.arange(n_features, dtype=np.intp)
    cdef object selected, remainder, rng
    cdef object index_array
    cdef object weighted_sum, seed
    if max_features < 0 or max_features >= n_features:
        return all_features
    # Keep the NumPy expression and choice order identical to _node_seed.
    index_array = np.asarray(indices)
    weighted_sum = int(np.sum((index_array.astype(np.uint64) + 1) * 2654435761) % 2**32)
    seed = int((base_seed + 1000003 * depth + weighted_sum) % 2**32)
    rng = np.random.RandomState(seed)
    selected = rng.choice(n_features, size=max_features, replace=False)
    remainder = np.setdiff1d(all_features, selected)
    return np.asarray(np.concatenate((selected, rng.permutation(remainder))), dtype=np.intp)


cdef tuple _best_clf(
    double[:, ::1] X,
    ITYPE_t[::1] y,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    int lookahead_depth,
    int depth,
    int max_depth,
    int min_samples_split,
    int min_samples_leaf,
    double min_weight_leaf,
    int max_split_candidates,
    int criterion,
    int n_classes,
    int max_features,
    object base_seed,
    bint allow_zero_gain,
    bint exact_weights,
    bint keep_split,
):
    cdef Py_ssize_t n_samples = indices.shape[0]
    cdef Py_ssize_t n_features = X.shape[1]
    cdef double* node_counts = <double*>malloc(n_classes * sizeof(double))
    cdef double* left_counts = <double*>malloc(n_classes * sizeof(double))
    cdef double* right_counts = <double*>malloc(n_classes * sizeof(double))
    cdef double* scratch_left = <double*>malloc(n_classes * sizeof(double))
    cdef double* scratch_right = <double*>malloc(n_classes * sizeof(double))
    cdef Py_ssize_t i, idx, k, j, p, selected, feature, feature_i
    cdef Py_ssize_t pos_count, eval_count, boundary, left_count, right_count
    cdef Py_ssize_t left_i, right_i, feature_budget
    cdef int cls, best_feature = -1
    cdef double weight, total = 0.0
    cdef double impurity, node_score, best_score, score, threshold
    cdef double best_threshold = np.nan
    cdef double left_weight, right_weight, error_bound
    cdef bint leaf_horizon, valid_seen = False
    cdef bint best_exact = True
    cdef bint candidate_exact
    cdef object best_left = None
    cdef object best_right = None
    cdef tuple left_result, right_result, weight_result
    cdef cnp.ndarray[ITYPE_t, ndim=1] features_arr, order_arr, positions_arr
    cdef cnp.ndarray[ITYPE_t, ndim=1] left_arr, right_arr
    cdef ITYPE_t[::1] features, order, positions, left_indices, right_indices
    cdef cnp.ndarray[double, ndim=1] values_arr
    cdef double[::1] values
    cdef cnp.ndarray[double, ndim=2] suffix_arr
    cdef double[:, ::1] suffix

    if (node_counts == NULL or left_counts == NULL or right_counts == NULL
            or scratch_left == NULL or scratch_right == NULL):
        free(node_counts)
        free(left_counts)
        free(right_counts)
        free(scratch_left)
        free(scratch_right)
        raise MemoryError()

    try:
        for cls in range(n_classes):
            node_counts[cls] = 0.0
        for i in range(n_samples):
            idx = indices[i]
            weight = sample_weight[idx]
            node_counts[<int>y[idx]] += weight
            total += weight
        impurity = _impurity(node_counts, total, n_classes, criterion)
        node_score = total * impurity
        best_score = node_score
        if ((max_depth >= 0 and depth >= max_depth)
                or n_samples < min_samples_split or total <= 0.0 or impurity <= _EPS):
            return -1, np.nan, None, None, node_score

        leaf_horizon = lookahead_depth <= 1 or (max_depth >= 0 and depth + 1 >= max_depth)
        error_bound = 64.0 * DBL_EPSILON * n_samples * max(total, 1.0)
        features_arr = _ordered_features(indices, depth, n_features, max_features, base_seed)
        features = features_arr
        feature_budget = n_features if max_features < 0 else min(max_features, n_features)
        values_arr = np.empty(n_samples, dtype=np.float64)
        values = values_arr
        positions_arr = np.empty(max(n_samples - 1, 1), dtype=np.intp)
        positions = positions_arr

        for feature_i in range(features.shape[0]):
            # A valid partition, not a positive gain, satisfies the feature budget.
            if feature_i >= feature_budget and valid_seen:
                break
            feature = features[feature_i]
            for i in range(n_samples):
                values[i] = X[indices[i], feature]
                if not isfinite(values[i]):
                    raise ValueError("Active feature values must be finite")
            order_arr = np.asarray(np.argsort(values_arr, kind="mergesort"), dtype=np.intp)
            order = order_arr
            pos_count = 0
            for k in range(1, n_samples):
                if (values[order[k - 1]] < values[order[k]]
                        and k >= min_samples_leaf and n_samples - k >= min_samples_leaf):
                    positions[pos_count] = k
                    pos_count += 1
            if pos_count == 0:
                continue
            eval_count = min(pos_count, max_split_candidates) if max_split_candidates > 0 else pos_count

            if leaf_horizon:
                boundary = 0
                left_weight = 0.0
                right_weight = total
                for cls in range(n_classes):
                    left_counts[cls] = 0.0
                    right_counts[cls] = node_counts[cls]
                if not exact_weights:
                    # Suffix sums avoid losing small right masses to total-prefix cancellation.
                    suffix_arr = np.empty((n_samples + 1, n_classes + 1), dtype=np.float64)
                    suffix = suffix_arr
                    for cls in range(n_classes + 1):
                        suffix[n_samples, cls] = 0.0
                    for i in range(n_samples - 1, -1, -1):
                        for cls in range(n_classes + 1):
                            suffix[i, cls] = suffix[i + 1, cls]
                        idx = indices[order[i]]
                        weight = sample_weight[idx]
                        suffix[i, <int>y[idx]] += weight
                        suffix[i, n_classes] += weight

            for j in range(eval_count):
                if eval_count == pos_count:
                    p = positions[j]
                elif eval_count == 1:
                    p = positions[0]
                else:
                    selected = <Py_ssize_t>((<double>j * (pos_count - 1)) / (eval_count - 1))
                    p = positions[selected]
                threshold = (values[order[p - 1]] + values[order[p]]) / 2.0

                if leaf_horizon:
                    # Midpoint rounding can move the actual boundary beyond p.
                    while boundary < n_samples and values[order[boundary]] <= threshold:
                        idx = indices[order[boundary]]
                        cls = <int>y[idx]
                        weight = sample_weight[idx]
                        left_counts[cls] += weight
                        left_weight += weight
                        if exact_weights:
                            right_counts[cls] -= weight
                            right_weight -= weight
                        boundary += 1
                    left_count = boundary
                    right_count = n_samples - boundary
                    if not exact_weights:
                        right_weight = suffix[boundary, n_classes]
                    if left_count < min_samples_leaf or right_count < min_samples_leaf:
                        continue
                    if (not exact_weights and min_weight_leaf > 0.0
                            and (fabs(left_weight - min_weight_leaf) <= error_bound
                                 or fabs(right_weight - min_weight_leaf) <= error_bound)):
                        weight_result = _partition_weights(values, sample_weight, indices, threshold)
                        # Do not replace the sweep accumulators with differently ordered sums.
                        if weight_result[0] < min_weight_leaf or weight_result[1] < min_weight_leaf:
                            continue
                    elif left_weight < min_weight_leaf or right_weight < min_weight_leaf:
                        continue
                    valid_seen = True
                    score = _leaf_score_counts(left_counts, left_weight, n_classes, criterion)
                    if exact_weights:
                        score += _leaf_score_counts(right_counts, right_weight, n_classes, criterion)
                    else:
                        score += _leaf_score_counts(&suffix[boundary, 0], right_weight, n_classes, criterion)
                    candidate_exact = exact_weights
                    if not exact_weights and fabs(score - best_score) <= error_bound + _EPS:
                        score = _partition_leaf_score(
                            X, y, sample_weight, indices, feature, threshold,
                            scratch_left, scratch_right, n_classes, criterion)
                        candidate_exact = True
                        if best_feature >= 0 and not best_exact:
                            best_score = _partition_leaf_score(
                                X, y, sample_weight, indices, best_feature, best_threshold,
                                scratch_left, scratch_right, n_classes, criterion)
                            if allow_zero_gain and best_score > node_score:
                                best_score = node_score
                            best_exact = True
                else:
                    left_count = 0
                    right_count = 0
                    left_weight = 0.0
                    right_weight = 0.0
                    for i in range(n_samples):
                        if values[i] <= threshold:
                            left_count += 1
                            left_weight += sample_weight[indices[i]]
                        else:
                            right_count += 1
                            right_weight += sample_weight[indices[i]]
                    if (left_count < min_samples_leaf or right_count < min_samples_leaf
                            or left_weight < min_weight_leaf or right_weight < min_weight_leaf):
                        continue
                    valid_seen = True
                    left_arr = np.empty(left_count, dtype=np.intp)
                    right_arr = np.empty(right_count, dtype=np.intp)
                    left_indices = left_arr
                    right_indices = right_arr
                    left_i = 0
                    right_i = 0
                    for i in range(n_samples):
                        if values[i] <= threshold:
                            left_indices[left_i] = indices[i]
                            left_i += 1
                        else:
                            right_indices[right_i] = indices[i]
                            right_i += 1
                    left_result = _best_clf(
                        X, y, sample_weight, left_indices, lookahead_depth - 1, depth + 1,
                        max_depth, min_samples_split, min_samples_leaf, min_weight_leaf,
                        max_split_candidates, criterion, n_classes, max_features, base_seed,
                        allow_zero_gain, exact_weights, False)
                    right_result = _best_clf(
                        X, y, sample_weight, right_indices, lookahead_depth - 1, depth + 1,
                        max_depth, min_samples_split, min_samples_leaf, min_weight_leaf,
                        max_split_candidates, criterion, n_classes, max_features, base_seed,
                        allow_zero_gain, exact_weights, False)
                    score = <double>left_result[4] + <double>right_result[4]
                    candidate_exact = True

                if (score < best_score - _EPS
                        or (allow_zero_gain and best_feature < 0 and score <= node_score + _EPS)):
                    best_score = min(score, node_score) if allow_zero_gain else score
                    best_exact = candidate_exact
                    best_feature = <int>feature
                    best_threshold = threshold
                    if keep_split and not leaf_horizon:
                        best_left = left_arr
                        best_right = right_arr

        if best_feature >= 0 and leaf_horizon:
            if not best_exact:
                best_score = _partition_leaf_score(
                    X, y, sample_weight, indices, best_feature, best_threshold,
                    scratch_left, scratch_right, n_classes, criterion)
                if allow_zero_gain:
                    best_score = min(best_score, node_score)
            if not allow_zero_gain and not (best_score < node_score - _EPS):
                return -1, np.nan, None, None, node_score
            if keep_split:
                left_count = 0
                for i in range(n_samples):
                    if X[indices[i], best_feature] <= best_threshold:
                        left_count += 1
                left_arr = np.empty(left_count, dtype=np.intp)
                right_arr = np.empty(n_samples - left_count, dtype=np.intp)
                left_indices = left_arr
                right_indices = right_arr
                left_i = 0
                right_i = 0
                for i in range(n_samples):
                    if X[indices[i], best_feature] <= best_threshold:
                        left_indices[left_i] = indices[i]
                        left_i += 1
                    else:
                        right_indices[right_i] = indices[i]
                        right_i += 1
                best_left = left_arr
                best_right = right_arr
        return best_feature, best_threshold, best_left, best_right, best_score
    finally:
        free(node_counts)
        free(left_counts)
        free(right_counts)
        free(scratch_left)
        free(scratch_right)


def best_lookahead_split_classification(
    double[:, ::1] X,
    ITYPE_t[::1] y,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    int lookahead_depth,
    int depth,
    int max_depth,
    int min_samples_split,
    int min_samples_leaf,
    double min_weight_leaf,
    int max_split_candidates,
    int criterion,
    int n_classes,
    int max_features=-1,
    base_seed=0,
    bint allow_zero_gain=True,
):
    """Return ``(feature, threshold, left_indices, right_indices, score)``.

    Required argument order matches the legacy classifier scorer. Criterion 0
    is Gini; 1 is entropy. Negative max_depth/max_split_candidates mean uncapped;
    max_features=-1 means all features. The horizon is clipped by actual depth.

    Restricted features follow _node_seed's NumPy weighted-index hash, ordered
    RandomState.choice, then a permutation of the remaining features. The tail
    is inspected only if the initial subset has no valid evaluated partition,
    and stops at its first feasible feature. Validity is independent of gain.
    This matches CART's feasibility extension, not its feature RNG or thresholds.

    A score improvement must exceed the legacy absolute 1e-12 tolerance. With
    allow_zero_gain=True, the first valid numerically non-worsening split is also
    accepted; ties keep their first candidate. Pure/size/depth stops still apply.
    Set allow_zero_gain=False for the legacy positive-gain policy. Zero weights
    count as observations if present in indices; the adapter removes them for
    CART-compatible bootstrap counts. Active weights must be finite/nonnegative.
    """
    cdef Py_ssize_t i, idx
    cdef double weight, total = 0.0
    cdef bint exact_weights = True
    if y.shape[0] != X.shape[0] or sample_weight.shape[0] != X.shape[0]:
        raise ValueError("X, y, and sample_weight must have matching lengths")
    if n_classes < 1 or criterion not in (0, 1):
        raise ValueError("n_classes must be positive and criterion must be 0 or 1")
    if lookahead_depth < 1 or depth < 0 or min_samples_split < 2 or min_samples_leaf < 1:
        raise ValueError("Invalid horizon, depth, or sample-count constraint")
    if not isfinite(min_weight_leaf) or min_weight_leaf < 0.0 or max_features == 0:
        raise ValueError("Invalid minimum leaf weight or feature budget")
    for i in range(indices.shape[0]):
        idx = indices[i]
        if idx < 0 or idx >= X.shape[0]:
            raise ValueError("indices contain an out-of-range observation")
        if y[idx] < 0 or y[idx] >= n_classes:
            raise ValueError("Active labels must lie in [0, n_classes)")
        weight = sample_weight[idx]
        if not isfinite(weight) or weight < 0.0:
            raise ValueError("Active weights must be finite and nonnegative")
        if weight != floor(weight):
            exact_weights = False
        if weight > 9007199254740992.0 - total:
            exact_weights = False
        total += weight
    if not isfinite(total):
        raise ValueError("Active total weight must be finite")
    if total > 9007199254740992.0:
        exact_weights = False
    return _best_clf(
        X, y, sample_weight, indices, lookahead_depth, depth, max_depth,
        min_samples_split, min_samples_leaf, min_weight_leaf, max_split_candidates,
        criterion, n_classes, max_features, int(base_seed), allow_zero_gain,
        exact_weights, True)
