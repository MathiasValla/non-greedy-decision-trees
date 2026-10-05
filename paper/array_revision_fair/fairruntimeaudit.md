# Isolated fair-runtime scorer audit

## Freeze and scope

READY was announced before the parent build. Frozen source:
`runtime/_sighted_fast.pyx`, SHA-256
`c6a339c64819e27b5a7738383e7508a02ecb16cfee14f9b2aeb46d6665eec255`.

Only this new scorer and this audit were authored here. The primary implementation
reference was the existing `treeple/tree/_lookahead_fast.pyx`; candidate ordering,
the node seed, and adapter behavior were checked against `_lookahead.py` and the
parent's `paper/scripts/fair_revision_runtime.py` / `verify_fair_revision.py`.
No legacy scorer, manuscript, adapter, old result, or benchmark output was edited.
Compilation used `/private/tmp/array-fair-scorer-audit-ApBR0E`, not a result cache.
No full benchmark, tuning grid, or ensemble-size curve was launched.

## Contract and policy

- The 13 required arguments and five-item return tuple retain their legacy order.
  Optional trailing arguments are `max_features=-1, base_seed=0,
  allow_zero_gain=True`, including positional use by the parent adapter.
- Classification supports multiclass weighted Gini (`criterion=0`); entropy
  (`criterion=1`) is retained and checked for compatibility. Horizons 1, 2, and 3
  were tested. The actual depth clips the horizon; independent child minima are
  added, not combined by a Cartesian product of child split choices.
- The caller resolves fractional sample constraints and `sqrt` / `log2` feature
  budgets. Negative depth/candidate limits mean uncapped; a negative feature
  budget or a budget at least the feature count searches all features in order.
  `base_seed` is the resolved `_base_seed`, not necessarily `random_state`.
- Restricted feature order uses the identical NumPy uint64 index-hash expression,
  `RandomState.choice(..., replace=False)`, and then
  `rng.permutation(np.setdiff1d(all_features, selected))`. Hypothetical descendants
  use their own indices and actual depth, just as the Python fallback does.
- Inspect the entire initial subset. Inspect the tail only if that subset has no
  valid evaluated partition, and stop after the first feasible extra feature.
  `valid_seen` is independent of gain, including with `allow_zero_gain=False`.
  A feasible zero-gain sampled feature does not justify searching more features.
- Improvement means `score < best_score - 1e-12`, the legacy absolute weighted-score
  tolerance. When enabled, the first valid candidate with
  `score <= node_score + 1e-12` is accepted even without an improvement. Later ties
  keep the first candidate. Tolerated upward roundoff is clamped to `node_score`
  so the builder's zero impurity-decrease threshold does not reject it.
- Pure nodes (impurity <= 1e-12), nonpositive node weight, insufficient sample
  count, and the actual maximum depth still stop growth. No pruning is introduced.
  The adapter remains responsible for `min_impurity_decrease` and whole-tree
  construction, including restoring the configured horizon at committed nodes.
- Zero-weight rows count if explicitly present in `indices`, matching the legacy
  low-level contract. The parent's adapter removes them at the actual root for
  CART-compatible bootstrap sample counts; negative weights are rejected.
- Lengths, active index/label bounds, positive class count, criterion, resolved
  sample constraints, feature budget, and finite nonnegative active weights / leaf
  weight are validated. Overflowing total weight is rejected. Typed buffers retain
  legacy dtype/contiguity requirements. Finite feature values are checked while
  inspecting a feature; the estimator must validate the complete input once.

This implements CART's **feature-budget feasibility extension and zero-gain
acceptance**, not bit-identical sklearn CART. The node RNG, feature ordering,
float64 thresholds, midpoint conventions, and absolute tolerance remain the
lookahead implementation's conventions.

## Optimization and numerical details

At a one-generation or depth-clipped horizon, each feature is sorted once. A
monotone sweep updates weighted class counts; a candidate score takes O(C) for C
classes. No child arrays are allocated for candidate thresholds. Only the chosen
root partition is materialized, preserving the incoming observation order.
Hypothetical one-generation descendants return scores without child arrays.
The sweep uses the actual `value <= midpoint` boundary, including midpoint
rounding to an upper endpoint and invalid partitions from midpoint overflow.

For nonnegative integer weights whose sum is at most 2^53, left additions and
right subtractions are exact. This includes the usual integer bootstrap counts.
Separate leaf products prevent compiler multiply-add contraction from changing
the legacy last bit. With q inspected features and m samples, the one-generation
path costs O(q m log m + q m C), with O(m + C + p) working memory, where p is the
total feature count. Returned child arrays add O(m) memory.

Other weights use prefix counts and reverse suffix counts rather than subtracting
small right-hand masses from a large total. Their suffix workspace is O(m C).
Near a score tie or minimum-leaf-weight boundary, the original observation order
is rescanned; the selected fractional-weight score is also recomputed once in
that order. The roundoff guard is `64 * DBL_EPSILON * m * max(node_weight, 1)`;
it triggers exact-order checks, not a new improvement tolerance. Consequently,
pathological fractional-weight near-tie cases can still incur O(q m^2) rescanning.
The no-per-threshold-rescan guarantee applies to the exact integer-weight path.
Bit-identical observed scores are a test result, not a universal numerical proof
for arbitrary floating-point inputs or compilers.

Higher horizons still construct each candidate's two children and recurse. Their
cost follows the additive recurrence

```text
T(h, I) = node work + feature sorting
          + sum over valid candidates s [partition work
              + T(h-1, I_left(s)) + T(h-1, I_right(s))],  h > 1,
```

