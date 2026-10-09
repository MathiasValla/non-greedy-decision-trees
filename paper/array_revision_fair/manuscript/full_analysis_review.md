# Full Numerical and Methods Audit

9 October 2026. **No actionable P1/P2 numerical, selection or accounting discrepancy found in the complete retained full analysis.** The evidence is ready for carefully qualified writing. This does not approve the forthcoming fragments, assembled manuscript/response, algorithmic novelty or final acceptance.

## Independent Checks

Read [full validation](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/analysis/full/validation.json), its fourteen hashed CSV/protocol exports, and retained raw task/selection/inner-block/refit metadata. All fourteen hashes match, including the pre-cosmetic-cleanup backup hash set. Protocol fingerprint: `d8999e02a5ad8a1398996fd3c851f5a68fd17d697f37cd048e2258a418475d7b`. Primary-comparison SHA256: `b3991e718b04aff40439ffdc59c02edb9d4a4b8e52ec734f4b4a8cb5c9286e23`.

- Verified all 285 final task manifests: six fixed blocks, three selected refits and eleven specified contrasts each. Repeat CSVs contain 136,800 fixed forest, 5,130 single-tree and 855 tuned records, without duplicate task/model keys; every model has all five seeds on all 57 datasets. All 28,557 dataset-mean rows cover 501 models. Independently reconstructed accuracy/balanced-accuracy dataset means from the repeat CSVs.
- Independently reproduced all eleven paired mean effects, medians, W/T/L, balanced-accuracy deltas, 20,000-resample percentile intervals, raw two-sided Wilcoxon p-values and one joint eleven-test Holm adjustment. Used the specified seed 41, dataset identity alignment, 12-decimal difference rounding and all-zero rule. No additional hypothesis family was introduced.
- Recomputed all 22 prespecified sensitivity means/intervals from dataset differences and manifest memberships: 48 equally weighted known families and 38 named non-synthetic tasks. No sensitivity p-values were generated.
- Independently reconstructed all 285 sets of three CV winners from 10,260 retained inner-block metadata files, including the 48/288/768 candidate spaces and accuracy/fit-work/ID ordering. All 855 refit checkpoints agree with locked choices and CSV configurations. There are 280 stratified three-fold tasks and five ordinary three-fold tasks, the latter all lymphography seeds 1000-1004. The documented rare-class validation limitation remains.

## Primary Findings for Writing

[Primary comparisons](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/analysis/full/paired_primary_comparisons.csv) support exactly three fixed anchors with Holm p below 0.05: D3/all-feature k2 replacements, +1.0577 points, pH=0.009961; D3/all-feature k3 replacements, +1.2727 points, pH=0.020656; D3/sqrt k3 replacements, +1.0411 points, pH=0.001503. D3/sqrt k2 has a positive mean-effect interval but pH=0.095386. All four unrestricted fixed anchors have pH above 0.05. These decisions do not establish a tested depth/feature interaction; other fixed grid contrasts remain descriptive.

Tuned family effects, in accuracy percentage points:

| Contrast | Mean [Pointwise 95% CI] | Median | W/T/L | Joint Holm p |
| --- | ---: | ---: | --- | ---: |
| Family 1/2 minus RF | +0.9674 [-0.0668, +2.2979] | +0.0062 | 29/8/20 | 1.000000 |
| Family 1/2/3 minus RF | +1.5693 [+0.2991, +3.2767] | 0 | 28/11/18 | 0.488383 |
| Family 1/2/3 minus Family 1/2 | +0.6019 [-0.1084, +1.6331] | 0 | 18/23/16 | 1.000000 |

The inclusive-family result is **a positive estimated mean benefit with a positive unadjusted mean-effect interval**, alongside **no rejection by the prespecified Holm-adjusted signed-rank test**. Neither summary cancels the other. Bootstrap mean inference and signed-rank location inference have different targets; the latter also needs its usual symmetry qualification. Do not write "no mean benefit", "equivalent to RF", "proved superior", or that zero median disproves the mean effect. Overlapping repetitions are not 285 independent inferential units.

For inclusive versus RF, the [sensitivities](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/analysis/full/sensitivities.csv) are +1.0308 points [-0.2750, +2.8959] with equal family weighting and +0.5279 [-0.9141, +2.7677] on the named 38-task subset. Both intervals cross zero. The other two tuned contrasts also have zero-crossing intervals under both sensitivities. Report attenuation and uncertainty, not robust general superiority, equivalence, or proof that synthetic tasks causally explain the observed benefit. These sensitivities change the weighting/sample and are not independent confirmation.

