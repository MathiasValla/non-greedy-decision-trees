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
- `REPRODUCING_RESULTS.md`: map from article claims to result files and
  commands.

Regenerate the assets with:

```bash
python paper/scripts/make_lookahead_letter_assets.py
```

The retained results used by the current article are in `tables/`, including
the 67-dataset aggregate benchmark and the 57-dataset mixed-forest grid used for
Figure 2. See `REPRODUCING_RESULTS.md` for exact provenance and retrieval
instructions.
