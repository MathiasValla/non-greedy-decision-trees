# Reproducing and Retrieving Article Results

This repository stores the implementation, retained benchmark results, figure
assets, and manuscript sources for the bounded split-optimization article.

Project repository:
<https://github.com/MathiasValla/non-greedy-decision-trees>

Completed historical results can be retrieved directly from retained CSV files.
The expanded fair revision below is still running: its final results must not
be inferred from the preceding evaluation or incomplete checkpoints.

## Matched and Equally Tuned Revision (In Progress)

The existing manuscript remains `paper/array_revision/main.tex`, with explicit
working-draft warnings until the new results are complete. The new protocol and
outputs live separately in `paper/array_revision_fair/`; never merge them with
preceding result records. See `README.md`, `PROTOCOL.md`, `launch_gates.json`, and
`fairruntimeaudit.md` there for design, timing boundaries, retained passing tests,
and scorer verification.

Both fixed and tuned experiments include one-, two-, and three-sighted members.
Fixed comparisons match permitted final depth, common hyperparameters, and no
pruning; all sixteen pure/mixed compositions span 20, 40, 60, 100, and 200 trees.
Tuned RF and both mixed families share structural and forest-size search grids
and inner folds. Their final refits, required selection work, and physical shared
benchmark work are recorded separately. The 200-tree curves are descriptive,
not candidates offered selectively to one tuned family.

From the repository root, use the Python environment listed in
`paper/array_revision_fair/README.md` and run:

```bash
.venv310/bin/python paper/scripts/build_fair_revision_runtime.py
.venv310/bin/python paper/scripts/archive_fair_launch_gates.py
.venv310/bin/python paper/scripts/run_array_fair_benchmark.py --stage fixed --include-triple --shard-index 0 --n-shards 5
```

Repeat the last command with shard indices 1 through 4. Once all five fixed
shards finish, run the five corresponding commands with `--stage tune` instead
of `--stage fixed`. Run at most five shards concurrently. Each shard handles one
of the five outer seeds on the same complete 57-dataset cohort. No fit timeout is
configured; errors stop execution and do not remove datasets. Existing compatible
checkpoints resume, including incomplete banks. A changed algorithm requires a
fresh `--out` directory, not deletion or reuse of incompatible evidence.

All source/environment/protocol identities are frozen. Do not edit induction or
runner sources while a production run is active. NPZ prediction caches are local
resumable work products, not article result tables, and are ignored by git.
The analysis implementation has passed synthetic completeness, numerical,
selection/accounting, and layout checks. Production analysis still requires the
complete cohort. Once all fixed shards finish, run:

```bash
.venv310/bin/python paper/scripts/analyze_array_fair_benchmark.py --fixed-only
```

After all tuned shards also finish, run the same command without `--fixed-only`.
The analyzer independently verifies raw identities, split indices, bank scores,
costs, and CV winners before exporting to `paper/array_revision_fair/analysis/`.
The `fixed_only/` export has no partial-family p-values; the `full/` export
requires all eleven contrasts and all three separate tuned refits.

When the completed analysis files are available in the repository, regenerate
figures directly from the retained hashed CSVs, without NPZ caches or refitting:

```bash
.venv310/bin/python paper/scripts/analyze_array_fair_benchmark.py --plot-summaries --fixed-only
.venv310/bin/python paper/scripts/analyze_array_fair_benchmark.py --plot-summaries
```

Use only the command for the corresponding completed export. See
`paper/array_revision_fair/analysis_audit.md` for required files, output schemas,
and safeguards. The reproduction instructions do not certify an unfinished run.

For a fresh replication on another machine, or after rebuilding the extension,
use a separate output root. Retained results intentionally reject changed
binary/environment identities, even when the algorithm source is unchanged.
For example, add `--out /tmp/array_fair_reproduction` to every fixed and tuned
shard command, and to the subsequent analyzer command. Keep that output root
consistent across all ten invocations. Do not rebuild the scorer during an
active run. Fresh clock measurements, and cost-based CV tie-breaking, can differ
between machines; the retained records certify the original choices and costs.

## Preceding Repeated Evaluation (Superseded Protocol)

The following completed experiment precedes the author's request for equally
tuned mixed forests, matched zero-gain stopping, weighted bootstrap semantics,
and repeated three-sighted fits. It is retained for provenance, not the final
fair-comparison conclusion. It uses 57 fixed datasets at maximum depths three,
six, and unlimited. No fit timeout was used.
See `paper/array_revision/README.md` for the full two-stage benchmark procedure,
runtime build, native-editor-compatible manuscript generation, and author checks.

| Article item | Source under `paper/array_revision/` |
| --- | --- |
| All repeat-level model scores and costs | `revision_results.csv` |
| Dataset means and aggregate performance | `dataset_means.csv`, `summary.csv` |
| Paired effects, uncertainty, multiplicity-adjusted tests, sensitivity | `paired_comparisons.csv`, `paired_dataset_deltas.csv` |
| Table 1 and Table 2 | `table_performance.tex`, `table_comparisons.tex` |
| Figures 1 and 2 | `Fig1_depth_sensitivity.pdf`, `Fig2_accuracy_cost.pdf` |
| Dataset definitions and input fingerprints | `dataset_manifest.csv`, `input_fingerprints.csv` |
| Training-only selected settings and CV rules | `tuning_results.csv`, `inner_cv_manifest.csv` |
| Completeness, environment, sources, protocol checks | `validation.json`, `reproducibility_manifest.json`, `harness_checks.json` |
| Full checkpoint records | `raw/`, `raw_cart/` |

