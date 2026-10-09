# Full Evidence Retrieval QA

Completed 9 October 2026 against the Git-index version of
`paper/array_revision_fair_exports/full` and its five retrieval source/cohort files.
Status: true index-only export, bundle verification, byte-preserving restoration
and all nine CSV-only figure pairs passed. This supersedes the preliminary
working-tree check. The tested inputs are staged, not a new committed release;
the final staged caption-literal source follow-up also passed. No fitting
experiment or manuscript inlining was performed.

## Bundle Identity

- Package schema: `array-fair-package-v2`; analysis schema: `array-fair-analysis-v2`.
- 57 datasets, five paired seeds, 285 outer tasks and 1,710 fixed blocks.
- 136,800 fixed-forest, 5,130 single-tree and 855 tuned model-score rows:
  142,785 total; full eleven-contrast Holm family and 501 model summaries.
- 21,480 originals, including 21,442 provenance JSONs; 23 independent volumes.
- 286,806,097 stored payload bytes (the sum of manifest `stored_files` sizes,
  excluding `manifest.json` and `SHA256SUMS` themselves).
- All 63 package files are present and below 95 MiB. Largest:
  `analysis/full/fixed_forests.csv.gz`, 13,155,586 bytes.
- Original plaintext size after restoration: 1,623,101,672 bytes.

```text
protocol fingerprint  d8999e02a5ad8a1398996fd3c851f5a68fd17d697f37cd048e2258a418475d7b
manifest.json         5463a0cd7199da9048bd5145f3cecd2d1a65a93326b3eab21fbb32945823b4f1
SHA256SUMS            03d59274f3de44b92814aa4312d21a44c22c55b2defb04175144929f0419a1d5
validation.json       025cfac98f563b0960d83db5d4cd78ed420f311b496b476a26366fe1492d759a
index snapshot        e75f7180c69daa2341f45c199ae7eba50717443513a19921bdb2a716beaae388
```

The analyzer source matches the current full certificate's `f3076...` hash,
including the approved Figure 3 cosmetics. No design or numerical output was
amended during this QA.

## Isolation and Commands

A new scratch parent was created at `/tmp/fair_full_index_qa_1qrosw69`
(`/private/tmp/...` is its macOS-resolved path). Both `index_export` and the
separate restoration destination `restored` were initially nonexistent.

The export used Git objects only, not working-tree file copies. The manifest
was read with `git show :paper/array_revision_fair_exports/full/manifest.json`.
Its complete stored-file set plus the manifest/checksum files was checked
against stage-zero entries from `git ls-files --stage -z`: exactly 63 bundle
files, including all nine PNGs and the actual `FigS_pair_facets_D3_Fall.png`.
The five source/cohort entries below were also present. No extra indexed
bundle file or missing required file was accepted.

All 68 paths were pinned to their stage-zero blob IDs and regular-file modes.
For each, `git cat-file blob <pinned-blob-id>` streamed the indexed bytes into
its portable relative path under `index_export`. The exported file set was
exactly those 68 files. No working-tree source, manuscript, fragment, scorer,
fitting runtime, dataset cache, or working-artifact directory was copied.

These commands ran using the original dependency environment but only the
exported source and bundle, with `index_export` as the working directory:

```sh
PY=/Users/mathiasvalla/Desktop/Post-doc/Papiers/Non_greedy_trees/treeple/.venv310/bin/python
QA=/tmp/fair_full_index_qa_1qrosw69
SRC="$QA/index_export"
BUNDLE="$SRC/paper/array_revision_fair_exports/full"
"$PY" -B "$SRC/paper/scripts/package_fair_revision_results.py" verify "$BUNDLE"
"$PY" -B "$SRC/paper/scripts/package_fair_revision_results.py" restore "$BUNDLE" --destination "$QA/restored"
MPLCONFIGDIR="$QA/matplotlib" TMPDIR=/tmp "$PY" -B "$SRC/paper/scripts/analyze_array_fair_benchmark.py" --out "$QA/restored" --plot-summaries
MPLCONFIGDIR="$QA/matplotlib" TMPDIR=/tmp "$PY" -B "$SRC/paper/scripts/finalize_fair_revision_source.py" --export-single-figure --out "$QA/restored"
"$PY" -B "$SRC/paper/scripts/package_fair_revision_results.py" verify "$BUNDLE"
```

The analyzer produced the eight forest/tuning/supplemental figure pairs; the
explicit finalizer mode produced only the ninth pair, `Fig1_single_trees`.
The finalizer returned before any manuscript access. No analysis export,
bank-score reconstruction, dataset download, model refit or fitting command ran.

