# Fixed Evidence Retrieval Check

Completed 7 October 2026 against committed Git snapshot `941e5aa4`.

## Checked Inputs

- The two retrieval scripts, the retained `fixed/` bundle, and the frozen cohort
  table `paper/tables/mixed_sighted_dataset_sample.csv` were exported from Git
  into a new temporary source tree. The initial minimal export omitted the
  cohort table and correctly failed protocol validation; including this already
  tracked repository file made the test equivalent to a fresh checkout.
- No working artifact directory, prediction NPZ bank, compiled scorer, fitted
  estimator, or PMLB data cache was copied into the test tree.
- The original analysis dependencies were used; dependency installation on a
  new machine was not tested. No model was fitted and no data were downloaded.

## Passing Checks

1. The packager's synthetic fixed/full tests passed: deterministic multi-volume
   layout, legacy compatibility, exact-byte restoration, corruption and unsafe
   path rejection, completeness gates, and isolation from active tuning files.
2. All 8,866 original file sizes and SHA-256 hashes agreed between the checked
   single-archive precursor and the versioned split-archive bundle.
3. Every required stored bundle file was present in the Git index, including all
   seven PNGs despite the repository's general PNG ignore rule.
4. Restoration using only the committed script and bundle passed, exposing a
   new root with 8,866 byte-verified files and 8,835 JSON provenance records.
5. CSV-only analysis using the committed analyzer and cohort table passed for
   498 model summaries, all 57 datasets, and the fixed-only inference scope.
6. Regenerated Figure 2 and pair-facet PNGs were byte-identical to their retained
   Git counterparts. No fitting or local prediction banks were required.

The bundle has seven provenance archives; the largest stored file is
13,155,586 bytes. Its manifest preserves the original analysis certificate and
plaintext hashes, rather than rewriting them for compressed files.

## Limits

This is a retrieval and packaging check, not a new independent bank-prediction
validation or replication of the original fits. The fixed-only certificate
records the original verification scopes, including range/checkpoint checks
only for single-tree scores. It does not certify unfinished tuning, the joint
eleven-contrast inference, a new machine's fitting times, or final manuscript
approval. The full bundle must pass its own checks after all tuning completes.
