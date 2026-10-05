"""Inline generated evidence into the existing source for the native editor.

The editable main.tex stays at its original path. Figures use pgfplots with
the same validated numeric summaries as the separately exported data plots.
The result contains no external project dependencies for native compilation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re

import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "array_revision"


def block(text, key, original, generated):
    start, end = f"% BEGIN GENERATED {key}", f"% END GENERATED {key}"
    replacement = start + "\n" + generated.strip() + "\n" + end
    if start in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: replacement,
                      text, count=1, flags=re.DOTALL)
    if original not in text:
        raise ValueError(f"Cannot find insertion point: {key}")
    return text.replace(original, replacement, 1)


def plot_tables(records, metric, error=False, offset=0):
    lines = ["x y" + (" low high" if error else "")]
    for index, depth in enumerate(("3", "6", "None")):
        r = records[records.left_depth == depth].iloc[0]
        line = f"{index+offset:.2f} {r[metric] * (100 if metric == 'mean_delta' else 1):.8f}"
        if error:
            line += f" {100*(r.mean_delta-r.ci_low):.8f} {100*(r.ci_high-r.mean_delta):.8f}"
        lines.append(line)
    return "\n".join(lines)


def figures(summary, comparisons):
    choices = (("tree_k2", "cart_control", "blue!65!black", "Tree vs. CART"),
               ("sighted2_20", "primary", "red!70!black", "Uniform forest (20)"),
               ("cart_mix10_100", "cart_control", "green!45!black", "CART mixture (100)"))
    first = [r"\begin{tikzpicture}",
             r"\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.35cm},",
             r"width=0.43\textwidth,height=5.4cm,",
             r"tick label style={font=\footnotesize},label style={font=\small},",
             r"title style={font=\small},xtick={0,1,2},xticklabels={3,6,Unlimited},",
             r"xlabel={Maximum tree depth}]",
             r"\nextgroupplot[title={(a) Paired accuracy difference},ylabel={Accuracy difference (pp)},",
             r"legend to name=revisionDepthLegend,legend columns=3,legend style={font=\scriptsize,draw=none}]"]
    for index, (model, test_family, color, label) in enumerate(choices):
        rows = comparisons[(comparisons.left == model) & (comparisons.test_family == test_family)]
        table = plot_tables(rows, "mean_delta", error=True, offset=(index-1)*.16)
        first.extend([r"\addplot+[only marks,mark=*,color=" + color +
                      r",error bars/.cd,y dir=both,y explicit] table[x=x,y=y,y error minus=low,y error plus=high] {",
                      table, "};", r"\addlegendentry{" + label + "}"])
    first.extend([r"\addplot[black!40,dashed,forget plot] coordinates {(-0.3,0) (2.3,0)};",
                  r"\nextgroupplot[title={(b) Relative fitting cost},ymode=log,ylabel={Ratio of mean costs}]"])
    for model, test_family, color, label in choices:
        rows = comparisons[(comparisons.left == model) & (comparisons.test_family == test_family)]
        first.extend([r"\addplot+[mark=*,color=" + color + r"] table[x=x,y=y] {",
                      plot_tables(rows, "mean_time_ratio"), "};"])
    first.extend([r"\end{groupplot}", r"\end{tikzpicture}",
                  r"\par\smallskip\pgfplotslegendfromname{revisionDepthLegend}"])

    models = (("cart_bag100", "black!55", "CART bagging (100)"),
              ("cart_mix10_100", "green!45!black", r"CART + 10\% two-sighted"),
              ("rf_sqrt_fixed", "blue!65!black", r"Random forest ($\sqrt p$)"),
              ("mix25_100", "red!70!black", r"Custom 25\% mixture"),
              ("cart_bag200", "violet!70!black", "CART bagging (200)"),
              ("rf_tuned", "black", "Tuned random forest"))
    displayed = summary[summary.model_id.isin([model for model, _, _ in models])]
    low, high = displayed.accuracy_ci_low.min(), displayed.accuracy_ci_high.max()
    padding = .04 * (high - low)
    second = [r"\begin{tikzpicture}",
              r"\begin{groupplot}[group style={group size=3 by 1,horizontal sep=0.85cm},",
              r"width=0.285\textwidth,height=5.0cm,xmode=log,",
              f"ymin={low-padding:.8f},ymax={high+padding:.8f},",
              r"tick label style={font=\scriptsize},label style={font=\small},",
              r"title style={font=\small},xlabel={Mean fitting cost (s)}]"]
    for index, depth in enumerate(("3", "6", "None")):
        title = "Unlimited depth" if depth == "None" else "Depth " + depth
        options = "title={" + title + "}"
        if index == 0:
            options += r",ylabel={Mean test accuracy},legend to name=revisionTradeoffLegend,legend columns=3,legend style={font=\scriptsize,draw=none}"
        second.append(r"\nextgroupplot[" + options + "]")
        for model, color, label in models:
            selected = summary[summary.model_id == model]
            r = selected.iloc[0] if model == "rf_tuned" else selected[selected.task_depth == depth].iloc[0]
            mark = "star" if model == "rf_tuned" else "*"
            second.extend([r"\addplot+[only marks,mark=" + mark + ",color=" + color +
                           r",error bars/.cd,y dir=both,y explicit] table[x=x,y=y,y error minus=low,y error plus=high] {",
                           "x y low high",
                           f"{r.fit_time_s:.8f} {r.accuracy:.8f} {r.accuracy-r.accuracy_ci_low:.8f} {r.accuracy_ci_high-r.accuracy:.8f}",
                           "};"])
            if index == 0:
                second.append(r"\addlegendentry{" + label + "}")
    second.extend([r"\end{groupplot}", r"\end{tikzpicture}",
                   r"\par\smallskip\pgfplotslegendfromname{revisionTradeoffLegend}"])
    return "\n".join(first), "\n".join(second)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-bibtex", action="store_true")
    args = parser.parse_args()
    path = OUT / "main.tex"
    text = path.read_text()
    if args.prepare_bibtex:
        keys = []
        for citation in re.findall(r"\\cite\{([^}]+)\}", text):
            for key in citation.split(","):
                if key not in keys:
                    keys.append(key)
        bibs = "references,references_additions"
        if (OUT / "shallow_references.bib").exists():
            bibs += ",shallow_references"
        aux = "\\relax\n\\citation{" + ",".join(keys) + "}\n\\bibstyle{elsarticle-num}\n\\bibdata{" + bibs + "}\n"
        (OUT / "revision_citations.aux").write_text(aux)
        return
    summary = pd.read_csv(OUT / "summary.csv", keep_default_na=False)
    comparisons = pd.read_csv(OUT / "paired_comparisons.csv", keep_default_na=False)
    for name in ("results_text", "discussion_text", "conclusion_text", "table_performance", "table_comparisons"):
        text = block(text, name, r"\input{" + name + ".tex}", (OUT / (name + ".tex")).read_text())
    fig1, fig2 = figures(summary, comparisons)
    text = block(text, "figure1", r"\includegraphics[width=\textwidth]{Fig1_depth_sensitivity.pdf}", fig1)
    text = block(text, "figure2", r"\includegraphics[width=\textwidth]{Fig2_accuracy_cost.pdf}", fig2)
    if "% BEGIN GENERATED bibliography" in text:
        text = block(text, "bibliography", "", (OUT / "revision_citations.bbl").read_text())
    else:
        text = re.sub(r"\\bibliographystyle\{[^}]+\}\s*\\bibliography\{[^}]+\}",
                      lambda _: "% BEGIN GENERATED bibliography\n" +
                      (OUT / "revision_citations.bbl").read_text() + "% END GENERATED bibliography", text)
    path.write_text(text)
    response = OUT / "response_to_reviewers.tex"
    response.write_text(block(response.read_text(), "response_results", r"\input{response_results.tex}",
                              (OUT / "response_results.tex").read_text()))
    print("Updated the existing manuscript and response sources in place.")


if __name__ == "__main__":
    main()