The source table below records the tested indexed bytes, including the staged
fair finalizer with the `y dir` fix, scientific assembler and final caption
literals. After the parent staged the two caption-only amendments, that one
source blob was re-exported into the same isolated tree and its explicit
Figure 1 export command was repeated. The other 67 indexed inputs were unchanged.
The preliminary working-tree snapshot and its regenerated PDF hashes are not
used as proof for this index-only run.

## Passing Checks

1. Full `verify` passed before and after retrieval. Stored hashes, gzip/tar
   integrity, safe relative paths, canonical volume partition/memberships,
   complete JSON provenance and the unchanged v2 certificate were checked.
2. All 21,480 restored paths, byte sizes and SHA-256 hashes independently
   matched `manifest.json` before plotting. There were no prediction NPZs.
3. CSV-only validation passed for all 57 datasets and 501 model summaries,
   complete paired means, deterministic classifications and all eleven primary
   contrasts. It independently recalculated paired effects, 20,000-resample
   bootstrap endpoints with seed 41, Wilcoxon p values and the joint Holm
   correction from retained dataset means. It did not recompute bank predictions.
4. All nine regenerated PNGs are byte-identical. All nine PDFs render to
   identical RGB pixels at 120 dpi using Poppler; each is a nonblank single page.
   Their raw bytes differ only in `/CreationDate`, not graphical content.
5. After regeneration, all 21,471 non-PDF originals still matched their original
   hashes/sizes. The only nine changed files were regenerated PDFs in `/tmp`.
   All fourteen certified CSV/protocol hashes, validation, JSON provenance and
   TeX fragments were unchanged. No extra restored file appeared.
6. Every stored bundle file, `manifest.json`, `SHA256SUMS` and the packaged
   validation retained its initial hash. All 68 exported files retained their
   indexed hashes/sizes; no extra exported file or Python bytecode appeared.
   Neither the exported bundle nor the production bundle was rewritten.
7. A visual contact-sheet inspection covered all nine regenerated figures;
   axes, legends and titles rendered without newly introduced clipping. The
   existing supplementary legend margins and Figure 3 labels were preserved.
8. The current index's path/mode/blob-ID mapping for all 68 files still exactly
   matched the pinned mapping after retrieval. No staging, reset, index-lock
   removal, commit or publication was performed by this QA.

## Figure Hashes

All filenames below are in `analysis/full`. The PNG SHA-256 is the same for
the original package, initial restoration and regenerated output.

| PNG | SHA-256 |
| --- | --- |
| `Fig1_single_trees.png` | `d630e443f406774172cc35711db5cc73ec93cb049c28ec799e27c52f98a68afe` |
| `Fig2_main_D3_Fall.png` | `b857104bd0f7e0f1139960263f613ad82242fa1515495d980d22aa630c04324f` |
| `Fig3_tuned_families.png` | `ab8ef01b0cd9f027f1a79fa441f40e927697aded5caea8cd09e36743b641a1cf` |
| `FigS_curves_D3_Fsqrt.png` | `69db8a06ef9bdac9d13bbd3f9b043377c15953c817439420ea01a7b7e70ccbd6` |
| `FigS_curves_D6_Fall.png` | `750d4ad3d31164648839a167489b44506e0031d360f78ddcf1eb468a118f790d` |
| `FigS_curves_D6_Fsqrt.png` | `902869fc4679e223b62fb4f0be05bee9bd5a5248f2763ccd56f550cf4a26f1d3` |
| `FigS_curves_DNone_Fall.png` | `d2432a76fa8a07aa866bee08a9fc56a65bfbbd8f13454bf082f8f60cfd0eb3df` |
| `FigS_curves_DNone_Fsqrt.png` | `27b375ae18a79674659bbbd0849d0bc4fa385aacccf685df82a3e1441d227399` |
| `FigS_pair_facets_D3_Fall.png` | `d5a7a2f792c822d412f1de66fa886db01583ec3ec9388abd042fb7bc99c56c77` |

