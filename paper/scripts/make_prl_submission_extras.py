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
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
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

PANEL_TITLE_SIZE = 6.0
PANEL_CAPTION_SIZE = 5.2
PANEL_NOTE_SIZE = 5.0
BULLET_TEXT_SIZE = 5.0
BULLET_MARK_SIZE = 5.8


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _panel_clip(ax, box: tuple[float, float, float, float]) -> Rectangle:
    """Rectangular clip region; rounded paths truncate text in PDF output."""
    x, y, w, h = box
    clip_patch = Rectangle(
        (x + 0.015 * w, y + 0.006 * h),
        0.970 * w,
        0.988 * h,
        linewidth=0.0,
        facecolor="none",
        edgecolor="none",
    )
    ax.add_patch(clip_patch)
    return clip_patch


def _panel_text(
    ax,
    clip_patch: Rectangle,
    x: float,
    y: float,
    text: str,
    *,
    fontsize: float,
    **kwargs,
) -> None:
    artist = ax.text(x, y, text, fontsize=fontsize, clip_on=True, **kwargs)
    artist.set_clip_path(clip_patch)


def _panel_caption(
    ax,
    x: float,
    y: float,
    text: str,
    *,
    fontsize: float = PANEL_CAPTION_SIZE,
    **kwargs,
) -> None:
    """Footer captions skip clipping so PDF backends do not truncate descenders."""
    ax.text(x, y, text, fontsize=fontsize, clip_on=False, **kwargs)


def _panel_title(
    ax,
    x: float,
    y: float,
    text: str,
    *,
    title_centered: bool = False,
    **kwargs,
) -> None:
    """Panel titles skip clipping; PDF backends truncate wide centered labels."""
    ax.text(
        x,
        y,
        text,
        ha="center" if title_centered else "left",
        va="center",
        fontsize=PANEL_TITLE_SIZE,
        fontweight="bold",
        color=COLORS["ink"],
        clip_on=False,
        **kwargs,
    )


def _panel(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    *,
    title_centered: bool = False,
) -> Rectangle:
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
    clip_patch = _panel_clip(ax, (x, y, w, h))
    _panel_title(
        ax,
        x + (0.50 * w if title_centered else 0.018),
        y + h - 0.052,
        title,
        title_centered=title_centered,
    )
    return clip_patch


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


def _draw_tree_panel(
    ax,
    clip_patch: Rectangle,
    x: float,
    y: float,
    w: float,
    h: float,
) -> None:
    root = (x + 0.50 * w, y + 0.64 * h)
    children = [(x + 0.33 * w, y + 0.46 * h), (x + 0.67 * w, y + 0.46 * h)]
    leaves = [
        (x + 0.21 * w, y + 0.28 * h),
        (x + 0.43 * w, y + 0.28 * h),
        (x + 0.57 * w, y + 0.28 * h),
        (x + 0.79 * w, y + 0.28 * h),
    ]

    zone = FancyBboxPatch(
        (x + 0.13 * w, y + 0.24 * h),
        0.74 * w,
        0.28 * h,
        boxstyle="round,pad=0.008,rounding_size=0.008",
        linewidth=0.8,
        edgecolor=COLORS["green"],
        facecolor="#e8f2f0",
        alpha=0.45,
        linestyle="--",
        zorder=0,
    )
    ax.add_patch(zone)
    _panel_text(
        ax,
        clip_patch,
        x + 0.13 * w,
        y + 0.45 * h,
        "depth-k\nsubtree",
        ha="center",
        va="center",
        fontsize=PANEL_NOTE_SIZE,
        color=COLORS["green"],
        fontstyle="italic",
        zorder=1,
    )

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

    _panel_text(
        ax,
        clip_patch,
        x + 0.50 * w,
        y + 0.70 * h,
        "candidate split",
        ha="center",
        va="bottom",
        fontsize=PANEL_NOTE_SIZE,
        color=COLORS["muted"],
    )
    _panel_caption(
        ax,
        x + 0.50 * w,
        y + 0.09 * h,
        "Split choice optimizes impurity\nover a bounded local subtree.",
        ha="center",
        va="center",
        color=COLORS["muted"],
    )


