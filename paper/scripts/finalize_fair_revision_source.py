"""Embed validated fair-run figures in the existing native-editor manuscript.

Numerical claims are supplied in reviewed manuscript fragments, not inferred
automatically from whichever contrasts happen to be significant.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from finalize_array_revision_source import block


PAPER = Path(__file__).resolve().parents[1]
MANUSCRIPT = PAPER / "array_revision/main.tex"
FAIR = PAPER / "array_revision_fair"
COLORS = ("222222", "1F77B4", "D62728", "2B8C55", "66A61E", "C59A00",
          "8C6D31", "7B3294", "A64C9C", "DC74AB", "B35806", "008B8B",
          "17A8BD", "527A9C", "7F7F7F", "9D8F11")
COUNTS = (20, 40, 60, 100, 200)
DEPTHS = ("3", "6", "None")


def validate(directory, fixed_only):
    from analyze_array_fair_benchmark import read_analysis_csv, validate_retained
    summary, primary, report = validate_retained(directory, fixed_only)
    name = "descriptive_paired_comparisons.csv"
    if hashlib.sha256((directory / name).read_bytes()).hexdigest() != report["output_sha256"].get(name):
        raise ValueError(f"Analysis output hash mismatch: {name}")
    return summary, primary, read_analysis_csv(directory / name)


def palette():
    return "\n".join(r"\definecolor{fairC" + str(i) + "}{HTML}{" + value + "}"
                     for i, value in enumerate(COLORS))


def pgf_style(index):
    return "solid" if index < 3 or index == 15 else "dashed" if index < 7 else "dotted" if index < 11 else "dashdotted"


def marker(index):
    return ("*", "square*", "triangle*", "diamond*", "triangle*")[index]


def points(rows, x, y):
    return " ".join(f"({float(row[x]):.9g},{float(row[y]):.9g})" for _, row in rows.iterrows())


def figure2(summary):
    rows = summary[(summary.stage == "fixed_forest") & (summary.task_depth == "3")
                   & (summary.max_features == "all")].copy()
    if len(rows) != 80 or rows.composition_id.nunique() != 16:
        raise ValueError("Figure 2 requires sixteen complete five-point curves")
    from analyze_array_fair_benchmark import compositions
    low, high = rows.accuracy.min(), rows.accuracy.max()
    margin = max(.004, (high - low) * .12)
    lines = [palette(), r"\begin{tikzpicture}",
             r"\begin{groupplot}[group style={group size=2 by 1,horizontal sep=0.95cm},",
             r"width=0.445\textwidth,height=5.5cm,grid=major,grid style={gray!15},",
             r"tick label style={font=\scriptsize},label style={font=\small},title style={font=\small},",
             f"ymin={max(0,low-margin):.9g},ymax={min(1,high+margin):.9g}]",
             r"\nextgroupplot[title={(a) Accuracy versus tree count},xlabel={Number of trees $T$},",
             r"ylabel={Mean test accuracy},xtick={20,40,60,100,200},",
             r"legend to name=fairCurveLegend,legend columns=4,legend style={font=\scriptsize,draw=none,",
             r"/tikz/every even column/.append style={column sep=3pt}}]"]
    ordered = []
    for index, (name, ticks) in enumerate(compositions()):
        selected = rows[rows.composition_id == name].set_index("n_estimators").loc[list(COUNTS)].reset_index()
        ordered.append(selected)
        lines.append(r"\addplot[color=fairC" + str(index) + "," + pgf_style(index)
                     + r",line width=0.8pt] coordinates {" + points(selected, "n_estimators", "accuracy") + "};")
        label = "/".join(str(5 * value) for value in ticks)
        horizon = sum(h * ticks[h - 1] / 20 for h in (1, 2, 3))
        lines.append(r"\addlegendentry{" + label + r"\% ($\bar k=" + f"{horizon:.2f}" + "$)}")
    lines.append(r"\nextgroupplot[title={(b) Accuracy versus fitting work},xmode=log,xlabel={Mean fitting work (s)}]")
    for index, selected in enumerate(ordered):
        lines.append(r"\addplot[color=fairC" + str(index) + "," + pgf_style(index)
                     + r",line width=0.8pt] coordinates {" + points(selected, "fit_work_s", "accuracy") + "};")
        for size_index, row in selected.iterrows():
            rotation = ",mark options={rotate=180}" if size_index == 4 else ""
            lines.append(r"\addplot[only marks,color=fairC" + str(index) + ",mark=" + marker(size_index)
                         + r",mark size=1.5pt" + rotation + "] coordinates {"
                         + f"({row.fit_work_s:.9g},{row.accuracy:.9g})" + "};")
    lines.extend([r"\addplot[black!55,dashed] coordinates {"
                  + f"(0.7,{max(0,low-margin):.9g}) (0.7,{min(1,high+margin):.9g})" + "};",
                  r"\end{groupplot}", r"\end{tikzpicture}",
                  r"\par\smallskip\scriptsize Composition: \% one-/two-/three-sighted members ($\bar k$: mean horizon).",
                  r"\par\pgfplotslegendfromname{fairCurveLegend}"])
    return "\n".join(lines)


def single_data(summary, descriptive):
    data = []
    for depth in DEPTHS:
        for horizon in (1, 2, 3):
            name = f"D{depth}_L1_Fall__" + ("cart" if horizon == 1 else f"single_k{horizon}")
            record = summary[summary.model_id == name].iloc[0]
            mean, low, high = 0., 0., 0.
            if horizon != 1:
                effect = descriptive[descriptive.left == name].iloc[0]
                mean, low, high = (100 * effect[key] for key in ("mean_delta", "ci_low", "ci_high"))
            data.append({"depth": depth, "horizon": horizon, "delta": mean,
                         "ci_low": low, "ci_high": high, "fit_s": record.direct_fit_time_s})
    return pd.DataFrame(data)


def figure1(data, directory):
    lines = [palette(), r"\begin{tikzpicture}",
             r"\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.1cm},",
             r"width=0.44\textwidth,height=5.2cm,grid=major,grid style={gray!15},",
             r"tick label style={font=\scriptsize},label style={font=\small},title style={font=\small},",
             r"xtick={1,2,3},xlabel={Sight horizon $k$}]",
             r"\nextgroupplot[title={(a) Paired single-tree differences},ylabel={Accuracy difference (pp)},",
             r"legend to name=fairDepthLegend,legend columns=3,legend style={font=\small,draw=none}]"]
    colors = (1, 3, 2)
    for index, depth in enumerate(DEPTHS):
        rows = data[data.depth == depth]
        lines.append(r"\addplot+[mark=*,color=fairC" + str(colors[index]) +
                     r",error bars/.cd,y dir=both,y explicit] table[x=x,y=y,y error minus=low,y error plus=high] {")
        lines.append("x y low high")
        for row in rows.itertuples():
            lines.append(f"{row.horizon+(index-1)*.06:.3f} {row.delta:.8g} {row.delta-row.ci_low:.8g} {row.ci_high-row.delta:.8g}")
        lines.extend(["};", r"\addlegendentry{" + ("Unlimited depth" if depth == "None" else "Depth " + depth) + "}"])
    lines.extend([r"\addplot[black!40,dashed,forget plot] coordinates {(0.8,0) (3.2,0)};",
                  r"\nextgroupplot[title={(b) Single-tree fitting cost},ymode=log,ylabel={Mean fitting time (s)}]"])
    for index, depth in enumerate(DEPTHS):
        rows = data[data.depth == depth]
        lines.append(r"\addplot+[mark=*,color=fairC" + str(colors[index]) + "] coordinates {"
                     + points(rows, "horizon", "fit_s") + "};")
    lines.extend([r"\end{groupplot}", r"\end{tikzpicture}", r"\par\smallskip\pgfplotslegendfromname{fairDepthLegend}"])
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5))
    for index, depth in enumerate(DEPTHS):
        rows = data[data.depth == depth]
        color = "#" + COLORS[colors[index]]
        label = "Unlimited depth" if depth == "None" else "Depth " + depth
        axes[0].errorbar(rows.horizon+(index-1)*.06, rows.delta,
                         yerr=[rows.delta-rows.ci_low, rows.ci_high-rows.delta],
                         color=color, marker="o", ms=3, capsize=2, label=label)
        axes[1].plot(rows.horizon, rows.fit_s, "o-", color=color, ms=3)
    axes[0].axhline(0, color=".5", ls="--", lw=.6)
    axes[0].set(ylabel="Accuracy difference (percentage points)", title="(a) Paired single-tree differences")
    axes[1].set(ylabel="Mean fitting time (s)", title="(b) Single-tree fitting cost", yscale="log")
    for axis in axes:
        axis.set(xlabel="Sight horizon k", xticks=[1, 2, 3])
        axis.grid(color=".9", lw=.5)
        axis.set_axisbelow(True)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False)
    fig.subplots_adjust(left=.09, right=.99, top=.9, bottom=.25, wspace=.35)
    fig.savefig(directory / "Fig1_single_trees.pdf")
    fig.savefig(directory / "Fig1_single_trees.png", dpi=220)
    plt.close(fig)
    return "\n".join(lines)


def replace_caption(text, figure_key, caption):
    end = f"% END GENERATED {figure_key}"
    pattern = re.escape(end) + r"\s*\\caption\{.*?\}\s*\\label"
    replacement = end + "\n\\caption{" + caption + "}\n\\label"
    result, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise ValueError(f"Missing figure caption: {figure_key}")
    return result


def figure3(summary, primary):
    rows = primary[primary.stage == "tuned"]
    if len(rows) != 3:
        raise ValueError("Figure 3 requires all three primary tuned contrasts")
    selected = summary[summary.stage == "tuned_forest"].set_index("model_id").loc[["rf", "mixed_k2", "mixed"]]
    labels = [r"Mixed (1,2) -- RF", r"Inclusive -- RF", r"Inclusive -- mixed (1,2)"]
    lines = [palette(), r"\begin{tikzpicture}",
             r"\begin{groupplot}[group style={group size=2 by 1,horizontal sep=1.35cm},",
             r"width=0.42\textwidth,height=5.2cm,grid=major,grid style={gray!15},",
             r"tick label style={font=\scriptsize},label style={font=\small},title style={font=\small}]",
             r"\nextgroupplot[title={(a) Paired tuned-family differences},xlabel={Accuracy difference (pp)},",
             r"ytick={0,1,2},yticklabels={" + ",".join("{" + label + "}" for label in labels) + r"},ydir=reverse,ymin=-0.4,ymax=2.4]"]
    for index, row in enumerate(rows.itertuples()):
        lines.extend([r"\addplot+[only marks,mark=*,color=fairC" + str((3, 2, 7)[index]) +
                      r",error bars/.cd,x dir=both,x explicit] table[x=x,y=y,x error minus=low,x error plus=high] {",
                      "x y low high", f"{100*row.mean_delta:.9g} {index} {100*(row.mean_delta-row.ci_low):.9g} {100*(row.ci_high-row.mean_delta):.9g}", "};"])
    lines.extend([r"\addplot[black!40,dashed] coordinates {(0,-0.4) (0,2.4)};",
                  r"\nextgroupplot[title={(b) Selection work and direct refit},ymode=log,ylabel={Mean time or work (s)},",
                  r"xtick={0,1,2},xticklabels={RF,{Mixed (1,2)},Inclusive},",
                  r"legend to name=fairTunedLegend,legend columns=1,legend style={font=\scriptsize,draw=none}]"])
    for column, color, mark, label in (
            ("selection_fitting_work_s", 1, "square*", "Selection: tree-fit work"),
            ("direct_fit_time_s", 10, "*", "Refit: direct wall time"),
            ("total_workflow_wall_s", 0, "diamond*", "Sum of measured stage wall times")):
        values = " ".join(f"({index},{float(value):.9g})" for index, value in enumerate(selected[column]))
        lines.extend([r"\addplot+[only marks,color=fairC" + str(color) + ",mark=" + mark
                      + "] coordinates {" + values + "};", r"\addlegendentry{" + label + "}"])
    lines.extend([r"\end{groupplot}", r"\end{tikzpicture}", r"\par\smallskip\pgfplotslegendfromname{fairTunedLegend}"])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-only", action="store_true")
    args = parser.parse_args()
    directory = FAIR / "analysis" / ("fixed_only" if args.fixed_only else "full")
    summary, primary, descriptive = validate(directory, args.fixed_only)
    text = MANUSCRIPT.read_text()
    text = block(text, "figure2", "", figure2(summary))
    text = replace_caption(text, "figure2", r"Fixed-architecture forests at depth three with all features: every composition spans 20, 40, 60, 100, and 200 members on the complete 57-dataset cohort, averaged over five paired repetitions and then equally across datasets. Circle, square, upward triangle, diamond, and downward triangle mark these sizes in the right panel. The dashed line denotes a 0.7 s mean-fitting-work reference, not a validated per-dataset budget. Composition is stated explicitly because equal average horizons can describe different mixtures. These descriptive curves do not include model-selection cost or show paired confidence intervals.")
    if not args.fixed_only:
        text = block(text, "figure1", "", figure1(single_data(summary, descriptive), directory))
        text = replace_caption(text, "figure1", r"Depth-matched unpruned single trees with all features. Left: paired accuracy differences from CART, with unadjusted dataset-bootstrap intervals; these single-tree effects are descriptive, not members of the eleven-test primary family. Right: measured mean single-tree fit duration, excluding construction and prediction. Sight horizon is varied independently of permitted final depth.")
        plot3 = figure3(summary, primary)
        if "% BEGIN GENERATED figure3" not in text:
            figure = "\n".join([r"\begin{figure*}[t]", r"\centering",
                                "% BEGIN GENERATED figure3", plot3, "% END GENERATED figure3",
                                r"\caption{Equally training-selected conventional and mixed forests. Left: paired dataset-mean accuracy differences, with unadjusted bootstrap intervals; the three tuned contrasts belong to the joint eleven-test Holm family. Right: standalone-family validation fitting work, direct final refit wall time, and the sum of recorded workflow stage wall times. The last measure excludes checkpoint I/O, process startup, and idle gaps; it is not uninterrupted end-to-end time. Common validation-bank work is charged fully to every family requiring it.}",
                                r"\label{fig:tuned}", r"\end{figure*}", ""])
            text = text.replace(r"\section{Discussion}", figure + "\n" + r"\section{Discussion}", 1)
        else:
            text = block(text, "figure3", "", plot3)
        fragments = FAIR / "manuscript"
        for name in ("results_text", "discussion_text", "conclusion_text", "table_performance", "table_comparisons"):
            text = block(text, name, "", (fragments / (name + ".tex")).read_text())
        response = PAPER / "array_revision/response_to_reviewers.tex"
        response_text = block(response.read_text(), "response_results", "", (fragments / "response_results.tex").read_text())
        response.write_text(response_text)
    MANUSCRIPT.write_text(text)
    print("Updated figures/fragments in the existing manuscript; draft warnings require separate author review.")


if __name__ == "__main__":
    main()