| PDF | Packaged SHA-256 | Regenerated SHA-256 |
| --- | --- | --- |
| `Fig1_single_trees.pdf` | `fab259b09aec7dd7b1915b6f932876c0d00b6e74d89c02fec1c84de668d81bd2` | `f03dd12b923d96f4afc93019161f8728024d4633330406c2cbd0e4329d51d978` |
| `Fig2_main_D3_Fall.pdf` | `f4995174b01aa6c095248ed6ad6997b29d4fa36ea2547a2c0ca0f3a4161a1435` | `e0089f553f9e501f545c13982e439bb39d0d1b6581d32de8ce21526307205b90` |
| `Fig3_tuned_families.pdf` | `e09263fd1521bc8e1422346fc1e354e73ffd4cc523b3f9601c679b7c02dc31a8` | `be13ea388d01950f28d2e83ee6dbf4b3a462495a4603f87f40f008513fe112aa` |
| `FigS_curves_D3_Fsqrt.pdf` | `07f951d59352dbc6d5be870801477378bb4587567337cc9f4ba3f452a6663541` | `df38ad0e1d5d48d4af4fe9016e5676a974764d351111c4c114366086448c20cd` |
| `FigS_curves_D6_Fall.pdf` | `a666a0db0f51aa1b3e33493e63a03e3ed528db285fdfd53bb1dbf2f733ab4cc8` | `4b397e171b18f5ff730cde4bb442ebc7660f1eaf4ee222f50e003bdaa59f72a3` |
| `FigS_curves_D6_Fsqrt.pdf` | `fb531c8fa98f9e455451d6bbb9eac9de46230fc883988c82b85c40a7b3dda845` | `96158f736f9988457a81b05fa245b00253c270692fba5c8d29e8a5cc5d30baca` |
| `FigS_curves_DNone_Fall.pdf` | `4f2f692cb9642302fa41b22ff05ad0f093788ba639575a4a5f52060ea058c0a5` | `5f89e5a4721da365f5d64daef5f5254eb660c14ffe1bc942f075e4a521e57cc0` |
| `FigS_curves_DNone_Fsqrt.pdf` | `8acdab3e18abe0c37ed84f77f9a40b8f5fe03e5d861e7a8836a4ea8a05f64c42` | `efa8b450162a083def758b860c076d97835265751de03d84bca660cf966551ce` |
| `FigS_pair_facets_D3_Fall.pdf` | `0019936cadca5a74df140bedbc92c490e2f5ee53944adbed7fe83f0fbfeb8b64` | `27f658ea3eac4da3b71cce1fa01ca8c36461d0af7d2143d9277f4e4ce2904758` |

For each PDF, replacing only the `/CreationDate`/`/ModDate` dictionary string
with the same comparison token made the entire byte stream identical; no
other normalization or PDF rewriting was used. Only `/CreationDate` was
present. Packaged creation times were 16:35:42 for Fig1 and 16:44:25--29 for
the remaining figures; final index-only regenerated times were 17:12:25 and 17:05:06--09,
respectively (9 October 2026, +02:00). Restored pre-regeneration PDFs were
byte-identical to the package. Future regeneration times will naturally differ.

## Certified Output Hashes

All fourteen entries remained unchanged. Paths are relative to `analysis/full`;
bulk hashes refer to restored plaintext `.csv`, not stored `.gz` bytes.

```text
a862076defac83b29a06cee965c11cf392dc15d1615d8d493b320ac411996e2e  dataset_manifest.csv
5edccdb3773ee041e3c8d50f0cbc4812bd9897a3d23e47eadb1547a1417d148d  dataset_means.csv
36c2567f63e98bad013b38d8c6f61523edc0de4dbdfb0b820078251e76eae09b  descriptive_paired_comparisons.csv
b83249f8e824da205a0b9653a88c476b226a8a2c93e9a4fb30cce394492c098f  fair_tuning_table.csv
09c0ff60c1ceaf55bfbcd0633fab9be8dee929fb50d662fb9662e7d767d5eb68  fixed_forests.csv
aa99a97b8c4721dca766b3c711e6b36235c8a4cf03779b2274ab8168acd4db22  fixed_trees.csv
48765e5074c5ac2ad93061d30b6393aae8f7fd7b43299811742813c4cf014fa3  paired_dataset_deltas.csv
b3991e718b04aff40439ffdc59c02edb9d4a4b8e52ec734f4b4a8cb5c9286e23  paired_primary_comparisons.csv
c6d407b2ad7df44321efa6f065c4429731fb59f458cbaca7cf94409a17c7ce4c  physical_cost_dataset_means.csv
6a3e09da2015f361288bfb977a624cc612a36ba7d9f005176823cd040ac0c0d5  protocol_snapshot.json
bf14d3739c95e848d7c5b9796a16d26ce77244e5fa25d4798feae93017efd392  sensitivities.csv
df5f39764649c82e710e6304c41b5f9cfa19c59b32263c461b1e7ecc647e9607  shared_accounting.csv
51c0db3c2ad933ad79058963e6f3322c6b04f79502cf7d6c0ee02d97cfcd5c81  summary.csv
b74f2b86d5a3820672aa22f8d8b0619e7fef506914ee5071b9007ee06bb68e81  tuned_forests.csv
```

## Retrieval Sources and Dependencies

The tested Git-index source export requires these five files. In particular,
the cohort table is required outside the bundle by analyzer protocol checks;
the legacy finalizer is imported for `block` even in Figure 1 export-only mode.

