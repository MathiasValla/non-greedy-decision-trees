# Array Revision Submission

Prepared on 12 October 2026 for **ARRAY-D-26-03529**, due **26 October 2026**.

**Title:** A few farther-sighted trees can improve shallow forests

**Sole and corresponding author:** Mathias Valla, Chaire DIALog, Institut Louis
Bachelier, Paris, France; mathias.valla@gmail.com.

The manuscript preserves the author's final edits, with the brief Methods AI
disclosure restored with explicit permission. The scientific text, figures,
numerical tables, and experimental design have not been regenerated. The
annotated October review PDF is preserved separately and is not in this packet.

## Upload Files

Upload the individual files using the item types available in the revision
portal; the outer packet ZIP is a convenience for retrieval, not a single
manuscript upload.

| Purpose | File |
| --- | --- |
| Clean revised manuscript | `output/pdf/revised_manuscript.pdf` |
| Editable LaTeX manuscript and class | `manuscript_source.zip` |
| Point-by-point response to editor and reviewers | `output/pdf/response_to_reviewers.pdf` |
| Editable response source | `response_to_reviewers.tex` |
| Cover letter | `cover_letter.docx` or paste `cover_letter.txt` |
| Separate editable highlights | `article_highlights.docx` |
| Plain-text highlights backup | `highlights.txt` |
| Existing data-derived graphical abstract, if requested | `graphical_abstract.tiff` |

The main source embeds all three figures, both tables, and the bibliography.
No additional image or BibTeX file is needed to compile it. The source ZIP
contains no reviewer response or internal audit files. Do not upload the
older `Fig1_depth_sensitivity.pdf` or `Fig2_accuracy_cost.pdf`: they belong to
a superseded protocol. No annotated PDF, auxiliary file, build log, or raw
checkpoint is included in this submission packet.

## Final Portal Checks

- Associate the upload with the existing revision, not a new submission. Keep
  the sole-author list unchanged and update the title in the portal if needed.
- Read the portal's assembled PDF and check all pages, figures, tables,
  references, affiliations, declarations, and highlight formatting.
- The response politely asks the editor to verify Reviewer 2's apparent
  manuscript mismatch. It does not assume why the report was attached.
- Both letters request consideration of a suitable no-mandatory-APC transfer,
  including a subscription route. They disclose the earlier PRL rejection;
  reconsideration would require receiving-editor agreement. No transfer,
  publication fee, acceptance, or receiving-journal eligibility is guaranteed.
- The end-of-article AI declaration is retained. The Methods statement names
  OpenAI Codex and OpenAI, and explicitly notes that historical application
  and model versions were not recorded. Do not invent those identifiers; if
  the editor requires further documentation, obtain it where available.
- Confirm the portal's required declarations and any marked-up-manuscript
  requirement. This packet supplies a clean revision and detailed point-by-point
  response; it does not substitute the author's annotated review PDF for a
  journal-requested marked revision.
- No submission has been made or editor contacted. Submission and any later
  transfer require the author's own approval and action.

## Evidence and Checks

The article uses the complete fair evaluation: 57 datasets, five paired outer
partitions, 142,785 model-score records, and one eleven-contrast Holm adjustment.
No new fitting or change to the frozen experiment is needed for this export.
Code, complete results, and retrieval/reproduction instructions are available at
[the project repository](https://github.com/MathiasValla/non-greedy-decision-trees),
especially `paper/REPRODUCING_RESULTS.md`.

`submission_manifest.json` records source and asset SHA-256 hashes, compiled
page counts, highlights lengths, citation closure, and evidence identity.
The two PDFs were compiled from copied current sources, not older assemblers.
The existing native editor remains on `paper/array_revision/main.tex`.

The official [Array Guide for Authors](https://www.sciencedirect.com/journal/array/publish/guide-for-authors)
was checked again on 12 October but returned HTTP 403 to automated access.
The packet uses the existing two-column Elsevier class and the supplied
editorial revision instructions; it is not a certification of every live
portal constraint. The accessible [Elsevier AI policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)
informs the restored disclosure. Five editable highlights each meet the
85-character maximum, including their bullet and space.
