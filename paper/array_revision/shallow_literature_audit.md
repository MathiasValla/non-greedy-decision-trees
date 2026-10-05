# Shallow Tree and Forest Literature Audit

Scope: read the current `paper/array_revision/main.tex`; investigate final tree size/depth and predictive performance only. No manuscript, response, code, or experimental records were changed. Six primary papers are assessed below. The companion `shallow_references.bib` adds five records; the sixth already exists as `bertsimas2017optimal`.

## Bottom Line

Depth three is defensible as a controlled, capacity-limited experimental setting: each binary tree has at most eight leaves and seven internal nodes. That is a mathematical property of the design, not a literature-derived optimum. Direct RF research provides conditional reasons to study smaller trees, especially in noisy settings, but does not establish that depth-three Gini forests generally match well-tuned deep forests. Keep the new depth-six, unrestricted-depth, and training-only selected conventional controls. The evidence below motivates including the shallow regime, not restricting the entire comparison to it.

## Six Verified Sources

### 1. Zhou and Mentch: Primary RF Regularization Evidence

**Record:** Siyu Zhou and Lucas Mentch (2023), *Statistical Analysis and Data Mining: The ASA Data Science Journal* **16**(1), 45--64. Key: `zhou2023trees`. [Publisher and DOI](https://onlinelibrary.wiley.com/doi/10.1002/sam.11594); [author-version PDF](https://arxiv.org/pdf/2103.16700).

**Evidence and limit:** Low-SNR RF regularization is supported by the publisher abstract and author-version Section 4.2 (regression; `maxnodes`, not fixed depth three). Section 4.1's formal argument concerns randomized linear ensembles, not a general RF risk theorem.

**Metadata:** Online 25 August 2022; issue February 2023; not the journal *Stat*. The supplied [researchers.one PDF](https://researchers.one/articles/21.03.00005.pdf) could not be parsed; the matching arXiv author version was read instead.

### 2. Duroux and Scornet: Tree Size and Resampling Must Be Distinguished

**Record:** Roxane Duroux and Erwan Scornet (2018), *ESAIM: Probability and Statistics* **22**, 96--128. Key: `duroux2018impact`. [DOI](https://doi.org/10.1051/ps/2018008); [published PDF](https://www.numdam.org/item/10.1051/ps/2018008.pdf).

**Supported:** Quantile-forest theory compares subsampling with early termination. Section 4.1 empirically studies leaf-limited Breiman-style regression forests; suitable leaf counts can yield performance comparable to, or better than, the standard construction.

**Limit:** The small-tree comparison also removes resampling; favourable leaf counts can substantially exceed eight. Leaf caps are not maximum path-depth constraints. This does not isolate bootstrap depth-three performance.

**Metadata correction:** The published title uses "tree depth"; the 2016 preprint used "pruning". Use the 2018 journal record supplied in the bibliography, not mixed preprint/journal metadata.

### 3. Scornet, Biau, and Vert: Theory Does Not Validate Fixed Depth Three

**Record:** Erwan Scornet, Gerard Biau, and Jean-Philippe Vert (2015), *The Annals of Statistics* **43**(4), 1716--1741. Key: `scornet2015consistency`. [DOI](https://doi.org/10.1214/15-AOS1321); [published electronic reprint](https://arxiv.org/pdf/1405.2881).

**Supported:** Theorem 1 establishes infinite-forest regression consistency under an additive model with uniform covariates, continuous additive components, and independent Gaussian noise. Its conditions include subsample size `a_n -> infinity`, leaf count `t_n -> infinity`, and `t_n (log a_n)^9 / a_n -> 0`.

**Limit/inference:** The theorem formalizes controlled tree growth, not permanently shallow trees. Fixed `D=3` implies `t_n <= 8`, so this theorem's growing-leaf regime does not apply. Do not describe it as a consistency guarantee for the manuscript's fixed-depth classification forests, or infer inconsistency merely because its sufficient conditions are unmet.

### 4. Bertsimas and Dunn: Shallow Single-Tree Classification Evidence

**Record:** Dimitris Bertsimas and Jack Dunn (2017), *Optimal classification trees*, *Machine Learning* **106**(7), 1039--1082. Existing key: `bertsimas2017optimal`. [Publisher and DOI](https://doi.org/10.1007/s10994-017-5633-9); [author's published PDF](https://web.mit.edu/dbertsim/www/papers/Machine%20Learning%20under%20a%20Modern%20Optimization%20Lens/Optimal_classification_trees_MachineLearning.pdf).

**Supported:** Section 6 benchmarks shallow single classifiers on 53 UCI datasets. Section 6.1 reports mean accuracy of 80.4% for axis-aligned OCT at depth four versus 80.7% for unrestricted CART, whose maximum realized depth across the benchmark was ten.

**Limit:** These are single-tree, not RF, results. They do not establish depth-three optimality. Separate depth-two oblique OCT-H results must not be attributed to axis-aligned trees. Reuse the existing entry.

### 5. Valavi et al. 2021: Applied Evidence With an Important Confound

**Record:** Roozbeh Valavi, Jane Elith, Jose J. Lahoz-Monfort, and Gurutzeta Guillera-Arroita (2021), *Ecography* **44**(12), 1731--1742. Key: `valavi2021presence`. [Publisher and DOI](https://nsojournals.onlinelibrary.wiley.com/doi/10.1111/ecog.05615).

**Supported:** In presence-background ecology, Hellinger-split probability forests with depth two or CV-selected depths one through four improve on default RF. Down-/equal-sampling variants perform slightly better on real data; selected shallow depths predominantly favour four.

**Limit:** This is not a depth-only Gini comparison. The Discussion reports unclear attribution between depth and splitting criterion, and poor performance of its supplementary shallow Gini implementation. Qualified applied evidence only.

### 6. Valavi et al. 2023: A Useful Counterweight, Not a Shallowness Endorsement

**Record:** Same four authors, same order (2023), *Flexible species distribution modelling methods perform well on spatially separated testing data*, *Global Ecology and Biogeography* **32**(3), 369--383. Key: `valavi2023flexible`. [Publisher and DOI](https://doi.org/10.1111/geb.13639).

**Supported:** Across ten approaches and 171 species, RF-shallow is mid-performing and down-sampled RF stronger (Results Section 3.1 and Discussion). The conclusion favours tuned flexibility, not universal simplicity.

**Limit:** Variants differ beyond depth and share the earlier NCEAS benchmark context. This is an applied counterweight, not independent general evidence for depth-three superiority.

## Candidate Manuscript Paragraph

This can follow the Introduction's explanation of the original depth-three screening design. Citations below use the verified keys; the text makes no claim about unfinished experiments.

```latex
Depth three defines a controlled capacity-limited setting, with at most eight
leaves per tree, rather than a generally optimal random-forest configuration.
Direct forest studies provide conditional motivation for limiting tree size,
including in low-signal-to-noise regression settings
\cite{zhou2023trees,duroux2018impact}, while shallow single classifiers have
also been evaluated competitively on multi-dataset benchmarks
\cite{bertsimas2017optimal}. These findings motivate including a shallow
regime but do not establish depth-three optimality for Gini classification
forests. Deeper forests can reduce underfitting and often improve prediction;
we therefore retain the shallow setting alongside depth-six, unrestricted-depth,
and training-only selected conventional controls.
```

## Candidate R1 Reply

> We agree that restricting every learner to depth three can disadvantage conventional random forests and cannot establish practical superiority. Our intent was to examine a controlled shallow setting, with at most eight leaves per member, not to prescribe the best RF depth. Direct forest research provides conditional motivation for tree-size regularization, particularly in noisy settings (Zhou and Mentch, 2023; Duroux and Scornet, 2018), but does not validate depth three as a general optimum. We explicitly acknowledge that deeper RFs are often beneficial. The revised protocol retains depth three while adding depth-six and unrestricted-depth comparisons, depth-matched CART ensembles, and conventional baselines selected using outer-training data only. Claims will be restricted to those paired comparisons once the full evaluation is complete. Shallow-tree results from boosting are not used as evidence for bootstrap-forest performance.

## Integration and Claim Boundaries

- Prefer Zhou and Mentch as the direct general RF citation, with Duroux and Scornet as supporting tree-size evidence. The two Valavi papers are verified applied leads, not general endorsements.
- Success of shallow weak learners in sequential boosting does not establish equivalent performance for independently fitted and aggregated bagging/RF members. No boosting paper is being substituted for direct forest evidence here.
- A forest of depth-three members is not itself limited to eight prediction regions; the eight-leaf bound applies to each member. Do not transfer single-tree interpretability or capacity claims wholesale to the ensemble.
- Additions are supplied separately and not integrated. `bertsimas2017optimal` already has correct author, year, volume, issue, pages, and DOI in `references.bib`; no duplicate entry is introduced.
- The tentative attribution "Wagner 2022 / Trees to Stumps" was not verified in this audit and is not cited. The verified pruning paper is by Zhou and Mentch, with 2023 issue metadata and 2022 online publication.
