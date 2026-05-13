"""Generate tables and figures for the lookahead decision-tree letter.

The raw PMLB result CSVs were temporary benchmark artifacts. This script
therefore regenerates the manuscript assets from the retained aggregate run
summary used in the draft. If the raw CSVs are restored, this script should be
replaced by a per-dataset analysis before journal submission.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/mplconfig")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
TABLE_DIR = ROOT / "tables"

COMPLETED_DATASETS = 67
RESULT_ROWS = 402
ATTEMPTED_DATASETS = 162

AGGREGATE_ROWS = [
    {
        "estimator": "Decision tree",
        "estimator_slug": "tree",
        "lookahead_depth": 1,
        "datasets": COMPLETED_DATASETS,
        "mean_accuracy": 0.693050,
        "median_accuracy": 0.755396,
        "mean_fit_time_s": 0.007554,
        "median_fit_time_s": 0.004333,
        "total_fit_time_s": 0.506,
    },
    {
        "estimator": "Decision tree",
        "estimator_slug": "tree",
        "lookahead_depth": 2,
        "datasets": COMPLETED_DATASETS,
        "mean_accuracy": 0.709993,
        "median_accuracy": 0.722222,
        "mean_fit_time_s": 0.372741,
        "median_fit_time_s": 0.054660,
        "total_fit_time_s": 24.974,
    },
    {
        "estimator": "Decision tree",
        "estimator_slug": "tree",
        "lookahead_depth": 3,
        "datasets": COMPLETED_DATASETS,
        "mean_accuracy": 0.714542,
        "median_accuracy": 0.733333,
        "mean_fit_time_s": 70.902457,
        "median_fit_time_s": 2.183356,
        "total_fit_time_s": 4750.465,
    },
    {
        "estimator": "Random forest",
        "estimator_slug": "forest",
        "lookahead_depth": 1,
        "datasets": COMPLETED_DATASETS,
        "mean_accuracy": 0.706771,
        "median_accuracy": 0.750000,
        "mean_fit_time_s": 0.018811,
        "median_fit_time_s": 0.011592,
        "total_fit_time_s": 1.260,
    },
    {
        "estimator": "Random forest",
        "estimator_slug": "forest",
        "lookahead_depth": 2,
        "datasets": COMPLETED_DATASETS,
        "mean_accuracy": 0.712458,
        "median_accuracy": 0.740741,
        "mean_fit_time_s": 0.694049,
        "median_fit_time_s": 0.120779,
        "total_fit_time_s": 46.501,
    },
    {
        "estimator": "Random forest",
        "estimator_slug": "forest",
        "lookahead_depth": 3,
        "datasets": COMPLETED_DATASETS,
        "mean_accuracy": 0.725979,
        "median_accuracy": 0.761194,
        "mean_fit_time_s": 96.186354,
        "median_fit_time_s": 4.057186,
        "total_fit_time_s": 6444.486,
    },
]

ACCOUNTING_ROWS = [
    {"outcome": "Completed datasets", "count": 67},
    {"outcome": "Dimension-filter skips", "count": 42},
    {"outcome": "Load/fetch skips", "count": 32},
    {"outcome": "Fit timeouts", "count": 21},
]

WIN_ROWS = [
    {"estimator": "Decision tree", "lookahead_depth": 1, "wins_or_ties": 30},
    {"estimator": "Decision tree", "lookahead_depth": 2, "wins_or_ties": 31},
    {"estimator": "Decision tree", "lookahead_depth": 3, "wins_or_ties": 37},
    {"estimator": "Random forest", "lookahead_depth": 1, "wins_or_ties": 36},
    {"estimator": "Random forest", "lookahead_depth": 2, "wins_or_ties": 29},
    {"estimator": "Random forest", "lookahead_depth": 3, "wins_or_ties": 29},
]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _delta_rows() -> list[dict[str, object]]:
    by_key = {
        (row["estimator"], row["lookahead_depth"]): row for row in AGGREGATE_ROWS
    }
    rows = []
    for estimator in ["Decision tree", "Random forest"]:
        baseline = by_key[(estimator, 1)]
        for depth in [2, 3]:
            current = by_key[(estimator, depth)]
            rows.append(
                {
                    "estimator": estimator,
                    "comparison": f"lookahead {depth} vs 1",
                    "mean_accuracy_delta": round(
                        current["mean_accuracy"] - baseline["mean_accuracy"], 6
                    ),
                    "mean_accuracy_delta_percentage_points": round(
                        100 * (current["mean_accuracy"] - baseline["mean_accuracy"]),
                        3,
                    ),
                    "mean_fit_time_ratio_for_comparison": round(
                        current["mean_fit_time_s"] / baseline["mean_fit_time_s"], 1
                    ),
                }
            )
        depth2 = by_key[(estimator, 2)]
        depth3 = by_key[(estimator, 3)]
        rows.append(
            {
                "estimator": estimator,
                "comparison": "lookahead 3 vs 2",
                "mean_accuracy_delta": round(
                    depth3["mean_accuracy"] - depth2["mean_accuracy"], 6
                ),
                "mean_accuracy_delta_percentage_points": round(
                    100 * (depth3["mean_accuracy"] - depth2["mean_accuracy"]), 3
                ),
                "mean_fit_time_ratio_for_comparison": round(
                    depth3["mean_fit_time_s"] / depth2["mean_fit_time_s"], 1
                ),
            }
        )
    return rows


def _rows_for(estimator: str) -> list[dict[str, object]]:
    return [row for row in AGGREGATE_ROWS if row["estimator"] == estimator]


def make_accuracy_cost_figure() -> None:
    colors = {
        "Decision tree": "#2f6f73",
        "Random forest": "#b07f2f",
    }
    depths = np.array([1, 2, 3])
    width = 0.35
    offsets = {
        "Decision tree": -width / 2,
        "Random forest": width / 2,
    }

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), constrained_layout=True)
    for estimator in ["Decision tree", "Random forest"]:
        rows = _rows_for(estimator)
        x = depths + offsets[estimator]
        accuracy = [row["mean_accuracy"] for row in rows]
        fit_time = [row["mean_fit_time_s"] for row in rows]
        axes[0].bar(x, accuracy, width=width, label=estimator, color=colors[estimator])
        axes[1].bar(x, fit_time, width=width, label=estimator, color=colors[estimator])

        for xi, yi in zip(x, accuracy):
            axes[0].text(xi, yi + 0.0025, f"{yi:.3f}", ha="center", va="bottom", fontsize=8)
        for xi, yi in zip(x, fit_time):
            axes[1].text(xi, yi * 1.25, f"{yi:.3g}s", ha="center", va="bottom", fontsize=8)

    axes[0].set_title("Mean test accuracy")
    axes[0].set_xlabel("Lookahead depth")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_xticks(depths)
    axes[0].set_ylim(0.66, 0.745)
    axes[0].grid(axis="y", color="#dddddd", linewidth=0.8)

    axes[1].set_title("Mean fit time")
    axes[1].set_xlabel("Lookahead depth")
    axes[1].set_ylabel("Seconds, log scale")
    axes[1].set_xticks(depths)
    axes[1].set_yscale("log")
    axes[1].set_ylim(0.003, 180)
    axes[1].grid(axis="y", color="#dddddd", linewidth=0.8, which="both")
    axes[1].legend(frameon=False, loc="upper left")

    fig.suptitle("Accuracy gains are small relative to fit-time growth", fontsize=14)
    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"lookahead_accuracy_cost.{suffix}", dpi=220)
    plt.close(fig)


def make_scope_figure() -> None:
    colors = ["#2f6f73", "#bda94b", "#999999", "#b85d4d"]
    fig, axes = plt.subplots(
        1, 2, figsize=(10.8, 4.2), gridspec_kw={"width_ratios": [1.35, 1.0]},
        constrained_layout=True
    )

    labels = [row["outcome"] for row in ACCOUNTING_ROWS]
    counts = [row["count"] for row in ACCOUNTING_ROWS]
    y = np.arange(len(labels))
    axes[0].barh(y, counts, color=colors, height=0.5)
    axes[0].set_yticks(y, labels)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Dataset count")
    axes[0].set_title(f"Benchmark accounting (n={ATTEMPTED_DATASETS} attempted)")
    axes[0].grid(axis="x", color="#dddddd", linewidth=0.8)
    axes[0].spines[["top", "right", "left"]].set_visible(False)
    for yi, count in zip(y, counts):
        axes[0].text(count + 1.5, yi, str(count), va="center", fontsize=10)

    axes[1].axis("off")
    axes[1].set_title("Evaluated lookahead grid")
    axes[1].text(0.55, 0.86, "lookahead depth", ha="center", fontsize=11, color="#555555")
    for j, depth in enumerate([1, 2, 3]):
        axes[1].text(0.35 + 0.2 * j, 0.78, str(depth), ha="center", fontsize=11, color="#555555")
    for i, estimator in enumerate(["Decision tree", "Random forest"]):
        yy = 0.56 - 0.36 * i
        axes[1].text(0.05, yy, estimator, ha="right", va="center", fontsize=12)
        for j, depth in enumerate([1, 2, 3]):
            xx = 0.27 + 0.2 * j
            rect = plt.Rectangle(
                (xx, yy - 0.09), 0.16, 0.18, fill=True,
                facecolor="#edf2ef", edgecolor="#4b5f5b", linewidth=1.2
            )
            axes[1].add_patch(rect)
            axes[1].text(xx + 0.08, yy, f"d={depth}", ha="center", va="center", fontsize=11)
    axes[1].set_xlim(-0.05, 1.0)
    axes[1].set_ylim(0.0, 1.0)

    fig.suptitle("PMLB lookahead benchmark scope", fontsize=14)
    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"lookahead_benchmark_scope.{suffix}", dpi=220)
    plt.close(fig)


def write_summary() -> None:
    lines = [
        "# Lookahead Letter Assets",
        "",
        f"Completed datasets: {COMPLETED_DATASETS}",
        f"Result rows: {RESULT_ROWS}",
        f"Attempted datasets in accounting: {ATTEMPTED_DATASETS}",
        "",
        "Generated tables:",
        "- tables/lookahead_aggregate_results.csv",
        "- tables/lookahead_accuracy_cost_deltas.csv",
        "- tables/lookahead_benchmark_accounting.csv",
        "- tables/lookahead_wins_or_ties.csv",
        "",
        "Generated figures:",
        "- figures/lookahead_accuracy_cost.png",
        "- figures/lookahead_accuracy_cost.pdf",
        "- figures/lookahead_benchmark_scope.png",
        "- figures/lookahead_benchmark_scope.pdf",
    ]
    (ROOT / "asset_summary.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(TABLE_DIR / "lookahead_aggregate_results.csv", AGGREGATE_ROWS)
    _write_csv(TABLE_DIR / "lookahead_accuracy_cost_deltas.csv", _delta_rows())
    _write_csv(TABLE_DIR / "lookahead_benchmark_accounting.csv", ACCOUNTING_ROWS)
    _write_csv(TABLE_DIR / "lookahead_wins_or_ties.csv", WIN_ROWS)
    make_accuracy_cost_figure()
    make_scope_figure()
    write_summary()


if __name__ == "__main__":
    main()
