# Revision Following the Author's PDF Comments

10 October 2026. Author-edited working source: `main.tex`. No new fits,
test-set model selection, or numerical-result changes are part of this pass.
The annotated PDF is preserved, not overwritten or re-exported.

## Source and Scope

All 34 nonempty comments are embedded as highlight annotations in
`output/pdf/revised_manuscript.pdf`, pages 1--9. Its 34 popup objects are
companions to those highlights, not additional comments. Source SHA-256:

`1f8ded758b6970b6348424ff0bbcf50c270f28006c99f78fb60add8b3dd85723`

The new title is *A few farther-sighted trees can improve shallow forests*.
The title, abstract, introduction, results, discussion, conclusion, availability
statement, disclosure, highlights and editorial letters are revised together.
The existing native editor stays open. The response is a revision to Array,
not a simultaneous new journal submission.

## Comment-by-Comment Resolution

Numbers follow PDF page order and annotation order within each page. The
object number identifies the original comment even after pagination changes.

| No. | Page / object | Comment and resolution |
| --- | --- | --- |
| 1 | 1 / 413 | Replace "previously": removed the retrospective abstract qualification; the introduction calls the search principle well-studied. |
| 2 | 1 / 415 | Rewrite the story around the positive sparse-mixture result; read Tao's writing advice; reduce caveat repetition; request possible PRL transfer in both letters, subject to editorial approval and no-mandatory-APC terms. |
| 3 | 2 / 417 | Remove implementation-specific Cython discussion from the article. |
| 4 | 2 / 419 | Remove float precision and other low-level implementation detail; retain the scientifically necessary matched-control definitions. |
| 5 | 3 / 421 | Begin the data section with a tractable 57-dataset PMLB sample. |
| 6 | 3 / 423 | Remove old-protocol comparisons from the manuscript's experimental description. |
| 7 | 3 / 425 | Replace literal seed values with fixed, reproducible seeds that differ across repetitions. |
| 8 | 3 / 427 | Explain RF plainly: only greedy members; feature policy is tuned, with all-feature bagged CART as one option. |
| 9 | 4 / 429 | Remove checkpoint/recovery/completion execution narrative. |
| 10 | 4 / 431 | Remove certificate and provenance-verification discussion from the article. |
| 11 | 4 / 433 | Remove the library-warning explanation; retain the definition of balanced accuracy. |
| 12 | 4 / 435 | Replace bank/schedule jargon with a short explanation of the full tree-fitting work needed for each candidate grid. |
| 13 | 4 / 437 | Remove the long AI/runtime paragraph. A brief plotting-code attribution remains in Methods because Elsevier specifically requires Methods disclosure for AI-assisted data visualization; see the policy note below. |
| 14 | 4 / 439 | Remove native-PGFPlots implementation discussion from visible text. |
| 15 | 4 / 441 | Remove the historical contrast-freezing narrative; retain the actual eleven-contrast testing definition. |
| 16 | 4 / 443 | Explain the nonsignificance/equality distinction once, in ordinary language, in the limitations subsection. |
| 17 | 4 / 445 | Remove execution counts and completion narrative from Results; open directly with the tables and measured outcomes. |
| 18 | 5 / 448 | Discuss overfitting as a plausible explanation for deeper unrestricted all-feature trees with lower test accuracy, rather than asserting a measured causal mechanism. |
| 19 | 6 / 450 | Remove the repeated equivalence warning from Results. |
| 20 | 7 / 452 | Remove the unnecessary "all" in the selected-family description. |
| 21 | 7 / 454 | Remove the end-to-end warning from Results; define the workflow timing scope once in Methods. |
| 22 | 7 / 456 | Consolidate interpretive qualifications under Discussion / Scope and limitations. Operational definitions remain in Methods and captions remain precise. |
| 23 | 8 / 458 | Emphasize the positive tuned mean effect and its mean-effect interval after fairly tuning the conventional baseline. |
| 24 | 8 / 460 | Remove "previously explored" from Discussion. |
| 25 | 8 / 462 | Use "rather small" for the sample. |
| 26 | 8 / 464 | Remove the repeated preprocessing/fallback/grid list from Discussion; factual protocol stays in Methods. |
| 27 | 8 / 466 | Remove the threshold/tie/bitwise-identity qualification from Discussion. Preserve candidate counts and measured selection costs needed to interpret the comparison. |
| 28 | 9 / 468 | Replace the future instruction to the author with a responsibility statement, without claiming author approval has already occurred. |
| 29 | 9 / 470 | State that sparse replacements consistently yielded higher observed benchmark-mean accuracy across the tested depth-three settings; consistency concerns the observed configuration means, not every dataset or significance of every contrast. |
| 30 | 9 / 472 | Strengthen the conclusion with the verified lower-work/higher-mean-accuracy example. Do not call it proof of exact equal-time superiority or of a prospective per-dataset budget policy: neither was tested. |
| 31 | 9 / 474 | Remove historical-table commentary from Data and code availability. |
| 32 | 9 / 476 | State that figures use experimental results without generative image tools; remove the unrecorded-model/version explanation from manuscript prose. |
| 33 | 9 / 478 | Remove the redundant sentence referring back to the deleted long Methods disclosure. |
| 34 | 9 / 480 | Check every reference's existence, metadata, cited use and relevance against primary sources; findings in `annotation_reference_audit_1.md` and `annotation_reference_audit_2.md`. Final citation-key closure is checked after integration. |

## Verified Figure 2 Examples

