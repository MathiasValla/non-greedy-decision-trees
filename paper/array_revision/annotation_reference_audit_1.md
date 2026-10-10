# Annotated-PDF Reference Audit: Entries 1-16

Audit date: 10 October 2026.

Target: `paper/array_revision/main.tex`, bibliography keys `breiman1984cart` through `kuncheva2003diversity`, in their current order. The manuscript is being edited concurrently; section names and citation keys below are more stable locators than line numbers.

## Scope and Evidence Standard

This audit checks existence, author identity/order, title, publication year, venue, volume/issue, page range or article number, and the DOI where one is supplied. It also checks the cited claims against substantive source portions, not merely titles. No fits, benchmark execution, figure changes, PDF changes, or manuscript edits were performed. This report is the only file written by this audit.

Sources are publisher pages/PDFs, official proceedings, author-hosted manuscripts, or author/institutional records. For selected metadata gaps, publisher-deposited Crossref records were retrieved directly; these establish registration metadata, not scientific results. Search-indexed text from an identified primary page is explicitly distinguished from a successfully opened page. Third-party bibliographies and the existing local literature audits were discovery aids, not verification authorities. An author-uploaded item on ResearchGate is used only where author provenance is explicit, not as an independent publisher record.

"Read" below means the specified portions, not an assertion that every page was read. PDF locators normally use printed article pages; preprint pagination is labeled separately. Access failures are recorded as failures, not evidence that a work or DOI does not exist.

## Executive Findings

- All 16 works exist. No fabricated reference or compelling reason to delete any was found. Retain all 32 existing references; entries 17-32 were not audited here.
- The current author initials/order, titles, years, venues, supplied DOIs, and page/article identifiers for entries 1-16 are consistent with the primary evidence obtained. Two entries repeat their article number unnecessarily: 13 and 15. These are presentation corrections, not changes to the underlying identifiers.
- Do not change Zhou and Mentch's journal year from 2023 to 2022: the latter is the online-first year. Do not change Horn et al. from 2026 to 2025 because the DOI contains `025`: the publisher dates publication to 3 January 2026.
- Shallow-tree motivation is appropriate only conditionally. Entries 2 and 3 motivate examining capacity, not a generally optimal depth-three bootstrap Gini classifier. Entry 3's small-tree empirical alternative also changes resampling. Entry 15 is not general evidence that shallower random-forest members improve accuracy.
- The root-only, repeated-lookahead commitment rule has clear prior art in Norton/IDX and Murthy-Salzberg/LOOK. Esmeir-Markovitch also evaluates non-greedy tree ensembles and explicitly discusses allocating resources between individual trees and committee size. The manuscript's empirical mixed-horizon contribution can remain; priority for root-only lookahead, non-greedy forests, or the general computation-allocation question would not be supported.
- Full cited-work text was not obtained for entries 8 and 10. Entry 8's metadata is verified, with the method checked in an official same-authors companion paper. Entry 10's metadata and broad relevance are supported, but a detailed algorithm/results audit is incomplete. These limitations must not be flattened into "all references fully verified."

## Entry-by-Entry Evidence Ledger

### 1. `breiman1984cart`

**Record:** Leo Breiman, Jerome H. Friedman, Richard A. Olshen, Charles J. Stone. *Classification and Regression Trees*. Wadsworth, Belmont, CA, 1984. A whole book, not a journal article; no article page interval is required. No DOI is supplied in `main.tex`.

