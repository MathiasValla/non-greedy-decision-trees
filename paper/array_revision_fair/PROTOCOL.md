# Expanded Fair Array Benchmark

The approved scope is fixed curves through 200 trees, training-only selection
through 100 trees, three tuned families, and five outer-seed shards. Outputs
default to `paper/array_revision_fair`. Older `array_revision` outputs and
sources are never modified or merged. No fit timeout, accuracy-based dataset
removal, candidate screening, adaptive cap, early stopping, or pruning is used.
Errors propagate with tracebacks and stop the shard.

## Paired Data and Missingness

All 57 datasets in `paper/tables/mixed_sighted_dataset_sample.csv` are used.
Five stratified 75/25 outer splits use seeds 1000 through 1004. Every method
shares the same outer indices. Predictors are contiguous float32 before either
library sees them; targets use sorted class encoding.

PMLB normally drops missing rows by default. This runner instead fetches the
raw frame with `dropna=False`, then explicitly keeps complete rows across all
columns, including target, for every family. No imputation is performed.
Manifest fields independently record raw and used row counts, dropped rows,
missing counts by column and retained source-row index hashes. The known
penguins complete-case reduction of 11 rows is therefore visible, not an
implicit change in cohort. Nonfinite predictors after float32 conversion raise.

## Matched Trees and Bootstrap Draws

CART is sklearn `DecisionTreeClassifier`. Horizons 2 and 3 use isolated
`fair_revision_runtime.Classifier`. All common parameters match: Gini, split
minimum 2, leaf minimum, total depth, features, tree seed, zero impurity
threshold and zero minimum leaf-weight fraction. CART uses `ccp_alpha=0`, best
splitting, no leaf-count cap and no class weighting. The sighted runtime has
no pruning and unrestricted split candidates. Horizon is the only deliberate
change. Total depth is actual tree depth, not lookahead horizon. Save actual
depth and leaf counts as well as configured depth.

The forest seed supplies `RandomState(seed).randint(INT32MAX, size=200)` tree
seeds. For each slot, weights are
`bincount(RandomState(tree_seed).randint(n, size=n), minlength=n)`. Fit on the
full training matrix with those sample weights, never a duplicated row matrix.
The sighted runtime excludes zero-weight root rows, matching CART's unique
sample constraints. Both bank sizes use prefixes of this exact seed sequence.

The parent harness verifies prepared CART banks against actual sklearn RF.
The runner pilot independently checks all five count prefixes for all/sqrt
features. Final selected RF always refits actual `RandomForestClassifier`
with `n_jobs=1`, not an approximate replacement estimator.

## Nested Disjoint Compositions

A fixed `RandomState(seed + 130363)` generates successive permutations of
20-slot blocks. Within each block, the lowest active horizon is the default;
successive higher horizons occupy disjoint consecutive segments of its random
priority permutation. All fractions are integer twentieths. Each complete
block therefore has the exact requested composition. Forest counts 20, 40,
60, 100 and 200 use prefixes of the same block assignment. For each pair,
the farther-horizon positions are nested across 5%, 10%, 25% and 50% fractions.
Priorities never inspect data, labels or accuracy and are shared across
structures and evaluation stages for the same outer seed.

There are 15 compositions: pure horizons 1/2/3, and pairs (1,2), (1,3),
(2,3), each at 5%, 10%, 25% or 50% farther horizon. `--include-triple` adds the
optional sixteenth composition, 85/10/5 at horizons 1/2/3, and changes the
protocol fingerprint. No forest uses two constituents from the same bootstrap
slot. Predictions align to the dataset class encoding and average in slot
order. Costs sum the measured fits of the actual selected slots, never a
pure-bank mean multiplied by composition fractions.

## Fixed Stage

Every dataset and outer seed uses depths 3, 6 and unlimited, leaf minimum 1,
and both all features and sqrt features. Each of these six structures fits
one unbootstrapped CART, one horizon-2 tree and one horizon-3 tree with matched
settings, plus three 200-tree bootstrap banks. Score all compositions at
20/40/60/100/200 trees on the paired outer test partition. Every score includes
accuracy, balanced accuracy, actual mean depth and selected-slot fitting work.
Completed structure files are available for analysis while tuning continues.

## Training-Only Selection

Use only outer training rows in inner CV. Count only classes actually present
in that training partition. For multiple classes with *every* nonzero class
count at least two, use shuffled stratified `min(3, cmin)` folds. If any class
is a singleton, or training has a single class, use shuffled ordinary 3-fold
CV. The shuffle seed is outer seed + 7. Fewer than three training rows in the
ordinary-fold fallback is an explicit error.

All families share the 12 structural settings: depths 3/6/unlimited, leaf
minimum 1/5, and features sqrt/all. At each fold/structure fit each horizon's
100-tree bank once. Derive all selection records at counts 20/40/60/100.
The fixed 100-tree search cap applies equally to every family; 200-tree curves
are descriptive fixed-stage results, not extra RF or mixed tuning options.

Select three families from the same CV records:

- `rf`: pure horizon 1 at all four counts, 48 candidates over the full grid.
- `mixed_k2`: pure 1, pure 2, and the four (1,2) mixtures, 288 candidates.
- `mixed`: all 15 compositions, 720 candidates (768 with the optional triple).

