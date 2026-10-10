# Revised Submission Assets

These files describe the complete matched and training-selected evaluation,
not the superseded PRL or first repeated protocol. The author's substantive
review and approval are required before upload. No submission has been made.

- `main.tex`: existing two-column manuscript, compiled in the native editor.
- `response_to_reviewers.tex`: completed point-by-point response, including the
  Reviewer 2 verification request and no-mandatory-APC transfer preference.
- `cover_letter.txt`: editable revision letter; sole-author list unchanged.
- `highlights.txt`: five editable bullets, each below 85 characters including
  its leading bullet and space.
- `graphical_abstract_fair.pdf`: vector statistical summary, 13.28 x 5.31 cm.
- `graphical_abstract_fair.tiff`: LZW-compressed, 1568 x 627 pixels at 300 dpi,
  exceeding the previously specified 1328 x 531 pixel minimum proportionally.
- `graphical_abstract_fair.png`: corresponding inspection image, not required
  instead of the preferred PDF/TIFF submission file.
- `graphical_abstract_fair.json`: input hashes, protocol identity and scope.

The graphical summary uses the two tuned-family contrasts against selected
RF, their pointwise mean-effect intervals, and all three families' selection
constituent-fit work and direct-refit wall times. The families may select pure
forests. This is not an equal-budget comparison, and the intervals are not
confidence intervals for the adjusted signed-rank tests. The caption should
preserve those distinctions, for example:

> Training-selected forest families on the complete repeated benchmark.
> Family 1/2 allows horizons one and two; Family 1/2/3 allows all three,
> including pure forests. Mean accuracy differences use pointwise, unadjusted
> dataset-bootstrap intervals. Selection work and final refit wall time have
> different measurement boundaries. Prepared from retained numerical results
> using Matplotlib 3.10.9; no generative-image artwork was used. AI assistance
> with plotting code is disclosed in the manuscript.

## Retrieval and Regeneration

After restoring the full retained bundle according to
`../REPRODUCING_RESULTS.md`, run from the repository root:

```sh
.venv310/bin/python -B paper/scripts/make_fair_graphical_abstract.py --out /tmp/fair_full_retained --destination /tmp/fair_graphical_summary
```

The script validates complete retained tables and hashes, does not fit models,
and does not edit the manuscript or immutable results bundle. It checks text
boundaries and principal-label overlap before writing the vector and raster
files. The final PDF was independently rendered for visual inspection; its
single-page size and raster dimensions were checked.

This is a directly data-derived statistical visualization generated through
reproducible Matplotlib code, not output from a generative image model. There
is no third-party illustration or icon material. Codex assisted with the code;
that assistance and the remaining author-review requirement are disclosed.
Elsevier's [current AI/artwork policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)
was checked on 9 October 2026. It permits reproducible, data-derived
visualization assistance, while excluding general-purpose generative-image
tools for graphical abstracts. This document does not certify portal-specific
requirements or replace the author's confirmation of applicable journal rules.

The native compiler confirms compilation but does not export a disk PDF.
The author's annotated `output/pdf/revised_manuscript.pdf` is the review copy
exported on 9 October, not the subsequent author-comment revision. Preserve
it; read the current revision in the existing editor's compiled preview.
