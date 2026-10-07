# Fixed-Results Interpretation Notes

Internal provisional review, 2026-10-07. The accompanying TeX file is an
include-ready fixed-only Results fragment, not an approved final article.
No conclusions about training-selected outcomes are drawn. No manuscript,
response, runtime, runner, protocol, or frozen output was edited; no models
were fitted and no production analysis or figures were regenerated.

## Sources and Completeness

Sources are the existing `analysis/fixed_only/validation.json`, `summary.csv`,
`descriptive_paired_comparisons.csv`, `paired_primary_comparisons.csv`,
`sensitivities.csv`, and `dataset_manifest.csv`, relative to
`paper/array_revision_fair`. Context was checked against the current
`PROTOCOL.md` and `paper/array_revision/main.tex` methods. The actual
`Fig2_main_D3_Fall.png` was inspected; its corresponding embedded Figure 2
has label `fig:tradeoff` and the same depth-three/all-feature scope.

- Validation reports 57 datasets, five repetitions each, 285 outer tasks,
  1,710 fixed blocks, 5,130 single-tree rows, and 136,800 forest rows;
  141,930 model records total. These records are not independent observations.
- `validated_complete_cohort=true`, `missing_or_skipped_tasks=0`,
  `fixed_only=true`, `tuned_rows=0`, `primary_contrasts=8`,
  `fixed_only_inference=pending_full_11_family`, `holm_family_size=null`.
- Forest scores were reconstructed from stored bank probabilities and
  selected-slot fitting work from constituent time sums. Single-tree checks
  are range/checkpoint consistency only, not independent prediction refits.
  Validation does not cover selected-model refits or inner-CV outcomes here.
- The manifest contains 48 known family groups and 38 named non-synthetic
  tasks. Used sample counts span 32--12,958, predictor counts 2--43;
  `penguins` is the only complete-case row reduction (11 rows).
- The five source CSV hashes were checked against `validation.json` during
  drafting. The protocol fingerprint is
  `d8999e02a5ad8a1398996fd3c851f5a68fd17d697f37cd048e2258a418475d7b`.

| Source CSV | Verified SHA-256 |
| --- | --- |
| `summary.csv` | `6fe23872401d33b38c7bef83ddc7a0e649752c07bce95a7bac73e52e5ae349d5` |
| `descriptive_paired_comparisons.csv` | `36c2567f63e98bad013b38d8c6f61523edc0de4dbdfb0b820078251e76eae09b` |
| `paired_primary_comparisons.csv` | `17ec56f3c08aa70ca7eb6991a62762b1b2d22b7b250817184a3f404d20455380` |
| `sensitivities.csv` | `e7cc3c7f8d2ad839cd94ef5fc977b3fcea97c1bd44f1020ccd3541ade0be3d15` |
| `dataset_manifest.csv` | `a862076defac83b29a06cee965c11cf392dc15d1615d8d493b320ac411996e2e` |

## Units and Inferential Limits

All effects and interval endpoints below are percentage points (CSV fractions
multiplied by 100). Absolute accuracies are percentages. Means average five
repetitions within each dataset before equal-dataset aggregation. Medians
and W/T/L likewise describe dataset-mean paired differences, not individual
partitions. W/T/L is left-model wins/ties/losses; each total is 57.

The supplied intervals are pointwise, unadjusted percentile bootstrap
intervals for the mean paired effect (20,000 dataset resamples, seed 41).
They are not simultaneous intervals, median intervals, or a substitute for
the pending eleven-contrast joint analysis. The bootstrap uses a
dataset-exchangeability approximation on a convenience sample. In particular,
a positive mean interval alongside a zero or negative median is not a
contradiction: the summaries describe different aspects of the distribution.
Do not infer a future signed-rank decision from either summary. No test
statistics, p-values, significance decisions, equivalence, or noninferiority
claims belong in this provisional draft.

Eight fixed anchors are T=100, 10% horizon-two/three replacement, D=3 or
unlimited, all or square-root features. D=6, single trees, pure forests,
the triple mixture, other proportions, and other T are descriptive, not
additional primary contrasts. Sensitivities change units or membership only
as already specified; they are not new hypothesis families.

## Timing Boundaries

- Fixed-tree `summary.csv:direct_fit_time_s` is fit-only despite its name:
  constructor and prediction are excluded. Do not call it complete refit cost.
- Fixed-forest `fit_work_s` is the sum of recorded fits of the actual selected
  slots. It excludes constructor/bootstrap preparation, prediction, unused
  bank members, and schedule evaluation. It is not full bank construction
  time, a new separately refitted forest stopwatch, or end-to-end time.
- Cost ratios are ratios of equal-dataset mean fitting costs, not means or
  medians of dataset cost ratios. Measured constituent slot sums, not linear
  estimates from pure-bank mean costs, underlie every composition.
