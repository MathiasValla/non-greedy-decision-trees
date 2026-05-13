# Lookahead Decision Tree Letter

This directory contains the compact paper draft and supporting assets for the
lookahead decision-tree benchmark.

Main files:

- `lookahead_letter.md`: manuscript draft.
- `venue_note.md`: target-journal recommendation.
- `scripts/make_lookahead_letter_assets.py`: regenerates tables and figures
  from the retained aggregate benchmark summary.
- `tables/`: generated CSV tables.
- `figures/`: generated manuscript figures.

Regenerate the assets with:

```bash
python paper/scripts/make_lookahead_letter_assets.py
```

Important provenance note: the original raw benchmark CSVs were temporary files
under `/private/tmp` and were not present when this paper package was assembled.
The current figures and tables therefore use the aggregate benchmark summary
retained from the completed run: 67 completed datasets, 402 model fits, 42
dimension-filter skips, 32 load/fetch skips, and 21 fit timeouts. Before journal
submission, rerun or recover the raw CSVs and add per-dataset supplementary
tables.
