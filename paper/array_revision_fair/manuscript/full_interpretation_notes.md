# Full-Results Interpretation and Integration

9 October 2026. First complete-results scientific writing pass for independent
review by Lagrange and the author. This is not journal approval, acceptance,
or confirmation that the surrounding manuscript is ready for submission.
Only the eight requested new sidecars were written. The approved historical
fixed-only draft and review remain untouched.

## Evidence and Verification Scope

Source directory: `paper/array_revision_fair/analysis/full`. Read the complete
CSV exports using structured parsing, checked all thirteen CSV hashes and
the protocol-snapshot hash (fourteen certified artifacts) against
`validation.json`, inspected the actual Figure 2 and Figure 3 PNGs (including
the corrected Figure 3 labels), and subsequently inspected the new Figure 1.
Read the current `paper/array_revision/main.tex`, `response_to_reviewers.tex`,
`PROTOCOL.md`, the full protocol snapshot, and physical-cost summary. No fits,
new inference, analyzer execution, figure generation, or frozen-output edits
were performed. Numerical conversions and selection tallies use recorded
values, not new selection decisions.

The certificate reports 57 datasets, five repeats, 285 outer tasks, 1,710
fixed blocks, 5,130 fixed-tree rows, 136,800 fixed-forest rows, and 855
selected-family refits: 142,785 outer score records. The exports contain
28,557 dataset-mean rows and 501 summary rows. There are no missing/skipped
tasks. `fixed_only=false`, `fixed_only_inference=complete_11_family`,
`holm_family_size=11`, `primary_contrasts=11`, and
`cv_winners_independently_reconstructed=true`.

Scope must remain precise: fixed and inner-CV forest probabilities and
selected-constituent cost sums were reconstructed from retained banks;
validation winners were independently reconstructed. Single-tree and direct
selected-refit scores have range/checkpoint consistency checks, not independent
prediction reconstruction. This writing pass does not refit any model or
repeat the original independent analyzer's statistical calculations.

The unchanged protocol fingerprint is
`d8999e02a5ad8a1398996fd3c851f5a68fd17d697f37cd048e2258a418475d7b`.
The refreshed certificate's analysis-source hash is
`f3076f010500f10e56cfa9815aa55190fff356f6a4827156536c45e9bd72c67b`;
cosmetic figure updates leave the certified numerical artifacts unchanged.
Bootstrap intervals use 20,000 resamples and seed 41. The manifest retains
48 known family groups, 19 named synthetic/constructed tasks, and 38 other
tasks, with used sample counts 32--12,958 and predictor counts 2--43.
Only `penguins` drops complete-case rows (11). This is the previously
explored convenience sample, not an independent confirmation cohort.

| Output checked | Rows | SHA-256 |
| --- | ---: | --- |
| `summary.csv` | 501 | `51c0db3c2ad933ad79058963e6f3322c6b04f79502cf7d6c0ee02d97cfcd5c81` |
| `descriptive_paired_comparisons.csv` | 454 | `36c2567f63e98bad013b38d8c6f61523edc0de4dbdfb0b820078251e76eae09b` |
| `paired_primary_comparisons.csv` | 11 | `b3991e718b04aff40439ffdc59c02edb9d4a4b8e52ec734f4b4a8cb5c9286e23` |
| `sensitivities.csv` | 22 | `bf14d3739c95e848d7c5b9796a16d26ce77244e5fa25d4798feae93017efd392` |
| `fair_tuning_table.csv` | 3 | `b83249f8e824da205a0b9653a88c476b226a8a2c93e9a4fb30cce394492c098f` |
| `tuned_forests.csv` | 855 | `b74f2b86d5a3820672aa22f8d8b0619e7fef506914ee5071b9007ee06bb68e81` |
| `dataset_manifest.csv` | 57 | `a862076defac83b29a06cee965c11cf392dc15d1615d8d493b320ac411996e2e` |

