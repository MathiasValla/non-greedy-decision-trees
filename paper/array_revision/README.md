# Array Revision: ARRAY-D-26-03529

Prepared for the author's revision due **26 October 2026**. The response requests
the possibility of an appropriate transfer offering publication without a
mandatory APC, with publication terms confirmed before agreement. It also
politely asks the editor to verify Reviewer 2's apparent manuscript mismatch.
Nothing is submitted and no editor/reviewer is contacted by these scripts.

**Complete numerical revision; author approval still required.** The matched
extension including three-sighted members, equally tuned conventional and
mixed-capable families, and complete forest-size curves finished on
9 October 2026. It is separately versioned under `paper/array_revision_fair/`,
with portable evidence in `paper/array_revision_fair_exports/full/`. The current
manuscript and response use these checked full results. The preceding 855+855
task records stored in this directory are historical and must not be reused
as the final fair-tuning evidence.

## Working Source Files

- `main.tex`: revised two-column Elsevier manuscript, open in the native editor.
- `response_to_reviewers.tex`: editable point-by-point reply.
- `cover_letter.txt`: editable cover letter.
- `Fig1_depth_sensitivity.pdf`, `Fig2_accuracy_cost.pdf`: preceding-protocol
  figures, not the final fair-comparison figures.
- `highlights.txt`: updated, editable five-bullet highlights.
- `graphical_abstract_fair.pdf/.tiff`: updated data-derived visual summary;
  see `SUBMISSION_ASSETS.md` for scope, dimensions and regeneration.
- `references.bib`, `references_additions.bib`, `shallow_references.bib`, result/table `.tex` files,
  `elsarticle.cls`, `elsarticle-num.bst`: compilation sources.
- `revision_results.csv`, `dataset_means.csv`, `paired_comparisons.csv`,
  `paired_dataset_deltas.csv`, `summary.csv`, `dataset_manifest.csv`,
  `tuning_results.csv`, `validation.json`: preceding-protocol evidence and checks.
- `raw/`, `raw_cart/`, `manifest_shard_*.json`: checkpoint/provenance records.
- `input_fingerprints.csv`, `inner_cv_manifest.csv`,
  `reproducibility_manifest.json`, `harness_checks.json`: reproducibility audit.

The old PRL and JOC documents are archived versions, not this revision.
Historical 67-dataset summaries have no retained raw-fit evidence here and must
not be treated as independently reconstructable inferential results. The old
57-dataset grid retains scores, but mixtures reused some bootstrap slots and
its times were allocated estimates. The final revised claims must rely on the
matched and equally tuned fits under `../array_revision_fair/`, not these
preceding numerical files.

## Fair-Revision Readiness Gate

The manuscript is not submission-ready until all of these checks are complete:

1. **Complete, 7 October 2026:** all five fixed shards finished without an omitted
   dataset, repeat, structure, horizon, composition, or tree count. Independent
   fixed-only validation passed and Figure 2 was replaced in the existing
   manuscript. That intermediate figure does not complete the tuned comparison
   or permit removing the draft warning.
2. **Complete, 9 October 2026:** all five tuning shards finished, with every
   training-only selection locked before three separate final refits.
   Independent full validation passed for 285 outer tasks, 136,800 fixed forest
   rows, 5,130 single-tree rows and 855 tuned-family rows. All eleven primary
   contrasts share one Holm adjustment. No dataset or task was omitted.
3. **Integrated:** preceding-protocol prose, tables, figures, abstract,
   conclusion, rebuttal numerical block and highlights were replaced using
   the complete fair evidence. Selection/refit costs, mean-versus-location
   inference, sensitivities and pure-versus-mixed selections are distinguished.
4. **Compiled:** Figures 1--3 are embedded in the same `main.tex` open in the
   native editor. Exported figures and the graphical summary were inspected.
   Manuscript and response compiled successfully with the native compiler.
   Recompile after review edits. Compilation alone is not scientific approval
   or an exported submission PDF.
5. **Internal agreement complete, 9 October 2026:** both requested scientific/
   editorial reviewers agree on the current source and response, with no
   unresolved actionable major blocker. Reviews and the final source hashes
   are in `../array_revision_fair/manuscript/full_manuscript_review.md` and
   `full_writer_final_review.md`. These AI-assisted checks are not external
   peer review, human author approval or editorial acceptance.
6. **Author gate remains:** approve the scientific interpretation and
   disclosures, inspect the final page layout in the compiled previews,
   confirm public release links and portal requirements, and consent to any
   submission or transfer. Publication without a mandatory APC is requested,
   not guaranteed. The historical Codex tool/model identifier is unrecorded;
   confirm whether the receiving journal needs further documentation.