**Primary evidence:** [Current publisher catalogue](https://www.routledge.com/Classification-and-Regression-Trees/Breiman-Friedman-Olshen-Stone/p/book/9780412048418) was blocked on direct opening; its indexed text identifies the first edition, 1984 copyright, and 368-page reprint. The [publisher-origin book preview](https://api.pageplace.de/preview/DT0400.9781351460491_A31471984/preview-9781351460491_A31471984.pdf), served by the distributor, was readable. Its title page gives the original author order above. Breiman's own [bagging manuscript, references](https://www.stat.berkeley.edu/~breiman/bagging.pdf) confirms the 1984 Wadsworth citation; the [Rendell-Ragavan proceedings paper, references](https://www.ijcai.org/Proceedings/93-2/Papers/017.pdf) additionally gives Belmont, CA.

**Substantive reading/support:** Book Section 2.3, printed pp. 23-26, describes impurity reduction, child-proportion weighting, choosing the maximizing split, and repeating the procedure at descendants. This supports the Introduction's immediate-impurity characterization of CART. It does not establish an optimal shallow-forest depth.

**Correction/limit:** Keep the current entry. The modern catalogue displays Stone before Olshen; do not propagate that catalogue-order discrepancy over the book title page. Do not silently attach a modern reprint DOI to the original Wadsworth edition; no original-edition DOI was verified. The total page count is supplementary reprint metadata, not a missing page range.

### 2. `zhou2023trees`

**Record:** Siyu Zhou, Lucas Mentch. "Trees, forests, chickens, and eggs: when and why to prune trees in a random forest." *Statistical Analysis and Data Mining: The ASA Data Science Journal* 16(1), 45-64 (2023). DOI `10.1002/sam.11594`. First online: 25 August 2022.

**Primary evidence:** [Wiley article record](https://onlinelibrary.wiley.com/doi/10.1002/sam.11594) verifies authors, title, journal, issue, pages, DOI, and the two dates. Metadata/abstract were readable; the complete publisher body was not available. The [authors' preprint](https://arxiv.org/pdf/2103.16700) was readable, including Section 4.1's randomized-linear-model analysis and Section 4.2's regression experiments, especially preprint pp. 16-18.

**Claim assessment:** The smaller-tree motivation in the Introduction and Tree-size regularization subsection is supported for low-signal/noisy settings. The regression comparisons vary terminal-node limits and signal-to-noise ratio; these are not an identification of depth three as optimal. The theoretical randomized-linear-model argument must not be described as a theorem about the manuscript's Gini forests.

**Correction/limit:** Keep the complete current entry, including 2023 and the online-first note. Read substantive preprint portions rather than asserting line-for-line verification of the inaccessible final publisher text. Preserve explicit separation between motivating regression evidence and the present classification experiment.

### 3. `duroux2018impact`

**Record:** Roxane Duroux, Erwan Scornet. "Impact of subsampling and tree depth on random forests." *ESAIM: Probability and Statistics* 22, 96-128 (2018). DOI `10.1051/ps/2018008`.

**Primary evidence:** The [official journal archive record](https://numdam.org/articles/10.1051/ps/2018008/) and [archived published PDF](https://www.numdam.org/item/10.1051/ps/2018008.pdf) verify the record, including first-page DOI and article pagination. Direct access to the [EDP journal PDF](https://www.esaim-ps.org/articles/ps/pdf/2018/01/ps170099.pdf) failed; the Numdam copy is the published article, not an unspecified secondary summary.

**Substantive reading/support:** Section 2.1 defines the regression setting; Section 3 studies a quantile-forest model. Section 4.1, pp. 104-105, compares small and standard Breiman-style regression forests. Critically, the small-tree alternative uses all observations without resampling, whereas the standard forest uses bootstrap samples; terminal-leaf and node-size settings also differ. Competitive results require suitable size choices, not universally eight leaves.

**Correction/limit:** Bibliography unchanged. Add the empirical resampling distinction. Prefer "quantile-split regression forests" to "quantile regression forests": Section 3 uses predictor-quantile splits to estimate a conditional mean, not response-quantile prediction. Do not convert "can be competitive" into a bootstrap-only depth effect, a Gini-classification theorem, or a depth-three recommendation.

### 4. `quinlan1986induction`

**Record:** J. R. Quinlan. "Induction of decision trees." *Machine Learning* 1(1), 81-106 (1986). DOI `10.1007/BF00116251`.

**Primary evidence:** [Springer article record](https://link.springer.com/article/10.1007/BF00116251) and [publisher PDF](https://link.springer.com/content/pdf/10.1007/BF00116251.pdf) verify title, author, year, venue, and pages. The [Springer-deposited DOI record](https://api.crossref.org/works/10.1007%2FBF00116251) explicitly verifies issue 1 and March 1986.

**Substantive reading/support:** Section 4, especially printed pp. 87-91, describes attribute selection using information gain and recursive induction. This supports the Related work statement that greedy induction is foundational.

**Correction/limit:** None. Do not describe ID3's particular information-gain/multiway-attribute procedure as identical to every CART binary Gini implementation. This is foundational single-tree literature, not evidence about bootstrap aggregation, shallow-forest optimality, or mixed-horizon benefits.

### 5. `breiman1996bagging`

**Record:** Leo Breiman. "Bagging predictors." *Machine Learning* 24(2), 123-140 (1996). DOI `10.1007/BF00058655`.

**Primary evidence:** [Springer article record](https://link.springer.com/article/10.1007/BF00058655) verifies the journal publication; the [publisher-deposited DOI record](https://api.crossref.org/works/10.1007%2FBF00058655) confirms volume 24, issue 2, August 1996, pages, and DOI. The [author-hosted manuscript](https://www.stat.berkeley.edu/~breiman/bagging.pdf) is Technical Report 421, September 1994, not the paginated 1996 journal version.

**Substantive reading/support:** The manuscript's Introduction, printed pp. 1-2, explains bootstrap resampling and averaging/voting, relating improvements to instability of the underlying procedure; Section 2 examines classification trees. This supports bootstrap aggregation as a foundation and the distinction between a single learner and an aggregated ensemble.

**Correction/limit:** None. Keep 1996 for the journal article, not the technical report's 1994. Bagging does not require per-split feature subsampling. The source does not recommend a fixed depth of three or imply every base learner benefits equally from bagging. The accessible author version supports these conceptual claims, not an assertion of complete final-version textual comparison.

### 6. `breiman2001random`

**Record:** Leo Breiman. "Random forests." *Machine Learning* 45(1), 5-32 (2001). DOI `10.1023/A:1010933404324`.

**Primary evidence:** [Springer article record](https://link.springer.com/article/10.1023/A:1010933404324), [publisher-deposited DOI record](https://api.crossref.org/works/10.1023%2FA%3A1010933404324), and [author-hosted manuscript](https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf). The first two verify the journal metadata, including issue 1 and October 2001. The author manuscript has its own pagination and January 2001 date.

**Substantive reading/support:** Sections 1, 3/3.1, and 4 distinguish the broad randomized-tree definition from the random-input-feature construction, using bootstrap samples and randomly selected feature candidates. The random-feature implementation grows trees without pruning. This supports the conventional feature-randomized baseline described in Related work.

**Correction/limit:** None. Breiman's broad definition encompasses more than one algorithm, including bagging as a special case. Thus, "all-feature bagging is not the conventional feature-subsampled baseline" is defensible; "bagging can never be called a random forest" would be too absolute. Convergence with the number of trees is not a consistency result for fixed-depth classifiers as sample size grows.

### 7. `norton1989generating`

**Record:** Steven W. Norton. "Generating better decision trees." *Proceedings of the Eleventh International Joint Conference on Artificial Intelligence*, 800-805 (1989). No DOI is supplied.

**Primary evidence:** [Official IJCAI PDF](https://www.ijcai.org/Proceedings/89-1/Papers/128.pdf). The title/author and first/last printed pages verify the six-page proceedings item. No DOI was identified in this primary source; that is not proof that no DOI exists anywhere.

**Substantive reading/support:** Section 3, pp. 801-802, explicitly contrasts non-overlapping, block-committing GOTA with overlapping IDX lookahead that commits only the shallowest tests and searches again below them. Section 4.2 reports no systematic error-rate difference in its robustness experiment; Section 5 discusses costs and gains.

**Correction/limit:** None to the bibliography. "Considered downstream tree quality" is accurate but understates the closely relevant commitment rule. Root-only receding lookahead is already present here. A stronger Related work description would identify overlapping IDX lookahead explicitly. Norton's cost/information criterion and task setting are not identical to the current exhaustive terminal-Gini implementation, and the paper does not promise universal predictive improvement.

### 8. `ragavan1993lookahead`

**Record:** Harish Ragavan, Larry A. Rendell. "Lookahead feature construction for learning hard concepts." In *Machine Learning Proceedings 1993*, Morgan Kaufmann, 252-259 (1993), the Tenth ICML proceedings. DOI `10.1016/B978-1-55860-307-3.50039-3`.

**Primary evidence:** The [Elsevier proceedings contents](https://www.sciencedirect.com/book/9781558603073/machine-learning-proceedings-1993) supplied indexed primary text confirming authors, chapter title, pages, publisher/imprint, and year. Direct chapter/DOI landing access failed, including the [publisher chapter endpoint](https://linkinghub.elsevier.com/retrieve/pii/B9781558603073500393). The [Elsevier-deposited DOI record](https://api.crossref.org/works/10.1016%2FB978-1-55860-307-3.50039-3), retrieved successfully as JSON, verifies the exact chapter DOI, title, authors, container, year, and 252-259 range.

**Substantive reading/support:** Read Section 5, especially pp. 956-957, of the same authors' [official IJCAI companion paper, "Improving the Design of Induction Methods by Analyzing Algorithm Functionality and Data-based Concept Complexity"](https://www.ijcai.org/Proceedings/93-2/Papers/017.pdf). It describes LFC's lookahead and caching of search information as constructed features and cites the ICML chapter. This supports the broad feature-construction relevance.

**Correction/limit:** Current initials and metadata are correct; Harish, not Hema. The cited ICML chapter's full text was not read. Method-level support here is corroboration from a same-authors primary account, not a completed chapter-level results audit. Do not attribute exact ICML numerical results or implementation details on that basis.

### 9. `murthy1995lookahead`

**Record:** S. K. Murthy, S. L. Salzberg. "Lookahead and pathology in decision tree induction." *Proceedings of the Fourteenth International Joint Conference on Artificial Intelligence*, 1025-1031 (1995). No DOI is supplied.

**Primary evidence:** [Official IJCAI PDF](https://www.ijcai.org/Proceedings/95-2/Papers/002.pdf), seven pages. The first page identifies Sreerama Murthy and Steven Salzberg; the final printed footer is 1031. The current interval is correct, not 1025-1033. No DOI was identified in the official PDF.

**Substantive reading/support:** Section 2, pp. 1025-1026, evaluates each candidate root using best subsequent splits of its children, commits the root, and recurses. This is the manuscript's two-generation structural analogue, allowing for horizon naming conventions and candidate/criterion details. Sections 3-4 examine synthetic pathology and an eight-domain empirical comparison, including pruning; the authors caution against strong generalization from the limited comparison.

**Correction/limit:** None. "Directly evaluates a split with optimally split children" is supported as a local search description, not a globally optimal-tree guarantee. The source supports doubt about reliable accuracy gains per added computation, not a theorem that lookahead always hurts or never helps. It also predates the present root-only commitment rule.

### 10. `elomaa2005lookahead`

**Record:** Tapio Elomaa, Tuomo Malinen. "On look-ahead and pathology in decision tree learning." *Journal of Experimental & Theoretical Artificial Intelligence* 17(1-2), 19-33 (2005). DOI `10.1080/09528130512331315936`.

**Primary evidence:** Direct [Taylor & Francis article](https://www.tandfonline.com/doi/abs/10.1080/09528130512331315936), full-text, and PDF access failed. Indexed text from the [author's Helsinki institutional record](https://researchportal.helsinki.fi/en/publications/on-look-ahead-and-pathology-in-decision-tree-learning/) and the successfully retrieved [publisher-deposited DOI record](https://api.crossref.org/works/10.1080%2F09528130512331315936) verify the metadata. The corresponding-author asterisk in the deposited author field is not part of Elomaa's surname.

**Substantive access/support:** The [author-uploaded ResearchGate item](https://www.researchgate.net/publication/220080316_On_look-ahead_and_pathology_in_decision_tree_learning) explicitly identifies Tapio Elomaa's upload. Its abstract discusses game-tree pathology, its connection to induction, and a computationally efficient numerical-domain splitting method with promising experiments. Full original body text was not obtained. The [publisher's special-issue introduction, Section 2](https://www.tandfonline.com/doi/full/10.1080/09528130512331315909), provides additional indexed primary editorial context.

**Correction/limit:** No bibliographic change. Tuomo, not Timo; current initials are correct. "Revisited pathology" is supported. Detailed algorithm equivalence or numerical results remain unverified. This source must not be used to assert that all lookahead is harmful: even the accessible author abstract reports a promising method.

### 11. `esmeir2007anytime`

**Record:** Saher Esmeir, Shaul Markovitch. "Anytime learning of decision trees." *Journal of Machine Learning Research* 8, 891-933 (2007). The journal identifies the paper as 8(33); 33 is its paper identifier, not a journal issue that must be inserted. No DOI is supplied or displayed on the inspected journal record.

**Primary evidence:** [Official JMLR record](https://www.jmlr.org/papers/v8/esmeir07a.html) and [published PDF](https://www.jmlr.org/papers/volume8/esmeir07a/esmeir07a.pdf), 43 pages, verify authors, title, year, venue, and pages.

**Substantive reading/support:** Sections 2.2-2.3, pp. 896-897, discuss fixed-depth lookahead and sampling consistent trees to estimate small attainable tree size; Section 3 develops anytime methods. Sections 4.5.1-4.5.2, pp. 918-921, compare bagged greedy learners with Bagging-LSID3. The end of that discussion explicitly raises the trade-off between resources spent on each tree and the number of ensemble members.

**Correction/limit:** None. The anytime-computation citation is sound but incomplete as a history of non-greedy ensembles. Acknowledge its ensemble experiment when positioning the contribution. Its size-oriented sampled-tree evaluation is different from exhaustive bounded terminal Gini. It does not preclude novelty of the present empirical heterogeneous-horizon study, but precludes claiming the general resource-allocation question or non-greedy committees are new.

### 12. `norouzi2015efficient`

**Record:** Mohammad Norouzi, Maxwell D. Collins, Matthew A. Johnson, David J. Fleet, Pushmeet Kohli. "Efficient non-greedy optimization of decision trees." *Advances in Neural Information Processing Systems* 28, 1729-1737 (2015). No DOI is supplied.

**Primary evidence:** [Official NeurIPS proceedings record](https://proceedings.neurips.cc/paper/2015/hash/1579779b98ce9edb98dd85606f2c119d-Abstract.html), [proceedings PDF](https://proceedings.neurips.cc/paper_files/paper/2015/file/1579779b98ce9edb98dd85606f2c119d-Paper.pdf), and [official metadata JSON](https://proceedings.neurips.cc/paper_files/paper/2015/file/1579779b98ce9edb98dd85606f2c119d-Metadata.json). The JSON explicitly gives published pages 1729-1737; the PDF's local pages 1-9 are not a contradictory interval. Proceedings metadata and the title page jointly support the current author initials. No DOI was found in these records.

**Substantive reading/support:** Sections 1-3 formulate joint optimization of oblique split parameters and leaf predictions using an upper-bound/surrogate objective and stochastic optimization. This supports the manuscript's "different form of non-greediness" distinction.

**Correction/limit:** No factual correction. Optional improvement: add the official proceedings URL to the bibliography. This is neither exhaustive axis-aligned local Gini search nor a certificate of globally optimal trees. It does not establish the shallow-depth or heterogeneous-horizon accuracy claims.

### 13. `donick2021stepwise`

**Record:** Delilah Donick, Sandro Claudio Lera. "Uncovering feature interdependencies in high-noise environments with stepwise lookahead decision forests." *Scientific Reports* 11, article 9238 (2021). DOI `10.1038/s41598-021-88571-3`. Published 29 April 2021.

**Primary evidence:** [Nature publisher full article](https://www.nature.com/articles/s41598-021-88571-3) verifies all bibliographic fields and supplies substantive text.

**Substantive reading/support:** Methods, "Random forest with stepwise lookahead decision trees," including equation (4), scores a two-generation, three-split-node block by weighted terminal Gini. Its stepwise construction fixes the block rather than retaining only its root. Candidate thresholds can use quantile buckets; it is not automatically the same candidate search as uncapped midpoint enumeration. The noisy-interaction experiments and financial application support its relevance as a direct forest precedent, not universal superiority.

**Correction:** Replace `Scientific Reports 11 (2021) 9238, article 9238.` with `Scientific Reports 11 (2021), article 9238.` or the journal style's equivalent single article identifier. Keep the authors, title, year, and DOI.

**Claim limit:** The technical contrast in Related work is supported. "The closest forest precedent" is an interpretive ranking, not something this single source can prove; "A direct forest precedent" is safer, with entry 11's earlier ensemble experiments also acknowledged. The root-only rule itself is not new; see entries 7 and 9.

### 14. `geurts2006extremely`

**Record:** Pierre Geurts, Damien Ernst, Louis Wehenkel. "Extremely randomized trees." *Machine Learning* 63(1), 3-42 (2006). DOI `10.1007/s10994-006-6226-1`.

**Primary evidence:** [Springer article record](https://link.springer.com/article/10.1007/s10994-006-6226-1), [publisher PDF](https://link.springer.com/content/pdf/10.1007/s10994-006-6226-1.pdf), and [authors' institutional repository record](https://orbi.uliege.be/handle/2268/9357). These verify author order, title, year, volume/issue, pages, and DOI. The journal issue is April 2006, with online publication in March 2006.

**Substantive reading/support:** Section 2.1, pp. 5-6, chooses random feature/threshold candidates and then selects a scored candidate. Its main construction uses the full learning sample rather than bootstrap resampling and grows unpruned trees. It supports randomized splitting as a different way of varying ensemble members.

**Correction/limit:** None. This is not mixed-horizon induction or randomized final depth. Do not imply every Extra-Trees split ignores labels: scoring among multiple randomized candidates uses the response. Nor does the paper prove that heterogeneity necessarily creates beneficial ensemble diversity or that shallow forests are generally better.

### 15. `horn2026randomdepth`

**Record:** Daniel Horn, Tobias Markus Krabel, Thi Ngoc Tien Tran, Andreas Groll, Carsten Jentsch. "The impact of random tree depth---a novel randomization process for ensemble methods." *Computational Statistics* 41, article 25 (2026). DOI `10.1007/s00180-025-01697-0`.

**Primary evidence:** [Springer publisher full article](https://link.springer.com/article/10.1007/s00180-025-01697-0) verifies the authors/order, title, volume, article identifier, DOI, and publication date of 3 January 2026. Acceptance in September 2025 and the DOI's `025` do not change the publication year.

**Substantive reading/support:** Sections 1-3 define random final depth bounds, sampled between one and an upper limit. Sections 4.3-4.4 and the Conclusion distinguish boosting/MART from random forests: boosting can be attractive, whereas random forests generally trade worse accuracy for reduced runtime. This supports varying final depth, not a generally beneficial depth-three prescription.

**Correction:** Replace `Computational Statistics 41 (2026) 25, article 25.` with `Computational Statistics 41 (2026), article 25.` or the equivalent single-identifier style. Keep 2026 and the DOI unchanged.

**Claim limit:** Random final depth changes capacity; the manuscript's lookahead horizon changes split search at fixed capacity. These must remain distinct. Do not cite the boosting gains as direct evidence for bagged classification forests.

### 16. `kuncheva2003diversity`

**Record:** Ludmila I. Kuncheva, Christopher J. Whitaker. "Measures of diversity in classifier ensembles and their relationship with the ensemble accuracy." *Machine Learning* 51(2), 181-207 (2003). DOI `10.1023/A:1022859003006`.

**Primary evidence:** [Springer article record](https://link.springer.com/article/10.1023/A:1022859003006), [publisher PDF](https://link.springer.com/content/pdf/10.1023/A:1022859003006.pdf), and the indexed [author's Bangor institutional record](https://research.bangor.ac.uk/en/publications/measures-of-diversity-in-classifier-ensembles-and-their-relations/). The latter explicitly identifies issue 2; the publication month is May 2003.

**Substantive reading/support:** Section 6's experiments and Section 7's discussion, especially pp. 202-203, examine several diversity measures and how their relationships with accuracy depend on the setting. Simple general monotone relationships do not follow from the experiments; particular controlled cases can exhibit relationships.

**Correction/limit:** Current volume-only citation is acceptable; optional consistency improvement is `51~(2)`. The general diversity-background citation is appropriate. This work does not establish that the current horizon mixture works by increased diversity, nor that diversity is irrelevant. Architectural heterogeneity, measured predictive disagreement, and a causal improvement mechanism are different claims. No diversity mechanism should be inferred without corresponding measurements/analysis.

## Manuscript Claim Checks and Proposed Wording

These are recommendations for the parent editor, not edits to `main.tex`. Claims from the paper's experiments, statistical tests, implementation, or entries 17-32 are outside this audit.

### Shallow-Tree Literature: Appropriate With Explicit Boundaries

The Introduction's "limiting member size can regularize" / "smaller trees can be beneficial in noisy settings" language is defensible with entries 2 and 3. The Tree-size regularization subsection distinguishes regression literature from the present bootstrap Gini classifiers and includes deeper controls; the quantile-split terminology clarification in entry 3 would improve precision. Do not turn this motivation into a literature-backed choice of an optimal depth-three default.

Suggested compact qualification for that subsection, using the already retained citations:

> These results motivate studying constrained member size rather than a universal depth-three default: the regression studies vary leaf limits and resampling, and Duroux and Scornet's small-tree empirical alternative also removes bootstrap resampling.

This avoids three unsupported inferences: a leaf-count limit equals a common path-depth limit; a comparison changing resampling isolates depth alone; and regression results establish an optimum for classification. A depth-three binary member has at most eight leaves, but neither source prescribes that value, and an ensemble can express more regions than one member. Entries 1, 4, 5, 6, 14, and 16 are not substitutes for evidence of a generally optimal shallow forest. Entry 15 is especially unsuitable as an unqualified shallow-random-forest endorsement because its random-forest findings differ from its boosting findings.

### Prior Art and Computation Allocation

The current manuscript says the split-search principle is well studied and locates its contribution in empirical horizon allocation. Preserve that framing. The strongest source-grounded improvements would be:

1. Describe Norton/IDX as overlapping lookahead that commits only the shallowest choice, rather than only as downstream-quality work. This puts the root-only rule's history beside the later contrast with blockwise forests.
2. Mention that Esmeir and Markovitch already compare greedy and non-greedy bagged committees and discuss per-tree computation versus committee size (Section 4.5.2, pp. 919-921).
3. Change "The closest forest precedent" to "A direct forest precedent" unless "closest" is explicitly qualified by the bounded weighted-Gini block-search criterion. "Closest" is a reasonable technical judgment, not verified priority or an exhaustive literature result.

Suggested sentence covering point 2:

> Earlier anytime-tree work also compared bagged greedy and non-greedy learners and discussed the trade-off between computation per tree and ensemble size.

Use the existing `esmeir2007anytime` citation. This does not require adding or deleting references. The inspected prior-art sources do not establish the present empirical finding that a minority of longer-horizon members improves these shallow ensembles; they establish that neither non-greedy committees nor the broad resource-allocation question begins here.

### Claims That Must Not Be Inferred

- A universal or theoretically justified depth-three optimum: unsupported by entries 1-16.
- Fixed-depth bootstrap Gini-classifier consistency: not supplied by the quantile-regression theory in entry 3 or the tree-count convergence discussion in entry 6.
- Root-only bounded lookahead as a newly introduced algorithmic principle: contradicted by entries 7 and 9.
- The first forest/committee of non-greedy trees, or the first per-tree-cost versus ensemble-size question: contradicted by entries 11 and 13.
- Guaranteed accuracy gains from lookahead, random splitting, random depth, or heterogeneity: unsupported; several sources explicitly motivate conditional trade-offs.
- "Diversity explains the gains" as a demonstrated mechanism: entry 16 does not supply that causal inference for the present models.

These are boundaries on interpretation, not a claim that the current manuscript explicitly makes every overstatement. Its present conditional and empirical framing largely avoids them. The specific remaining attribution risk is the unqualified "closest" wording combined with underdescribing entry 11's ensemble experiments.

## Precise Bibliographic Actions for the Parent

| Entry/key | Action | Reason |
| --- | --- | --- |
| 13 / `donick2021stepwise` | Render article 9238 once, not `9238, article 9238` | Article identifier, not pages; current duplication is unnecessary. |
| 15 / `horn2026randomdepth` | Render article 25 once, not `25, article 25` | Same presentation issue; keep the verified 2026 year. |
| 12 / `norouzi2015efficient` | Optionally add the official NeurIPS proceedings URL above | Improves traceability; current metadata is correct. |
| 16 / `kuncheva2003diversity` | Optionally add issue `(2)` | Confirmed by the author's institutional record; omission is not an error. |
| 1 / `breiman1984cart` | Keep original-edition citation and author order; no unverified DOI addition | Avoid conflating current reprint catalogue metadata with the 1984 book. |
| 2 / `zhou2023trees` | Keep 2023, with the existing 2022 online-first note | Both dates are independently meaningful. |
| 8 / `ragavan1993lookahead` | Keep current initials/DOI/pages; if names are expanded, use Harish | Primary metadata is verified; full chapter reading remains incomplete. |
| 9 / `murthy1995lookahead` | Keep 1025-1031 | Official final printed page is 1031. |
| 10 / `elomaa2005lookahead` | Keep current initials/metadata; if names are expanded, use Tuomo | Full body unavailable, not a bibliographic error. |
| Remaining audited entries | No correction indicated | No conflicting primary evidence was found. |

## Residual Verification Limits

The most material unresolved reading is the complete ICML chapter in entry 8 and complete article body in entry 10. Their identities and bibliographic fields are supported, but their detailed results are not certified here. For entries 2, 5, and 6, substantive checks used identified author preprints/manuscripts alongside publisher final-publication metadata; version-specific wording or result changes were not exhaustively compared. Entry 1 used a publisher-origin reprint preview for substantive book content, with author-origin references establishing the original imprint citation. For entries 7, 9, 11, and 12, no DOI was found in the inspected official proceedings/journal sources; omission is retained, without claiming that a DOI search can prove nonexistence.

No evidence found warrants removing a reference, changing the experimental record, or running any model. The parent can apply the narrow presentation fixes and attribution qualifications independently of this report.

## Focused Scientific and Editorial Pass on the Rewritten Draft

Review date: 10 October 2026, approximately 11:55 UTC. This addendum concerns the parent's CURRENT rewritten draft, not an earlier manuscript. The inspected `main.tex` has 932 lines and SHA-256 `70fee24e3eb1e301147a65a3ccd9611c866da5d92ca88836bba81a4099dc9fb4`. Line references below belong to that snapshot; quoted anchors remain useful after integration.

Scope: read the current abstract, Introduction, Related work, Method, protocol, numerical tables, Results prose/captions, Discussion, and Conclusion. Consulted the existing `paper/array_revision_fair/analysis/full/summary.csv`, `protocol_snapshot.json`, and `validation.json` read-only. The CSV checks below are arithmetic on already recorded aggregate results, not fits, new inferential analyses, or regeneration of figures. This is not a fresh implementation audit or a cell-by-cell revalidation of every numerical block. Only this report was edited.

### Findings and Changes Needed

1. **[P2, wording] Distinguish a replacement effect from a demonstrated mixing mechanism.** Discussion, line 619: "the fixed replacement comparisons isolate the contribution of mixing." The fixed controls do isolate the observed effect of replacing the designated greedy members at fixed ensemble size and common settings. They do not separately identify a causal benefit of heterogeneity, as opposed to the predictive quality of the substituted learners, or prove that mixing is preferable to every pure farther-sighted architecture. The Figure 2 prose appropriately acknowledges a competitive pure two-sighted forest. Replace the quoted clause with "the fixed comparisons isolate the effect of replacing specified greedy members with farther-sighted members." This retains the positive finding and matches the more precise wording already used in the Introduction, line 30. No additional experiment is required to make this wording correction.

2. **[P2, interpretation] Do not make the depth controls sound like a mechanism experiment.** Discussion, line 621: "The depth controls explain where this strategy is most useful." Prefer "The depth controls indicate where the observed benefits are strongest." The subsequent recovery-of-partitions and overfitting accounts are plausible interpretations, not experimentally separated causes. Importantly, the existing "consistent with overfitting" and "plausible explanation to test" at lines 627-631 are already appropriately cautious and should remain. Increased realized depth plus worse test accuracy does not by itself establish a larger training-validation gap, nor does the study directly track whether greedy trees recover the same interactions later. This is a wording refinement, not a demand for new training curves in the present revision.

3. **[P3, concrete unit correction] Relabel the 219/285 count.** Discussion, lines 625-626: RF chooses depth six or unrestricted depth in "219 of 285 tasks." The 285 denominator is 57 datasets times five repetitions, not 285 independent benchmark datasets. The result is correct as a count of selections: 87 depth-six plus 132 unrestricted. Write "219 of 285 outer dataset-repetition selections." The Results' "285 inclusive choices" is already a suitable label. This avoids suggesting a larger independent task sample than was studied.

4. **[P3, literature precision] Apply the existing shallow-literature qualifications.** Tree-size regularization, line 48: use "quantile-split regression forests" for Duroux-Scornet, and briefly note the resampling change in their small-tree empirical alternative. See entry 3 above for primary evidence. The current paragraph already distinguishes the present bootstrap Gini classifiers from regression motivation, so no reversal of the shallow-forest rationale is needed. The Introduction's conditional "can regularize" and "can be beneficial" at line 32 are suitable. Neither reference identifies depth three as generally optimal.

### Agree: Positive Benchmark-Mean Framing

The title's "can improve" is appropriately bounded. The abstract and Introduction explicitly speak about mean accuracy, distinguish fixed replacements from expanded-family tuning, and report the additional computation. There is no need to replace these empirical positive statements with a blanket "no improvement" interpretation merely because some adjusted signed-rank tests do not reject.

Table 2's four primary depth-three replacement mean effects are all positive: 1.06 and 1.27 percentage points with all features, and 0.42 and 1.04 with square-root features. The Discussion correctly states that three of the four adjusted signed-rank values are below 0.05. The fourth is 0.09539, not a significant adjusted test. Methods explicitly distinguishes pointwise unadjusted mean-effect intervals from the signed-rank location tests, and the limitations correctly reports zero medians, heterogeneity, and sensitivity to benchmark weighting/membership. Preserve these distinctions; neither a positive mean nor a positive pointwise interval establishes a typical-dataset gain or simultaneous significance across settings.

The tuned-family paragraph is also defensible as evidence about the observed benchmark mean under the original equal-dataset weighting. It correctly says the inclusive family can select pure forests as well as mixtures. The mean interval above zero does not contradict its adjusted signed-rank value of 0.48838, since these summarize/test different aspects of the distribution. Keep the following sensitivity paragraph: the family-weighted and non-synthetic-subset mean intervals cross zero. "Strengthens the predictive finding" is acceptable as bounded corroboration, not as evidence of universal or weighting-robust superiority; adding "under the original benchmark weighting" would make that scope explicit.

### Agree With a Scope Clarification: "Consistently" in the Conclusion

Conclusion, lines 667-668: "Sparse farther-sighted replacements can consistently improve mean accuracy across the shallow settings studied here."

The underlying descriptive assertion is supported, not contradicted by the nonsignificant fourth primary test. A read-only comparison of existing `summary.csv` rows found all 40 depth-three settings formed by 5% or 10% replacement, horizons two or three, both feature policies, and five ensemble sizes have positive benchmark-mean accuracy differences from their same-size/same-policy pure-CART controls. The smallest is approximately 0.168 percentage points for `D3_L1_Fsqrt__T040__pair_k1_k2_q05`. These are descriptive signs across configurations, not 40 independent confirmations or 40 multiplicity-adjusted tests.

**Recommendation:** keep the positive result, but make "consistently" refer unambiguously to observed configuration means, not to reliable gains on every dataset or future benchmark. A clean replacement is:

> Across the tested depth-three settings, sparse replacements yielded higher observed benchmark-mean accuracy than their matched greedy controls.

An even narrower, directly table-supported version is:

> Sparse replacements increased benchmark-mean accuracy in all four primary depth-three comparisons.

The current sentence is defensible if read descriptively; this is a precision improvement rather than a finding of numerical falsity. Do not imply that every task/repetition benefits, that every shallow contrast passes adjusted inference, or that the result extends to all depths. "Observed benchmark-mean" also improves the abstract's first mean-effect statement without weakening it.

### Agree: Matched Controls and Tuning Fairness

The fixed-control description in lines 65-70 and the protocol is well aligned with the scientific comparison: matched permitted depth, split/leaf minima, feature policy, unpruned fitting, bootstrap positions/seeds, ensemble size, and scoring. It now avoids a pruned-versus-unpruned or tuned-versus-untuned contrast. Matching a feature policy need not mean identical feature sets at corresponding hypothetical nodes after the trees diverge; the manuscript does not need to claim that stronger condition. Likewise, matching a depth bound is not matching realized tree shape, leaf count, or fitting work. The tables make realized-depth differences visible.

Training-only tuning uses the same common structural grid, inner folds, and outer evaluation separation. The 48/288/768 candidate counts and large selection costs are disclosed, and both expanded families include the greedy option. This is a valid comparison of the specified model families under their specified search procedures; it is not an equal-computation or equal-number-of-candidates comparison. The current limitations recognizes that distinction. "Fairly tuned" in the Conclusion can be retained in that limited sense, although "training-only tuning with matched common hyperparameters" is more precise and less evaluative. No claim is made here that the external implementation or selection code was independently reverified during this editorial pass.

### Agree: Figure 2 Is a Descriptive Lower-Mean-Work Example

The new example at lines 490-498 matches both plotted coordinates and the existing aggregate CSV:

| Architecture, depth three, all features | Observed mean accuracy | Benchmark-mean member-fitting work |
| --- | --- | --- |
| 20 members: 15 greedy plus 5 two-sighted | 74.063578% | 0.0954602 s |
| 200 greedy members | 73.020360% | 0.1338263 s |
| 20 members: 18 greedy plus 2 two-sighted | 73.372712% | 0.0470039 s |
| 20 pure two-sighted members | 74.790382% | 0.3381338 s |

For the first versus second row, the gain is 1.043218 percentage points and the ratio-of-means work reduction is 28.6686%, so the manuscript's 1.04 points and "about 29%" are correct. The comparison supports "higher observed mean accuracy with lower benchmark-mean member-fitting work" for those two fixed architectures. It is not exact equal-time matching, a per-dataset budget guarantee, a whole-training-workflow speedup, or an estimate of the best attainable greedy accuracy under every resource cap. It excludes selection, bootstrap preparation, construction, and prediction as specified in Methods.

The figure caption labels the curves descriptive, and the later limitations explicitly covers benchmark means, untested interpolation, excluded selection, pure-forest alternatives, and training-only resource-constrained deployment. That combination is scientifically appropriate. Keep the concrete positive example and the sentence acknowledging the competitive pure two-sighted forest below 0.7 s; do not promote the example to universal Pareto dominance or an equal-time proof. "In this example" is an important existing qualifier.

### Editorial Bottom Line

Agree with the rewritten draft's positive empirical emphasis and its separation of fixed replacement effects, family-selection benefits, and computation scopes. The principal changes needed are the replacement-effect wording, the noncausal depth-control lead-in, the 285-selection unit, and the already identified shallow-literature precision. The conclusion's "consistently" is supported descriptively but is clearer as "higher observed benchmark-mean accuracy" with an explicit depth-three scope. Keep the overfitting explanation as a hypothesis, not a demonstrated cause. No numerical cells, full plot blocks, figures, or PDFs need changes for these recommendations, and no new fits were run.

## Final Read-Only Review After Integration

Checked 10 October 2026, approximately 12:00 UTC. Current `main.tex`: 937 lines; SHA-256 `080c18db915beb891c6afa23dd90371f1b47ec3705a0b54e36da9029ae391d16`. This final status supersedes the previous scientific pass's requests for changes; that pass is retained above as an audit trail.

**Assessment: agree with the integrated scientific/editorial wording. No residual material issue was identified within the focused review scope.**

- The Discussion now identifies the effect of replacing specified greedy members, rather than claiming an independently established heterogeneity/mixing mechanism.
- The depth controls now "indicate" the strongest observed benefits, and greedy induction "may" recover useful partitions. The overfitting account remains explicitly a plausible explanation requiring further testing, not a demonstrated cause.
- The 219/285 count is correctly labeled outer dataset-repetition selections, avoiding an implication of 285 independent datasets.
- The tuned-family finding is qualified by original benchmark weighting. The sensitivity results, zero median, and non-rejecting adjusted signed-rank test remain visible, so the positive mean claim is not presented as universal or weighting-robust superiority.
- The Conclusion's retained "consistently" now modifies a past-tense observation of higher benchmark-mean accuracy across tested depth-three settings. This is compatible with the prior read-only check of all 40 sparse 5%/10% replacement configurations. It does not claim every dataset benefits or every adjusted test rejects; no further change is requested.
- Training-only tuning with matched common hyperparameters is now the explicit description. The disclosed unequal candidate counts and selection costs continue to distinguish comparable structural choices from equal-computation comparisons.
- The shallow-literature paragraph now uses quantile-split terminology, states the resampling difference, and rejects a universal classification-depth prescription. Norton, Esmeir-Markovitch, and the direct Donick-Lera precedent are now positioned consistently with the primary-source audit.
- Figure 2 retains the verified 20-member 75/25 example, 74.06% at 0.0955 s versus 73.02% at 0.1338 s. Its descriptive caption and computation limitations support lower benchmark-mean member-fitting work, without an exact equal-time, per-dataset budget, or universal best-pure-forest claim.

The bibliography now also renders article numbers once in entries 13 and 15, includes the official proceedings URL for entry 12, and includes issue 2 for entry 16. These resolve the narrow presentation recommendations from this half of the reference audit.

Residual verification limits are unchanged: full original bodies for references 8 and 10 were not obtained, as documented above. Final agreement is not a new certification of every implementation detail, numeric cell, or unavailable source portion. No additional scientific/editorial change is requested on the reviewed points. Only this report was written; `main.tex` was read-only. No fits, native-editor opening, compilation, PDF export, or figure regeneration was performed.

## Latest Source Recheck and Reviewed Hash

Checked 10 October 2026. The current `main.tex` SHA-256 matches the parent's supplied value:

`38ef96694143de238dab6f39dc96a00873c54660f53711808dc7a9a66737331a`

**Final agreement remains unchanged: no residual material issue found in the reviewed changes.** This hash supersedes the preceding reviewed hash; earlier assessments remain as history.

The ensemble-position and member-fitting-work wording preserves the matched-control and cost definitions. Naming DL8.5, MurTree, and STreeD makes the existing related-work attribution more explicit, consistently with the [AAAI DL8.5 abstract](https://ojs.aaai.org/index.php/AAAI/article/view/5711), [JMLR MurTree record](https://jmlr.org/papers/v23/20-520.html), and [STreeD proceedings paper, Introduction and Section 3](https://proceedings.neurips.cc/paper_files/paper/2023/file/1d5fce9627e15c84db572a66e029b1fc-Paper-Conference.pdf). The [Demsar journal abstract](https://jmlr.org/papers/v7/demsar06a.html) supports the general paired-test citation; zero omission is now clearly this study's calculation rule, not attributed to that source.

The [official Hu proceedings record](https://proceedings.neurips.cc/paper/2019/hash/ac52c626afc10d4075708ac4c778ddfc-Abstract.html) supports the electronic citation's authors, title, volume 32, and 2019 year; no unverified page interval is needed. The [Aghaei publisher record](https://pubsonline.informs.org/doi/10.1287/opre.2021.0034) explicitly gives online publication on 31 July 2024 and a July-August 2025 volume 73(4) issue, with pages 2223-2241. Retaining the issue year while stating online-first timing is clear; the publisher's automated "Cite as" uses 2024, so the two dates should not be silently conflated.

These were focused source/wording checks, not a new full audit of references 17-32 or all numeric cells. Previous access limits remain documented. Only this report was updated. No manuscript edit, editor opening, export, compilation, figure regeneration, or fit was performed.

## Final Cross-Review After Figure 2 Attribution Fix

Read-only check on 10 October 2026 confirms the current `main.tex` SHA-256:

`4c31ad499b8bcc2c926b5d84c057757c1a82610be9084e8d9c599aad3752d01e`

This is the latest reviewed hash and supersedes the earlier hash above. Read current lines 489-495 and the companion `annotation_reference_audit_2.md` final review and closing Figure 2 addendum.

**Final agreement: the attribution fix is correct; no residual material issue or requested correction remains within this focused cross-review.** The sentence now explicitly assigns 73.37% mean accuracy and 0.0470 s member-fitting work to the 20-member mixture with two two-sighted members. The preceding text separately assigns 73.02% and 0.1338 s to the 200-member greedy comparator. The grammatical ambiguity correctly identified by audit 2, but not flagged in my earlier pass, is resolved. The comparison remains a descriptive higher-mean-accuracy/lower-mean-work observation, not an exact-time guarantee.

Agree with audit 2's final assessment and its explicitly disclosed source-access limits. This narrow recheck does not independently recertify its entire reference range or all numerical data. Prior verification limits in both reports remain disclosed, not new requests for work. Only this report was updated; no new research, manuscript edits, fits, PDF operations, editor opening, or exports were performed.
