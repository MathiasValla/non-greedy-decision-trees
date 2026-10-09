"""Draw a data-derived submission summary without refitting or generated artwork."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze_array_fair_benchmark import validate_retained


PAPER = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=PAPER / "array_revision_fair",
                        help="Original or restored complete fair-results root")
    parser.add_argument("--destination", type=Path, default=PAPER / "array_revision")
    args = parser.parse_args()
    source = args.out / "analysis/full"
    summary, primary, report = validate_retained(source, False)
    cost_path = source / "fair_tuning_table.csv"
    if hashlib.sha256(cost_path.read_bytes()).hexdigest() != report["output_sha256"][cost_path.name]:
        raise ValueError("Tuning table hash mismatch")
    costs = pd.read_csv(cost_path).set_index("model_id").loc[["rf", "mixed_k2", "mixed"]]
    effects = primary.set_index("contrast_id")
    rows = effects.loc[["tuned__mixed_k2_vs_rf", "tuned__mixed_vs_rf"]]
    if len(summary) != 501 or report["fixed_only"]:
        raise ValueError("A complete full export is required")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig = plt.figure(figsize=(13.28 / 2.54, 5.31 / 2.54), facecolor="white")
    accuracy = fig.add_axes([.145, .45, .33, .21])
    timing = fig.add_axes([.66, .45, .32, .21])
    colors = ("#444444", "#25835e", "#b04c40")
    for position, row in enumerate(rows.itertuples(), start=1):
        accuracy.errorbar(100 * row.mean_delta, position,
                          xerr=[[100 * (row.mean_delta - row.ci_low)],
                                [100 * (row.ci_high - row.mean_delta)]],
                          fmt="o", ms=4, capsize=2, lw=1.2, color=colors[position])
    accuracy.plot(0, 0, "o", color=colors[0], ms=4)
    accuracy.axvline(0, color=".7", lw=.7, ls="--", zorder=0)
    accuracy.set(xlim=(-.55, 3.6), ylim=(-.5, 2.5), xticks=[0, 1, 2, 3],
                 yticks=[0, 1, 2], yticklabels=["RF", "Family 1/2", "Family 1/2/3"],
                 xlabel="Accuracy difference from RF (pp)",
                 title="Estimated mean gains")
    accuracy.invert_yaxis()
    for position, row in enumerate(costs.itertuples()):
        timing.plot(row.direct_fit_time_s, position - .1, "o", color=colors[position], ms=4)
        timing.plot(row.selection_fitting_work_s, position + .1, "D", color=colors[position], ms=3.5)
    timing.set(xscale="log", xlim=(.015, 6000), ylim=(-.5, 2.5),
               xticks=[.1, 10, 1000], yticks=[0, 1, 2],
               yticklabels=["RF", "1/2", "1/2/3"],
               xlabel="Mean time / fitting work (s)", title="Much greater computation")
    timing.invert_yaxis()
    for axis in (accuracy, timing):
        axis.tick_params(labelsize=6.5, length=2, pad=2)
        axis.set_axisbelow(True)
        axis.grid(axis="x", color=".92", lw=.5)
        axis.title.set_fontsize(8)
    handles = [plt.Line2D([], [], marker="o", color=".35", linestyle="none", ms=4),
               plt.Line2D([], [], marker="D", color=".35", linestyle="none", ms=3.5)]
    legend = timing.legend(handles, ["Direct refit", "CV tree-fit work"], loc="upper center",
                           bbox_to_anchor=(.5, -.90), ncol=2, frameon=False, fontsize=6.1,
                           handletextpad=.3, columnspacing=.8)
    heading = fig.text(.5, .98, "Farther sight: conditional gains, substantial costs",
             ha="center", va="top", fontsize=9.5, weight="bold")
    subtitle = fig.text(.5, .84, "Training-selected forests | 57 datasets | Five paired repetitions",
             ha="center", va="top", fontsize=7)
    interval_note = fig.text(.5, .075, "Pointwise mean intervals; adjusted location tests and sensitivities qualify gains.",
             ha="center", va="bottom", fontsize=6.4)
    scope_note = fig.text(.5, .02, "Families allow the indicated horizons, including pure forests; not an equal-budget comparison.",
             ha="center", va="bottom", fontsize=6.1)
    fig.canvas.draw()
    bounds = fig.bbox
    for artist in fig.findobj(matplotlib.text.Text):
        if not artist.get_visible() or not artist.get_text():
            continue
        box = artist.get_window_extent(fig.canvas.get_renderer())
        if box.x0 < -1 or box.y0 < -1 or box.x1 > bounds.width + 1 or box.y1 > bounds.height + 1:
            raise ValueError(f"Text extends beyond graphical abstract: {artist.get_text()}")
    major_labels = (heading, subtitle, accuracy.title, timing.title, legend,
                    accuracy.xaxis.label, timing.xaxis.label, interval_note, scope_note)
    boxes = [artist.get_window_extent(fig.canvas.get_renderer()) for artist in major_labels]
    for index, box in enumerate(boxes):
        for other_index in range(index + 1, len(boxes)):
            if box.overlaps(boxes[other_index]):
                raise ValueError(f"Graphical-abstract labels overlap: {index}, {other_index}")
    destination = args.destination
    destination.mkdir(parents=True, exist_ok=True)
    stem = destination / "graphical_abstract_fair"
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Title": "Bounded split optimization: gains and costs"})
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    fig.savefig(stem.with_suffix(".tiff"), dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    audit = {"protocol_fingerprint": report["protocol_fingerprint"],
             "input_sha256": {name: report["output_sha256"][name] for name in
                              ("summary.csv", "paired_primary_comparisons.csv", "fair_tuning_table.csv")},
             "matplotlib": matplotlib.__version__, "numpy": np.__version__,
             "pandas": pd.__version__, "drawing_method": "Direct data-derived Matplotlib plots; no image-generation model",
             "cost_scope": "Standalone CV constituent-fit sums and direct selected-model refit wall times; not equal budgets",
             "interval_scope": "Pointwise unadjusted mean-effect intervals, not signed-rank confidence intervals",
             "author_approval_required": True}
    stem.with_suffix(".json").write_text(json.dumps(audit, indent=2) + "\n")
    print(f"Wrote {stem}.pdf/.png/.tiff and provenance JSON; no models fitted.")


if __name__ == "__main__":
    main()