- No chosen-forest refit-time evidence is available in this fixed-only set.
  No selection-cost or selected-family comparison is made here.
- Times reflect five concurrent one-thread shards on an Apple M3 MacBook
  Air (eight CPU cores, 16 GB memory), including shared load and differences
  between the library CART and isolated sighted implementation. They do not
  establish an algorithm-independent cost lower bound or prospective budget
  feasibility. Rounded seconds below are reporting precision, not new fits.

## Single Trees: All Features

Source IDs: `D{3,6,None}_L1_Fall__cart` and
`D{3,6,None}_L1_Fall__single_k{2,3}` in `summary.csv`.
Contrast IDs: `descriptive__D{3,6,None}_L1_Fall__single_k{2,3}_vs_cart`
in `descriptive_paired_comparisons.csv`. All have minimum leaf size one.

| D | k | Accuracy (%) | Mean fit-only (s) | Mean realized depth |
| --- | --- | ---: | ---: | ---: |
| 3 | 1 | 67.8243 | 0.001028717 | 2.9649 |
| 3 | 2 | 70.5934 | 0.028217403 | 3.0000 |
| 3 | 3 | 71.3649 | 1.684489134 | 3.0000 |
| 6 | 1 | 72.8238 | 0.001128263 | 5.5789 |
| 6 | 2 | 73.2131 | 0.056911269 | 5.9439 |
| 6 | 3 | 73.4126 | 3.772365297 | 5.9474 |
| unlimited | 1 | 74.5112 | 0.001690356 | 10.1158 |
| unlimited | 2 | 69.3823 | 0.159224192 | 15.0877 |
| unlimited | 3 | 66.2200 | 7.965748526 | 17.0246 |

| D | k versus CART | Mean delta [95% interval] | Median delta | W/T/L | Ratio of mean fit costs |
| --- | --- | ---: | ---: | --- | ---: |
| 3 | 2 | +2.7691 [+0.6798, +5.2208] | +0.1250 | 29/3/25 | 27.4297 |
| 3 | 3 | +3.5406 [+1.4479, +6.0084] | +0.4000 | 31/3/23 | 1637.4658 |
| 6 | 2 | +0.3892 [-1.8992, +2.9851] | -0.4800 | 21/5/31 | 50.4415 |
| 6 | 3 | +0.5888 [-1.9153, +3.5252] | -1.2698 | 18/4/35 | 3343.5167 |
| unlimited | 2 | -5.1289 [-8.6930, -1.8421] | -3.2024 | 17/2/38 | 94.1956 |
| unlimited | 3 | -8.2912 [-12.4510, -4.3891] | -3.9394 | 15/2/40 | 4712.4676 |

Interpretation: increasing horizon is not increasing the configured depth;
realized size can nevertheless change within a common depth constraint.
D=3/k=3/all features is the shallow full-horizon case described in Methods,
not evidence that k=3 is globally optimal at D=6 or unlimited. Coincident
larger realized trees and lower test scores do not establish overfitting as
the cause. The scorer objective remains terminal training Gini, not accuracy.

## Pure Forests at Matched T=100

Each row contrasts `D{3,6,None}_L1_F{all,sqrt}__T100__pure_k{2,3}` with
the same prefix ending `pure_k1`, from the descriptive paired CSV. All
settings share T, D, minimum leaf size, feature policy, bootstrap slots and
seeds. Numerical threshold, tie, and random-feature-order differences remain
as disclosed in Methods; common parameter matching is not bitwise identity.

| D | Features | k | Mean delta [95% interval] | Median delta | W/T/L | Ratio of mean fit work |
| --- | --- | --- | ---: | ---: | --- | ---: |
| 3 | all | 2 | +1.8997 [+0.5365, +3.4321] | +0.2459 | 30/6/21 | 24.8209 |
| 3 | all | 3 | +2.3381 [+0.7262, +4.1162] | +0.9524 | 31/6/20 | 1184.8618 |
| 3 | sqrt | 2 | +2.3772 [+1.2202, +3.6474] | +0.6061 | 37/7/13 | 39.0613 |
| 3 | sqrt | 3 | +2.8534 [+1.5755, +4.2301] | +0.8889 | 41/5/11 | 1046.1498 |
| 6 | all | 2 | -0.5842 [-2.7472, +1.8310] | -0.4687 | 17/6/34 | 46.9316 |
| 6 | all | 3 | -1.0904 [-3.8153, +2.0380] | -1.4013 | 17/4/36 | 2514.3706 |
| 6 | sqrt | 2 | +1.2701 [+0.3300, +2.2562] | +0.1639 | 31/6/20 | 94.6235 |
| 6 | sqrt | 3 | +1.9552 [+0.5611, +3.5153] | +0.1439 | 29/5/23 | 2487.3157 |
| unlimited | all | 2 | -6.8385 [-10.3570, -3.6697] | -3.0328 | 10/3/44 | 66.6790 |
| unlimited | all | 3 | -9.6804 [-13.8208, -5.7373] | -5.0000 | 11/2/44 | 2642.1010 |
| unlimited | sqrt | 2 | +1.0761 [+0.3452, +1.8758] | +0.2878 | 31/7/19 | 180.6204 |
| unlimited | sqrt | 3 | +0.7846 [-0.7541, +2.4382] | 0.0000 | 24/10/23 | 3648.2889 |

