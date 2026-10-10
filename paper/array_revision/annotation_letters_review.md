# Annotation Letters Review

## Scope

Read the current `main.tex` first, then all 34 comments by Mathias VALLA in
`output/pdf/revised_manuscript.pdf`. Edited only `response_to_reviewers.tex`
and `cover_letter.txt`; this report is the third permitted write file. No
manuscript, PDF, figure, benchmark, README, commit, or push was changed by this
work. The annotated PDF was read, not overwritten.

## Changes

- Both letters use "A few farther-sighted trees can improve shallow forests"
  and explicitly describe the substantial improvement in evidence and writing.
  They follow the positive shallow-forest storyline, with reduced execution
  detail and limitations located in manuscript Section 6.1.
- R1's matched-depth/no-pruning controls, supportive conditional shallow-tree
  literature, tuning on both sides, candidate-count/cost differences, repeated
  paired analysis, and numerical/statistical qualifications are retained.
- Figure 2 now leads with 15 CART + five k=2 members at T=20: accuracy
  0.74063578 and fitting work 0.095460218 s, versus 0.73020360 and
  0.13382638 s for 200 greedy members (+1.043218 percentage points,
  28.6686% less work). The 18 CART + two k=2 example and the pure-k=2
  highest observed point below the 0.7 s reference remain. The text specifies
  benchmark means, member-fitting-only cost, no exact equal-time proof, and
  no validated per-dataset budget policy.
- R2 remains a polite request to check an apparent report mismatch, without
  attributing its cause or inventing responses to an unrelated telecom study.
- Both letters specifically request editorial guidance on PRL transfer or
  reconsideration, disclose the earlier decline, and require receiving-editor
  agreement and confirmation of a no-mandatory-APC route (including
  subscription) before consent. Neither letter authorizes transfer, makes a
  new/simultaneous submission, or implies acceptance.
- No human approval, AI model/version record, new experiment, or exhaustive
  reference-verification claim has been invented. Reference-audit and
  manuscript-wide annotation work remain outside this letters-only scope.

## Verification

- Native desktop LaTeX compilation succeeded. The response source was opened
  through the native editor; no PDF export was created or replaced.
- Figure 2 arithmetic independently checks to +1.043218 percentage points
  and 28.6686093% less member-fitting work; the letters use matching rounding.
- `git diff --check` passed. Current manuscript title, section numbering,
  matched-control/tuning definitions, and result summaries were rechecked.
- The annotated PDF and the two existing revision figure PDFs retain their
  pre-edit SHA-256 values. Concurrent parent edits to the manuscript and
  READMEs were observed and left untouched; this work's writes remain limited
  to the two letters and this report.

## Parent Considerations

- Confirm the receiving editor is willing to consider the substantially
  revised study despite PRL's earlier decline; no transfer has been initiated.
- Obtain applicable publication terms and explicit author consent before any
  transfer. The letters request a no-mandatory-APC route; they do not assert
  that current journal terms or eligibility have already been confirmed.
- Keep the annotated PDF intact. Manuscript-wide reference checking (comment
  34) and any submission-asset/title synchronization are separate parent work;
  this review does not certify those tasks as complete.

## Parent Integration

The parent shortened the transfer request in both letters while retaining the
earlier PRL rejection, receiving-editor agreement, confirmation of a route
without a mandatory APC, and author consent. Other suitable journals are
explicitly welcome. The parent also corrected the quantile-split terminology,
noted the resampling difference in the shallow-tree reference, labeled the
285 selections as outer dataset-repetition selections, and expanded the R1
prior-art response to include Norton and Esmeir--Markovitch. The revised
response compiled successfully through the native compiler after these edits.
