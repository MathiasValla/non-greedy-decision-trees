# Editorial transition audit

Read-only scientific/editorial review, not a handling-editor decision. Fair data
are pending. Only this audit was written; no manuscript, response, runner,
runtime, build, core, protocol, or result file was changed or executed.

Both documents were updated by the parent during review. Findings below use the
refreshed versions, not the superseded passages that have already been corrected.
Line anchors refer to these snapshots; quoted clauses remain useful if lines move:

- `paper/array_revision/main.tex`: SHA-256
  `e0a911f7fbd0ffe4609a53ff56dd7716e6946f5f4f027b2fa7296f46428480d2`.
- `paper/array_revision/response_to_reviewers.tex`: SHA-256
  `7aad9d5344752f94f98be2325f8e8c9e05983d742ec2b12caff173955b1249cb`.
- `paper/array_revision_fair/PROTOCOL.md`: SHA-256
  `debfd341b3402a41e4f3c80911cc349e0cd9bcb043cf2ed5c38007d29a022836`.

## Remaining replacements

**P1 means a final-submission blocker, not a claim that the explicitly marked
working draft is concealing old evidence.** The current transition notices
properly disclose that the retained numerical blocks belong to the prior run.

| Priority / current location | Residual issue | Exact replacement requirement |
|---|---|---|
| P1: [Discussion limitation, main:354](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:354) | Outside the generated block: "only the conventional baselines undergo inner model selection" directly contradicts the new Methods. | Replace only this limitation with: **All three families receive training-only selection over common structural and ensemble-size settings, but the mixed families search additional compositions and can incur greater selection uncertainty and computational cost. This is not an equal-total-compute experiment.** Preserve the convenience-sample and solver-comparison limitations. |
| P1: [Tuned-results paragraph, main:130](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:130), [cost/interpretation, main:132](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:132), [Discussion, main:349](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:349), [rebuttal result, response:79](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:79) | The prior tuned-RF versus fixed-mixture deficits are not evidence about the new equally selected procedures. "The conventional baselines are tuned and the mixtures are not" is now stale; "do not favour the fixed mixtures" answers the old question. | Replace with the **three tuned contrasts**: k2-family minus RF, inclusive-family minus RF, and inclusive-family minus k2-family. Use the separately locked/refitted selected models on the same outer partitions, then average paired repeat effects within each dataset. Recompute accuracy, balanced accuracy, mean/median effect, intervals, W/T/L, and the new primary-family adjusted tests. Report each family's selection and refit costs. Do not retain the old deficits or predict the direction of the new results. |
| P1: [completion/results block, main:115](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:115), [response:73](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:73) | "855 ... in each ... stage" and "16,245" describe the older task organization. The old effects, depths, selection frequencies and costs throughout both generated results blocks also remain old evidence. | Replace the **entire generated numerical blocks**, not just the tuned comparison. Derive completeness, record counts, used dimensions and CV-fallback occurrences from the finished fair manifest. Require all 57 datasets x five outer splits, six fixed structures, every required bank/composition/count, and all three selected refits. Name the actual completed units; do not relabel old stage counts as fair completion. Do not merge old and fair repeats. |
| P1: [performance table, main:137](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:137), [comparison-table caption, main:165](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:165) | The table still includes the previous custom-greedy contrasts/tuned CART and "Holm-adjusted over all 15 rows". That conflicts with the new eleven-contrast plan. | Regenerate tables from fair records. Show k1/library CART, k2 and k3 where applicable, matched all/sqrt settings, and all three tuned families. Do not label old custom k1 controls or tuned single CART as new-protocol models. Primary inference uses **one Holm family of eleven**: eight T=100, q=10% (1,2)/(1,3) anchors at D=3/unlimited and all/sqrt, plus three tuned contrasts. D=6, single-tree and other grid contrasts remain descriptive under the stated plan. Caption each timing metric precisely. |
| P1: [depth-figure caption, main:244](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:244), [tradeoff caption, main:341](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:341) | Figures still encode old two-sighted/custom-control points and a tuned RF versus fixed mixtures. Changing prose alone leaves stale visual evidence. | Replace all plot coordinates, legends and captions. New fixed curves must identify T=20/40/60/100/200, horizon composition, depth, and feature setting; include k3, not only k2. Display matched controls at the same T. Distinguish fixed curves from the three training-selected families; selected T and D need not equal a panel's fixed T/D. The 200-tree points are **not tuned options**. Marginal accuracy bars are not paired-effect intervals or significance tests. Any aggregate 0.7-second reference remains descriptive, never a validated per-dataset budget. |
| P1: [Discussion results, main:347](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:347), [Conclusion, main:360](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:360), [rebuttal summary, response:81](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:81) | "Shallow benefit", "mean advantage shrinks", unrestricted-depth harm, and RF superiority are outcomes of the old stopping/bootstrap/tuning protocol, not established new conclusions. | Rewrite all outcome sentences from the completed fixed anchors and tuned contrasts. Treat uniform k2/k3, fixed sparse replacements, and selected candidate families as different questions. A favourable fixed shallow point does not establish superiority over tuned RF; an unfavourable old tuned-versus-fixed point does not establish tuned-mixture inferiority. Retain conditional benchmark scope regardless of direction. Replace the abstract's pending sentence with checked new outcomes only after completeness. |
| P2: [future budget paragraph, main:356](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:356), [R1.4, response:96](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:96) | A future experiment is described mainly as choosing depth/T/proportions from training data, which the new tuned experiment already does. | Replace the prospective requirement with **training-only selection that additionally enforces a prespecified per-dataset computation limit, charges selection cost, and verifies selected-refit feasibility before test evaluation**. Retain the historical explanation of why the old vertical slice was not such a policy. |
| P2: [response introduction:22](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:22), [timing correction, response:102](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:102) | The overview still mentions only "tuned conventional baselines" / "baseline selection cost", despite the correctly refreshed R1.1/R1.2. | Say **training-only selection for conventional RF and both sighted candidate families**, with matched unpruned common settings and repeated k1/k2/k3 evidence. State selection costs for **every family**, not merely the baseline. Finalize all section/table/figure references after replacement. The cover letter's scientific summary should receive the same eventual consistency update; its transfer preference needs no change. |