## What Was Actually Selected

Counts below are correlated dataset/repetition selections, not independent dataset counts. Source: [tuned repeat records](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/analysis/full/tuned_forests.csv), checked against every locked raw selection.

| Selected Configuration | Family 1/2 | Family 1/2/3 |
| --- | ---: | ---: |
| Pure k1 | 85 | 61 |
| Pure k2 | 83 | 28 |
| Pure k3 | 0 | 44 |
| Actual two-/three-horizon mixtures | 117 | 152 |
| Total | 285 | 285 |

The inclusive mixtures comprise 67 horizon-1/2, 42 horizon-1/3, 37 horizon-2/3 and six 85/10/5 three-way selections. Horizon three appears in 129/285 inclusive selections, including pure k3. Thus the inclusive tuned contrast evaluates an expanded **selection family**, not sparse mixing alone; even actual mixtures include 50/50 options. Its mean effect does not isolate the causal contribution of mixing, horizon three or a diversity mechanism. RF refits are actual library RF; 151 selected all features and 134 selected sqrt, so distinguish the all-feature bagging-style configuration from conventional feature-randomized RF.

## Cost Accounting

[Tuning table](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/analysis/full/fair_tuning_table.csv), equal-dataset means after averaging repeats:

| Family | Direct Refit Wall (s) | CV Tree-Fit Work (s) | Summed Workflow Stages (s) |
| --- | ---: | ---: | ---: |
| RF | 0.062618 | 2.271417 | 3.404992 |
| 1/2 | 0.951821 | 112.079219 | 118.035100 |
| 1/2/3 | 12.937408 | 2671.049489 | 2693.803156 |

Ratios of mean costs versus RF are respectively 15.20x/206.61x for direct refits, 49.34x/1175.94x for CV fitting work, and 34.67x/791.13x for summed workflow stages. These are not mean dataset-specific ratios. Do not describe the 1175.94x selection-work ratio as a refit/runtime ratio or treat constituent fit work as uninterrupted wall time.

Recomputed required-horizon bank sums, schedule charges, bookkeeping, direct-refit/prediction additions and physical totals for every raw task. Each standalone family is charged all required CV banks, including unused members and discarded candidates. Physical shared work is counted once: mean selection fit work is 2671.049489 s, not the 2785.400124 s sum of overlapping family charges. Mean physical selection-plus-all-refits workflow is 2694.838189 s, not the 2815.243248 s sum of standalone family workflows. Fixed-stage work is separate; its raw sums also match [shared accounting](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/analysis/full/shared_accounting.csv).

Physical summary values are mean retained stage totals per task, not elapsed duration of the parallel run. Workflow sums exclude checkpoint I/O, startup/downloads and idle gaps. RF's combined fitting field adds whole-refit wall time to CV tree-fit sums; prepared families use constituent-fit sums throughout. Preserve those measurement-kind labels. No equal-total-compute or prospective fixed-time superiority follows; the retrospective 0.7-second fixed-curve reference does not change this.

## Verification and Release Boundary

The v2 certificate correctly distinguishes bank-probability/selected-slot reconstruction and independently reconstructed inner winners from **range/checkpoint-only** single-tree and selected-direct-refit scores. This audit further checks CV choices and metadata/accounting consistency, not missing test predictions or fitted models. All fourteen CSV/protocol hashes certify the numerical export set; they do not individually hash raw checkpoints, figures, TeX fragments, `physical_cost_summary.json`, or the certificate itself. The physical summary was separately checked against the accounting CSV.

Parent's cosmetic figure/source changes are outside this numerical audit. A changed analyzer-source SHA is expected after that regeneration; retaining the identical fourteen numerical/protocol hashes is the relevant invariance check. No new algorithmic novelty or causal sparse-allocation claim follows automatically from these outcomes. Review the actual forthcoming prose sequentially before integration or submission.

Only this review file was written. No fits, analyzer entry points, production regeneration, figures, core/protocol/analysis/main/response edits, publication actions or commits were performed. All recalculations were read-only/in-memory checks of already specified quantities from complete retained outputs and raw metadata.
