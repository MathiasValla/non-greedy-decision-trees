# Fair Results Packaging

`paper/scripts/package_fair_revision_results.py` is a standard-library-only
engineering sidecar. It packages an existing, independently validated analysis;
it does not fit, analyze scores, select methods, regenerate figures, publish,
run Git commands, or modify source artifacts. Run it only after the applicable
analysis has passed. New packages use `array-fair-package-v2` with independent
provenance volumes; the existing single-archive `array-fair-package-v1` format
remains supported by verify/restore. This document does not certify a completed
full run, and the existing exported v1 package must not be rewritten in place.

## Gates and Scope

The input root defaults to `paper/array_revision_fair`. Both modes require the
unchanged `array-fair-analysis-v2` certificate, its exact verification scopes,
protocol fingerprint, all 57 datasets/five seeds, correct model/count spaces,
and all original `output_sha256` checksums. Relevant CSV record counts are also
checked using a CSV parser, including quoted embedded newlines. The tool checks
checkpoint schemas and identities, not numerical score values or inference.
It neither upgrades old certificates nor marks an incomplete cohort complete.

- **Fixed-only:** requires `analysis/fixed_only`, 1,710 fixed blocks, 136,800
  forest repeat rows and 5,130 single-tree repeat rows. JSON collection uses
  explicit filenames for all 285 tasks: one `split.json`, and six structures
  each containing the structural JSON, `__curves.json`, and three
  `__single_k{1,2,3}.json` files. Exactly **8,835 JSONs** enter the archive.
  It does not traverse/read `inner`, selection, tuned, refit, task-result or
  completion-marker files, even when tuning is concurrently writing them.
  Launch records and separate `data_manifest` JSONs are not included in this
  mode; the validated plain analysis manifest and split identities retain
  dataset/source metadata.
- **Full:** requires `analysis/full`, the complete eleven-contrast inference
  certificate, all 855 tuned repeat rows, and every complete task/refit.
  Includes the fixed JSONs, all 12 structures in every two/three-fold inner CV,
  selection, all three direct-refit checkpoints, tuned/task results, completed
  scope markers, all 57 data-manifest JSONs, and existing matching launch
  manifests. Unknown JSONs in these completed task locations are errors, not
  silently dropped. Package only when these inputs are quiescent.

JSON bank completion is checked through the four per-slot array lengths:
200 for fixed and 100 for CV. Structural/curves/single checkpoint contents
must agree; selected configurations and refit records must agree. No NPZ is
read. These checks supplement, not replace, the independent analyzer's
previous numerical validation.

Only the selected protocol fingerprint's provenance is included. NPZ/model
binaries, public-data caches, compiled runtime caches, locks, temporary files,
other runs, and the other analysis mode are excluded. `protocol.json`, its
validated snapshot and the hash-matching `PROTOCOL.md` are retained verbatim.

## Layout

The package is a **new directory outside the input root**:

```text
protocol.json
PROTOCOL.md
analysis/fixed_only/                 # or analysis/full, never both
  validation.json
  protocol_snapshot.json
  dataset_means.csv
  summary.csv
  paired_primary_comparisons.csv
  dataset_manifest.csv
  fair_tuning_table.csv              # full only
  fixed_forests.csv.gz
  fixed_trees.csv.gz
  tuned_forests.csv.gz               # full only
  paired_dataset_deltas.csv.gz
  ...other small CSVs, JSON summary, TeX fragments and all PDF/PNG figures...
json_provenance.part000001.tar.gz
json_provenance.part000002.tar.gz     # when needed; consecutive six-digit parts
...
manifest.json
SHA256SUMS
```

The figure-retrieval files stay plain even if `dataset_means.csv` is sizable.
Only the four named bulk CSVs are gzipped; every other exported CSV remains
plain. Original plaintext filenames are recorded, not renamed in validation.
All seven fixed or eight full PDF/PNG figure pairs and relevant TeX fragments
are required and copied without rewriting.

