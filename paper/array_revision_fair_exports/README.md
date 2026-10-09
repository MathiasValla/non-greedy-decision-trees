# Retained Fair-Benchmark Evidence

`full/` is the completed, independently validated full export for 57 datasets
and five paired repetitions: 142,785 model-score rows, including 855 tuned
rows, and the complete eleven-contrast Holm family. It retains 21,480 original
files, including 21,442 JSON provenance records in 23 independent archives,
all nine PDF/PNG figure pairs, and 286,806,097 stored payload bytes as reported
by the packager. The largest file is 13,155,586 bytes, below the 95 MiB cap.

`fixed/` remains the separate, independently validated fixed-parameter export
with 8,835 immutable JSON provenance records in seven archives. Its original
fixed-only certificate is not relabeled as a full eleven-contrast certificate.
Bulk CSVs are gzipped; small retrieval files stay plain. Original plaintext
SHA-256 hashes remain in `manifest.json`; `SHA256SUMS` covers stored files.

Full retrieval from the repository root, using a new destination:

```sh
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py verify paper/array_revision_fair_exports/full
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py restore paper/array_revision_fair_exports/full --destination /tmp/fair_full_retained
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --out /tmp/fair_full_retained --plot-summaries
.venv310/bin/python -B paper/scripts/finalize_fair_revision_source.py --export-single-figure --out /tmp/fair_full_retained
```

Do not regenerate inside either immutable bundle. For fixed-only retrieval,
use `fixed`, a different new destination, and analyzer `--fixed-only`; omit the
Fig1 finalizer command. CSV-only retrieval needs the analysis dependencies,
the cohort CSV and the source helper imported by the Fig1 finalizer, but no
compiled scorer, PMLB download, prediction NPZ bank, manuscript, or model fit.

Full retrieval QA on 9 October 2026 restored every original byte/hash, reproduced
all nine PNGs byte-for-byte and every PDF page pixel-for-pixel. PDF bytes differ
only in creation-date metadata. All fourteen certified CSV/protocol files and
the immutable bundle remained unchanged. See [full_RETRIEVAL_QA.md](full_RETRIEVAL_QA.md)
for exact hashes, dependencies, commands and validation scopes. The final test
exported only all 63 bundle files, including the nine explicitly staged PNGs,
and five retrieval source/cohort files from pinned Git-index blobs into a new
temporary tree. All 68 exported files stayed unchanged, and the final index
still matched the tested blob IDs. This proves retrieval of the staged inputs;
no commit or publication was performed by the QA.
The final staged caption-only finalizer also passed a fresh Fig1-only recheck;
its tested SHA-256 is
`be8465f6d0fe1f5ec1775451da6e125bf50a84d41a7361f733a5e09079949498`.
The other 67 indexed inputs, eight other figure pairs and fourteen certified
hashes were unchanged. Retrieval QA is complete for this final staged source;
commit/push and manuscript approval remain separate parent actions.

The previous fixed Git-only check is recorded separately in
[RETRIEVAL_QA.md](RETRIEVAL_QA.md). Retrieval does not repeat the original
bank-probability reconstruction or refit models. Single-tree and direct-refit
scores retain the certificate's range/checkpoint-consistency-only scope.

See `../REPRODUCING_RESULTS.md` for fresh fitting and the separation between
these results and historical protocols, and `../array_revision_fair/PACKAGING.md`
for packaging safety, completeness checks, and exact byte restoration.
Completed fitting, validation and retrieval QA do not constitute final
manuscript approval or publication.
