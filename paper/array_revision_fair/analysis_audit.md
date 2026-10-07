# Fair Analysis Audit

This analyzer is independent of the runner and estimator imports. It never
fits an estimator, fetches a dataset, modifies frozen source/protocol files,
reads older-run outputs, or selects a design from observed benchmark scores.
Development tests use only explicitly labeled synthetic fixtures under a
temporary root. Do not execute production analysis before the required cohort
is complete.

## Expected Counts

The launched protocol includes the optional 85/10/5 composition, so all 16
compositions are required. There are 57 datasets, five paired seeds, 285 outer
tasks and six fixed structures per task. The analyzer rejects a 15-composition
run rather than pretending the requested triple is available.

| Artifact | Fixed-Only | Full |
| --- | ---: | ---: |
| Fixed structural blocks | 1,710 | 1,710 |
| Fixed forest repeat rows | 136,800 | 136,800 |
| Fixed single-tree repeat rows | 5,130 | 5,130 |
| Tuned forest repeat rows | 0 | 855 |
| All forest repeat rows | 136,800 | 137,655 |
| All model repeat rows, including singles | 141,930 | 142,785 |
| Dataset-mean rows | 28,386 | 28,557 |
| Summary rows | 498 | 501 |
| Primary contrasts available | 8, descriptive until full | 11 |

Thus 137,655 is the full *forest-only* row count, not the count including
single trees. CV block counts depend on the prescribed two/three-fold rule;
each fold has 12 structures and 64 candidate records. Full selection spaces
contain 48 RF, 288 k2-only and 768 inclusive candidates.

## Validation Gates

Normal analysis reads `raw/{protocol_fingerprint}/{dataset}/s{seed}`. An
explicit preflight requires every split and six completed fixed JSON blocks
for all 285 tasks before any export. Full mode additionally requires all
three independent refits, locked selection, tuned JSON and complete task JSON.
Unexpected datasets/seeds, partial banks, missing rows, duplicate IDs or
incompatible fingerprints are errors with tracebacks, not skipped tasks.

Independently verify:

- The protocol's self-hash, source hashes, 57-dataset list, structural/count
  spaces, 16 compositions and literal ordered 11-contrast specification.
- Cached public source hashes, float32 feature and encoded target hashes,
  raw/used/dropped row counts and retained complete-case source-row hashes.
- Exact paired outer split indices/hashes from seeds 1000..1004 and the 75/25
  stratified rule. Class counts refer only to classes actually present.
- Every complete fixed/inner bank's identity, 200/100 completed slots, seed
  prefix hash, float64 normalized probabilities, finite nonnegative times,
  integer depths/leaves and configured depth caps.
- JSON/NPZ agreement for every per-slot metric. Independently reconstruct
  block-20 horizon assignments, forest scores and actual selected-slot fit
  sums, avoiding fraction-weighted pure-bank means.
- All 80 fixed forest rows and three single trees per structure, including
  matching all/sqrt features, common parameters, exact integer compositions,
  scores in [0,1], finite nonnegative costs and independent single checkpoints.
  Single-tree predictions are not retained: their scores receive range and
  checkpoint-consistency checks only, not independent prediction reconstruction.
- Full mode's inner splits, 12-setting grid, four counts through 100, 64
  records per fold/structure and three separate CV winners using accuracy,
  selected-fit-work and stable-ID ordering. k2-only excludes every k3 option;
  all families include the same pure-CART candidates.
- Locked model/refit configuration equality and family eligibility. Actual
  RF direct-refit wall time remains distinct from bank constituent fitting
  work. Refit test probabilities are not persisted by the frozen runner, so
  tuned test scores can be range/identity checked but not recomputed without
  refitting; this analyzer deliberately does not refit.
- Selection prediction/workflow accounting, family bookkeeping attribution,
  combined physical bookkeeping and shared bank work counted once. Complete
  task JSON must literally match the six fixed records, tuned record and all
  11 paired accuracy differences.

The `array-fair-analysis-v2` certificate records explicit `verification_scopes`:

| Scope | Fixed-Only | Full |
| --- | --- | --- |
| `fixed_bank_forest_scores` | Bank-probability reconstruction | Same |
| `fixed_selected_slot_fit_work` | Actual bank-slot sum reconstruction | Same |
| `inner_cv_bank_forest_scores` | Not checked | Bank-probability reconstruction |
| `inner_cv_selected_slot_fit_work` | Not checked | Actual bank-slot sum reconstruction |
| `single_tree_scores` | Range/checkpoint consistency only | Same |
| `direct_refit_scores` | Not checked | Range/checkpoint consistency only |

