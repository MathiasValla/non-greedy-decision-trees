# Execution Amendments

This log describes the **preceding, superseded protocol**, not amendments to the
currently frozen matched/equally-tuned run. That run is documented separately in
`../array_revision_fair/PROTOCOL.md` and must not reuse these result records.

The predictive comparisons, five seeds, dataset cohort, and depths were fixed
before numerical result analysis. Neither amendment below selects a model or
dataset based on outer-test performance.

1. A PMLB cache directory race stopped one shard at `new_thyroid`; resuming it
   after the cache existed completed all affected tasks. Dataset-specific cache
   locks were subsequently added to prevent concurrent fetch/write races.
2. `lymphography` has a very rare class with a single member in some outer
   training partitions. Stratified inner cross-validation is impossible there.
   The original guard stopped the relevant task before writing its results.
   The fallback is now shuffled three-fold ordinary KFold, using only the outer
   training partition, for every dataset/repetition with minimum training class
   count one. Otherwise the original stratified inner CV is unchanged. The
   fallback is retained in tuning records and described in the paper. The
   dataset is retained, and the outer partition remains stratified.

`provenance_initial/` retains the initial runner and manifests before these
amendments. Already completed normal-class tasks remain valid: neither change
alters their fitted models or metrics. Final source/data/runtime fingerprints
and amended manifests accompany the complete analysis. This is an amended
extension of an exploratory study, not a preregistered experiment.
