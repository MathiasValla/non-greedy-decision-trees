# cython: boundscheck=False, wraparound=False, initializedcheck=False, nonecheck=False
"""Cython helpers for lookahead split scoring."""

import numpy as np
cimport numpy as cnp

from libc.float cimport DBL_MAX
from libc.math cimport log
from libc.stdlib cimport free, malloc


ctypedef cnp.intp_t ITYPE_t

cdef double _LOG2 = log(2.0)


cdef double _weight_sum(double[::1] sample_weight, ITYPE_t[::1] indices):
    cdef Py_ssize_t i
    cdef double total = 0.0
    for i in range(indices.shape[0]):
        total += sample_weight[indices[i]]
    return total


cdef double _clf_impurity(
    ITYPE_t[::1] y,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    int n_classes,
    int criterion,
):
    cdef double* counts = <double*>malloc(n_classes * sizeof(double))
    cdef Py_ssize_t i
    cdef int cls
    cdef double total = 0.0
    cdef double impurity = 0.0
    cdef double p

    if counts == NULL:
        raise MemoryError()

    try:
        for cls in range(n_classes):
            counts[cls] = 0.0

        for i in range(indices.shape[0]):
            cls = <int>y[indices[i]]
            counts[cls] += sample_weight[indices[i]]
            total += sample_weight[indices[i]]

        if total <= 0.0:
            return 0.0

        if criterion == 0:
            impurity = 1.0
            for cls in range(n_classes):
                p = counts[cls] / total
                impurity -= p * p
        else:
            impurity = 0.0
            for cls in range(n_classes):
                if counts[cls] > 0.0:
                    p = counts[cls] / total
                    impurity -= p * log(p) / _LOG2
        return impurity
    finally:
        free(counts)


cdef double _clf_leaf_score(
    ITYPE_t[::1] y,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    int n_classes,
    int criterion,
):
    return _weight_sum(sample_weight, indices) * _clf_impurity(
        y, sample_weight, indices, n_classes, criterion
    )


cdef bint _clf_is_terminal(
    ITYPE_t[::1] y,
    double[::1] sample_weight,
    ITYPE_t[::1] indices,
    int depth,
    int max_depth,
    int min_samples_split,
    int n_classes,
    int criterion,
):
    if max_depth >= 0 and depth >= max_depth:
        return True
    if indices.shape[0] < min_samples_split:
        return True
    if _weight_sum(sample_weight, indices) <= 0.0:
        return True
    return _clf_impurity(y, sample_weight, indices, n_classes, criterion) <= 1e-12


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
    bint keep_split,
):
    cdef Py_ssize_t n_samples = indices.shape[0]
    cdef Py_ssize_t n_features = X.shape[1]
    cdef double node_score = _clf_leaf_score(
        y, sample_weight, indices, n_classes, criterion
    )
    cdef double best_score = node_score
    cdef double score
    cdef int best_feature = -1
    cdef double best_threshold = np.nan
    cdef object best_left = None
    cdef object best_right = None

    cdef Py_ssize_t feature
    cdef Py_ssize_t i
    cdef Py_ssize_t k
    cdef Py_ssize_t j
    cdef Py_ssize_t p
    cdef Py_ssize_t pos_count
    cdef Py_ssize_t eval_count
    cdef Py_ssize_t selected
    cdef Py_ssize_t left_count
    cdef Py_ssize_t right_count
    cdef Py_ssize_t left_i
    cdef Py_ssize_t right_i
    cdef double threshold
    cdef double left_weight
    cdef double right_weight
    cdef tuple left_result
    cdef tuple right_result

    cdef cnp.ndarray[double, ndim=1] values_arr
    cdef double[::1] values
    cdef cnp.ndarray[ITYPE_t, ndim=1] order_arr
    cdef ITYPE_t[::1] order
    cdef cnp.ndarray[ITYPE_t, ndim=1] positions_arr
    cdef ITYPE_t[::1] positions
    cdef cnp.ndarray[ITYPE_t, ndim=1] left_arr
    cdef cnp.ndarray[ITYPE_t, ndim=1] right_arr
    cdef ITYPE_t[::1] left_indices
    cdef ITYPE_t[::1] right_indices

    if _clf_is_terminal(
        y, sample_weight, indices, depth, max_depth, min_samples_split,
        n_classes, criterion
    ):
        return -1, np.nan, None, None, node_score

    for feature in range(n_features):
        values_arr = np.empty(n_samples, dtype=np.float64)
        values = values_arr
        for i in range(n_samples):
            values[i] = X[indices[i], feature]

        order_arr = np.asarray(np.argsort(values_arr, kind="mergesort"), dtype=np.intp)
        order = order_arr
        positions_arr = np.empty(max(n_samples - 1, 1), dtype=np.intp)
        positions = positions_arr
        pos_count = 0

        for k in range(1, n_samples):
            if values[order[k - 1]] < values[order[k]]:
                if k >= min_samples_leaf and n_samples - k >= min_samples_leaf:
                    positions[pos_count] = k
                    pos_count += 1

        if pos_count == 0:
            continue

        if max_split_candidates > 0 and pos_count > max_split_candidates:
            eval_count = max_split_candidates
        else:
            eval_count = pos_count

        for j in range(eval_count):
            if eval_count == pos_count:
                p = positions[j]
            elif eval_count == 1:
                p = positions[0]
            else:
                selected = <Py_ssize_t>((<double>j * (pos_count - 1)) / (eval_count - 1))
                p = positions[selected]

            threshold = (values[order[p - 1]] + values[order[p]]) / 2.0
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

            if left_count < min_samples_leaf or right_count < min_samples_leaf:
                continue
            if left_weight < min_weight_leaf or right_weight < min_weight_leaf:
                continue

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

            if lookahead_depth <= 1 or (max_depth >= 0 and depth + 1 >= max_depth):
                score = (
                    _clf_leaf_score(y, sample_weight, left_indices, n_classes, criterion)
                    + _clf_leaf_score(y, sample_weight, right_indices, n_classes, criterion)
                )
            else:
                left_result = _best_clf(
                    X, y, sample_weight, left_indices, lookahead_depth - 1,
                    depth + 1, max_depth, min_samples_split, min_samples_leaf,
                    min_weight_leaf, max_split_candidates, criterion, n_classes, False
                )
                right_result = _best_clf(
                    X, y, sample_weight, right_indices, lookahead_depth - 1,
                    depth + 1, max_depth, min_samples_split, min_samples_leaf,
                    min_weight_leaf, max_split_candidates, criterion, n_classes, False
                )
                score = <double>left_result[4] + <double>right_result[4]

            if score < best_score - 1e-12:
                best_score = score
                best_feature = <int>feature
                best_threshold = threshold
                if keep_split:
                    best_left = left_arr
                    best_right = right_arr

    return best_feature, best_threshold, best_left, best_right, best_score


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
):
    """Return the best root split under recursive classification lookahead.

    ``max_depth`` and ``max_split_candidates`` use ``-1`` to encode ``None``.
    The returned tuple is ``(feature, threshold, left_indices, right_indices,
    terminal_score)``. ``feature == -1`` means no valid improving split exists.
    """
    return _best_clf(
        X, y, sample_weight, indices, lookahead_depth, depth, max_depth,
        min_samples_split, min_samples_leaf, min_weight_leaf,
        max_split_candidates, criterion, n_classes, True
    )