Machine values are `bank_probability_reconstruction`,
`bank_slot_sum_reconstruction`, `range_and_checkpoint_consistency_only`, and
`not_checked_fixed_only`, respectively. These describe the original validation,
not fresh bank reconstruction during CSV-only retrieval. The obsolete broad
`probabilities_and_selected_costs_reconstructed` flag is no longer emitted or
accepted, even alongside the scoped certificate. No claim of independent
single-tree or direct-refit score reconstruction is made.

No cost field is silently changed into an end-to-end timer. Total workflow
fields are sums of measured stage wall times and exclude checkpoint I/O,
startup, downloading and idle time. Physical accounting also records actual
fixed bank/single work separately and combines stages once, never sums
per-composition costs or all three families' overlapping attributed costs.
Although fixed single-tree records use the field name `direct_fit_time_s`,
their timer surrounds `fit` alone, excluding construction and prediction.
Their paired cost label is therefore `single_tree_fit_wall`, not the tuned
family's `direct_refit_wall` (which includes construction/bootstrap preparation).
Ratios always compare matching stages and measurement boundaries.

## Aggregation and Inference

Require exactly seeds 1000..1004 for each dataset/model. First average these
five repeats within each dataset; then give each of the 57 datasets equal
weight. Neither sample count nor repeated task count weights a dataset more.
Costs follow the same repeat-first, dataset-equal aggregation.

All paired effect CIs resample the dataset differences, 20,000 bootstrap
samples with seed 41, using the 2.5% and 97.5% quantiles. The primary family is
exactly the eight fixed T=100/q=10% anchors at depths 3/unlimited and all/sqrt
features, plus three tuned-family comparisons. Full mode uses two-sided
Wilcoxon signed-rank tests with `zero_method=wilcox`, `method=auto`, rounding
differences to 12 decimals for zero/tie stability. All-zero differences have
p=1. Apply Holm once across these 11 primary p-values, in protocol order.

Fixed-only mode does not substitute an eight-test Holm family: its eight
anchor effects/CIs are explicitly pending the full 11-member inference family
and contain no p-value columns. Other fixed curves and matched single-tree
contrasts are descriptive paired CIs only. A CI crossing zero is not evidence
of equivalence. CIs are pointwise, not simultaneous intervals.

Prespecified sensitivities use the same legacy naming rules: 48 known-family
groups, each contributing its mean dataset difference, and 38 named
non-synthetic datasets after excluding 19 named synthetic/constructed tasks.
Both receive paired bootstrap CIs but no additional
unadvertised significance-test family. There are no fixed-versus-tuned
headline comparisons.

## Exports

Outputs are isolated under `analysis/fixed_only` and `analysis/full` so a
partial mode cannot overwrite or masquerade as a completed tuned analysis.

- `fixed_forests.csv`, `fixed_trees.csv`, and full-only `tuned_forests.csv`
  retain every paired repeat and configuration. Composition IDs, not mean
  horizon, distinguish curves with the same average sightedness.
- `dataset_means.csv`, `summary.csv`, `dataset_manifest.csv`,
  `paired_primary_comparisons.csv`, `descriptive_paired_comparisons.csv`,
  `paired_dataset_deltas.csv` and `sensitivities.csv` keep units and scopes
  explicit.
- The 57-row `dataset_manifest.csv` retains the source/complete-case metadata
  and adds `family_group` and boolean `named_synthetic`. These use exactly the
  existing sensitivity naming rules, not classifications inferred from scores:
  48 groups, 19 excluded synthetic/constructed tasks and 38 retained tasks.
  Every dataset's membership is independently rechecked during retrieval.
- `shared_accounting.csv`, `physical_cost_dataset_means.csv` and
  `physical_cost_summary.json` count actual shared work once. Full mode also
  emits `fair_tuning_table.csv` with direct refit, selection fitting work and
  summed workflow-stage wall time as separate columns.
- Escaped TeX fragments provide paired comparisons and full-only tuned
  performance. Percent signs, underscores and other TeX metacharacters are
  escaped. Manuscript assembly remains the parent's responsibility.
- `protocol_snapshot.json` and `validation.json` freeze the input protocol,
  analyzer hash/versions, count assertions and SHA256 hashes of all exported
  CSVs, including summary and primary comparison CSVs. Validation is written
  only after successful table/figure generation.

## Figures and Retrieval