The refreshed Abstract/Introduction/Methods, R1.1/R1.2, R1.3 and stopping correction
are already materially improved. Do **not** reintroduce the superseded
"three-sighted only historical", "mixed learners remain fixed" or "custom k1 is
the primary control" wording. The old historical single-split data remain
excluded; the **new** repeated k3 data are included.

## Definition and provenance checks

- **Composition count is conditional on the frozen run.** [Main:89](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:89)
  asserts sixteen compositions and [main:91](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:91)
  asserts 768 inclusive candidates. [Protocol:61](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision_fair/PROTOCOL.md:61)
  makes the 85/10/5 triple optional. Verify the production manifest actually
  includes that frozen option. If absent, the scientific description is fifteen
  compositions / 720 inclusive candidates, with no triple result. RF=48 and
  k2-family=288 in either variant. Describe the executed approved variant; do not
  choose compositions after viewing results or modify the protocol here.
- **"Equally tuned" needs its explicit qualification.** The current shared-grid
  language in main:91 and response:64 is good: same folds, structural options and
  T<=100 access, not the same number of candidates, composition choices, training
  time or total resource budget. All-feature selections are bagging-like members
  of the RF candidate family, not necessarily sqrt-feature forests.
- **Selected family is not synonymous with heterogeneous forest.** Both sighted
  families include pure CART; the inclusive family also includes pure k2/k3 and
  (2,3) mixtures. Report selected T/D/leaf/features/compositions and how often
  selections are pure versus genuinely mixed. Calling all selected inclusive
  outputs "sparse mixed forests" would overstate what was selected. Candidate-set
  containment implies no lower best CV accuracy on shared records, not guaranteed
  improvement on outer test data or proof of a diversity mechanism.
- **Timing scopes must survive table compression.** Main:100 appropriately
  distinguishes constituent `fit` sums, construction/bootstrap preparation,
  direct refit wall time, prediction, family-attributed selection work and physical
  shared work. Do not put differently scoped values under one unqualified "fit
  cost" column or subtract shared banks from a standalone family's requirements.
  Follow protocol:127--144, including actual library RF refit wall time versus
  prepared-forest constituent sums. Stage-wall sums exclude startup/I/O/idle time;
  "end-to-end wall time" would be too strong without that qualification.
- **Matched means matching common settings, not identical internal algorithms.**
  Retain main:66 and response:103's numeric/tie caveats. The common seed and sqrt
  budget do not force identical per-node random feature orders. Describe gains as
  effects of the implemented induction rules under matched common settings, not
  an isolated causal effect of horizon with every internal detail held identical.
- **Verification claims need the retained gate reports.** Main:68 and response:103
  should describe exactly the tested RF-prefix/depth/leaf/rare-class fixtures.
  "Across all" must be backed by logs; a synthetic gate is not per-dataset proof
  that every production bank was separately compared against RF. This review did
  not run or inspect the production gates.
