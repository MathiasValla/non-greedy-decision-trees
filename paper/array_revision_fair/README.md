# Matched and Equally Tuned Extension

This is a separately versioned extension requested after the first repeated
revision evaluation. Results in `../array_revision/` must not be silently mixed
with its outputs: bootstrap sample-count semantics, zero-gain stopping, and the
compiled scorer are changing for a closer comparison with library CART/RF.
This directory is not completed evidence until its validation gate passes.

## Shared Attributes

Matched comparisons use Gini, the same allowed final depth, minimum split size
two, the same minimum leaf size and feature setting, zero minimum weight
fraction, no class weighting, and zero minimum impurity decrease. CART uses
`ccp_alpha=0`; bounded trees have no post-fit pruning. Feasible zero-gain splits
are allowed. Numeric/tie conventions can still differ between induction rules.

Bootstrap multiplicities are sample weights on the same full training rows.
Zero-weight observations are excluded from bounded-tree split/leaf counts.
A retained pre-run test compares a prepared CART bank with the actual scikit-learn
random forest, not merely a similarly named custom greedy ensemble. Inputs
are float32 for both implementations. PMLB's default complete-case loading is
shared by every family and explicitly recorded; it removes 11 rows of penguins.

## Separate Questions

- Untuned fixed-architecture curves use one-, two-, and three-sighted members,
  pure forests, pairwise mixtures, and a prespecified sparse three-way mixture.
  Every composition spans 20, 40, 60, 100, and 200 members. All proportions are
  assigned to distinct positions in blocks of 20, preserving nested prefixes.
- Matched deeper comparisons use final depths three, six, and unlimited, not a
  search horizon that grows with final depth. Feature settings are all features
  and square root of the predictor count.
- Both the conventional forest and mixed families receive training-only inner
  model selection over the same structural grid: depth three/six/unlimited,
  leaf size one/five, and all-feature/square-root feature settings. Both may
  select 20, 40, 60, or 100 members. The 200-member curves are descriptive,
  not candidates secretly made available to only one tuned family.
- A two-sighted-only mixed family and a one-/two-/three-sighted mixed family
  can be selected from the same validation banks; each selected configuration
  requires its own outer-training refit before test evaluation.

Five paired stratified outer holdouts use the fixed 57-dataset cohort, with one
seed assigned to each of five shards. Inner folds are shared across all families
and use training data only. No fit timeout, candidate cap, or performance-based
dataset removal is introduced. `PROTOCOL.md` freezes candidates, tie-breaking,
cost accounting, primary contrasts, and completeness checks before the run.

## Computation and Interpretation

Validation banks are fitted once per fold/shared configuration/horizon and
reused to score ensemble sizes and compositions. Reuse saves fitting a forest
separately for every candidate; it does not eliminate exhaustive three-sighted
search. Partial banks are checkpointed for recovery. Final-fit cost, required
selection work, physical shared benchmark work, and workflow overhead must be
reported distinctly. No discarded search work may be hidden in a cheap final fit.

A dashed 0.7-second line on aggregate curves is a descriptive mean-cost
reference only. It cannot certify that each dataset meets that budget or that
a configuration was chosen without consulting test scores. Such a prospective
budget claim would require a separate training-only feasibility policy.

The source remains in the existing editor at `../array_revision/main.tex`.
Methods are updated in place; final numerical claims, tables, and figures must
be replaced only after complete new results have been checked. The transfer request asks for a suitable journal
with no mandatory APC and confirmation of publication terms before consent.

## Run and Verify

Use Python 3.10, NumPy 1.26.4, scikit-learn 1.7.2, SciPy 1.15.3, pandas,
Matplotlib, PMLB, Cython, and setuptools. Build and verify the isolated scorer:

```bash
.venv310/bin/python paper/scripts/build_fair_revision_runtime.py
.venv310/bin/python paper/scripts/archive_fair_launch_gates.py
```

`launch_gates.json` retains successful test output and exact source/compiled
hashes. From the repository root, run indices 0 through 4, at most five at once:

```bash
.venv310/bin/python paper/scripts/run_array_fair_benchmark.py --stage fixed --include-triple --shard-index 0 --n-shards 5
```

After all five fixed shards finish, use the same five commands with
`--stage tune`. Both stages share the frozen identity and resume compatible
incremental checkpoints. Production uses `--include-triple` in every command.
Never change the frozen runner, adapter, scorer, or build sources mid-run.