`manifest.json` records each original input's portable relative path, byte
size and SHA256, its stored path/encoding, and its tar member if applicable.
For v2, `provenance_volumes` records each canonical volume's member count and
plaintext JSON byte sum; `provenance_volume_payload_limit` records the chosen
limit. Verification independently reconstructs the sorted greedy partition
and checks every member's assigned volume, not just archive checksums.
It also records stored-file sizes/SHA256, the analyzer/packager source hashes,
and the protocol's declared frozen implementation source hashes. Declared
implementation identifiers can contain original absolute paths; these are
informational JSON strings, never extraction paths. Their bytes/hashes are
preserved; referenced source files/binaries are not bundled or rebuilt.

`SHA256SUMS` covers all stored files plus `manifest.json`. It does not hash
itself. Hashes detect corruption and consistency problems; they are not a
signature from an independent authority and cannot authenticate a maliciously
rewritten certificate and all its checksums. Figures and extra provenance,
which are not covered by the analyzer's CSV hash map, receive new packaging
hashes. The original analysis hash map/certificate are never changed.

## Volume and File Limits

Each new provenance volume has at most **64 MiB (67,108,864 bytes)** of original
plaintext JSON payload, or a smaller user-selected limit. This is the sum of
original file sizes, excluding tar headers/padding and gzip overhead. Sort
all JSON relative paths lexicographically, then greedily append each whole
file to the current volume until the next file would exceed the limit; start
the next consecutive volume at that file. An exact-boundary payload is allowed.
A single JSON larger than the chosen limit is rejected before staging. Files
are never split, reserialized, truncated or dropped.

Names are canonical `json_provenance.part000001.tar.gz`, `...part000002.tar.gz`,
and so on. Each file is a complete independent gzip/USTAR archive, not a byte
fragment of a larger archive: standard `tar -tzf`/`tar -xzf` can read an
individual volume. All volumes are required for cohort verification and full
restoration; do not concatenate or rename them to the legacy archive name.
The utility verifies per-volume hashes/sizes, exact memberships, safe paths,
ordering, gzip integrity and the absence of nonzero trailing payloads.

New v2 packages also enforce **95 MiB (99,614,720 bytes)** as the maximum size
of every output file, including compressed CSVs, volumes, plain retrieval
files, `manifest.json` and `SHA256SUMS`. This separate release guard covers
tar/gzip overhead and does not assume a compression ratio. If any file exceeds
it, packaging fails without exposing a destination. It does not silently
compress required plain retrieval files or alter source/analysis hashes.
The returned packaging summary reports the largest output file size.

The old v1 reader still accepts `json_provenance.tar.gz` with its original
manifest and checksums; the new volume/file-limit rules are not retroactively
applied to legacy packages. No conversion, relabeling or rewrite is needed
to verify/restore the already exported v1 artifact. New creation always emits
v2, even when all provenance fits into one numbered volume.

## Determinism and Safety

Compression streams bytes directly, preserving CSV order, floating-point
spellings, quoting, line endings and JSON formatting. Gzip uses level 9,
`mtime=0` and an empty filename header. Tar members are lexicographically
ordered USTAR regular files, mode 0644, uid/gid/mtime zero and empty owner names.
Greedy volume boundaries depend only on sorted names, original sizes and the
chosen payload limit. Resetting gzip at these fixed boundaries is deterministic.
No absolute source/destination path or packaging time is injected into the
package manifest. Identical input bytes and packager/compression-runtime
versions produce identical packages; differing zlib versions are not promised
to produce identical compressed streams. Restoration remains byte-identical
and portable with standard gzip/tar implementations.

Internal source/package symlinks, archive links, special files, absolute paths,
drive/backslash paths, traversal components, duplicates, unexpected archive
members and noncanonical tar metadata are rejected. All archive names are
relative to the fair root, with ASCII letters, digits, underscore, period,
hyphen and plus allowed in path components. In particular, the legitimate
dataset name `parity5+5` is supported; plus does not relax the rejection of
traversal, backslash or colon/drive paths. The tool checks stored
and decoded hashes/sizes and gzip integrity before publishing a package.
Changed source bytes during copying cause failure. Failed work is removed from
private staging; an existing destination is never overwritten. This is not a
filesystem snapshot service: the included inputs must be immutable/quiescent.
Fixed-only mode deliberately allows unrelated tuning outputs to keep changing.

