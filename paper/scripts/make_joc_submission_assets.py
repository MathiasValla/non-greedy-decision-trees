"""Generate Journal of Classification submission figures.

The journal requests figures no larger than 4.8 by 6.8 inches and prefers EPS
for vector line graphics. These figures are compact versions of the retained
article result summaries.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/mplconfig")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "tables"
OUT_DIR = ROOT / "joc_submission"

COLORS = {
    "tree": "#2f6f73",
    "forest": "#b07f2f",
    "k1": "#2f6f73",
    "mix": "#b07f2f",
    "k2": "#a04e44",
    "grid": "#d9dee5",
    "ink": "#17202a",
}


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def make_accuracy_time() -> None:
    rows = _read_rows(TABLE_DIR / "lookahead_aggregate_results.csv")
    by_estimator = {
        "Decision tree": [row for row in rows if row["estimator"] == "Decision tree"],
        "Bootstrap forest": [row for row in rows if row["estimator"] == "Random forest"],
    }

    fig, axes = plt.subplots(2, 1, figsize=(4.8, 5.1), sharex=True)
    for label, items in by_estimator.items():
        items.sort(key=lambda row: int(row["lookahead_depth"]))
        depths = np.array([int(row["lookahead_depth"]) for row in items])
        accuracy = np.array([float(row["mean_accuracy"]) for row in items])
        fit_time = np.array([float(row["mean_fit_time_s"]) for row in items])
        color = COLORS["tree"] if label == "Decision tree" else COLORS["forest"]
        axes[0].plot(
            depths,
            100 * (accuracy - accuracy[0]),
            marker="o",
            linewidth=1.6,
            color=color,
            label=label,
        )
        axes[1].plot(
            depths,
            fit_time,
            marker="o",
            linewidth=1.6,
            color=color,
            label=label,
        )

    axes[0].set_ylabel("Accuracy gain\nvs. k=1 (p.p.)")
    axes[0].grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Mean fit time (s)")
    axes[1].set_xlabel("Sight depth k")
    axes[1].set_xticks([1, 2, 3])
    axes[1].grid(axis="y", color=COLORS["grid"], linewidth=0.7, which="both")
    for ax in axes:
        ax.tick_params(labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    for suffix in ("pdf", "eps"):
        fig.savefig(OUT_DIR / f"Fig1_accuracy_time.{suffix}")
    plt.close(fig)


def make_mixed_tradeoff() -> None:
    rows = _read_rows(TABLE_DIR / "mixed_sighted_forest_grid_summary.csv")
    keep = {
        "pure_k1": ("k=1", COLORS["k1"], "o"),
        "mix_1_75_2_25": ("mixed k=1.25", COLORS["mix"], "D"),
        "pure_k2": ("k=2", COLORS["k2"], "s"),
    }

    fig, ax = plt.subplots(figsize=(4.8, 3.6))
    for curve_id, (label, color, marker) in keep.items():
        curve = [row for row in rows if row["curve_id"] == curve_id]
        curve.sort(key=lambda row: int(row["tree_count"]))
        times = [float(row["mean_fit_time_s"]) for row in curve]
        accuracies = [float(row["mean_accuracy"]) for row in curve]
        ax.plot(
            times,
            accuracies,
            marker=marker,
            linewidth=1.6,
            markersize=4,
            color=color,
            label=label,
        )

    budget = 0.7
    ax.axvline(budget, color=COLORS["ink"], linestyle="--", linewidth=0.9)
    mixed = next(
        row
        for row in rows
        if row["curve_id"] == "mix_1_75_2_25" and int(row["tree_count"]) == 20
    )
    ax.scatter(
        [float(mixed["mean_fit_time_s"])],
        [float(mixed["mean_accuracy"])],
        s=55,
        facecolors="none",
        edgecolors=COLORS["ink"],
        linewidth=1.0,
        zorder=5,
    )
    ax.annotate(
        "fixed-time\ncomparison",
        xy=(float(mixed["mean_fit_time_s"]), float(mixed["mean_accuracy"])),
        xytext=(1.12, float(mixed["mean_accuracy"]) + 0.006),
        arrowprops={"arrowstyle": "->", "color": COLORS["ink"], "linewidth": 0.8},
        fontsize=8,
        ha="left",
    )
    ax.set_xscale("log")
    ax.set_xlabel("Mean fit time (s, log scale)")
    ax.set_ylabel("Mean accuracy")
    ax.grid(axis="both", color=COLORS["grid"], linewidth=0.7, which="both")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.tick_params(labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    for suffix in ("pdf", "eps"):
        fig.savefig(OUT_DIR / f"Fig2_mixed_tradeoff.{suffix}")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_accuracy_time()
    make_mixed_tradeoff()


if __name__ == "__main__":
    main()