with the optimized one-generation case above and earlier terminal/depth stops.
There is no memoization, approximation, or branch-and-bound. The number of
candidate search nodes can grow on the order of (2B)^(h-1) when B bounds candidates
per node. These optimizations do not certify that the entire uncapped k3 grid
will finish within any proposed runtime budget.

## Executed gates

Build: CPython 3.10, NumPy 1.26.4, Cython 3.3.0, arm64 macOS, clang `-O2`.
Only the standard NumPy deprecated-API and duplicate-rpath warnings appeared.
Inline tests used `python -B` and one-thread BLAS/OpenMP settings to avoid new
repository bytecode/test artifacts. All following gates passed:

| Gate | Cases | Checked |
|---|---:|---|
| Direct legacy comparison | 648 | Feature, exact threshold, original-order child arrays, bit-identical score; strict policy, all features |
| Scalar exhaustive oracle | 1,080 | Gini, both zero-gain policies, sampled features and feasibility tail, recursive seeds, split/score parity |
| Parent full-fit oracle | 36 | All k1/k2/k3, depths 2/4/unlimited, all/sqrt features, leaf sizes 1/3, weighted multiclass probability and realized-depth parity |
| XOR full fit | 3 | k1/k2/k3 all learn XOR at actual maximum depth 2; feasible zero-gain root is not pruned |
| Gain-independent feature-tail cases | 4 | Strict and zero-enabled modes both stop at first feasible extra feature; no extension for a feasible zero-gain initial subset |
| Exact legacy numerical edges | 36 | Adjacent floating-point levels, duplicates, missing classes, extreme finite coordinates, large/dynamic-range and tiny weights, all horizons |
| Exact legacy dynamic-range cases | 180 | Log-distributed fractional weights, tight original-order minimum-leaf-weight boundaries, all horizons; inputs unchanged |
| Invalid-input rejection | 20 | Lengths, indices, labels/classes, weights including overflowing total, criterion, horizon/depth/sample constraints, feature budget and nonfinite inspected feature |
| Terminal cases | 5 | Pure, all-zero weight, empty indices, actual depth cap, insufficient split count |

Legacy comparison details: seeds 0..23, 11 observations / 3 features, reordered
9..11 active indices, three classes, unit/integer-including-zero/fractional weights,
k1/k2/k3, maximum depths 1/2/unlimited, leaf sizes 1/2, minimum leaf weights
0/.25/1, and candidate caps all/1/3. This comprises 513 Gini and 135 entropy cases,
432 integer-weight and 216 fractional-weight cases. Every reported score was
bit-identical to the previously built legacy extension in this environment.

The additional 180 strict-policy Gini comparisons used seeds 901..930, 10
observations / 3 continuous features, four classes, reordered indices, weights
`10 ** uniform(-9, 9)`, all thresholds, all horizons, and minimum leaf weight
either zero or an exact original-order sum at a selected feature-0 threshold.
Every feature, threshold, partition, and reported score matched the legacy
extension exactly. Input X, y, weights, and indices remained unchanged.

Scalar-oracle details: seeds 107..136, 9 observations / 5 features with varying
constant columns, reordered 7..9 active indices, four classes, integer and
fractional weights, all horizons, budgets 1/2/all, both zero-gain policies,
nonzero actual depths and clipped horizons, caps all/1/3, and base seeds including
values above 2^32. The oracle used scalar original-order sums, stable sorting,
actual threshold masks, the same feature RNG expression, and exhaustive child
recursion; it did not use the optimized prefix implementation.

The parent's 36-case oracle and XOR checks were run inline against the temporary
extension. Its `main()` was not invoked here because it also writes
`harness_checks.json`, outside this task's two-file write scope. Parent-controlled
build/verification entry points remain:

```sh
.venv310/bin/python paper/scripts/build_fair_revision_runtime.py
.venv310/bin/python paper/scripts/verify_fair_revision.py
```

## Bounded performance pilots only

Two deterministic **single-root scorer** pilots used normally distributed
features, three classes, positive integer weights 1..3, all thresholds, all
features, strict gain policy, and three timed repeats after an output-parity
check/warmup. Seeds were `513 + horizon`; times are medians in seconds.

| m | q | k | min leaf | Legacy | New | Observed ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 2,000 | 6 | 1 | 1 | 0.112592 | 0.000729 | 154.55x |
| 64 | 3 | 3 | 2 | 2.649305 | 0.299415 | 8.85x |

Splits, child arrays, and scores were identical in both pilots. These timings are
not forest fitting times, tuning times, whole-benchmark estimates, or scientific
performance results. The parent owns formal pilots and grid feasibility decisions.

## Integration caveats

- The backend's fallback feasibility is based on **evaluated** valid candidates.
  If a positive threshold cap is used, a Python prescan of every uncapped position
  can disagree. Mirror the capped candidates in the oracle, or keep
  `max_split_candidates=None`, the intended exhaustive fair setting.
- A feasibility prescan based on nominal sorted positions or total-minus-prefix
  weights can also differ on adjacent-double midpoint rounding or severe weight
  cancellation. For exact edge-case oracle parity, apply the actual midpoint mask
  and original-order weight constraints. Ordinary integer bootstrap cases passed.
- The scorer does not assert equality of the custom k1 tree to a library CART
  realization. Matching resampling, stopping, and feature-budget semantics is
  distinct from matching sklearn's internal randomized feature traversal.
- No equally tuned RF/mixed-forest comparison or 20/40/60/100/200 curve was run
  here; this file provides the frozen scorer and local correctness/performance
  checks needed before those parent-controlled experiments.