## Exact Usage

From the repository root, using the parent-approved Python environment:

```sh
TMPDIR=/tmp .venv310/bin/python -B paper/scripts/package_fair_revision_results.py self-test
```

After the fixed-only analyzer has passed, the parent may create a package in
a new directory (the command below is an example, not executed here):

```sh
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py package --out paper/array_revision_fair --destination /tmp/fair_fixed_package --fixed-only
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py verify /tmp/fair_fixed_package
```

The unchanged commands now create v2 numbered volumes automatically. Optional
`--volume-payload-mib N` accepts integers 1..64 (default 64); it changes only
storage partitioning, not the experiment or plaintext hashes. For example,
`--volume-payload-mib 1` forces small volumes for integration tests. The same
`verify`/`restore` commands auto-detect v1 versus v2 from the manifest.

Only after the full analyzer has passed and tuning writers have finished:

```sh
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py package --out paper/array_revision_fair --destination /tmp/fair_full_package
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py verify /tmp/fair_full_package
```

The parent chooses any tracked/distributed layout separately. This utility
does not stage, commit, publish or remove the original uncompressed outputs.

## Restore Before Existing Tools

Keep the package immutable. Restore into a **new** fair root:

```sh
.venv310/bin/python -B paper/scripts/package_fair_revision_results.py restore /tmp/fair_fixed_package --destination /tmp/fair_fixed_restored
.venv310/bin/python -B paper/scripts/analyze_array_fair_benchmark.py --out /tmp/fair_fixed_restored --plot-summaries --fixed-only
```

For full mode, use the full package/new destination and omit `--fixed-only`
from the analyzer command. The restore command first verifies the package,
then decompresses bulk CSVs to their **original `.csv` filenames** and restores
JSON members from every independent volume at their original relative paths.
Legacy v1 restoration reads its single archive instead. Every restored file is checked
against its original size/SHA256 before the new directory is exposed. All
original `validation.json.output_sha256` entries therefore remain applicable.
Do not edit the certificate's recorded original output-directory string; it
is provenance, not a request to write back to that location.

Restore before any existing tool that expects plaintext repeat CSVs. Do not
run figure-regenerating tools inside the package directory: they would change
the package's hashed figures. `--plot-summaries` on the restored root needs no
NPZs/refits. Normal raw-data analysis/bank-score reconstruction is intentionally
not supported by this compact bundle alone: caches and NPZ predictions are
excluded. Restoration preserves bytes, not original filesystem timestamps or
ownership.

## Tests and Boundary

`self-test` creates only explicitly labeled synthetic fixtures under `/tmp`.
It covers both complete cohort modes, malformed active tuning files ignored
by fixed-only mode, missing/corrupt artifacts, wrong mode, exact CRLF/quoted
CSV and JSON byte round-trips (including synthetic `parity5+5` dataset paths in
fixed and full modes), deterministic repeated packaging despite mtime
changes, portable relative tar paths, existing destinations, source links,
unsafe paths, archive links/nonzero trailing payloads, and corrupted/unsafe
archives even with refreshed transfer hashes.
Multivolume tests force 1 MiB partitions for both fixed/full modes, check exact
greedy boundaries and determinism, compare all restored original hashes/bytes,
and reject missing/extra/corrupt volumes, unsafe volume paths/members and
oversized single JSONs. A sparse-file boundary fixture checks rejection above
95 MiB. A synthetic legacy v1 package is independently verified/restored, with
unchanged original plaintext hashes. No real exported package is inspected or
rewritten by these tests.
Synthetic opaque `.pdf`/`.png` fixtures are byte-test payloads, not plots.
No production packaging, publication, fits or production-score interpretation
was performed during development.