def _draw_uniform_panel(
    ax,
    clip_patch: Rectangle,
    box: tuple[float, float, float, float],
) -> None:
    x, y, w, h = box
    bullets = [
        "Single trees gain only thin\naccuracy improvements.",
        "Uniformly farther-sighted forests\nrarely repay their time cost.",
        "A few k=2 trees in a greedy forest\ncan lift accuracy at similar fit time.",
    ]
    bullet_y = y + 0.74 * h
    line_gap = 0.138 * h
    for index, text in enumerate(bullets):
        yy = bullet_y - index * line_gap
        _panel_text(
            ax,
            clip_patch,
            x + 0.06 * w,
            yy,
            "\u2022",
            ha="left",
            va="top",
            fontsize=BULLET_MARK_SIZE,
            color=COLORS["green"],
        )
        _panel_text(
            ax,
            clip_patch,
            x + 0.10 * w,
            yy,
            text,
            ha="left",
            va="top",
            fontsize=BULLET_TEXT_SIZE,
            color=COLORS["ink"],
            linespacing=1.12,
        )
    _panel_caption(
        ax,
        x + 0.50 * w,
        y + 0.08 * h,
        "Extra sight helps little on average;\nsparse sight inside forests is the exception.",
        ha="center",
        va="bottom",
        color=COLORS["muted"],
    )


def _draw_mixed_panel(
    fig,
    ax,
    clip_patch: Rectangle,
    box: tuple[float, float, float, float],
) -> None:
    rows = _read_rows(TABLE_DIR / "mixed_sighted_forest_grid_summary.csv")
    keep = {
        "pure_k1": ("k=1", COLORS["green"], "o"),
        "mix_1_75_2_25": ("k=1.25", COLORS["gold"], "D"),
        "pure_k2": ("k=2", COLORS["red"], "s"),
    }

    x, y, w, h = box
    plot = fig.add_axes([x + 0.20 * w, y + 0.34 * h, 0.48 * w, 0.38 * h])
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
    plot.set_xlabel("fit time", fontsize=4.8, labelpad=1)
    plot.set_ylabel("accuracy", fontsize=4.3, labelpad=0)
    plot.yaxis.set_label_coords(-0.26, 0.5)
    plot.tick_params(axis="x", labelsize=3.9, length=2, pad=1)
    plot.tick_params(axis="y", labelsize=3.2, length=2, pad=0)
    plot.grid(axis="both", color="#e6ebef", linewidth=0.6, which="both")
    for spine in ["top", "right"]:
        plot.spines[spine].set_visible(False)

    handles, labels = plot.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        frameon=False,
        fontsize=3.4,
        loc="center",
        bbox_to_anchor=(x + 0.87 * w, y + 0.53 * h),
        handlelength=1.0,
        handletextpad=0.3,
        labelspacing=0.18,
        markerscale=0.6,
        borderaxespad=0.0,
    )

    _panel_caption(
        ax,
        x + 0.50 * w,
        y + 0.08 * h,
        "Mixed forests outperform uniform ones\nat equal computation time.",
        ha="center",
        va="bottom",
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
        (0.035, 0.17, 0.285, 0.62, "Bounded non-greedy splits", True),
        (0.357, 0.17, 0.285, 0.62, "Greedy defaults stay competitive", True),
        (0.679, 0.17, 0.285, 0.62, "Sparse sight helps forests", True),
    ]
    clips: list[Rectangle] = []
    for x, y, w, h, title, centered in panels:
        clips.append(_panel(ax, x, y, w, h, title, title_centered=centered))
    _draw_tree_panel(ax, clips[0], *panels[0][:4])
    _draw_uniform_panel(ax, clips[1], panels[1][:4])
    _draw_mixed_panel(fig, ax, clips[2], panels[2][:4])

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