From the repository root, regenerate the analyses and exported numerical figures
without refitting models:

```bash
.venv310/bin/python paper/scripts/analyze_array_revision.py
.venv310/bin/python paper/scripts/export_array_revision_provenance.py
```

The analyzer refuses incomplete runs or mismatched splits. Costs are retained
with their timing scope; total conventional-baseline selection time is separate
from final fitting cost. Mixtures replace distinct bootstrap positions, and the
custom greedy learner is distinguished from standard CART. The manuscript source
embeds numerical plots from the same validated summaries for native compilation.

## Historical PRL Results (Not the Revised Evidence)

The files below are retained for provenance only. The 67-dataset aggregate is a
historical summary without independently reconstructable raw-fit records in this
repository. The old 57-dataset mixed grid contains overlapping bootstrap positions
and allocated timing estimates. Its exploratory vertical mean-time slice is not
a validated per-dataset budget comparison. Do not use these historical aggregates
for the revision's statistical inference or mix them with the corrected records.

Historical CSV files are stored under `paper/tables/`.

| Article item | Source file |
| --- | --- |
| Aggregate single-tree and forest results in Table 1 | `paper/tables/lookahead_aggregate_results.csv` |
| Accuracy and fitting-time deltas | `paper/tables/lookahead_accuracy_cost_deltas.csv` |
| Accuracy-time utility thresholds | `paper/tables/lookahead_utility_thresholds.csv` |
| Dataset-level best-or-tied counts | `paper/tables/lookahead_wins_or_ties.csv` |
| Full mixed-forest Figure 2 grid, dataset level | `paper/tables/mixed_sighted_forest_grid_results.csv` |
| Full mixed-forest Figure 2 grid, aggregated curves | `paper/tables/mixed_sighted_forest_grid_summary.csv` |
| Five shard outputs used to assemble the Figure 2 grid | `paper/tables/mixed_sighted_forest_grid_shard_0.csv` through `paper/tables/mixed_sighted_forest_grid_shard_4.csv` |
| Dataset sample for the mixed-forest grid | `paper/tables/mixed_sighted_dataset_sample.csv` |

For example, the archived exploratory 0.7 s comparison is in
`paper/tables/mixed_sighted_forest_grid_summary.csv`:

```text
mix_1_75_2_25, tree_count=20: mean_accuracy=0.741165, mean_fit_time_s=0.661388
mix_1_90_2_10, tree_count=40: mean_accuracy=0.736770, mean_fit_time_s=0.637750
mix_1_95_2_05, tree_count=60: mean_accuracy=0.734029, mean_fit_time_s=0.614111
```

## Regenerate Historical Assets

The old figure-generation script regenerates historical summaries and figures.
It does not recreate independently retained fits for the 67-dataset aggregate:

```bash
python paper/scripts/make_lookahead_letter_assets.py
```

The script writes:

- `paper/figures/lookahead_accuracy_time_tradeoff.pdf`
- `paper/figures/sighted_forest_tradeoff.pdf`
- `paper/prl_submission/Fig1_accuracy_time.pdf`
- `paper/prl_submission/Fig2_forest_size.pdf`
- `paper/tables/mixed_sighted_forest_grid_summary.csv`

If the default Python environment does not have `numpy` and `matplotlib`, use an
environment that does, for example:

```bash
.venv310/bin/python paper/scripts/make_lookahead_letter_assets.py
```

## Rebuild the Archived PRL PDF

The PRL submission source is in `paper/prl_submission/`.

```bash
cd paper/prl_submission
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The compiled PDF is `paper/prl_submission/main.pdf`.

## Rerun the Historical Mixed-Forest Grid

The full mixed-forest grid is computationally expensive. The retained results
already contain the completed five-shard run. To rerun it from scratch:

```bash
python paper/scripts/run_mixed_sighted_forest_grid.py --make-shard-plan
python paper/scripts/run_mixed_sighted_forest_grid.py --shard-index 0 --n-shards 5
python paper/scripts/run_mixed_sighted_forest_grid.py --shard-index 1 --n-shards 5
python paper/scripts/run_mixed_sighted_forest_grid.py --shard-index 2 --n-shards 5
python paper/scripts/run_mixed_sighted_forest_grid.py --shard-index 3 --n-shards 5
python paper/scripts/run_mixed_sighted_forest_grid.py --shard-index 4 --n-shards 5
python paper/scripts/run_mixed_sighted_forest_grid.py --combine-shards --n-shards 5
```

This regenerates `paper/tables/mixed_sighted_forest_grid_results.csv`, which is
then summarized by `paper/scripts/make_lookahead_letter_assets.py`.