The remaining checked exports are `fixed_trees.csv`, `fixed_forests.csv`,
`dataset_means.csv`, `paired_dataset_deltas.csv`, `shared_accounting.csv`,
and `physical_cost_dataset_means.csv`; their full hashes are retained in
the certificate. All complete fixed descriptive values are unchanged from
the approved fixed-only draft. Primary status and joint tests are now complete.

## Central Scientific Reading

- Inclusive versus selected RF has a positive full-cohort estimated mean
  effect and a pointwise bootstrap interval above zero. Do not write that
  tuning removed all improvement, that RF has higher mean accuracy, or that
  there is no evidence of a mean benefit. Those would misstate the new data.
- Its zero median, heterogeneous W/T/L, non-rejected joint-Holm signed-rank
  location null, and sensitivities crossing zero limit a typical-task or
  broadly robust benefit claim. They do not establish equivalence or
  contradict a mean-effect interval. Signed-rank location inference requires
  the usual symmetry qualification; it is not simply a test of the mean
  or the observed median.
- The one-/two-sighted family also has a positive mean estimate, with a
  mean interval crossing zero and a very small positive median. Do not
  silently round its median to zero in precise interpretive statements.
- Selected-family effects concern expanded candidate-space policies.
  Many selected models are pure. Do not attribute the aggregate gain to
  sparse replacement, heterogeneity, or a measured diversity mechanism.
- Shallow all-feature gains cannot be extrapolated to all depths or to
  square-root features. Conversely, unrestricted all-feature pure-forest
  losses do not establish a corresponding loss with square-root features.
- The cost conclusion concerns substantially larger measured selection and
  refit costs in this implementation. There is no equal-computation design,
  algorithm-independent lower bound, or validated cost frontier.

All mean/median effects and interval endpoints below are percentage points;
the underlying CSV stores fractions. W/T/L is across 57 dataset-mean paired
differences, not 285 independent trials. Pointwise intervals are unadjusted
and not simultaneous. One Holm family contains exactly eight fixed anchors
and three selected-family contrasts. No new tests were added for D=6,
single trees, pure forests, extra proportions/counts, or sensitivities.

## Tuned Effects and Sensitivities

Source IDs in `paired_primary_comparisons.csv` are the three `tuned__...`
rows. Displayed precision below is greater than the main Results prose.

| Contrast | Mean [pointwise 95% interval] | Median | W/T/L | Joint Holm p | Balanced-accuracy delta | Direct-refit cost ratio |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| `mixed_k2_vs_rf` | +0.967393 [-0.066829, +2.297895] | +0.00617284 | 29/8/20 | 1.000000 | +1.095159 | 15.200502 |
| `mixed_vs_rf` | +1.569297 [+0.299137, +3.276698] | 0 | 28/11/18 | 0.488383 | +1.603022 | 206.609322 |
| `mixed_vs_mixed_k2` | +0.601903 [-0.108375, +1.633093] | 0 | 18/23/16 | 1.000000 | +0.507863 | 13.592270 |

| Contrast | 48 known-family groups | 38 named non-synthetic tasks |
| --- | ---: | ---: |
| `mixed_k2_vs_rf` | +0.614339 [-0.315213, +2.017356] | +0.382767 [-0.662640, +2.086917] |
| `mixed_vs_rf` | +1.030799 [-0.274996, +2.895915] | +0.527932 [-0.914059, +2.767693] |
| `mixed_vs_mixed_k2` | +0.416460 [-0.182374, +1.142529] | +0.145165 [-0.413581, +0.785519] |