The final fair-analysis directory is `../array_revision_fair/analysis/full/`.
Its figures, CSVs, protocol snapshot and validation report must travel together;
the preceding PDFs listed above must not be included as final figures. Use the
fair-run instructions in `../REPRODUCING_RESULTS.md` for fitting, analysis and
CSV-only figure retrieval.

The full evidence and retrieval scripts were committed as `d67a9061`; all
63 bundle files and five retrieval/cohort dependencies passed a true Git-index
export/restoration check before that commit. The full numerical figures and
graphical summary were visually checked. The main article and response passed
native compilation, but full-page preview inspection was not accessible to
the automation and remains an author check. No replacement document or separate
main-article PDF was compiled/exported; the existing editor stays open.

## Reproduce

Use Python 3.10 with NumPy 1.26.4, scikit-learn 1.7.2, SciPy 1.15.3, PMLB,
pandas, Matplotlib, Cython and setuptools. The exact runtime/source hashes and
versions are retained with the new outputs. The isolated scorer build uses
the repository's unchanged tree module and Cython scorer, avoiding unrelated
treeple extension dependencies. No new induction algorithm is introduced.

```bash
.venv310/bin/python paper/scripts/build_revision_runtime.py
.venv310/bin/python paper/scripts/run_array_revision_benchmark.py --shard-index 0 --n-shards 5
.venv310/bin/python paper/scripts/run_array_revision_benchmark.py --shard-index 1 --n-shards 5
.venv310/bin/python paper/scripts/run_array_revision_benchmark.py --shard-index 2 --n-shards 5
.venv310/bin/python paper/scripts/run_array_revision_benchmark.py --shard-index 3 --n-shards 5
.venv310/bin/python paper/scripts/run_array_revision_benchmark.py --shard-index 4 --n-shards 5
.venv310/bin/python paper/scripts/run_array_cart_controls.py --shard-index 0 --n-shards 5
.venv310/bin/python paper/scripts/run_array_cart_controls.py --shard-index 1 --n-shards 5
.venv310/bin/python paper/scripts/run_array_cart_controls.py --shard-index 2 --n-shards 5
.venv310/bin/python paper/scripts/run_array_cart_controls.py --shard-index 3 --n-shards 5
.venv310/bin/python paper/scripts/run_array_cart_controls.py --shard-index 4 --n-shards 5
.venv310/bin/python paper/scripts/analyze_array_revision.py
.venv310/bin/python paper/scripts/export_array_revision_provenance.py
```

Run at most five shards concurrently. No fit timeout is configured. Complete
outputs are required: 57 datasets x five seeds x three depth settings = 855
tasks in each stage. Do not combine incomplete stages or change sources while
reusing checkpoints. For a fresh experiment, move the old `raw/` and `raw_cart/`
directories into a separately named archive before rerunning.

The following assembly commands apply to the preceding protocol only. Do not
run its inliner after embedding the fair results: it would restore old figures
and numerical claims. The current fair inliner is
`paper/scripts/finalize_fair_revision_source.py`.

The existing manuscript source is self-contained: generated text, tables,
numerical pgfplots, and the bibliography are inlined for the native LaTeX editor.
Editable generation inputs and separate PDF figures are retained. After editing
those inputs or citations, update that same source with:

```bash
.venv310/bin/python paper/scripts/finalize_array_revision_source.py --prepare-bibtex
cd paper/array_revision
bibtex revision_citations
cd ../..
.venv310/bin/python paper/scripts/finalize_array_revision_source.py
```

The editor compiles `main.tex` directly. A conventional LaTeX installation can
also compile that self-contained source in two passes without BibTeX, and compile
the response in two passes. Only claim successful compilation after verification.

## Author Checks Before Upload

Confirm that the linked repository and retained results are publicly accessible
before submission; the scripts do not change repository visibility.
Read the full new results, claims, point-by-point response, and AI disclosure;
the author's substantive approval is required before claiming human verification
or submitting. Keep Mathias Valla as the sole author. Confirm portal metadata
and any required institutional postal address. Review the new title in the portal
and use the original title/reference to associate the revision correctly.

The official Array guide was consulted but automated access was blocked:
<https://www.sciencedirect.com/journal/array/publish/guide-for-authors>.
The package follows Elsevier's existing two-column class and numerical reference
style, but this is not a certification of every current portal-specific constraint.
The editor's supplied revision requirements govern the response. Elsevier's
current AI policy was accessible and informs the draft disclosure:
<https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals>.
