# Reproducing and Retrieving Article Results

This repository stores the implementation, retained benchmark results, figure
assets, and manuscript sources for the k-sighted decision-tree article.

Project repository:
<https://github.com/MathiasValla/non-greedy-decision-trees>

After cloning the repository, the reported article results can be retrieved
directly from the retained CSV files; rerunning the benchmarks is not required.

## Retrieve Results Without Rerunning Benchmarks

The article results are stored as CSV files under `paper/tables/`.

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

For example, the 0.7 s mixed-forest comparison discussed in the article is in
`paper/tables/mixed_sighted_forest_grid_summary.csv`:

```text
mix_1_75_2_25, tree_count=20: mean_accuracy=0.741165, mean_fit_time_s=0.661388
mix_1_90_2_10, tree_count=40: mean_accuracy=0.736770, mean_fit_time_s=0.637750
mix_1_95_2_05, tree_count=60: mean_accuracy=0.734029, mean_fit_time_s=0.614111
```

## Regenerate Tables and Figures From Retained Results

The figure-generation script reads the retained CSV files and rewrites the
manuscript figures and summary tables:

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

## Rebuild the PRL Manuscript PDF

The PRL submission source is in `paper/prl_submission/`.

```bash
cd paper/prl_submission
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The compiled PDF is `paper/prl_submission/main.pdf`.

## Rerun the Mixed-Forest Figure 2 Benchmark

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