These are the six existing tuned rows in `sensitivities.csv`, not newly
chosen subsets. The sixteen fixed sensitivity rows retain their approved
values and no extra hypothesis family. The Results prose quotes only the
all-feature shallow fixed anchors when discussing their family/subset
robustness. In particular, the positive mean interval for shallow sqrt/k2
does not imply a joint adjusted rejection (`p_H=0.0953855861`). The three
fixed contrasts with adjusted p below 0.05 are D3/all/k2, D3/all/k3, and
D3/sqrt/k3. None of the four unrestricted anchors or three tuned-family
contrasts has an adjusted p below 0.05. This is not a statement that their
mean effects are zero.

The unrestricted sqrt/k3 mean interval's lower endpoint is
`0.0004747890741235188` percentage points. Table 2 deliberately prints
`0.00047`, rather than rounding it to zero or interpreting it as an
adjusted decision. No primary p-values are assigned to the descriptive
single-tree or pure-forest effects.

## What Selection Actually Chooses

Tallies were read from `tuned_forests.csv:selected` JSON, not inferred from
mean horizon or rounded weights. Each family has 285 outer selections.
The corrected Fig3 labels ``Family 1/2'' and ``Family 1/2/3'' denote the
spaces allowing those horizons, not necessarily mixed or pure horizon-two
forests. The cosmetic relabeling was re-inspected after the parent's update.
RF permits all and square-root features;
all-feature selected RF configurations are bagged CART, not necessarily
conventional feature-subsampled random forests.

| Selected composition | RF | One-/two-sighted | Inclusive |
| --- | ---: | ---: | ---: |
| pure k1 | 285 | 85 | 61 |
| pure k2 | 0 | 83 | 28 |
| pure k3 | 0 | 0 | 44 |
| pair k1/k2, 5% farther | 0 | 29 | 16 |
| pair k1/k2, 10% farther | 0 | 20 | 10 |
| pair k1/k2, 25% farther | 0 | 22 | 12 |
| pair k1/k2, 50% farther | 0 | 46 | 29 |
| pair k1/k3, 5% farther | 0 | 0 | 8 |
| pair k1/k3, 10% farther | 0 | 0 | 15 |
| pair k1/k3, 25% farther | 0 | 0 | 12 |
| pair k1/k3, 50% farther | 0 | 0 | 7 |
| pair k2/k3, 5% farther | 0 | 0 | 5 |
| pair k2/k3, 10% farther | 0 | 0 | 6 |
| pair k2/k3, 25% farther | 0 | 0 | 12 |
| pair k2/k3, 50% farther | 0 | 0 | 14 |
| triple 85/10/5 | 0 | 0 | 6 |
| Total | 285 | 285 | 285 |

Inclusive selects 133 pure and 152 actual mixed forests (146 two-horizon
and six three-horizon).
It uses a horizon-three member in 129 selections, including 44 pure-k3
choices. One-/two-sighted selects 168 pure and 117 mixed forests. Counts
do not identify how much of the mean gain each composition causes: a
post-selection subgroup comparison would change the question and is not
performed. RF candidates are nested in both expanded spaces, but outer
test performance need not improve under a larger inner selection space.

| Selected setting | RF | One-/two-sighted | Inclusive |
| --- | ---: | ---: | ---: |
| depth 3 | 66 | 90 | 104 |
| depth 6 | 87 | 106 | 103 |
| unrestricted | 132 | 89 | 78 |
| all features | 151 | 156 | 149 |
| sqrt features | 134 | 129 | 136 |
| leaf minimum 1 | 189 | 183 | 185 |
| leaf minimum 5 | 96 | 102 | 100 |
| T=20 | 105 | 119 | 116 |
| T=40 | 58 | 59 | 64 |
| T=60 | 51 | 56 | 56 |
| T=100 | 71 | 51 | 49 |

These are configuration counts across outer tasks, not independent votes
for a universally optimal depth. They support retaining deeper controls.
The tree-size literature remains conditional: noisy regression, leaf caps,
and resampling choices differ from fixed-depth Gini classification. Growing
leaf-count consistency does not prove fixed-depth-three consistency; shallow
boosting is not direct bootstrap-forest evidence. Existing checked citation
keys were reused without new bibliography or priority claims.

