# Reference Audit 2: Entries 17-32

Audit date: 2026-10-10. Scope: the sixteen bibliography items from `bertsimas2017optimal` through `holm1979sequential` in `main.tex`, plus their manuscript uses. Prepared for Mathias's annotated-PDF revision. This is an audit report, not a manuscript edit.

## Final Status and Integration Notes

**Final update following the requested checkpoint and a fresh read of the current draft on 2026-10-10.** All sixteen works exist; each entry's authors, title, year, venue, pagination/article identifier where supplied, and DOI or official identifier record have been checked with the limitations below. The Hu electronic citation avoids an unresolved printed-edition pagination conflict. No further bibliographic change is required in the current `main.tex`. One minor Figure 2 attribution clarification remains, described in the focused review below.

The current manuscript contains the Hu electronic URL without pages, Aghaei's first-online note with the 2025 issue year, explicit DL8.5/MurTree/STreeD naming, and study-specific zero omission separated from the Demsar citation. The user independently reports corresponding BibTeX changes and successful native compilation; neither compilation nor a fresh BibTeX-file inspection was performed by this audit. Source-access limitations are intentional: a search hit is not full-text verification, an arXiv DOI is not a journal DOI, and an ordinary author manuscript alone does not establish final publisher pagination.

1. **Entry 19, Hu et al.: primary-source pagination conflict.** The manuscript gives `7265--7273`. NeurIPS's own BibTeX leaves `pages` empty. Curran's printed-volume contents instead puts this article at 7235 and the next article at 7244, implying **7235--7243** for that edition, consistent with the nine-page paper. Do not silently replace one edition's pages with another's. Safest electronic-proceedings correction: omit pages and add the official NeurIPS URL; alternatively use 7235--7243 explicitly for the checked Curran edition. See entry 19.
2. **Entry 24, Aghaei et al.: document a date discrepancy, not a fabricated-paper problem.** The publisher assigns the paper to volume 73(4), July-August **2025**, pp. 2223--2241, but states first online publication on **31 July 2024** and generates a `Cite as` string using 2024. Retaining 2025 as the issue year is defensible; adding the online date would remove ambiguity. The `2021` inside the DOI is not the publication year.
3. **Entry 26, SPLIT: retain 2025, PMLR 267, 2114--2175.** The unusually long page range is explicitly present in PMLR's official citation. SPLIT and LicketySPLIT are real and substantively relevant. Their distinction from the manuscript's terminal-Gini objective should remain explicit. Optional precision: SPLIT includes an optimal-subtree postprocessing option, while LicketySPLIT recursively repeats one-step search with greedy-completion scoring.
4. **Entry 23, STreeD: retain the title, NeurIPS 36 (2023), 9173--9212, DOI `10.52202/075280-0404`.** The DOI and page range are in the official NeurIPS BibTeX. STreeD is the method introduced in the cited paper, not a mismatched title.
5. **Entry 27, TMLR 2026: retain the journal/year.** TMLR's official accepted-paper index lists this exact work in **August 2026**; its official BibTeX also authenticates the journal and 2026 year. Author manuscript v3 is dated 6 August 2026 and declares TMLR (2026). OpenReview forum and final-PDF endpoints presented browser verification; this audit has not inspected the final OpenReview artifact or acceptance discussion. Do not downgrade the work to a 2024 preprint merely because its first arXiv version is from 2024.
6. **Entry 18: do not change 1625--1632 to 1624--1632.** Official AAAI metadata and the paper itself start at 1625; the DOI's ending `1624` is not the first page.
7. **Entry 32, Holm: retain the current stable URL and bibliographic fields.** Publisher/official archival metadata supports them. The official issue contents links to a DOI-bearing XML export for `10.2307/4615733`, authenticating that identifier's association with the article, although the resolver/XML payload was not readable. Adding the DOI is optional, not a necessary correction. The original argument was read in a clearly identified university-hosted JSTOR facsimile because the official full-text endpoints did not expose readable text.
8. **Entry 28, Scornet: all metadata now confirmed.** The author-hosted published electronic reprint explicitly prints the journal, 2015, volume 43, issue 4, pages 1716--1741, and DOI on its first page. Its notice warns that the reprint's own pagination differs; no metadata field needs to await Project Euclid access.

## Method and Boundaries

- The initial and final manuscript snapshots were read from the filesystem, not opened in an application. The final focused review used the current abstract, related work, methods/protocol, tables, Figure 2 coordinates/caption/text, discussion including Section 6.1, conclusion, and corrected inline references. Earlier checkpoint line numbers are superseded; the final review gives current anchors, which can still move with concurrent revisions.
- Metadata was checked on publishers, official proceedings, journal indexes, and author-deposited manuscripts. Direct URLs are included so another reviewer can reproduce the checks. Unsupported BibTeX downloads were read directly over HTTPS without saving local copies.
- Substantive checking means reading the identified methods, theorems, experiments, or recommendations, not just finding a matching title. Summaries below are paraphrases.
- No model fits, benchmark runs, figure changes, PDF exports, or manuscript modifications were performed. The only audit write is this report. Other agents' work is outside this audit's ownership.
- `No DOI supplied by checked record` means precisely that; it is not proof that no identifier exists anywhere. Optional issue numbers and URLs are distinguished from genuine errors.

