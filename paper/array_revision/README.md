# Array Revision: ARRAY-D-26-03529

Prepared for the author's revision due **26 October 2026**. The response requests
the possibility of an appropriate transfer offering publication without a
mandatory APC, with publication terms confirmed before agreement. It also
politely asks the editor to verify Reviewer 2's apparent manuscript mismatch.
Nothing is submitted and no editor/reviewer is contacted by these scripts.

**Working draft, not ready for submission:** the author has requested a further
matched-stopping extension including three-sighted members, equally tuned greedy
and mixed forests, and new forest-size curves. That extension is separately
versioned under `paper/array_revision_fair/`. The completed 855+855-task records
in this directory precede that request; tuned-versus-fixed comparisons must not
serve as the final fair-tuning conclusion. Remove draft warnings only after all
required new records and analyses have passed validation.

## Submission Files

- `main.tex`: revised two-column Elsevier manuscript, open in the native editor.
- `response_to_reviewers.tex`: editable point-by-point reply.
- `cover_letter.txt`: editable cover letter.
- `Fig1_depth_sensitivity.pdf`, `Fig2_accuracy_cost.pdf`: separate data figures.
- `highlights.txt`: editable highlights.
- `references.bib`, `references_additions.bib`, `shallow_references.bib`, result/table `.tex` files,
  `elsarticle.cls`, `elsarticle-num.bst`: compilation sources.
- `revision_results.csv`, `dataset_means.csv`, `paired_comparisons.csv`,
  `paired_dataset_deltas.csv`, `summary.csv`, `dataset_manifest.csv`,
  `tuning_results.csv`, `validation.json`: new evidence and checks.
- `raw/`, `raw_cart/`, `manifest_shard_*.json`: checkpoint/provenance records.
- `input_fingerprints.csv`, `inner_cv_manifest.csv`,
  `reproducibility_manifest.json`, `harness_checks.json`: reproducibility audit.

The old PRL and JOC documents are archived versions, not this revision.
Historical 67-dataset summaries have no retained raw-fit evidence here and must
not be treated as independently reconstructable inferential results. The old
57-dataset grid retains scores, but mixtures reused some bootstrap slots and
its times were allocated estimates. The revised claims rely on new fits.

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