All values below come from the unchanged full `summary.csv`, depth three,
all features, equal-dataset means of five repetitions. They are illustrative
fixed-grid comparisons, not additions to the eleven-test primary family.

| Composition | Members | Mean accuracy | Mean member-fitting work (s) |
| --- | ---: | ---: | ---: |
| 75% greedy / 25% two-sighted | 20 | 0.74063578 | 0.095460218 |
| 90% greedy / 10% two-sighted | 20 | 0.733727 | 0.047004 |
| Pure greedy | 200 | 0.73020360 | 0.13382638 |
| Pure two-sighted | 20 | 0.74790382 | 0.33813378 |

The first mixture exceeds the 200-member greedy mean by 1.043218 percentage
points with 28.6686% less mean fitting work. The pure two-sighted 20-member
forest remains the highest-accuracy observed point below the 0.7 s reference.
The manuscript states both results, rather than claiming that mixing dominates
every pure alternative.

## Writing and Disclosure

Tao's [writing index](https://terrytao.wordpress.com/advice-on-writing-papers/)
and its advice on [foregrounding the result](https://terrytao.wordpress.com/advice-on-writing-papers/use-the-introduction-to-%E2%80%9Csell%E2%80%9D-the-key-points-of-your-paper/),
[accurate claims](https://terrytao.wordpress.com/advice-on-writing-papers/describe-the-results-accurately/),
[appropriate detail](https://terrytao.wordpress.com/advice-on-writing-papers/give-appropriate-amounts-of-detail/),
[organization](https://terrytao.wordpress.com/advice-on-writing-papers/organise-the-paper/),
and [individual voice](https://terrytao.wordpress.com/advice-on-writing-papers/write-in-your-own-voice/)
informed this pass. The advice is used as an editorial guide, not copied into
the article or treated as scientific support for its findings.

Elsevier's [AI policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)
was checked on 10 October 2026. It requires Methods disclosure when AI assists
data-visualization code. The concise attribution is retained there and the
general declaration states the purposes of assistance. No generative image
tool was used. The author still needs to approve the scientific content and
applicable disclosures before submission; the policy's version-documentation
requirements cannot be satisfied by inventing an unavailable historical model
identifier. The article does not claim that human review has already happened.

## Validation

- Native compilation passed for the manuscript after the integrated reference
  corrections, and for the revised point-by-point response. No separate PDF
  was exported and the annotated review PDF was not overwritten.
- Benchmark sources, checkpoints, statistical outputs and immutable retained
  bundle are not edited or rerun.
- Preservation checks against pre-annotation commit `fbd1f933` passed: all
  three numerical plot blocks are byte-identical, and the numeric cells of
  all 27 performance-table rows and eleven comparison-table rows are unchanged.
- Citation closure passed: 32 unique bibliography entries, all cited, with
  no undefined or unused inline bibliography keys. The five highlights have
  73, 76, 68, 79 and 71 characters including their bullet and space.
- The annotated PDF retains its original SHA-256 above and all 34 comments.
- A read-only arithmetic check of the retained summary confirms positive
  observed mean differences for all 40 sparse 5%/10% replacements at depth
  three (two horizons, two feature policies and five ensemble sizes). This
  is a descriptive sign check, not new inference or independent replication.
- The previous 9 October source-review hashes remain historical records;
  they do not certify this later edit. The native PDF preview is the current
  reading copy, while the annotated disk PDF is the preserved review input.

## Reference Corrections and Access Limits

Both halves of the reference audit check existence, metadata, cited relevance
and substantive support using the primary records or clearly identified author
versions and archival facsimiles. The reports preserve exact access limits.
Full original bodies were not obtained for Ragavan--Rendell (1993) and
Elomaa--Malinen (2005); their limited manuscript uses are corroborated by
primary metadata, author accounts or abstracts. Several other final publisher
PDFs were unavailable; available author versions are identified, not presented
as final-edition text. The TMLR accepted-paper index authenticates its 2026
entry despite the inaccessible final OpenReview PDF.

Hu et al. (2019) is now cited as the official electronic NeurIPS paper with
its URL and no unverified page range, rather than silently substituting a
different printed edition's pagination. Aghaei et al. retains the 2025 issue
year and now identifies its 2024 first-online date. Duplicate article numbers,
a missing issue number, and the Norouzi proceedings link are corrected.
Norton's root-commitment precedent and Esmeir--Markovitch's non-greedy ensemble
and resource-allocation precedent are now explicit. Scornet's author-hosted
reprint header confirms its journal metadata. No optional DOI is added to
Holm's sufficient stable archival citation; the second audit records the
authenticated association and remaining access limits.

These checks establish bibliographic existence and bounded cited support;
they do not certify every result in every unavailable final full text.

## Final Reviewed Sources

The two internal scientific/editorial passes and their resolutions are
documented in the reference-audit reports. Both reviewers agree on the final
manuscript hash below, with no residual material issue in their review scopes.
The second reviewer identified a
minor Figure 2 sentence ambiguity: 73.37% belongs to the 20-member mixture,
not the 200-member greedy comparator (73.02%). The sentence now attaches the
score explicitly to the mixture. No number or plotted coordinate changed.
These AI-assisted reviews are not external peer review or author approval.

Final manuscript SHA-256:
`4c31ad499b8bcc2c926b5d84c057757c1a82610be9084e8d9c599aad3752d01e`

Final response SHA-256:
`52030f40f2a1949bf88d70c404171e4a7b2eccbcdb40f51cfdb773122f0affd5`

Both sources passed the native compiler after the last manuscript correction.
The final author approval and submission/transfer consent remain outstanding.