Main `Fig2_main_D3_Fall` uses all 16 compositions, all five counts and the
repeat-first/equal-dataset means for depth 3/all features. Panels show accuracy
against T and log mean measured selected-tree fitting work. Pure k1/k2/k3 are
black/blue/red; composition colors stay consistent and pair-specific line
styles distinguish (1,2), (1,3), (2,3). Legends show % k1/k2/k3 and mean horizon;
point markers encode the five counts. The dashed 0.7 s line is explicitly a
MEAN-COST reference, not a validated budget or per-dataset guarantee.

The main and other five matched-structure plots use 7.2 x 4.5 inch white
figures, restrained light grids, an external four-column composition legend
at fontsize 7, and PDF/PNG exports. Supplementary pair facets clarify each
pair without collapsing equal-mean-horizon compositions. Full-only Fig3 shows
three paired tuned-family effects and selection fit work versus direct refit
wall time; its third cost marker is labeled "Sum of measured stage wall times".
Layout validation checks drawn labels, annotations and legends before saving.

Because NPZ banks are ignored by Git, `--plot-summaries` independently verifies
retained CSV hashes/schema and validation counts before regenerating figures.
It needs no scorer, public data cache, raw results, NPZ banks or refitting.
Retain these files together for this mode:

- `validation.json`, `protocol_snapshot.json`, `summary.csv`,
  `paired_primary_comparisons.csv`, `dataset_means.csv`, `dataset_manifest.csv`.
- In full mode, also `fair_tuning_table.csv`.

The retained dataset-mean cohort must have all 57 datasets and five-repeat
certification for all 498/501 models. Summary means are checked against these
dataset means, and six complete 16-by-5 curve spaces are checked. The manifest
must have exactly the deterministic family/synthetic labels and 57/48/19/38
counts. Retrieval requires the v2 scoped certificate with exactly the fixed-only
or full verification scope; old broad-only v1 certificates are not accepted.

Retrieval also independently recomputes the eight fixed-only or eleven full
primary paired bootstrap endpoints from alphabetically aligned dataset means,
using the same 20,000 draws and seed 41. Full mode recomputes all eleven raw
Wilcoxon p-values and their one-family Holm adjustment from those differences,
with the same 12-decimal rounding and all-zero rule. CSV round-trip comparisons
allow absolute tolerance 1e-12; round-trip float parsing preserves saved dataset
means without introducing additional rounding at the Wilcoxon boundary.
Fixed-only mode still forbids p-value columns.
These inexpensive statistic checks do not require probabilities or refits.
Wrong mode, changed files, truncated cohorts, incorrect memberships/statistics
even with refreshed hashes, or partial-family inference raise before plotting. Hashes
certify consistency with the original validated export, not a cryptographic
signature from an external authority.

## Checks and Integration

Use the parent-approved environment; no production analysis has been invoked
during development:

```sh
TMPDIR=/tmp .venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --self-test
TMPDIR=/tmp .venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --self-test --qa-dir /tmp/TEST_array_fair_analysis_qa
```

After **all fixed blocks for all five seeds** are complete:

```sh
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --fixed-only
```

After **every fixed block, locked selection and all three tuned refits** are
complete, run default full mode:

```sh
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py
```

Later, regenerate from published/retained analysis CSVs without local banks:

```sh
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --plot-summaries --fixed-only
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --plot-summaries
```

`--out` changes the fair input/output root, not the cohort or statistical
design. The older `array_revision` root is rejected in every mode.
When integrating this change, generate analysis exports with this analyzer
only after the applicable complete-cohort gate. An older analysis certificate
must not be relabeled v2 or have classifications guessed by hand; regenerate
through normal validation. Frozen benchmark outputs and protocol hashes are
unchanged. Keep the manifest and dataset means with the certificate for later
`--plot-summaries` retrieval.

Synthetic tests cover complete and corrupted structure/bank records, missing
or duplicate candidates, wrong scores/weights/features/costs, pending k3 banks,
paired-repeat imbalance, independent CV winners and family eligibility, three
tuned records, missing refits, shared-cost double counting, complete retained
fixed/full schemas, altered hashes and refreshed-hash incomplete cohorts.
Additional tests reject broad/overclaimed verification scopes, missing/wrong
family labels, missing/wrong/nonboolean synthetic labels, and incorrect primary
bootstrap endpoints or Wilcoxon/Holm values with refreshed hashes. Nonconstant
synthetic dataset effects and shuffled retained mean rows verify that statistical
reconstruction uses paired identities and stable dataset order. Same-count
label swaps are rejected, and a float round-trip fixture checks exact parsing.
TEST-only layout QA checks all six curve plots, pair facets and tuned panels;
the main PDF is also rendered and visually inspected. The verified PDF page
size is 518.4 x 324 points (7.2 x 4.5 inches). No synthetic figure is a final
benchmark result or a manuscript figure.