Feature-context caveat: these are separate contrasts against each policy's
own CART control, not a formal interaction test or a direct all-versus-sqrt
comparison. For example, unrestricted T=100 CART mean accuracy is 77.5242%
with all features and 76.3909% with sqrt. The positive sqrt horizon effects
must not be rewritten as a universal absolute-accuracy benefit of feature
randomization. No error-correlation, diversity, bias/variance, or causal
mechanism was evaluated in this results fragment.

## Eight Fixed Anchors

Source: `paired_primary_comparisons.csv`, IDs
`fixed__D{3,None}_L1_F{all,sqrt}__k{2,3}_vs_k1`. Each left model is a
T=100 `pair_k1_k{2,3}_q10` forest: exactly ten replacement members, not
ten additional members. The right model is its matched `pure_k1` forest.
All rows retain status `primary_pending_full_11_family`.

| D | Features | Replacement k | Mean delta [95% interval] | Median delta | W/T/L | Balanced-accuracy delta | Cost ratio |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| 3 | all | 2 | +1.0577 [+0.4523, +1.7699] | 0.0000 | 27/21/9 | +1.1472 | 3.3868 |
| 3 | all | 3 | +1.2727 [+0.6079, +2.0193] | 0.0000 | 28/14/15 | +1.3253 | 119.5235 |
| 3 | sqrt | 2 | +0.4236 [+0.0749, +0.7848] | 0.0000 | 27/22/8 | +0.4757 | 4.8434 |
| 3 | sqrt | 3 | +1.0411 [+0.4586, +1.7365] | +0.1274 | 32/19/6 | +1.1212 | 106.7335 |
| unlimited | all | 2 | +0.0516 [-0.2691, +0.4353] | 0.0000 | 19/20/18 | -0.0842 | 7.6415 |
| unlimited | all | 3 | -0.0196 [-0.4930, +0.5485] | 0.0000 | 16/20/21 | -0.2036 | 262.8098 |
| unlimited | sqrt | 2 | +0.2161 [-0.0235, +0.4724] | 0.0000 | 23/18/16 | +0.2361 | 18.8991 |
| unlimited | sqrt | 3 | +0.2771 [+0.0004748, +0.5883] | 0.0000 | 25/16/16 | +0.2722 | 367.0384 |

The last lower endpoint is deliberately not rounded to zero; its exact
fraction in the source is `4.747890741235188e-06`. Its positivity is not
an adjusted inferential decision. Small unrestricted means and zero medians
are not equivalence evidence. Even the balanced-accuracy means change sign
for the two unrestricted all-feature anchors.

Additional descriptive T=100/all-feature records cited in the TeX:

| D | Composition (% k1/k2/k3) | Mean delta [95% interval] | Median delta | W/T/L | Mean fit work (s) | Cost ratio |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| 3 | 85/10/5 | +1.3584 [+0.5164, +2.3001] | 0.0000 | 28/17/12 | 4.226034 | 62.4108 |
| 6 | 90/10/0 | +0.2694 [-0.0649, +0.6409] | 0.0000 | 22/18/17 | 0.446333 | 5.6028 |
| 6 | 90/0/10 | +0.5807 [+0.0623, +1.2486] | 0.0000 | 22/24/11 | 20.119599 | 252.5585 |

These are `descriptive__D3_L1_Fall__T100__triple_85_10_05_vs_k1` and
`descriptive__D6_L1_Fall__T100__pair_k1_k{2,3}_q10_vs_k1`.
The triple is not a new primary anchor and its slightly higher observed
mean does not establish a paired advantage over either two-way mixture.

## Prespecified Sensitivities

Source: all 16 existing rows in `sensitivities.csv`, using the eight fixed
anchor IDs above. Columns below give mean delta [pointwise 95% interval].
Family units average related task effects before equal weighting (48 groups);
the other sensitivity retains only the 38 explicitly named non-synthetic
tasks. Neither is a newly chosen favorable subset or an independent dataset.