## Costs and Their Boundaries

All entries are equal-dataset means after averaging repeats, from
`fair_tuning_table.csv` / the matching `summary.csv` selected-family rows.

| Quantity (seconds) | RF | One-/two-sighted | Inclusive |
| --- | ---: | ---: | ---: |
| Standalone CV constituent fit work | 2.271416719 | 112.079218896 | 2671.049488742 |
| Selection bank wall sum | 3.190668873 | 116.269687818 | 2678.745772459 |
| Selection schedule-evaluation wall sum | 0.147625944 | 0.796233529 | 2.094852016 |
| Selection bookkeeping attribution | 0.001592065 | 0.004512679 | 0.011321889 |
| Direct selected-model refit wall time | 0.062617738 | 0.951821055 | 12.937408338 |
| Test prediction wall time | 0.002486982 | 0.012845270 | 0.013801693 |
| Sum of workflow stage wall times | 3.404991602 | 118.035100350 | 2693.803156396 |

RF, one-/two-sighted, and inclusive candidate counts are 48/288/768.
They share the structural grid and training folds, not equal candidate
spaces or computation. Standalone CV fitting-work ratios to RF are
49.3433 and 1175.9399; direct-refit ratios are 15.2005 and 206.6093.
Do not substitute one ratio for another. Families pay for all required
horizon banks even when their selected model is pure k1. Fixed banks are
not charged to selection. Prediction and evaluation are separate from
constituent fit work.

Direct refit wall time includes construction/bootstrap preparation but not
test prediction. Workflow totals add selection bank and schedule wall sums,
bookkeeping, direct refit, and prediction. They exclude checkpoint I/O,
startup, downloads, idle gaps, and an uninterrupted elapsed wall clock.
Recorded times also reflect resume history, shared hardware load, and
implementation differences. Do not call these totals uninterrupted
end-to-end run duration or sum family attributions to obtain physical work.

The physical-cost summary counts shared banks once. For example, physical
selection constituent fit work averages 2671.049488742 s, not the sum of
2.271416719, 112.079218896, and 2671.049488742. Physical selected-workflow
stage sums average 2694.838188744 s across all three final refits; physical
all-stages workflow sums including the fixed stage average 5080.961533074 s.
These are dataset/repetition means, not elapsed duration for the entire
benchmark. They are retained for accounting context, not added to the main
performance table.

For fixed models, single-tree `direct_fit_time_s` is actually fit-only,
excluding construction/prediction. Forest `fit_work_s` sums exactly the
selected constituent slots, excluding construction/bootstrap preparation,
prediction, unused bank fits, and schedule evaluation. Table 1 distinguishes
these from the selected-family direct-refit measurement. Do not compare its
rows as an equally scoped end-to-end timing experiment.

## Tables and Prose: Integration Contract

- `table_performance.tex` and `table_comparisons.tex` are COMPLETE six-column
  `table*` environments, with replacement captions and existing labels
  `tab:performance` / `tab:comparisons`. Replace the old whole environments,
  not only the rows inside the generated markers. Do not double-wrap them.
- Table 1 has exactly 27 data rows: for each D=3/6/unlimited, three all-feature
  single trees, three pure T=100 all-feature forests, and two 10% replacement
  forests; then three selected-family rows. All fixed rows use leaf minimum
  one. The last three rows have selected D/features/leaf/T/composition, not
  depth-matched or fixed-feature settings. The cost header says ``Fit
  measure'' because row-specific timing scopes differ. Scores are proportions,
  unlike percentage accuracies in the Results prose. Realized depth is a
  mean across selected members/repeats/datasets, not the configured cap.
- Table 1 source IDs, in each depth block, are
  `D{3,6,None}_L1_Fall__{cart,single_k2,single_k3,T100__pure_k1,T100__pure_k2,T100__pure_k3,T100__pair_k1_k2_q10,T100__pair_k1_k3_q10}`.
  The final three IDs are `rf`, `mixed_k2`, `mixed` with stage `tuned_forest`.
