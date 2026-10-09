# Second Sequential Manuscript Review

9 October 2026. Internal expert-tree/methods/editorial review, not a journal
editorial decision. **Accept internal scientific readiness after the corrections
below, subject to Mathias Valla's author gate and the agreement cycle. No remaining
actionable P1/P2 scientific or numerical blocker was found.** This is not approval
to submit without the author's review and consent, or a prediction of acceptance.

## Findings and Disposition

- **P2, resolved: distinguish the verification scopes in the article itself.**
  [main.tex:98](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:98)
  now distinguishes bank-probability/constituent-cost reconstruction and independently
  reconstructed CV winners from range/checkpoint-only single-tree and selected-refit
  scores. The response already made this distinction. The CART-bank harness is now
  explicitly a controlled check with absolute tolerance 1e-12 and zero relative
  tolerance, not evidence of identity between CART and farther-sighted trees.
- **P2, resolved: feature and comparator descriptions were underspecified.**
  [main.tex:67](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:67)
  states the initial floor-sqrt feature count and admissible-partition fallback;
  it does not imply a hard inspection cap or identical random-feature ordering.
  [main.tex:92](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:92)
  and the Results identify the actual library RF family, including all-feature
  bagged CART. This preserves the validated standard-library comparator without
  relabeling every selected configuration as conventional feature-subsampled RF.
- **P2, resolved disclosure omission; documentary limitation remains explicit.**
  [main.tex:107](/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/paper/array_revision/main.tex:107)
  now discloses OpenAI Codex, developer OpenAI, code/visualization assistance,
  data-derived rendering, and the unrecorded tool version/model identifier.
  Python and library versions remain in the protocol/environment records and
  full-analysis certificate; no version or human approval was invented.
  This follows the Methods-disclosure requirement in the
  [official Elsevier policy, updated June 2026](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals).
  Honest disclosure of unavailable identifiers is not a guarantee that a receiving
  journal will waive further documentation. The author must resolve that question.

Also clarified the training-only, hardware-dependent included-member fit-work
tie-break; replaced ambiguous "equally tuned" response wording with matched-grid
selection; specified pointwise 95% mean intervals in Figures 1 and 3; and made the
Introduction's tuned question explicitly about mixed-capable selection families.
No numerical result, comparison family, model choice, or experimental scope changed.

## Evidence Checked

Read the entire assembled manuscript and response, including abstract, bibliography,
native PGFPlots code/captions, endmatter and all current full-results fragments.
Used the complete `paper/array_revision_fair/analysis/full` exports, protocol,
adapter description, prior independent full numerical audit and retained literature
audits. No duplicate literature investigation or production analysis was performed.

- All fourteen certified numerical/protocol artifact hashes match the current v2
  certificate. Analyzer source SHA256 remains
  `f3076f010500f10e56cfa9815aa55190fff356f6a4827156536c45e9bd72c67b`;
  protocol fingerprint remains
  `d8999e02a5ad8a1398996fd3c851f5a68fd17d697f37cd048e2258a418475d7b`.
- Independently checked all 27 Table 1 rows, including all 108 score/cost/depth
  cells, and all eleven Table 2 means, interval endpoints, Holm values, W/T/L and
  cost ratios against the full CSVs at displayed precision. No discrepancy found.
  The near-zero unrestricted sqrt/k3 interval endpoint remains 0.00047 percentage
  points. The family-weighted inclusive lower bound correctly rounds to -0.27.
- Checked all 160 native Figure 2 curve coordinates against the full summary;
  Figure 1's means/interval widths and nine costs; and Figure 3's three mean/interval
  pairs and nine cost coordinates. Captions now identify mean-effect intervals,
  descriptive versus primary status, feature scope, and distinct timing boundaries.
- Rechecked all eleven raw signed-rank p-values and their single joint Holm
  adjustment from the dataset deltas, using the retained SciPy convention:
  12-decimal rounding, `zero_method=wilcox`, `method=auto`, all-zero p=1.
  The earlier full audit independently reconstructed mean intervals, sensitivities,
  repeat-first means and every inner winner; its certified numerical inputs are
  unchanged. No extra tests or adaptive contrasts were introduced here.
- Recounted the 855 selected-family rows: 57 datasets and every seed 1000--1004
  in each family. Inclusive selections are 133 pure and 152 actual mixtures;
  the k2-capable family selects 168 pure and 117 mixtures. Depth and feature
  counts agree with the narrative. All recorded workflow component sums agree.