| Repository-relative source | Tested SHA-256 |
| --- | --- |
| `paper/scripts/package_fair_revision_results.py` | `de45837f4205ff10313ac96fef015a323dfa450af3745faa478e4bebe202429c` |
| `paper/scripts/analyze_array_fair_benchmark.py` | `f3076f010500f10e56cfa9815aa55190fff356f6a4827156536c45e9bd72c67b` |
| `paper/scripts/finalize_fair_revision_source.py` | `be8465f6d0fe1f5ec1775451da6e125bf50a84d41a7361f733a5e09079949498` |
| `paper/scripts/finalize_array_revision_source.py` | `5608721b8763f7209433f5fa28c1ce9507e1ee2ebfe58a008195fb93a0e82f80` |
| `paper/tables/mixed_sighted_dataset_sample.csv` | `fbd3c74a1acebb8a2eb46a355487315339e21bafc1744a61ccf639daef8582ef` |

Python was 3.10.18 (Clang 14.0.6). Retrieval used NumPy 1.26.4, pandas 2.3.3,
SciPy 1.15.3, scikit-learn 1.7.2 and Matplotlib 3.10.9, matching the full
certificate's recorded analysis versions. Pillow 12.2.0 and Poppler 26.05.0 were also
available for image QA; Poppler is not required by the retrieval scripts.
The packager itself is standard-library-only. No new dependency installation
or cross-platform/fresh-environment test was performed.

The cohort table's ordered 57 names match the protocol. The retained
`dataset_manifest.csv` has 57 distinct rows, 48 deterministic family groups,
19 named synthetic and 38 retained non-synthetic datasets. Retrieval checked
classification identities, complete-case row accounting and dataset/source
fingerprints. Frozen fitting-source hashes were retained as provenance and
validated as declared identifiers, not resolved against external local source
or binary files by this index-only test. The compact bundle and source export
deliberately do not include or need the fitting scorer or its compiled binary.

## Git-Index Release Proof

All 63 bundle files, including the nine explicitly staged PNGs, and the exact
five source/cohort files above were exported from the Git index and passed.
The existing `.gitignore:16:*.png` rule did not omit any required indexed file.
The exporter used only read-only Git commands; no index lock was removed.

The index snapshot SHA-256 above identifies the canonical JSON mapping of
all 68 repository-relative paths to `mode` and `blob_oid`, serialized with
sorted keys and separators `(',', ':')`. The complete pinned entries and
per-file content hashes are retained in the scratch
`index_export_record.json`. A final index read matched every pinned entry;
both the exported source and bundle remained byte-identical to those entries.
The source table, package manifest and `SHA256SUMS` identify the exact tested
contents without depending on regenerated PDF timestamps.

These staged contents passed Git-only retrieval in the retained dependency
environment and are the tested inputs for the parent's commit. No commit,
reset, staging edit, publication or production inlining was performed here.
This does not claim a committed/remote release, fresh dependency installation
or fresh model fitting. Changes to any tested input after the final index guard
require checking its new hash and repeating the relevant retrieval checks.

The final caption-source follow-up completed after the parent staged the two
Fig1/Fig3 caption-literal amendments. The finalizer was exported from indexed
blob `87d12ddab9b7b137c67db37954dc4bcfc279d09a`, not the working tree. The diff
contained only those two literals; AST comparisons confirmed unchanged
`validate`, `single_data` and `figure1` functions. Repeating only
`--export-single-figure` passed: the Fig1 PNG remained byte-identical, its PDF
rendered identically and differed only in creation date, all fourteen certified
hashes were unchanged, and all eight other figure pairs retained their earlier
hashes. All 68 exported files matched the final index mapping above. The
recorded source hash therefore covers the actual final staged code, not the
superseded pre-caption version. This completes retrieval QA for these staged
inputs; commit/push and final manuscript approval remain the parent's work.

## Verification Scope and Limits

The original independent full validation records:

| Certificate field | Original validation scope |
| --- | --- |
| `fixed_bank_forest_scores`, `inner_cv_bank_forest_scores` | `bank_probability_reconstruction` |
| `fixed_selected_slot_fit_work`, `inner_cv_selected_slot_fit_work` | `bank_slot_sum_reconstruction` |
| `single_tree_scores`, `direct_refit_scores` | `range_and_checkpoint_consistency_only` |

Full CV winners were independently reconstructed by the original analysis.
This retrieval QA verifies retained hashes, schemas, cohort/classifications,
paired statistics and graphical reproduction; it does not repeat prediction
reconstruction because NPZ banks are excluded. Single-tree and selected direct
refit scores are not certified as reconstructed predictions or independently
refitted models. No new timing measurement or performance claim is made.
Selection tree-fit work, direct refit wall time and the sum of measured stage
wall times retain their distinct original accounting; the last is not
uninterrupted end-to-end elapsed time. Scientific conclusions, manuscript
approval, fresh fitting reproducibility and publication remain separate work.