## Entry-by-Entry Findings

### 17. `bertsimas2017optimal`

**Metadata:** Dimitris Bertsimas; Jack Dunn. *Optimal classification trees*. **Machine Learning 106(7), 1039--1082 (2017)**. DOI **10.1007/s10994-017-5633-9**. All listed fields match. Springer states online publication 3 April 2017 and issue date July 2017.

**Primary sources:** [Springer article record](https://link.springer.com/article/10.1007/s10994-017-5633-9); [Bertsimas's MIT-hosted personal copy of the published paper](https://web.mit.edu/dbertsim/www/papers/Machine%20Learning%20under%20a%20Modern%20Optimization%20Lens/Optimal_classification_trees_MachineLearning.pdf).

**Substance read:** Mixed-integer tree formulation and computational comparison; the shallow-tree results and appendix tables for depths 3 and 4 were inspected. The paper optimizes whole, size-controlled classification trees, including axis-aligned and hyperplane variants. Its comparisons concern single-tree accuracy, not bootstrap forests.

**Manuscript support:** The related-work mathematical-programming statement is supported. The tree-size paragraph's narrowly worded motivation from competitive shallow single trees is supported; it correctly does not infer depth-three forest optimality. **Correction:** none.

### 18. `verwer2019learning`

**Metadata:** Sicco Verwer; Yingqian Zhang. *Learning Optimal Classification Trees Using a Binary Linear Program Formulation*. **Proceedings of the AAAI Conference on Artificial Intelligence 33(01), 1625--1632 (2019)**. DOI **10.1609/aaai.v33i01.33011624**. All manuscript fields match; issue 01 is optional.

**Primary sources:** [AAAI article record](https://ojs.aaai.org/index.php/AAAI/article/view/3978); [official paper](https://ojs.aaai.org/index.php/AAAI/article/view/3978/3856). An initially attempted different AAAI article number was not used as evidence.

**Substance read:** The BinOCT formulation, Boolean threshold encoding, and counts of decision variables and constraints, especially pp. 1625--1629. It minimizes training classification error at a prescribed depth. Decision-variable dependence is reduced; the paper still acknowledges row-dependent constraints.

**Manuscript support:** Supports mathematical programming as a distinct optimal-tree approach. It does not certify this manuscript's Gini recursion or its runtime. **Correction:** none; retain first page 1625 despite the DOI suffix.

### 19. `hu2019optimal`

**Metadata:** Xiyang Hu; Cynthia Rudin; Margo Seltzer. *Optimal Sparse Decision Trees*. **Advances in Neural Information Processing Systems 32 (2019)**. Authors, title, year, and venue match. No DOI is supplied on the checked official article/BibTeX record.

**Primary sources:** [NeurIPS record](https://proceedings.neurips.cc/paper/2019/hash/ac52c626afc10d4075708ac4c778ddfc-Abstract.html); [official nine-page paper](https://proceedings.neurips.cc/paper_files/paper/2019/file/ac52c626afc10d4075708ac4c778ddfc-Paper.pdf); [official BibTeX with empty pages](https://proceedings.neurips.cc/paper_files/paper/2019/file/ac52c626afc10d4075708ac4c778ddfc-Bibtex.bib); [Curran printed-volume contents, PDF page 24](https://www.proceedings.com/content/053/053719webtoc.pdf).

**Pagination finding:** The manuscript's `7265--7273` is not confirmed by the official electronic record. Curran's contents lists this paper starting at **7235**, followed by another paper at **7244**. Thus **7235--7243** is supported for that checked printed edition, with the endpoint inferred from the next start and paper length. This is an edition discrepancy, not evidence that the paper is nonexistent.

**Substance read:** Sections 3.1--3.3: misclassification plus a leaf-count penalty, analytical bounds, and branch-and-bound pruning. Supports the manuscript's bounds/caching literature context, but is not the same objective as terminal Gini.

**Recommended correction:** Prefer no page range plus the NeurIPS URL for the electronic proceedings, or explicitly cite the checked printed edition. Do not assert 7265--7273 was primary-verified. Further reconciliation of the alternate pagination remains open.

### 20. `lin2020generalized`

**Metadata:** Jimmy Lin; Chudi Zhong; Diane Hu; Cynthia Rudin; Margo Seltzer. *Generalized and Scalable Optimal Sparse Decision Trees*. **Proceedings of the 37th International Conference on Machine Learning, PMLR 119:6150--6160 (2020)**. All fields match. No DOI supplied by the official PMLR citation.

**Primary sources:** [PMLR record and citation](https://proceedings.mlr.press/v119/lin20g.html); [official paper](https://proceedings.mlr.press/v119/lin20g/lin20g.pdf).

**Substance read:** Sections 3--4, particularly the bucketization caveat, support-set problem representation, dynamic programming with bounds, and scheduling/cache design. The optimization framework accommodates objectives beyond accuracy, including imbalance-related metrics; its efficient DPB implementation has explicit loss assumptions.

**Manuscript support:** Supports modern optimized search, reusable subproblems, and objective differences. It does not make all continuous preprocessing lossless or prove superiority of the current local-impurity builder. **Correction:** none. Adding PMLR as publisher would be optional style consistency.

### 21. `aglin2020caching`

**Metadata:** Gael Aglin (publisher spelling: Gael with diaeresis on e); Siegfried Nijssen; Pierre Schaus. *Learning Optimal Decision Trees Using Caching Branch-and-Bound Search*. **AAAI 34(04), 3146--3153 (2020)**. DOI **10.1609/aaai.v34i04.5711**. Initials, title, pages, year, and DOI match; optional issue 04 is missing from the compact manuscript citation.

**Primary sources:** [AAAI record](https://ojs.aaai.org/index.php/AAAI/article/view/5711); [official paper](https://ojs.aaai.org/index.php/AAAI/article/view/5711/5567).

**Substance read:** DL8 and DL8.5 pseudocode and cache discussion, pp. 3148--3150. DL8.5 combines recursive partition optimization with branch-and-bound; importantly it caches unsuccessful bounded searches as well as found solutions.

**Manuscript support:** Direct support for cached and bounded solvers in related work and discussion. This is a valid reason not to equate the manuscript's scorer cost with a universal non-greedy lower bound. **Correction:** none; optionally add `(04)`.

### 22. `demirovic2022murtree`

**Metadata:** Emir Demirovic; Anna Lukina; Emmanuel Hebrard; Jeffrey Chan; James Bailey; Christopher Leckie; Kotagiri Ramamohanarao; Peter J. Stuckey. The publisher renders Demirovic with an acute c, as the manuscript does. *MurTree: Optimal Decision Trees via Dynamic Programming and Search*. **Journal of Machine Learning Research 23(26):1--47 (2022)**. All authors/order and other fields match. No DOI supplied by the official JMLR record.

**Primary sources:** [JMLR record](https://jmlr.org/papers/v23/20-520.html); [official paper](https://jmlr.org/papers/volume23/20-520/20-520.pdf).

**Substance read:** Method description and section 4.5's cache/subtree/lower-bound handling, including storage after exhaustive subproblem exploration. The solver controls both depth and number of nodes and exploits specialized classification-tree structure.

**Manuscript support:** Supports dynamic programming, search, caching, and bounds as alternatives to naive exhaustive computation. It does not establish the current builder's accuracy/cost ranking. **Correction:** none. Preserve `MurTree` capitalization.

### 23. `vanderlinden2023separable` (STreeD)

**Metadata:** Jacobus van der Linden; Mathijs de Weerdt; Emir Demirovic. *Necessary and Sufficient Conditions for Optimal Decision Trees using Dynamic Programming*. **Advances in Neural Information Processing Systems 36, 9173--9212 (2023)**. DOI **10.52202/075280-0404**. Official proceedings verifies title, authors/order, year, venue, pages, DOI. The proceedings abbreviates the first two names; expanded middle initials in `main.tex` are consistent with the later author manuscript but are not all displayed in the 2023 proceedings record.

**Primary sources:** [NeurIPS record](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1d5fce9627e15c84db572a66e029b1fc-Abstract-Conference.html); [official BibTeX](https://proceedings.neurips.cc/paper_files/paper/2023/file/1d5fce9627e15c84db572a66e029b1fc-Bibtex-Conference.bib); [official 40-page paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/1d5fce9627e15c84db572a66e029b1fc-Paper-Conference.pdf).

**Substance read:** Theorem 4.6, section 4.3, proof of Theorem 4.7, and classification-accuracy appendix G. Separability has specific Markovian, order-preservation, and constraint requirements. STreeD is the resulting generic DP solver.

**Manuscript support:** The citation for separable subproblems and optimized solvers is directly relevant. It does not assert that every tree objective is separable or that the current implementation has STreeD's machinery. **Correction:** none. The current related-work paragraph explicitly names STreeD alongside DL8.5 and MurTree.

### 24. `aghaei2025strong`

**Metadata:** Sina Aghaei; Andres Gomez; Phebe Vayanos (publisher accents: Andres and Gomez both accented as appropriate; manuscript correctly accents Gomez). *Strong Optimal Classification Trees*. **Operations Research 73(4), 2223--2241**, issue dated **July-August 2025**. DOI **10.1287/opre.2021.0034**. Authors/title/volume/issue/pages/DOI match.

**Primary sources:** [INFORMS article and issue assignment](https://pubsonline.informs.org/doi/10.1287/opre.2021.0034); [author preprint](https://arxiv.org/abs/2103.15965); [author manuscript PDF](https://arxiv.org/pdf/2103.15965).

**Date limitation:** INFORMS states first online publication **31 July 2024**, while its `Cite as` text also uses 2024 even beside the 2025 issue. This discrepancy is in the primary record. The attempted publisher PDF link redirected to the abstract, so substantive reading used the author manuscript, not a claimed accessible final publisher PDF.

**Substance read:** Section 3, especially 3.1: flow-based MIO, max-flow subproblems, Benders decomposition, and strengthening cuts. Supports mathematical programming/decomposition in the manuscript's group citation.

**Recommendation:** Keep 2025 as issue year; optionally append `first published online 31 July 2024`. Do not change the DOI or infer 2021 publication from it.

### 25. `mctavish2022reference`

**Metadata:** Hayden McTavish; Chudi Zhong; Reto Achermann; Ilias Karimalis; Jacques Chen; Cynthia Rudin; Margo Seltzer. *Fast Sparse Decision Tree Optimization via Reference Ensembles*. **AAAI 36(9), 9604--9613 (2022)**. DOI **10.1609/aaai.v36i9.21194**. All manuscript fields match; issue 9 is an optional addition.

**Primary sources:** [AAAI record](https://ojs.aaai.org/index.php/AAAI/article/view/21194); [official paper](https://ojs.aaai.org/index.php/AAAI/article/view/21194/20943).

**Substance read:** Threshold guessing, Theorem 4.1, and experimental discussion around guessed thresholds/lower bounds, pp. 9606--9610. A reference ensemble guides threshold selection, depth and bound guesses, restricting or steering difficult optimization. Reference-model quality matters.

**Manuscript support:** The statement that reference ensembles can guide restricted search is accurate. This is not a precedent for averaging differently sighted members or evidence for a diversity mechanism. **Correction:** none; optionally add `(9)`.

### 26. `babbar2025nearoptimal` (SPLIT and LicketySPLIT)

**Metadata:** Varun Babbar; Hayden McTavish; Cynthia Rudin; Margo Seltzer. *Near-Optimal Decision Trees in a SPLIT Second*. **Proceedings of the 42nd International Conference on Machine Learning, PMLR 267:2114--2175 (2025)**. PMLR displays the second surname as `Mctavish`; the author's own manuscript uses `McTavish`, so retain the manuscript capitalization. No proceedings DOI supplied by PMLR.

**Primary sources:** [PMLR article and official citation](https://proceedings.mlr.press/v267/babbar25a.html); [author manuscript record](https://arxiv.org/abs/2502.15988); [author manuscript v2, 20 June 2025](https://arxiv.org/html/2502.15988v2).

**Access limitation:** Both the PMLR PDF route and its publisher-linked raw GitHub PDF returned tool-access errors. Metadata is verified on PMLR; substantive verification used the identified author manuscript.

**Substance read:** Sections 5.1--5.2 and Algorithms 2--3. SPLIT scores bounded lookahead with greedy completion to the final depth and can postprocess leaf subproblems optimally. LicketySPLIT recursively repeats one-step SPLIT without that optimal postprocessing. Their loss includes sparsity regularization. Section 6 separates search depth from final depth.

**Manuscript support:** The related-work description is accurate at its present broad level. The difference from truncated terminal Gini is substantive, not cosmetic. **Correction:** none to bibliographic fields. Optional clarification: mention SPLIT's postprocessing and LicketySPLIT's receding-root structure; do not imply LicketySPLIT is simply a one-time greedy completion.

### 27. `vanderlinden2026optimalgreedy` (TMLR 2026)

**Metadata:** Jacobus G. M. van der Linden; Daniel Vos (author spelling has diaeresis on e); Mathijs M. de Weerdt; Sicco Verwer; Emir Demirovic. *Optimal or Greedy Decision Trees? Revisiting their Objectives, Tuning, and Performance*. **Transactions on Machine Learning Research (2026)**. Authors/order, title and journal/year match. Official TMLR index lists **August 2026**. Its official BibTeX supplies journal/year/ISSN/OpenReview URL, but no volume, issue, pages or DOI; it spells Mathijs de Weerdt without middle initials, while the author manuscript supplies them.

**Primary sources:** [TMLR accepted-paper index: search the exact title](https://jmlr.org/tmlr/papers/); [official TMLR BibTeX, successfully read](https://jmlr.org/tmlr/papers/bib/DvDOAtskXl.bib); [official OpenReview record, blocked during this audit](https://openreview.net/forum?id=DvDOAtskXl); [author-deposited record with TMLR journal reference](https://arxiv.org/abs/2409.12788); [v3 full text, 6 August 2026](https://arxiv.org/html/2409.12788v3).

**Access limitation:** OpenReview forum and final-PDF URLs redirected to browser verification. Official acceptance/publication-year evidence comes from TMLR's index, not the inaccessible forum. `10.48550/arXiv.2409.12788` is the preprint DOI, not an authenticated TMLR DOI.

**Substance read:** Sections 4--5 on objective choice, size tuning, size-error comparison, overfitting, and experimental recommendations. They recommend tuning both greedy and optimal methods and selecting size controls according to accuracy/runtime/interpretability goals. Their tuned/size-controlled results do not support a universal claim that optimal trees overfit more than greedy trees.

**Manuscript support:** Directly supports the cautious statement that objectives, size constraints, and tuning affect comparisons. It is not proof about the present mixed bootstrap forests. **Correction:** none; optional month August and author-preprint fallback link. Exact final-PDF identity and acceptance date remain uninspected.

### 28. `scornet2015consistency`

**Metadata:** Erwan Scornet; Gerard Biau; Jean-Philippe Vert. *Consistency of random forests*. **The Annals of Statistics 43(4), 1716--1741 (2015)**. DOI **10.1214/15-AOS1321**. All fields match the first-page header of the author-hosted published electronic reprint, not merely an inferred page count.

**Primary sources:** [publisher DOI destination](https://doi.org/10.1214/15-AOS1321); [author manuscript](https://arxiv.org/abs/1405.2881); [author PDF/reprint](https://arxiv.org/pdf/1405.2881).

**Access limitation and resolution:** The Project Euclid DOI destination exposed only an iframe, and following it failed. The attempted direct publisher PDF did not supply usable text. The readable author PDF's first-page header gives the complete final publication metadata, and its notice identifies it as an electronic reprint of the original IMS article whose pagination/typography differ. The original journal page range is therefore verified from an explicit publication header, not from the reprint's physical length. The parent independently confirmed the same header.

**Substance read:** Theorem 1: additive-regression assumptions, increasing subsample size, increasing leaf count, and a leaf-growth restriction. In particular `t_n -> infinity` is a theorem condition. This is regression consistency under assumptions, not fixed-depth-three Gini-classification consistency.

**Manuscript support:** The current tree-size paragraph accurately contrasts constrained member size with consistency theory allowing tree size to grow with the sample. It does not claim this regression theorem proves fixed-depth classification consistency. **Correction:** none; the header check is complete.

### 29. `olson2017pmlb`

**Metadata:** Randal S. Olson; William La Cava; Patryk Orzechowski; Ryan J. Urbanowicz; Jason H. Moore. *PMLB: a large benchmark suite for machine learning evaluation and comparison*. **BioData Mining 10, article 36 (2017)**. DOI **10.1186/s13040-017-0154-4**. All manuscript fields match. `36` is an article number, not a first page. Publication date 11 December 2017.

**Primary source:** [publisher full text and metadata](https://link.springer.com/article/10.1186/s13040-017-0154-4).

**Substance read:** Introduction, PMLB description, evaluation methodology, and discussion. PMLB standardizes and distributes benchmark data, including real, simulated, and toy tasks. The paper discusses limited diversity and common-origin datasets, so availability does not establish independent or representative sampling.

**Manuscript support:** Supports PMLB provenance and public availability at the dataset-sample and availability citations. It does not document the present 57-task cohort, missing penguin rows, particular split hashes, or current package snapshot; those need the project's manifest. The manuscript correctly distinguishes its convenience sample. **Correction:** none; optionally label `article 36` explicitly.

### 30. `cawley2010selection`

**Metadata:** Gavin C. Cawley; Nicola L. C. Talbot. *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation*. **Journal of Machine Learning Research 11(70), 2079--2107 (2010)**. All manuscript fields match; article identifier 70 is optional. No DOI supplied by the checked JMLR record.

**Primary sources:** [JMLR record](https://jmlr.org/papers/v11/cawley10a.html); [official paper](https://jmlr.org/papers/volume11/cawley10a/cawley10a.pdf).

**Substance read:** Introduction and section 5 on biased evaluation, including repeated repartitioning after preliminary model selection. Model selection is part of training and must be repeated within evaluation training samples; a held-out outer evaluation must not select candidates.

**Manuscript support:** Direct support for the training-only selection/refit separation. It does not independently certify implementation correctness or validate the timing tie-break. Current Section 6.1 already states the small, related/constructed benchmark scope and need for larger independent tasks; no repeated historical-protocol prose is requested. **Correction:** none; optional `(70)`.

### 31. `demsar2006comparisons`

**Metadata:** Janez Demsar (publisher spelling: Demsar with caron on s, correctly encoded in the manuscript). *Statistical Comparisons of Classifiers over Multiple Data Sets*. **Journal of Machine Learning Research 7(1), 1--30 (2006)**. All manuscript fields match; article identifier 1 is optional. No DOI supplied by the checked JMLR record.

**Primary sources:** [JMLR record](https://jmlr.org/papers/v7/demsar06a.html); [official paper](https://jmlr.org/papers/volume7/demsar06a/demsar06a.pdf).

**Substance read:** Section 3.1.3, especially printed page 7, explains signed-rank comparisons across datasets; section 3.2 discusses multiple comparisons and Holm's step-down procedure. These support dataset-level paired tests and multiplicity handling.

**Qualification, now resolved in the manuscript:** Demsar ranks zero differences and divides their ranks between the positive and negative sums, ignoring one if an odd count prevents equal division. The study instead omits zero differences. The current sentence puts the general signed-rank citation before a semicolon and explicitly calls omission "our calculation," so it no longer attributes that convention to Demsar. Any all-zero `p=1` implementation convention is also study-specific. The symmetry qualification is appropriate but is not explicitly developed in the source passage located here.

**Manuscript support:** Relevance is strong; do not interpret the signed-rank result as a test of the bootstrap mean effect or multiply effective dataset count by repetitions. **Correction:** none to the reference; optional `(1)`.

### 32. `holm1979sequential`

**Metadata:** Sture Holm. *A Simple Sequentially Rejective Multiple Test Procedure*. **Scandinavian Journal of Statistics 6(2), 65--70 (1979)**. Author, title, year, venue, issue, and pages match the official archive's issue contents and the publisher's retrospective. No DOI appears in the manuscript.

**Primary publisher/archive sources:** [JSTOR issue contents](https://www.jstor.org/stable/i412579); [JSTOR article](https://www.jstor.org/stable/4615733); [DOI-bearing XML export linked by the official issue contents](https://www.jstor.org/doi/xml/10.2307/4615733); [Wiley's journal 50th-anniversary retrospective](https://onlinelibrary.wiley.com/doi/toc/10.1111/%28ISSN%291467-9469.50thanniversary).

**Clearly labeled access fallback:** [University of Sao Paulo-hosted facsimile of the original JSTOR article](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf). This is a reproduction of the primary article, with the JSTOR cover sheet and original pagination, but **not an author- or publisher-hosted file**. It is used for reading the original argument, not to claim publisher full-text access.

**Substance read:** Original section 2, Scheme I and Theorem 1 on pp. 66--67, and the weighted extension. The ordered thresholds and Bonferroni argument give strong family-wise-error protection for valid individual tests without requiring their mutual independence. This supports the eleven-contrast adjustment; it does not make pointwise mean intervals simultaneous or repair invalid individual p-values from dependent dataset units.

**Identifier status:** The official issue contents' XML-export target explicitly contains `10.2307/4615733`, authenticating the association independently of secondary search results. Its response redirected to the unreadable article page, so neither readable XML metadata nor successful DOI resolution is claimed. Adding this identifier is optional; the existing stable URL suffices. **Correction:** none to existing fields; no further DOI pursuit is needed.

## Final Focused Current-Draft Review

**Overall agreement:** The current positive interpretation is supported by the displayed numerical results and the audited literature. The consolidated Section 6.1 supplies the necessary interpretative limits. No additional general caveat, repeated historical-protocol discussion, or retreat from the observed mean improvements is warranted by this audit. The only requested wording clarification is the Figure 2 number attribution below. This is a claim/source and internal-consistency review, not a rerun of the statistical or benchmarking code.

### Positive Findings and Mean versus Location

- **Abstract/introduction/conclusion (current lines 20, 30--36, 664--677): agree.** The claims concern observed benchmark-mean improvements in shallow forests, not improvement on every task or universal superiority. The conclusions preserve the distinction between selective replacements and making every member farther-sighted.
- **Four primary shallow anchors (lines 291--307 and Table 2): agree.** Mean effects are 1.06, 1.27, 0.42, and 1.04 percentage points; adjusted signed-rank values are 0.00996, 0.02066, 0.09539, and 0.00150. Thus all four means are positive and exactly three of four location tests have `p_H < 0.05`. A positive mean interval for the square-root/horizon-two contrast is not inconsistent with its nonrejecting adjusted signed-rank test.
- **Tuned finding (lines 565--571, 608--616, 632--643): agree.** Inclusive versus RF is +1.57 points with pointwise mean interval [0.30, 3.28], while its median is zero and adjusted location-test p-value is 0.48838. The draft distinguishes these estimands and explicitly says nonsignificance does not show equality. It does not claim a significant signed-rank result for the tuned comparison.
- **Scope/sensitivity placement (Section 6.1): agree.** Equal-family weighting and removal of named synthetic/constructed tasks yield inclusive intervals spanning zero; the text gives their actual values and retains "rather small," related/constructed tasks, within-task averaging, and larger independent-task comparisons. Those qualifications need not be repeated in every positive result paragraph.

### Matched Controls, Tuning, and Shallow Motivation

- **Fixed controls (lines 64--68, 85, 220--229): agree.** The declared common settings cover final depth, Gini, split/leaf minima, feature policy, no pruning, paired bootstrap draws/seeds, and one member per position. Each feature policy has its own matched CART control. These statements support a replacement comparison, not an all-feature versus square-root confound.
- **Tuned controls (lines 89--93, 574--593, 608--616, 645--658): agree.** All families tune the same common parameter grid and use training-only shared folds; RF includes both all-feature bagged CART and feature-subsampled forests. Expanded families can choose pure forests, so the tuned result is correctly attributed to family expansion rather than mixing alone. Counts of 48/288/768 candidates and separate selection/refit costs make clear that this is not equal-search-budget tuning. The statement that the finding is not merely tuned mixtures versus untuned RF is supported as written.
- **Shallow motivation (lines 32, 48, 618--629): agree.** Eight leaves per depth-three member does not limit the whole forest to eight regions. Constrained-size evidence motivates the experiment without prescribing a universal depth; Scornet's growing-tree regression theorem is not misused as fixed-depth Gini-classification consistency. Depth-six/unrestricted controls and the stated feature-policy difference are retained.

### Overfitting as a Hypothesis

**Agree with lines 623--629.** Unrestricted all-feature farther-sighted single trees have larger observed realized depths (15.1/17.0 versus 10.1) and lower accuracy than CART. The manuscript calls this "consistent with overfitting" and a "plausible explanation to test" using training--validation curves and regularization. This is an appropriately scoped hypothesis, not an established causal diagnosis. It does not contradict TMLR 2026's warning against a general optimal-tree-overfitting conclusion: the present setting is unpruned local Gini search without a size penalty, not their fully tuned/size-controlled comparison. The acknowledged positive unrestricted feature-subsampled means prevent overgeneralization across feature policies.

### Figure 2: Lower Work, Not an Exact-Time Guarantee

**Agree with the comparison and its scope (lines 482--505, 648--658).** The figure identifies depth-three/all-feature fixed architectures, dataset-mean accuracy and summed member-fitting work, five discrete ensemble sizes, a descriptive 0.7 s mean-work reference, and exclusion of selection cost. It does not promise equal per-dataset wall time or interpolation to an unevaluated model.

The displayed five-two-sighted/fifteen-CART example is 74.06% at 0.0955 s, versus 73.02% at 0.1338 s for 200 CART members: +1.04 percentage points and about 28.6% less work, correctly rounded to 29%. The figure also explicitly acknowledges the competitive pure horizon-two alternative (74.79% at 0.3381 s), so it does not claim mixtures dominate all pure forests at every budget.

**One minor necessary clarification, current lines 492--494:** "also exceeds the 200-member greedy forest's mean accuracy (73.37%)" grammatically attaches 73.37% to the greedy forest, although that is the **two-two-sighted/eighteen-CART mixture's** mean; the greedy comparator is 73.02%. The plotted coordinate is approximately 0.73372712 and supports 73.37%. Suggested replacement sentence, without changing any data:

> The 20-member mixture with only two two-sighted members reaches 73.37% mean accuracy at 0.0470 s of fitting work, also exceeding the 200-member greedy forest at lower work.

## Residual Access and Verification Limits

No remaining required metadata or focused-review task is awaiting discovery. The following are disclosed limitations, not silently verified fields or reasons to delay the revision:

1. **Hu printed pagination:** competing page conventions remain unreconciled. The current electronic citation's omission of pages and official URL resolve the manuscript issue without asserting which uninspected edition uses 7265--7273.
2. **TMLR final artifact:** official index and official BibTeX authenticate journal/year; author v3 supplies substantive text. The inaccessible final OpenReview PDF and acceptance discussion were not inspected, so exact final-artifact identity and acceptance date are not claimed.
3. **SPLIT and Aghaei full text:** official proceedings/publisher records authenticate metadata; the identified author manuscripts supplied substantive reading because final publisher PDF routes were unusable. No line-for-line equivalence to inaccessible final PDFs is asserted.
4. **Scornet:** Project Euclid full text remained unreadable, but the published electronic reprint explicitly resolves every metadata field and supplies the theorem. Its own different physical pagination is not confused with the journal range.
5. **Holm:** official archive/publisher records authenticate metadata and the archive's export link authenticates the DOI association; readable official full text/XML and direct DOI resolution remain unverified. The original theorem was read in the explicitly labeled university-hosted facsimile. Optional DOI addition is not needed.
6. **Preservation/compilation:** this auditor edited only this report. No manuscript/BibTeX/benchmark/figure/PDF changes, application opening, new browser tabs, PDF exports, or fits were performed for the final review. The user's reported compilation and preservation checks were not rerun.

## Outside the Assigned Range

`horn2026randomdepth` is entry 15, not 17-32. It has not been audited here; the existence and correctness of its 2026 citation must not be inferred from this report. Entries 1-16 belong to the companion audit.

## Closure Addendum: SHA-256-Matched Final Read

**Closed on 2026-10-10 at the user's request.** A fresh filesystem SHA-256 check matches the supplied current manuscript exactly:

```text
38ef96694143de238dab6f39dc96a00873c54660f53711808dc7a9a66737331a
```

The final read covered the current abstract/introduction (lines 19--36), related-work context (38--48), method (50--78), experimental protocol including Sections 4.2--4.4 (86--107), all results prose and figure captions (109--594), discussion including the consolidated Section 6.1 (596--659), and conclusion (661--678). Numeric figure code was skipped in this final pass. No further web discovery, optional identifier searches, or attempts to access the final OpenReview artifact were made.

### Final Verified Fields and Correction Status

| Entries | Final status |
| --- | --- |
| 17 Bertsimas; 18 Verwer; 20 Lin; 21 Aglin; 22 MurTree; 25 McTavish; 29 Olson; 30 Cawley | Authors/order, title, year, venue, and supplied pagination/article identifier match the primary records detailed above. Supplied DOIs match where present; no new identifier is required. Retain Verwer's first page 1625 and Olson's article number 36. |
| 19 Hu | Authors/title/NeurIPS 32/2019 verified. Unverified electronic pagination removed and official proceedings URL supplied: correction closed. Printed-edition reconciliation remains unnecessary for the present electronic citation. |
| 23 STreeD | Authors/title/NeurIPS 36/2023/pages 9173--9212/DOI verified. Explicit algorithm naming applied: clarification closed. |
| 24 Aghaei | Authors/title/Operations Research 73(4)/2223--2241/DOI verified. Retain the 2025 issue year with first-online date 31 July 2024: date clarification closed. |
| 26 SPLIT | Authors/title/ICML 2025/PMLR 267/pages 2114--2175 verified. No bibliographic correction or new identifier needed. |
| 27 TMLR | Exact title/authors and 2026 publication authenticated by official index/BibTeX; August 2026 independently confirmed by the parent. No page range or new journal DOI is required. |
| 28 Scornet | Authors/title/Annals of Statistics 43(4)/2015/1716--1741/DOI 10.1214/15-AOS1321 explicitly authenticated by the arXiv-hosted published electronic-reprint header, also independently checked by the parent. Metadata check closed despite unavailable Project Euclid full text. |
| 31 Demsar | Reference fields match. Current methods explicitly make zero omission the study's calculation rather than Demsar's convention: attribution clarification closed. |
| 32 Holm | Existing author/title/year/venue/6(2)/65--70 and stable archive URL verified. No new identifier or additional access attempt is needed. |

### Final Review Agreement

**No material issue with the substantive interpretation or audited references was found in this hash-matched draft.** The positive shallow-forest findings remain supportable; the text does not claim every task benefits. Methods distinguish fixed matched replacements from training-only family selection, expose unequal candidate counts, and separate member-fitting work, direct refit wall time, and selection work. The tuned finding concerns an expanded family that can choose pure forests, not an isolated causal effect of mixing.

The mean-effect/bootstrap and location/signed-rank distinction is explicit, including the nonrejecting tuned signed-rank result and the warning against interpreting nonsignificance as equality. The shallow motivation does not prescribe a universal depth. The overfitting explanation remains a hypothesis for the unpruned all-feature results, not a general claim about optimal trees. Figure 2 describes lower measured benchmark-mean fitting work rather than an exact-time, per-task, or universally optimal-budget guarantee. The existing Section 6.1 adequately consolidates sample scope, sensitivities, timing limits, and need for larger independent tasks; no historical-protocol text needs restoring.

**One minor numerical-attribution clarification still present at lines 492--494:** the parenthesis `73.37%` follows "the 200-member greedy forest's mean accuracy," although it describes the 20-member mixture with two two-sighted members. The greedy comparator is 73.02%. This does not change the direction of the finding. The replacement sentence already proposed above identifies the mixture explicitly; no numeric figure-code change is needed.

### Explicit Access Limits at Closure

- **Hu:** alternative printed pagination remains unreconciled; no pages are asserted for the electronic citation.
- **TMLR:** final OpenReview PDF and acceptance discussion remain unread. Official index/BibTeX establish publication metadata; author v3 supplied substantive reading. Exact identity with the inaccessible final PDF is not claimed.
- **SPLIT and Aghaei:** final publisher PDF routes were unusable. Official metadata records and identified author manuscripts support the respective metadata and substantive checks; final-PDF textual identity is not claimed.
- **Scornet:** Project Euclid full text was unavailable, but the published electronic reprint supplies both explicit final metadata and the theorem. Different reprint pagination is disclosed, not an unresolved bibliographic field.
- **Holm:** official archive/publisher metadata is readable; official article full text, XML payload, and direct DOI resolution were not verified. Original substantive text was read in the clearly labeled university-hosted facsimile. No optional identifier is requested.

These are final disclosed limits, not pending tasks. Only this report was written. No manuscript/BibTeX changes, editor opening, browser tabs, PDF exports, compilation, fits, or benchmark runs were performed by this auditor for closure.

## Final Agreement After Figure 2 Clarification

Read-only verification on 2026-10-10 confirms that current lines 492--495 explicitly assign **73.37% mean accuracy and 0.0470 s of fitting work to the 20-member mixture with two two-sighted members**, then compare it with the 200-member greedy forest at lower work. The previously identified attribution ambiguity is resolved. This section supersedes all earlier statements that this minor clarification remained outstanding.

Current `main.tex` SHA-256, obtained by a read-only hash:

```text
4c31ad499b8bcc2c926b5d84c057757c1a82610be9084e8d9c599aad3752d01e
```

**Final agreement: no residual material issues or requested corrections remain within this reference audit and focused prose review.** The documented source-access limits remain disclosed limitations, not pending work or requests for new identifiers. No further discovery was performed. Compilation, preservation checks, and Git handling remain with the parent; this auditor wrote only this report.