- The positive inclusive mean, +1.57 points [0.30, 3.28], is correctly retained
  alongside median zero and Holm p=0.48838. This is not equivalence, a rejected
  mean benefit, or proof of improvement on a typical future task. The 48-family
  and 38-task sensitivities attenuate the effect and cross zero. No sparse-mixing
  causal attribution, robustness guarantee, or algorithmic-priority claim remains.
- Common structural/count grids and training folds are shared, not candidate-space
  size or computation. Required discarded bank work is charged; standalone family
  charges must not be summed as physical work. The 206.61x inclusive refit ratio
  is not its approximately 1175.94x selection-fit-work ratio. Fixed constituent
  fit sums, direct refit wall times, and workflow-stage sums remain distinct.
- The 0.7-second line is explicitly retrospective benchmark-mean comparison, not
  test-driven deployment selection, per-dataset feasibility or an evaluated
  interpolated model. Pure k2/T20 is correctly identified as the highest observed
  mean below that line; sparse superiority is not asserted.

The local Gini recurrence, root-only commitment/restored horizon, depth-bounded
special case and candidate-evaluation bound are appropriately qualified. Shallow
citations motivate conditional tree-size regularization, not a depth-three default,
fixed-depth consistency or transfer of boosting evidence to bagging. Limitations
cover previous cohort exploration, benchmark dependence, rare classes, encodings,
finite grids, implementation differences and unequal computation.

## Synchronization and Author Gate

Edits are limited to `paper/array_revision/main.tex`,
`paper/array_revision/response_to_reviewers.tex`, and the allowed full-results
fragments `results_text.tex` and `abstract_suggestion.tex`, plus this review.
The latter now preserves the parent's actual higher-mean/heterogeneity abstract.
Results narrative and Figure 3 caption match their fragment; table, discussion,
conclusion and response-results fragments remain consistent. Native figure/table
insertion is intentionally different from the include-ready fragment wrappers.
Future inlining must preserve the new Methods paragraphs and native captions.

Both current standalone sources compiled successfully with the desktop compiler;
the final main source was compiled again after the last correction. Source citation
keys and cross-references resolve. This pass checks native plot data and captions,
not final rendered-page visual QA; the author/parent must inspect the final PDFs.

The response politely requests verification of the unrelated LogBERT report,
does not attribute blame, requests a suitable no-mandatory-APC transfer with terms
confirmed before consent, and expressly disclaims acceptance guarantees. Mathias
Valla remains the sole author. Do not replace the endmatter's pending author-review
statement with a claim of completed human review until it is true. Before actual
submission, the author must approve the scientific interpretation and disclosures,
verify the released reproducibility links/assets and receiving-journal terms,
inspect the final typesetting, and complete the requested agreement cycle.
Any graphical abstract requires its own policy/source check; none is approved here.

No fits, production analyzer runs, algorithm/protocol/certificate changes,
analytical figure regeneration, publication actions or commits were performed.
Numerical checks were read-only and in memory; neither the algorithm nor its
certified results were regenerated. Figure edits were confined to the permitted
manuscript captions, not plotted values or analytical assets.

## Final Agreement on the Current Version

9 October 2026. Read `full_writer_final_review.md` and checked the corrected
main/response passages and three matching fragments. **Agree with Mencius:
accept current internal scientific readiness, with no unresolved P1/P2 blocker.**
"38 tasks outside the named synthetic/constructed set" correctly describes the
frozen complement without asserting that all retained tasks are non-synthetic.
Earlier shorthand in this review is not an exhaustive provenance classification.
Membership, estimands and inference are unchanged.

Current main SHA256 is
`efef6b005c2a9fd0d5e289d66271ac7c150478226ea26be781a1251b40e741f3`;
response SHA256 is
`6ea6238878c3cd2da7684cb54c05d849a3a09619f5821c7ddd2e45eaec985fc4`.
Both match the writer-reviewed snapshot. The certificate also matches that
snapshot, all fourteen certified artifact hashes verify, and the corrected
fragment contracts pass. This follow-up performed no fits, new statistical
calculations, compilation or source edits; only this agreement was appended.

These are two internal AI-assisted expert passes, not journal acceptance or
completed human author approval. All author, release, final rendered-page,
policy-documentation and transfer-consent gates above still stand. Parent's
final native compilation/tests and documentation staging remain separate.