- Table 2 follows the eleven primary CSV rows in order. Feature labels are
  explicit for all eight fixed anchors. No old 15-row caption, custom-greedy
  comparison, or newly adjusted descriptive row remains. The first eight
  ratios use selected-slot fit sums; the last three use direct-refit wall
  time, never CV-fit or total-workflow ratios. Five decimals retain the
  requested adjusted values; the near-zero mean-interval endpoint has extra
  precision. Do not infer precise ratios from rounded Table 1 costs.
- `results_text.tex` replaces the Results narrative. Move the actual
  validated Figure 2 environment to its indicated insertion point so the
  marked `FIGURE2_POSTPLOT_TEXT` follows it immediately in source order.
  Keep Figure 2's label `fig:tradeoff`. The supplied Figure 3 environment
  reads the existing full-analysis PDF and defines `fig:tuned`. Do not add
  a second Figure 3 from the same output. Float placement may still need
  author adjustment during typesetting.
- The Figure 3 path is relative to the intended existing
  `paper/array_revision/main.tex`, not to this sidecar directory. If the
  parent changes the manuscript's build working directory, update the
  inclusion path there rather than copying or regenerating analysis artwork.
- `discussion_text.tex` replaces the ENTIRE Discussion body, including
  paragraphs after its existing generated marker. `conclusion_text.tex`
  replaces the Conclusion body. Both omit section wrappers. Do not retain
  an obsolete claim that selected conventional forests have higher mean
  accuracy or compare selected RF with a fixed mixture as the tuned result.
- `abstract_suggestion.tex` is abstract body only and contains no numerical
  results. Remove the old pending-evaluation notice. It states scope and
  conditional interpretation without promising submission acceptance.
- `response_results.tex` replaces the obsolete results/status block under
  R1.2, not the entire response letter. It is first-person-compatible factual
  prose and does not alter the author list, Reviewer 2 mismatch, or the
  no-mandatory-APC transfer preference.

The fragments are include-ready material, not standalone LaTeX documents.
Only syntax/numerical checks are appropriate in this restricted pass; no
wrapper, PDF, or manuscript build output was written. Parent must compile
the integrated manuscript and response, inspect table width/float placement,
resolve references, and retain the independent-review correction cycle.

## Figures: Exact Supported Reading

Figure 2 / `full/Fig2_main_D3_Fall` is the same validated fixed D=3,
all-feature graphic as before: sixteen compositions, five T values, 80
observed coordinates. Pure k2/T20 has the highest observed mean accuracy
among plotted points at mean fit work <=0.7 s: 74.790382% at 0.338133776 s.
The T100/25%-k2 mixture is 74.572595% at 0.470881029 s. The cheaper T20/
25%-k2 mixture is 74.063578% at 0.095460218 s. These show a tradeoff and
counterexamples to universal sparse-mixture dominance, not uncertainty-backed
cross-T superiority. No point is exactly at 0.7 s. The minimum mean cost
of a plotted k3-containing configuration is 0.834736148 s. This statement
is limited to the D3/all panel, not every dataset or feature/depth setting.
Lines/intersections are not evaluated intermediate models, equal-cost fits,
or per-dataset feasibility. The highest observed mean is retrospective, not
a trained policy or certified frontier. Selection work is absent from this
axis and paired uncertainty is not displayed.

Figure 3 / `full/Fig3_tuned_families` shows mean paired effects and
pointwise intervals for the three tuned contrasts, not Holm-adjusted
signed-rank intervals. The right panel separately shows CV constituent
fit work, direct-refit wall time, and workflow-stage sums on a log scale.
It does not display an uninterrupted learning stopwatch, pure mixed-model
effects, or an equal-budget comparison. Its corrected ``Family 1/2'' and
``Family 1/2/3'' labels denote horizon-capable selection spaces. The supplied
caption follows these labels and states that both may select pure models.

