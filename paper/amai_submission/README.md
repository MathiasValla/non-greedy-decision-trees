# AMAI Submission Draft

This folder is a flat Springer Nature/AMAI-style LaTeX submission package.

Important files:

- `main.tex`: manuscript source.
- `references.bib`: bibliography.
- `sn-jnl.cls`, `sn-mathphys-num.bst`, `sn-basic.bst`: Springer Nature template files.
- `Fig1_accuracy_time.pdf`: main accuracy-time tradeoff figure.
- `Fig2_forest_size.pdf`: small forest-size pilot figure.

Compile from this directory:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Author affiliation and funding statements are placeholders and should be filled
before submission.
