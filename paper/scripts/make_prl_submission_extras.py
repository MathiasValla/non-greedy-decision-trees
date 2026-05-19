"""Generate PRL submission side files.

The graphical abstract uses only original vector/raster elements and retained
article result summaries from this repository.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/mplconfig")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "tables"
PRL_DIR = ROOT / "prl_submission"


COLORS = {
    "ink": "#17202a",
    "muted": "#586474",
    "line": "#d6dde3",
    "green": "#2f6f73",
    "sage": "#7aa37b",
    "gold": "#b07f2f",
    "red": "#a04e44",
    "violet": "#6b5b95",
    "bg": "#f7faf9",
}


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _panel(ax, x: float, y: float, w: float, h: float, title: str) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=0.9,
        edgecolor=COLORS["line"],
        facecolor="white",
    )
    ax.add_patch(box)
    ax.text(
        x + 0.018,
        y + h - 0.052,
        title,
        ha="left",
        va="center",
        fontsize=7.0,
        fontweight="bold",
        color=COLORS["ink"],
    )


def _node(ax, xy: tuple[float, float], label: str, color: str) -> None:
    ax.add_patch(Circle(xy, 0.026, facecolor=color, edgecolor="white", linewidth=1.0))
    ax.text(*xy, label, ha="center", va="center", fontsize=6.8, color="white")


def _arrow(
    ax,
    xy1: tuple[float, float],
    xy2: tuple[float, float],
    color: str = COLORS["muted"],
    style: str = "-",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            xy1,
            xy2,
            arrowstyle="-|>",
            mutation_scale=7,
            linewidth=0.8,
            linestyle=style,
            color=color,
            shrinkA=1,
            shrinkB=1,
        )
    )


def _draw_tree_panel(ax, x: float, y: float, w: float, h: float) -> None:
    root = (x + 0.50 * w, y + 0.62 * h)
    children = [(x + 0.34 * w, y + 0.42 * h), (x + 0.66 * w, y + 0.42 * h)]
    leaves = [
        (x + 0.22 * w, y + 0.24 * h),
        (x + 0.45 * w, y + 0.24 * h),
        (x + 0.55 * w, y + 0.24 * h),
        (x + 0.78 * w, y + 0.24 * h),
    ]
    for child in children:
        _arrow(ax, root, child, COLORS["green"])
    for child, leaf_pair in zip(children, [leaves[:2], leaves[2:]]):
        for leaf in leaf_pair:
            _arrow(ax, child, leaf, COLORS["sage"], ":")
    _node(ax, root, "split", COLORS["green"])
    _node(ax, children[0], "L", COLORS["sage"])
    _node(ax, children[1], "R", COLORS["sage"])
    for leaf in leaves:
        _node(ax, leaf, "", COLORS["gold"])
    ax.text(
        x + 0.50 * w,
        y + 0.09 * h,
        "Split choice looks ahead\nto descendant leaves.",
        ha="center",
        va="center",
        fontsize=6.7,
        color=COLORS["muted"],
    )


def _draw_uniform_panel(fig, box: tuple[float, float, float, float]) -> None:
    rows = _read_rows(TABLE_DIR / "lookahead_aggregate_results.csv")
    forest = [row for row in rows if row["estimator_slug"] == "forest"]
    forest.sort(key=lambda row: int(row["lookahead_depth"]))
    k = np.array([int(row["lookahead_depth"]) for row in forest])
    acc = np.array([float(row["mean_accuracy"]) for row in forest])
    time = np.array([float(row["mean_fit_time_s"]) for row in forest])
    acc_gain = 100 * (acc - acc[0])
    log_time = np.log10(time / time[0])

    x, y, w, h = box
    plot = fig.add_axes([x + 0.11 * w, y + 0.34 * h, 0.76 * w, 0.38 * h])
    plot.plot(k, acc_gain, marker="o", linewidth=1.7, color=COLORS["green"])
    plot.set_xticks([1, 2, 3])
    plot.set_xlabel("k", fontsize=5.8, labelpad=0)
    plot.set_ylabel("gain", fontsize=5.8, color=COLORS["green"], labelpad=0)
    plot.tick_params(axis="both", labelsize=5.5, length=2, pad=1)
    plot.tick_params(axis="y", colors=COLORS["green"])
    plot.grid(axis="y", color="#e6ebef", linewidth=0.6)
    for spine in ["top", "right"]:
        plot.spines[spine].set_visible(False)

    twin = plot.twinx()
    twin.plot(k, log_time, marker="s", linewidth=1.7, color=COLORS["red"])
    twin.set_ylabel("cost", fontsize=5.8, color=COLORS["red"], labelpad=0)
    twin.tick_params(axis="y", labelsize=5.5, colors=COLORS["red"], length=2, pad=1)
    twin.spines["top"].set_visible(False)

    fig.text(
        x + 0.50 * w,
        y + 0.09 * h,
        "Accuracy rises slowly;\ntime rises sharply.",
        ha="center",
        va="center",
        fontsize=6.7,
        color=COLORS["muted"],
    )


def _draw_mixed_panel(fig, box: tuple[float, float, float, float]) -> None:
    rows = _read_rows(TABLE_DIR / "mixed_sighted_forest_grid_summary.csv")
    keep = {
        "pure_k1": ("k=1", COLORS["green"], "o"),
        "mix_1_75_2_25": ("mixed k=1.25", COLORS["gold"], "D"),
        "pure_k2": ("k=2", COLORS["red"], "s"),
    }

    x, y, w, h = box
    plot = fig.add_axes([x + 0.12 * w, y + 0.34 * h, 0.76 * w, 0.38 * h])
    for curve_id, (label, color, marker) in keep.items():
        curve = [row for row in rows if row["curve_id"] == curve_id]
        curve.sort(key=lambda row: int(row["tree_count"]))
        times = [float(row["mean_fit_time_s"]) for row in curve]
        acc = [float(row["mean_accuracy"]) for row in curve]
        plot.plot(times, acc, marker=marker, linewidth=1.5, markersize=3.4, color=color, label=label)

    budget = 0.7
    plot.axvline(budget, color=COLORS["ink"], linestyle="--", linewidth=0.8, alpha=0.7)
    mixed = next(
        row
        for row in rows
        if row["curve_id"] == "mix_1_75_2_25" and int(row["tree_count"]) == 20
    )
    plot.scatter(
        [float(mixed["mean_fit_time_s"])],
        [float(mixed["mean_accuracy"])],
        s=40,
        facecolors="none",
        edgecolors=COLORS["ink"],
        linewidth=1.0,
        zorder=5,
    )
    plot.set_xscale("log")
    plot.set_xlabel("fit time", fontsize=5.8, labelpad=0)
    plot.set_ylabel("accuracy", fontsize=5.8, labelpad=0)
    plot.tick_params(axis="both", labelsize=5.5, length=2, pad=1)
    plot.grid(axis="both", color="#e6ebef", linewidth=0.6, which="both")
    plot.legend(frameon=False, fontsize=5.1, loc="lower right", borderpad=0.1)
    for spine in ["top", "right"]:
        plot.spines[spine].set_visible(False)

    fig.text(
        x + 0.50 * w,
        y + 0.09 * h,
        "At fixed time,\nmixed forests can be higher.",
        ha="center",
        va="center",
        fontsize=6.7,
        color=COLORS["muted"],
    )


def make_graphical_abstract() -> None:
    PRL_DIR.mkdir(parents=True, exist_ok=True)
    width_cm, height_cm = 13.28, 5.31
    fig = plt.figure(
        figsize=(width_cm / 2.54, height_cm / 2.54),
        dpi=300,
        facecolor="white",
    )
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.add_patch(
        FancyBboxPatch(
            (0.006, 0.006),
            0.988,
            0.988,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor=COLORS["bg"],
            edgecolor="#ecf0f2",
            linewidth=0.6,
        )
    )

    ax.text(
        0.035,
        0.93,
        "Sparse farther-sighted trees improve forest tradeoffs",
        ha="left",
        va="center",
        fontsize=8.8,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        0.035,
        0.855,
        "k-sighted induction evaluates splits through optimized local descendants.",
        ha="left",
        va="center",
        fontsize=6.9,
        color=COLORS["muted"],
    )

    panels = [
        (0.035, 0.17, 0.285, 0.62, "Bounded non-greedy splits"),
        (0.357, 0.17, 0.285, 0.62, "Uniform sight is costly"),
        (0.679, 0.17, 0.285, 0.62, "Sparse sight helps forests"),
    ]
    for panel in panels:
        _panel(ax, *panel)
    _draw_tree_panel(ax, *panels[0][:4])
    _draw_uniform_panel(fig, panels[1][:4])
    _draw_mixed_panel(fig, panels[2][:4])

    ax.text(
        0.50,
        0.075,
        "Takeaway: greedy trees are strong; use extra sight sparsely inside forests.",
        ha="center",
        va="center",
        fontsize=6.8,
        fontweight="bold",
        color=COLORS["ink"],
    )

    base = PRL_DIR / "graphical_abstract"
    fig.savefig(base.with_suffix(".pdf"))
    fig.savefig(base.with_suffix(".eps"))
    fig.savefig(base.with_suffix(".png"), dpi=300)
    tiff_path = base.with_suffix(".tiff")
    fig.savefig(tiff_path, dpi=300)
    plt.close(fig)
    with Image.open(tiff_path) as image:
        image.convert("RGB").save(tiff_path, compression="tiff_lzw")


def main() -> None:
    make_graphical_abstract()


if __name__ == "__main__":
    main()