## Remaining Parent Edits Outside Existing Generated Blocks

These were identified in the current sources read for this pass; the parent,
not this task, must make them. Original line numbers can move during inlining.

- Main abstract (currently line 18): delete the pending notice and replace
  the abstract body with the suggested nonnumerical text, including its
  obsolete final future-tense sentence.
- Main Results opening (around line 112): remove the draft-transition notice
  once all replacement text/tables/figures are integrated. Completion alone
  is not final article approval.
- Main old Figure 1 block (around lines 188--246 in the source read initially):
  replace the preceding-protocol plot with the new, inspected
  `full/Fig1_single_trees.pdf` export (all-feature single trees, including k3),
  or remove/reorganize it and reconcile figure numbering. Its caption must
  state the all-feature scope and that intervals are descriptive mean-effect
  intervals, not extra joint-Holm anchors. Do not retain stale plotted values
  alongside the new Figures 2--3.
- Main Discussion after generated markers (around lines 421--425): replace
  with the full new body, not a mixture of old and new paragraphs. Retain
  the objective-alignment, mean-cost, and implementation limitations but
  remove any duplicate or contradictory result framing.
- Main data/code availability and AI disclosure (around lines 439--441):
  the parent should verify release links, reproduction documentation, and
  whether figures are externally included or equivalently embedded. These
  sidecars do not verify that all final outputs have been publicly released.
- Response opening notice (currently line 20): replace the running-stage
  status with a factual complete-and-validated status, without implying
  journal acceptance or that independent writing review has finished.
- Response E1 (currently line 32): replace ``will replace''/future conclusions
  with completed integration wording after the parent actually integrates.
- Response R1.1: replace ``Completion and validation ... remain a submission
  prerequisite'' and ``Results and figure references will be finalized ...''
  with completed-evaluation statements and correct final references. Keep
  the conditional regression/leaf-cap/fixed-D3 literature caveats and local
  horizon versus final depth distinction.
- Response R1.2: change ``planned analysis'' to completed analysis; delete
  the bold draft-completion notice before the results marker. Replace the
  marker body with `response_results.tex`, then update the locations list
  to include Figure 3. Do not leave either obsolete ``still running'' sentence.
- Response timing correction: retain actual included-slot sums and direct
  refit scopes, avoiding the ambiguous older ``direct prepared-slot fits''
  wording where it could be mistaken for a whole-forest refit stopwatch.
- Retain the user's existing transfer wording requesting a suitable journal
  with no mandatory APC and confirmation of terms, not an asserted free
  publication guarantee. Retain the no-acceptance-guarantee paragraph.

## Mathematical and Literature Guardrails

Retain the existing additive terminal-Gini recurrence and root-only
commitment with restored/clipped local horizon. The uniform abstraction
`E_h <= m + 2m E_(h-1)` counts candidate evaluations (m>=1; no feasible
candidate is a stopping case). It is exponential in horizon before sorting,
partitioning, changing node sizes, and final-node sums, not a tight runtime
formula or an exponential-in-final-depth proof for fixed k. Complete split
assignment counts must not replace it. Full-horizon shallow optimal terminal
training impurity under all features and stated constraints is not global
optimal test accuracy, and feature-restricted search is conditional on its
seeded policy.

No algorithmic-priority claim is restored. LOOK, stepwise lookahead forests,
and modern cached/bounded/hybrid methods remain relevant prior art. Distinct
objectives and stopping/representation constraints preclude a solver ranking
from this benchmark. The literature is not repeated as new empirical evidence
for these exact Gini depth-three forests. The title and abstract should keep
the empirical gains/costs/limits framing, not revive ``enlighten the forest,''
an ad hoc logarithmic utility, or fractional optimization-horizon semantics.