| D | Features | Replacement k | 48-family sensitivity | 38-non-synthetic sensitivity |
| --- | --- | --- | ---: | ---: |
| 3 | all | 2 | +0.7749 [+0.2460, +1.4482] | +0.5348 [+0.0578, +1.2195] |
| 3 | all | 3 | +0.9137 [+0.3227, +1.6275] | +0.6283 [+0.0701, +1.3519] |
| 3 | sqrt | 2 | +0.1887 [-0.0744, +0.4548] | +0.1080 [-0.1648, +0.3670] |
| 3 | sqrt | 3 | +0.5708 [+0.2356, +0.9900] | +0.4541 [+0.1867, +0.7388] |
| unlimited | all | 2 | +0.0060 [-0.3614, +0.4478] | -0.0649 [-0.5258, +0.4930] |
| unlimited | all | 3 | -0.0544 [-0.6102, +0.5950] | -0.1265 [-0.8226, +0.7140] |
| unlimited | sqrt | 2 | +0.0985 [-0.1566, +0.3724] | +0.0774 [-0.2265, +0.4049] |
| unlimited | sqrt | 3 | +0.1290 [-0.1429, +0.4019] | +0.0652 [-0.2374, +0.3626] |

The prose limits its sensitivity statement to the all-feature D=3 anchors;
do not generalize it to every row, to D=6, or to unreported pure-forest or
single-tree sensitivities. Known grouping cannot resolve all dependence.

## Actual Figure 2: Supported Reading

Figure 2 / `Fig2_main_D3_Fall.png` shows all 16 compositions at five
evaluated counts, D=3, all features. Panel (a) is mean test accuracy versus
T; panel (b) is the same mean accuracy versus measured mean selected-slot
fit work on a logarithmic axis. The vertical line is a 0.7 s mean-cost
reference. No evaluated model is exactly at that reference. Markers, not
intermediate line crossings, identify evaluated models. Neither panel
contains paired confidence intervals.

Selected observed coordinates, from `summary.csv`:

| Model-ID suffix after `D3_L1_Fall__` | Accuracy (%) | Mean fit work (s) | Reason retained |
| --- | ---: | ---: | --- |
| `T020__pure_k2` | 74.790382 | 0.338133776 | Highest observed mean accuracy among plotted points at or below 0.7 s |
| `T040__pure_k2` | 74.264583 | 0.672754496 | Increasing T need not increase this observed mean |
| `T020__pair_k1_k2_q25` | 74.063578 | 0.095460218 | A lower-cost mixture tradeoff, not pure-forest dominance at every cost |
| `T100__pair_k1_k2_q25` | 74.572595 | 0.470881029 | Larger mixed forest can have lower mean accuracy and higher mean work than pure k2/T20 |
| `T200__pair_k1_k2_q10` | 73.845566 | 0.457367181 | Same counterexample for a sparse 10% mixture |
| `T020__pair_k1_k3_q05` | 72.920301 | 0.834736148 | Minimum observed mean work among all plotted k3-containing models, already above 0.7 s |
| `T100__pure_k1` | 72.877168 | 0.067713161 | Matched all-feature shallow reference |
| `T100__pure_k2` | 74.776853 | 1.680702267 | Matched pure horizon-two forest |
| `T100__pure_k3` | 75.215289 | 80.230739424 | Matched pure horizon-three forest |
| `T100__pair_k1_k2_q10` | 73.934871 | 0.229333711 | Primary shallow horizon-two replacement anchor |
| `T100__pair_k1_k3_q10` | 74.149888 | 8.093312075 | Primary shallow horizon-three replacement anchor |

These coordinates support a descriptive accuracy/work tradeoff with strong
implementation-dependent k3 costs. They refute a blanket claim that sparse
mixtures necessarily improve on smaller pure farther-sighted forests.
The highest observed point below a reference is a retrospective comparison
of this finite plotted set, not a trained policy, a statistically established
winner, or a validated resource frontier. No new cross-T paired interval
was computed or inferred from the lines.

Do not claim a 0.7 s model obtained by interpolation, universal per-dataset
cost feasibility, equal total computation, an error-diversity explanation,
or superiority to a selected conventional baseline. No conclusions about
unfinished selection experiments follow from these fixed coordinates.
Nonmonotone sampled means do not imply that adding trees is generally harmful.
The k3-above-reference statement is restricted to this D=3/all-feature panel,
not every dataset or every structural setting.

## Integration Requirements

- Insert only after parent review; do not use this fragment to approve the
  surrounding manuscript or its older draft-marked numerical sections.
- Retain the fixed/tuned stage distinction and all timing labels. Forest
  curves are architecture-matched, not equally timed or training-selected.
- Preserve the nuance that a shallow constrained experiment is informative
  without establishing fixed depth three as universally best. The shallow
  literature does not supply a substitute for the measured deeper controls.
- At final integration, apply the single planned eleven-contrast joint
  analysis to the full completed results; do not adjust the eight fixed
  anchors as a separate family or promote descriptive contrasts to primaries.
- Check all final Results, tables, captions, abstract, discussion, and reviewer
  replies against the final source set. These sidecars make no predictions
  about, and require no changes to, the running selection experiments.