Both mixed families include the RF candidate space. Highest unweighted
fold-mean validation accuracy wins, then lowest fold-mean selected-tree fit
work, then lexicographically smallest stable candidate ID. Balanced accuracy
and outer test scores never select or break ties. The cost tie breaker is
reproducible from saved measurements, not guaranteed identical on another
machine's fresh run.

Lock all three selected configurations before any outer-test refit. Refit
three models separately on full outer training data: actual sklearn RF,
prepared weighted k2-only forest, and prepared weighted inclusive forest.
Both prepared forests use the exact seed prefix, weighted draws and block
schedule above. Store full selected configuration, validation mean, outer
accuracy/balanced accuracy, direct fit time, prediction time and mean depth.
Direct fitting includes construction/bootstrap preparation but excludes test
prediction. No full trees are persisted.

## Eleven Primary Contrasts

Eight fixed anchors use T=100, q=10%, leaf minimum 1, depths 3/unlimited, and
all/sqrt features: each (1,2) and (1,3) mixture versus its matching pure CART
forest. Three tuned contrasts are k2-only versus RF, inclusive versus RF, and
inclusive versus k2-only. IDs/configurations are frozen in the protocol
manifest and completed task JSON. Other count/depth/composition curves are
descriptive. This runner computes paired differences, not inferential tests.
No fair-results release is approved until the new full run is complete.

## Selection and Shared Costs

Report fitting work, prediction work, bank wall time, bootstrap/construction
preparation, and schedule-evaluation wall time separately. RF is attributed
all horizon-1 selection work; k2-only is attributed all horizon-1/2 work;
inclusive is attributed all horizon-1/2/3 work. Each family is charged its
applicable schedule evaluation. Physical shared-bank accounting counts common
horizon-1 and horizon-2 work only once, not once per attributed family.
Fixed-stage banks are never charged to tuning.

Workflow wall time is the sum of measured selection bank/schedule wall times,
selection bookkeeping, direct selected refit and test prediction. It excludes
downloads, checkpoint I/O, idle gaps and process startup; it is labeled a sum
of stage wall times, not a single uninterrupted stopwatch. Historical stage
measurements survive resume. Family totals use that family's candidate-choice
time plus common accounting; physical totals count combined bookkeeping once.
RF exposes whole-refit wall time rather than
per-tree refit durations, so its combined fitting measurement explicitly
labels selection-tree fit sum plus actual RF refit wall time. Prepared-family
combined fitting work uses constituent fit sums throughout.

## Atomic Progress and Frozen Provenance

All bank checkpoints are mandatory. After every 20 completed trees, atomically
write NPZ with aligned individual probabilities, fit/prediction times, depths,
leaf counts, completed-slot count, accumulated bank/preparation wall times,
and source/protocol identity. Resume loads this prefix and fits only remaining
slots. A failure can lose at most the current unfinished 20-tree block, not
an entire k3 bank. Temporary files are passed as open handles to NumPy to avoid
its filename-extension behavior. Cached arrays are loaded without pickle.

Each completed fixed structure and inner-fold/structure writes atomic JSON
with every candidate score and slot-specific cost metadata. Completed JSON
loads without fitting. Single trees, locked selections and three refits have
separate atomic checkpoints. `results.json`, containing all six fixed
structures, all three tuned models and 11 contrasts, is written only when
every required component is complete. Scoped completion markers cannot claim
a partial run is a full protocol task.

Protocol/implementation/environment fingerprints guard the output root and
every checkpoint. Freeze runner/runtime/scorer source, compiled extension,
build script, dataset list and Python/library versions. Raw feature/target
and source-file hashes independently guard data. Freeze outer index lists and
outer/inner global-index hashes. Implementation or algorithm changes require
a fresh output root and cannot silently reuse old caches. Documentation-only
amendments are hashed separately and do not invalidate computational caches;
the original root manifest remains frozen. Sources are checked before each
outer task. Locks serialize duplicate dataset/seed jobs. No failed dataset
is silently skipped.

## Five Balanced Shards and Checks

Shard i handles seed `1000 + i` for all 57 datasets, with the same stages and
hyperparameter grid. Thus each shard has identical cohort and nominal work,
with only split-dependent fitting variation. Sort datasets by descending
frozen CSV sample-count times feature-count, then name, to frontload expensive
jobs without using accuracy. Dataset/seed filters apply after this fixed
assignment; `--n-shards` is fixed to five.

```sh
python paper/scripts/run_array_fair_benchmark.py --self-test
python paper/scripts/run_array_fair_benchmark.py --pilot
python paper/scripts/run_array_fair_benchmark.py --dry-run --shard-index 0
```

Pure-function tests need no fair scorer. The small synthetic pilot uses one
structural CV fixture, not production datasets: exact RF prefixes, three
weighted banks, direct mixtures, all three tuned refits, locked/no-refit
resume, and partial-bank continuation are checked. Pilot outputs are temporary.

Only after parent review and approval, run indices 0 through 4:

```sh
python paper/scripts/run_array_fair_benchmark.py --stage both --shard-index 0
```

`--stage fixed`, `--stage tune`, or `--stage both` (default) share one protocol
hash. `--depths`, `--datasets` and `--seeds` scope execution without changing
the full tuning grid. `--cache-banks` is accepted explicitly but cannot disable
mandatory incremental caching. `--out` can choose a fresh fair output root;
the older `array_revision` root is rejected.
