# Retained Fair-Benchmark Evidence

`fixed/` is the complete, independently validated fixed-parameter export for
57 datasets and five paired repetitions. It contains the analysis certificate,
all exported scores and summaries, numerical figures, unchanged protocol, and
8,835 immutable JSON provenance records. Bulk CSVs are gzipped; JSON records
use seven independent deterministic archives. Original plaintext SHA-256 hashes
are retained in `manifest.json`; `SHA256SUMS` covers stored files. Every file
is below the packager's 95 MiB cap.

The equally tuned stage is still running. There is no completed `full/` bundle
yet, no interim joint significance test, and no final tuned conclusion here.
The fixed-only export does not include actively written tuning records.

From the repository root:

```sh
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py verify paper/array_revision_fair_exports/fixed
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py restore paper/array_revision_fair_exports/fixed --destination /tmp/fair_fixed_retained
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --out /tmp/fair_fixed_retained --plot-summaries --fixed-only
```

Use a new restoration destination. Do not regenerate files inside the immutable
bundle. CSV-only figure retrieval requires the analysis dependencies, but no
compiled scorer, PMLB download, prediction NPZ banks, or model fitting. The
restored Figure 2 and pair-facet PNGs were reproduced byte-for-byte on the
retained environment. Raw prediction reconstruction requires local NPZ banks
and is not repeated by the retrieval command.

See `../REPRODUCING_RESULTS.md` for fresh fitting and the separation between
these results and historical protocols, and `../array_revision_fair/PACKAGING.md`
for packaging safety, completeness checks, and exact byte restoration. The
current manuscript remains a working draft until the equally tuned evaluation,
complete eleven-contrast analysis, and final scientific review are finished.