- **Full-horizon wording needs the feature restriction.** Main:63 is defensible
  only for the stated candidate/stopping/numerical conventions. Explicitly limit
  unrestricted feature-space optimality to the all-feature case. Sqrt-feature
  search is conditional on its per-node feature policy, not an optimum over all
  axis-aligned trees. Preserve the correct additive evaluation-count recurrence;
  it is not elapsed time or a guarantee of large-data tractability.

## Shallow literature

No blocking literature overclaim was found in [main:34](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:34),
[main:48](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:48)
or [response:53](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:53).
They already distinguish motivation from depth-three optimality, acknowledge the
different regression/leaf/resampling settings, retain deeper controls, and do not
substitute boosting evidence for independently fitted forests.

Two optional precision improvements should remain aligned between paper and R1:

- Qualify Zhou/Mentch's low-SNR predictive examples locally as **regression with
  terminal-node limits**, rather than letting "smaller trees" imply direct
  fixed-depth-three Gini-classification evidence. The cited record is the 2023
  issue of *Statistical Analysis and Data Mining*, with 2022 online publication,
  not *Stat*. [Publisher/DOI](https://doi.org/10.1002/sam.11594).
- Make Duroux/Scornet's resampling caveat explicit: the small-tree empirical
  construction also differs in resampling, so it is not a clean depth-only
  bootstrap experiment. Their theory concerns quantile regression forests and
  their empirical leaf-limited trees need not have eight leaves.
  [Published article](https://doi.org/10.1051/ps/2018008).

Preserve Scornet/Biau/Vert's controlled **growing** tree-size caveat. Their
regression consistency conditions do not establish fixed-D=3 classification
consistency, and unmet sufficient conditions do not establish inconsistency.
[Published article](https://doi.org/10.1214/15-AOS1321). Preserve the separation of
shallow single-tree classification evidence from forest evidence, and the fact
that eight leaves bound each member, not the forest's total prediction regions
or ensemble interpretability. Deeper forests can reduce underfitting and be
beneficial; D=6/unlimited and training-selected capacity must remain in the final
evidence regardless of whether a shallow anchor is favourable.

These checks reuse the retained `shallow_literature_audit.md` and its previously
verified primary-source records. No new bibliography search, applied-reference
addition, or citation invention was undertaken.

## Final-result release requirements

1. Complete and validate the entire frozen fair run before replacing submission
   claims. Until then, retain the working-draft notices; do not insert guessed
   result text or treat a completed fixed stage as completed tuned evidence.
2. Use the eleven frozen primary contrasts and the current mean/location
   distinction in main:105--107 and response:68. A positive unadjusted mean CI
   need not agree with a Holm-adjusted signed-rank decision; zero median and a
   nonsignificant test do not establish equivalence. Do not promote the best
   descriptive curve point to a new primary discovery.
3. Recompute family-weighted and constructed-task sensitivities from the same
   fair records and released subgroup definitions. Retain the task-dependence,
   overlapping-holdout and convenience-sample qualifications. Repeated use of
   this cohort is not fresh external or preregistered independent confirmation.
4. Keep outcome templates conditional until checked: **fixed-architecture effects
   under common capacity/stopping/feature settings** are separate from **outer
   performance of all three training-selected procedures**. Report uncertainty,
   selected-family composition and selection overhead, not an assumed shallow
   success, RF dominance or beneficial heterogeneity mechanism.
5. Regenerate prose, tables, figures, captions, rebuttal summaries and release
   references together. Remove the transition notices only then. Check no
   preceding-protocol custom controls, 855/16,245 completion claim, old 15-row
   adjustment, or old timing/result figures survive under a fair-results label.
   Confirm the public data/code statement at main:370 actually points to the
   released fair records and reproduction instructions; this audit did not
   verify the remote repository's publication state.

## Transfer preference

[Response:24](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/response_to_reviewers.tex:24)
and response:32, together with
[cover letter:21](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/cover_letter.txt:21),
already express the newest preference correctly: welcome the **possibility** of
transfer to a suitable journal with **no mandatory APC**, including a subscription
route, request confirmation of terms before consent, and acknowledge independent
assessment with no acceptance guarantee. Preserve this wording. Do not infer
that a particular receiving journal has agreed to waive a fee, that optional
paid OA is mandatory, or that transfer/acceptance is assured. No journal or fee
policy recommendation was made or verified here, and there is no scientific
reason to put the publication-route preference in the manuscript's Results.
