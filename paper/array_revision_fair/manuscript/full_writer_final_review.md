# Final Writer Scientific Review

9 October 2026. Internal scientific/editorial review, not a journal decision.

## Disposition

**AGREE with Lagrange on internal scientific readiness, after the terminology
correction below. No unresolved actionable P1/P2 scientific or numerical issue
was found.** Author approval remains required. This is neither authorization to
submit nor a prediction of acceptance. The small post-Lagrange wording change
is available for his acknowledgement in the final agreement cycle.

## Correction Made

The manifest's `named_synthetic` field marks 19 explicitly named
synthetic/constructed tasks; its complement contains 38 tasks. It is not an
independent, exhaustive provenance taxonomy. Replaced "named non-synthetic"
wording with "38 tasks outside the named synthetic/constructed set" in the
Results and Discussion of `main.tex`, the results block of
`response_to_reviewers.tex`, and the matching `results_text.tex`,
`discussion_text.tex`, and `response_results.tex` fragments.

Methods already describes the exclusion correctly and was not changed.
Membership, scores, intervals, tests, tables, plot coordinates and frozen
analysis artifacts were not changed. Historical audit shorthand and frozen
export field names remain untouched; they must not be read as a guarantee that
every retained task is naturally occurring. Hash checks confirm that these
six wording replacements are the only changes to the five existing sources.

## Scientific Checks

- **Inference is correctly qualified.** The inclusive selected family's
  +1.5693-point mean and pointwise interval [0.2991, 3.2767] coexist with median
  zero, 28/11/18 wins/ties/losses and joint Holm p=0.48838. The mean interval and
  signed-rank location test address different estimands. The text neither
  discards the mean benefit nor claims equivalence, a negligible effect, or
  reliable improvement on a typical future task. Family-weighted and named-set
  exclusion intervals cross zero. All eleven primary contrasts use the joint
  adjustment; remaining grid comparisons are descriptive.
- **Selection and capacity are not conflated with mixing.** The inclusive
  family selects 133 pure forests and 152 actual mixtures; the one-/two-sighted
  family selects 168 pure forests and 117 mixtures. Depth counts and both
  feature policies agree with the retained selections. RF denotes the library
  candidate family, including all-feature bagged CART, not exclusively
  square-root-feature forests. The initial floor-sqrt feature subset and
  admissible-partition fallback are explicit, without claiming identical
  random-feature ordering across implementations.
- **Timing boundaries and tie-breaking are accurate.** Fixed fit-only and
  constituent-fit-work measures, standalone cross-validation work, direct refit
  wall times and sums of workflow stages remain distinct. The inclusive
  family's 2671.049-second selection fit work is not its 12.9374-second refit;
  the RF counterparts are 2.271 seconds and 0.0626 seconds. Workflow sums are
  not uninterrupted end-to-end times. The training-only tie-break uses mean
  included-member fit work, is hardware dependent, and is neither an equal
  computation budget nor an intrinsic complexity bound.
- **Verification claims respect the certificate.** Bank forest predictions,
  selected-slot cost sums and inner winners are reconstructed. Single-tree
  and selected direct-refit scores receive range/checkpoint-consistency checks,
  not independent prediction reconstruction. Provenance checks are not an
  independent replication of the experiment.
- **Algorithm and literature claims remain bounded.** The additive local-Gini
  recurrence, root-only commitment, restored horizon and depth clipping are
  correctly distinguished from final tree depth and global prediction
  optimality. The candidate-evaluation bound is not a whole-run cost formula.
  Established lookahead work is acknowledged without priority claims. The
  shallow-tree literature motivates conditional size regularization, with
  regression, leaf-cap and growing-tree caveats; it does not establish a
  universal depth-three default, fixed-depth consistency or a boosting-to-
  bagging justification. Deeper RF controls and their benefits remain visible.

## Numerical and Assembly Checks

All fourteen certified CSV/protocol artifact hashes match the full certificate.
Checked all 27 performance rows (108 score/cost/depth cells), all eleven primary
comparison rows, and the 855 selected records against the complete exports.
Checked Figure 1's effects, intervals and nine costs; Figure 2's 16 curves at
five observed sizes in both panels (160 coordinate pairs), including the 80
right-panel markers; and Figure 3's effects, intervals and nine cost coordinates.

Figure 2 correctly identifies pure k2/T20 as the highest observed mean below
the 0.7-second benchmark-mean reference. Neither the figure nor its immediately
following discussion asserts a prospective budget policy, per-dataset
feasibility, an evaluated interpolated model or universal sparse-mixture
dominance over smaller pure forests.

The seven full-results TeX fragments and assembled narrative/tables agree;
native figure insertion intentionally replaces the fragment wrapper. Main has
two native tables and three native plots, unique labels, resolved source
references/citation keys, and no external duplicate plots or stale running-result
prose. The abstract has no numerical results. Both current standalone sources
compiled successfully with the desktop compiler after the wording correction.
This does not replace final rendered-page visual inspection by the author.

These were read-only checks of retained exports and source representations, not
new fits, analyzer runs, bootstrap generation, hypothesis testing or analytical
asset regeneration. Lagrange's independent statistical reconstruction is
documented in his review; no new independence claim is made here.

## Submission Materials and Author Gates

Read-only cover/highlights checks found no broader priority, production or
acceptance claim. All five highlights meet the checked 85-character limit. The
transfer request correctly specifies a suitable no-mandatory-APC route, with
terms confirmed before consent. The unrelated-report query is appropriately
polite and the sole-author list is unchanged.

The graphical summary's retained inputs/provenance agree with the certified
results. Its existing PNG and source show direct data-derived Matplotlib
graphics, not generative-image artwork. AI assistance with code is disclosed.
Methods honestly says the historical Codex tool version/model identifier was
not recorded; current app identifiers cannot repair historical provenance.
The [official Elsevier policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)
distinguishes reproducible data visualizations from generative-image use and
requires disclosure of research coding assistance. This check is not a blanket
policy-compliance determination or a receiving journal's waiver of missing
identifiers. The author must confirm its documentation and graphical-summary
requirements, approve all interpretations/disclosures, verify public release
links, inspect final typesetting and consent to any transfer or submission.

Only the five TeX sources named above and this review were written in this pass.
No runner, runtime, core, protocol, numerical output, design asset or submission
document was changed. No publication action was taken.

## Reviewed Snapshot

SHA256 after the terminology correction:

- `main.tex`: `efef6b005c2a9fd0d5e289d66271ac7c150478226ea26be781a1251b40e741f3`
- `response_to_reviewers.tex`: `6ea6238878c3cd2da7684cb54c05d849a3a09619f5821c7ddd2e45eaec985fc4`
- Full `validation.json`: `025cfac98f563b0960d83db5d4cd78ed420f311b496b476a26366fe1492d759a`
- Lagrange's `full_manuscript_review.md`: `394e154b581d9286b44ac1f8c52cce5567a5a602073a715a410c5060bc0752c9`
- Protocol fingerprint: `d8999e02a5ad8a1398996fd3c851f5a68fd17d697f37cd048e2258a418475d7b`
- Analyzer source SHA256: `f3076f010500f10e56cfa9815aa55190fff356f6a4827156536c45e9bd72c67b`
