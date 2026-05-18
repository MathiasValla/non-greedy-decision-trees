"""Generate tables and figures for the k-sighted decision-tree letter.

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
PRL_DIR = ROOT / "prl_submission"
MIXED_FOREST_RESULTS = TABLE_DIR / "mixed_sighted_forest_results.csv"
MIXED_FOREST_GRID_RESULTS = TABLE_DIR / "mixed_sighted_forest_grid_results.csv"
TREE_COUNTS_FOR_FIGURE = (20, 40, 60, 100, 200)

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

FOREST_SIZE_SMALL_DATASETS = [
    "iris",
    "wine_recognition",
    "ecoli",
    "haberman",
    "balance_scale",
]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
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
                    "comparison": f"k={depth} vs k=1",
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
                "comparison": "k=3 vs k=2",
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


def _utility_rows() -> list[dict[str, object]]:
    by_key = {
        (row["estimator"], row["lookahead_depth"]): row for row in AGGREGATE_ROWS
    }
    rows = []
    for estimator in ["Decision tree", "Random forest"]:
        baseline = by_key[(estimator, 1)]
        for depth in [2, 3]:
            current = by_key[(estimator, depth)]
            delta_accuracy = current["mean_accuracy"] - baseline["mean_accuracy"]
            log_time_ratio = float(
                np.log(current["mean_fit_time_s"] / baseline["mean_fit_time_s"])
            )
            rows.append(
                {
                    "estimator": estimator,
                    "comparison": f"k={depth} vs k=1",
                    "delta_accuracy": round(delta_accuracy, 6),
                    "log_fit_time_ratio": round(log_time_ratio, 3),
                    "break_even_lambda": round(delta_accuracy / log_time_ratio, 6),
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
    axes[0].set_xlabel("Sight depth k")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_xticks(depths)
    axes[0].set_ylim(0.66, 0.745)
    axes[0].grid(axis="y", color="#dddddd", linewidth=0.8)

    axes[1].set_title("Mean fit time")
    axes[1].set_xlabel("Sight depth k")
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


def make_accuracy_time_tradeoff_figure() -> None:
    colors = {
        "Decision tree": "#2f6f73",
        "Random forest": "#b07f2f",
    }
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0), constrained_layout=True)
    depths = np.array([1, 2, 3])
    for estimator in ["Decision tree", "Random forest"]:
        rows = _rows_for(estimator)
        base_acc = rows[0]["mean_accuracy"]
        gain = np.array([100 * (row["mean_accuracy"] - base_acc) for row in rows])
        fit_time = np.array([row["mean_fit_time_s"] for row in rows])
        axes[0].plot(
            depths,
            gain,
            marker="o",
            linewidth=2,
            color=colors[estimator],
            label=estimator,
        )
        axes[1].plot(
            depths,
            fit_time,
            marker="o",
            linewidth=2,
            color=colors[estimator],
            label=estimator,
        )

    axes[0].set_xlabel("Sight depth k")
    axes[0].set_ylabel("Accuracy gain vs. k=1 (p.p.)")
    axes[0].set_xticks(depths)
    axes[0].grid(axis="y", color="#dddddd", linewidth=0.8)
    axes[0].legend(frameon=False)

    axes[1].set_xlabel("Sight depth k")
    axes[1].set_ylabel("Mean fit time (s, log scale)")
    axes[1].set_xticks(depths)
    axes[1].set_yscale("log")
    axes[1].grid(axis="y", color="#dddddd", linewidth=0.8, which="both")
    axes[1].legend(frameon=False)

    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"lookahead_accuracy_time_tradeoff.{suffix}", dpi=220)
    for suffix in ["pdf", "png"]:
        fig.savefig(ROOT / "amai_submission" / f"Fig1_accuracy_time.{suffix}", dpi=220)
    if PRL_DIR.exists():
        for suffix in ["pdf", "png"]:
            fig.savefig(PRL_DIR / f"Fig1_accuracy_time.{suffix}", dpi=220)
    plt.close(fig)


def _read_forest_size_small() -> list[dict[str, object]]:
    path = TABLE_DIR / "forest_size_tradeoff.csv"
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["dataset"] not in FOREST_SIZE_SMALL_DATASETS:
                continue
            row["n_samples"] = int(row["n_samples"])
            row["n_features"] = int(row["n_features"])
            row["lookahead_depth"] = int(row["lookahead_depth"])
            row["n_estimators"] = int(row["n_estimators"])
            row["fit_time"] = float(row["fit_time"])
            row["accuracy"] = float(row["accuracy"])
            rows.append(row)
    return rows


def _forest_size_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[int, int], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(
            (row["lookahead_depth"], row["n_estimators"]), []
        ).append(row)
    summary = []
    for (lookahead_depth, n_estimators), items in sorted(grouped.items()):
        accuracies = np.array([row["accuracy"] for row in items])
        times = np.array([row["fit_time"] for row in items])
        summary.append(
            {
                "lookahead_depth": lookahead_depth,
                "n_estimators": n_estimators,
                "datasets": len(items),
                "mean_accuracy": round(float(accuracies.mean()), 6),
                "median_accuracy": round(float(np.median(accuracies)), 6),
                "mean_fit_time_s": round(float(times.mean()), 6),
                "median_fit_time_s": round(float(np.median(times)), 6),
            }
        )
    return summary


def _read_mixed_forest_results() -> list[dict[str, object]]:
    if not MIXED_FOREST_RESULTS.exists():
        return []
    rows: list[dict[str, object]] = []
    with MIXED_FOREST_RESULTS.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row["n_samples"] = int(row["n_samples"])
            row["n_features"] = int(row["n_features"])
            row["effective_k"] = float(row["effective_k"])
            row["depth_1_trees"] = int(row["depth_1_trees"])
            row["depth_2_trees"] = int(row["depth_2_trees"])
            row["depth_3_trees"] = int(row["depth_3_trees"])
            row["n_estimators"] = int(row["n_estimators"])
            row["fit_time_s"] = float(row["fit_time_s"])
            row["accuracy"] = float(row["accuracy"])
            rows.append(row)
    return rows


def _read_mixed_forest_grid_results() -> list[dict[str, object]]:
    if not MIXED_FOREST_GRID_RESULTS.exists():
        return []
    rows: list[dict[str, object]] = []
    with MIXED_FOREST_GRID_RESULTS.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row["n_samples"] = int(row["n_samples"])
            row["n_features"] = int(row["n_features"])
            row["display_order"] = int(row["display_order"])
            row["effective_k"] = float(row["effective_k"])
            row["tree_count"] = int(row["tree_count"])
            row["depth_1_trees"] = int(row["depth_1_trees"])
            row["depth_2_trees"] = int(row["depth_2_trees"])
            row["depth_3_trees"] = int(row["depth_3_trees"])
            row["fit_time_s"] = float(row["fit_time_s"])
            row["accuracy"] = float(row["accuracy"])
            rows.append(row)
    return rows


def _mixed_forest_grid_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((row["curve_id"], row["tree_count"]), []).append(row)

    summary = []
    for (curve_id, tree_count), items in sorted(
        grouped.items(), key=lambda kv: (kv[1][0]["display_order"], kv[0][1])
    ):
        first = items[0]
        accuracies = np.array([row["accuracy"] for row in items])
        times = np.array([row["fit_time_s"] for row in items])
        summary.append(
            {
                "curve_id": curve_id,
                "curve_label": first["curve_label"],
                "display_order": first["display_order"],
                "effective_k": first["effective_k"],
                "tree_count": tree_count,
                "depth_1_trees": first["depth_1_trees"],
                "depth_2_trees": first["depth_2_trees"],
                "depth_3_trees": first["depth_3_trees"],
                "datasets": len(items),
                "mean_accuracy": round(float(accuracies.mean()), 6),
                "median_accuracy": round(float(np.median(accuracies)), 6),
                "mean_fit_time_s": round(float(times.mean()), 6),
                "median_fit_time_s": round(float(np.median(times)), 6),
            }
        )

    baseline = next(
        (
            row
            for row in summary
            if row["curve_id"] == "pure_k1" and row["tree_count"] == 100
        ),
        None,
    )
    if baseline is not None:
        for row in summary:
            row["accuracy_gain_vs_k1_100_pp"] = round(
                100 * (row["mean_accuracy"] - baseline["mean_accuracy"]), 3
            )
            row["time_ratio_vs_k1_100"] = round(
                row["mean_fit_time_s"] / baseline["mean_fit_time_s"], 3
            )
    return summary


def _make_mixed_forest_grid_tradeoff_figure(rows: list[dict[str, object]]) -> None:
    summary = _mixed_forest_grid_summary(rows)
    _write_csv(TABLE_DIR / "mixed_sighted_forest_grid_summary.csv", summary)

    completed_datasets = len({row["dataset"] for row in rows})
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in summary:
        grouped.setdefault(row["curve_id"], []).append(row)

    curve_order = sorted(
        grouped,
        key=lambda curve_id: grouped[curve_id][0]["display_order"],
    )
    colors = {
        "pure_k1": "#2f6f73",
        "mix_1_95_2_05": "#6f9b6d",
        "mix_1_90_2_10": "#8ea65b",
        "mix_1_95_3_05": "#7f6aa6",
        "mix_1_75_2_25": "#bda94b",
        "mix_1_50_2_50": "#b07f2f",
        "pure_k2": "#a04e44",
        "mix_2_95_3_05": "#7a4f63",
        "pure_k3": "#374151",
    }
    markers = {
        "pure_k1": "o",
        "mix_1_95_2_05": "P",
        "mix_1_90_2_10": "X",
        "mix_1_95_3_05": "D",
        "mix_1_75_2_25": "v",
        "mix_1_50_2_50": ">",
        "pure_k2": "s",
        "mix_2_95_3_05": "<",
        "pure_k3": "^",
    }

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.4))
    for curve_id in curve_order:
        curve_rows = sorted(grouped[curve_id], key=lambda row: row["tree_count"])
        label = curve_rows[0]["curve_label"]
        tree_counts = [row["tree_count"] for row in curve_rows]
        accuracies = [row["mean_accuracy"] for row in curve_rows]
        times = [row["mean_fit_time_s"] for row in curve_rows]
        axes[0].plot(
            tree_counts,
            accuracies,
            marker=markers[curve_id],
            linewidth=1.8,
            markersize=5.2,
            color=colors[curve_id],
            label=label,
        )
        axes[1].plot(
            times,
            accuracies,
            marker=markers[curve_id],
            linewidth=1.8,
            markersize=5.2,
            color=colors[curve_id],
            label=label,
        )

    all_accuracies = [row["mean_accuracy"] for row in summary]
    y_min = min(all_accuracies) - 0.004
    y_max = max(all_accuracies) + 0.006

    axes[0].set_xlabel("Number of trees")
    axes[0].set_ylabel("Mean accuracy")
    axes[0].set_title("Accuracy as forests grow")
    axes[0].set_xticks(list(TREE_COUNTS_FOR_FIGURE))
    axes[0].set_ylim(y_min, y_max)
    axes[0].grid(axis="both", color="#dddddd", linewidth=0.8)

    axes[1].set_xscale("log")
    axes[1].set_xlabel("Mean fit time (s, log scale)")
    axes[1].set_ylabel("Mean accuracy")
    axes[1].set_title("Accuracy-time frontier")
    axes[1].set_ylim(y_min, y_max)
    axes[1].grid(axis="both", color="#dddddd", linewidth=0.8, which="both")

    greedy_budget = next(
        row
        for row in summary
        if row["curve_id"] == "pure_k1" and row["tree_count"] == 100
    )
    mixed_at_budget = next(
        row
        for row in summary
        if row["curve_id"] == "mix_1_95_2_05" and row["tree_count"] == 40
    )
    axes[1].axvline(
        greedy_budget["mean_fit_time_s"],
        color="#111827",
        linestyle="--",
        linewidth=1.1,
        alpha=0.75,
        zorder=0,
    )
    axes[1].scatter(
        [greedy_budget["mean_fit_time_s"]],
        [greedy_budget["mean_accuracy"]],
        s=70,
        facecolors="none",
        edgecolors="#111827",
        linewidth=1.2,
        zorder=5,
    )
    axes[1].scatter(
        [mixed_at_budget["mean_fit_time_s"]],
        [mixed_at_budget["mean_accuracy"]],
        s=78,
        facecolors="none",
        edgecolors="#111827",
        linewidth=1.4,
        zorder=5,
    )
    axes[1].annotate(
        "similar time,\nhigher accuracy",
        xy=(mixed_at_budget["mean_fit_time_s"], mixed_at_budget["mean_accuracy"]),
        xytext=(
            greedy_budget["mean_fit_time_s"] * 1.9,
            mixed_at_budget["mean_accuracy"] + 0.0055,
        ),
        arrowprops={
            "arrowstyle": "->",
            "color": "#111827",
            "linewidth": 0.9,
        },
        fontsize=8,
        ha="left",
        va="bottom",
    )
    axes[1].text(
        greedy_budget["mean_fit_time_s"] * 1.07,
        y_min + 0.001,
        "100-tree\nk=1 time",
        fontsize=7.5,
        rotation=90,
        ha="left",
        va="bottom",
        color="#111827",
    )

    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        frameon=False,
        ncol=3,
        fontsize=8,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
    )
    fig.suptitle(
        f"Forest size, sight depth, and mixed k-sighted forests (n={completed_datasets})",
        fontsize=13,
        y=0.98,
    )
    fig.tight_layout(rect=[0, 0.16, 1, 0.93])
    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"sighted_forest_tradeoff.{suffix}", dpi=220)
    for suffix in ["pdf", "png"]:
        fig.savefig(ROOT / "amai_submission" / f"Fig2_forest_size.{suffix}", dpi=220)
    if PRL_DIR.exists():
        for suffix in ["pdf", "png"]:
            fig.savefig(PRL_DIR / f"Fig2_forest_size.{suffix}", dpi=220)
    plt.close(fig)


def _mixed_forest_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(row["schedule_id"], []).append(row)

    summary = []
    for schedule_id, items in sorted(grouped.items(), key=lambda kv: kv[0]):
        first = items[0]
        accuracies = np.array([row["accuracy"] for row in items])
        times = np.array([row["fit_time_s"] for row in items])
        summary.append(
            {
                "schedule_id": schedule_id,
                "label": first["label"],
                "kind": first["kind"],
                "effective_k": first["effective_k"],
                "depth_1_trees": first["depth_1_trees"],
                "depth_2_trees": first["depth_2_trees"],
                "depth_3_trees": first["depth_3_trees"],
                "n_estimators": first["n_estimators"],
                "datasets": len(items),
                "mean_accuracy": round(float(accuracies.mean()), 6),
                "median_accuracy": round(float(np.median(accuracies)), 6),
                "mean_fit_time_s": round(float(times.mean()), 6),
                "median_fit_time_s": round(float(np.median(times)), 6),
            }
        )

    baseline = next(
        (
            row
            for row in summary
            if row["schedule_id"] == "pure_k1_100"
        ),
        None,
    )
    if baseline is not None:
        for row in summary:
            row["accuracy_gain_vs_k1_100_pp"] = round(
                100 * (row["mean_accuracy"] - baseline["mean_accuracy"]), 3
            )
            row["time_ratio_vs_k1_100"] = round(
                row["mean_fit_time_s"] / baseline["mean_fit_time_s"], 3
            )
    return summary


def _mixture_annotation(row: dict[str, object]) -> str:
    d1 = row["depth_1_trees"]
    d2 = row["depth_2_trees"]
    d3 = row["depth_3_trees"]
    if d1 and d2:
        return f"{row['effective_k']:.2f}"
    if d1 and d3:
        return "1.10*"
    if d2 and d3:
        return "2.05"
    return f"{row['effective_k']:.2f}"


def _make_mixed_forest_tradeoff_figure(rows: list[dict[str, object]]) -> None:
    summary = _mixed_forest_summary(rows)
    _write_csv(TABLE_DIR / "mixed_sighted_forest_summary.csv", summary)

    completed_datasets = len({row["dataset"] for row in rows})
    colors = {1: "#2f6f73", 2: "#b07f2f", 3: "#a04e44"}
    markers = {1: "o", 2: "s", 3: "^"}

    fig, ax = plt.subplots(figsize=(7.1, 4.8), constrained_layout=True)
    for depth in [1, 2, 3]:
        subset = [
            row
            for row in summary
            if row["kind"] == "pure_size"
            and row[f"depth_{depth}_trees"] == row["n_estimators"]
        ]
        subset = sorted(subset, key=lambda row: row["n_estimators"])
        if not subset:
            continue
        x = [row["mean_fit_time_s"] for row in subset]
        y = [row["mean_accuracy"] for row in subset]
        labels = [row["n_estimators"] for row in subset]
        ax.plot(
            x,
            y,
            marker=markers[depth],
            linewidth=2,
            color=colors[depth],
            label=f"integer k={depth}",
        )
        for xi, yi, label in zip(x, y, labels):
            ax.annotate(
                str(label),
                (xi, yi),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
                color=colors[depth],
            )

    mixtures = sorted(
        [row for row in summary if row["kind"] == "mixture"],
        key=lambda row: (row["effective_k"], row["depth_3_trees"], row["depth_2_trees"]),
    )
    if mixtures:
        ax.scatter(
            [row["mean_fit_time_s"] for row in mixtures],
            [row["mean_accuracy"] for row in mixtures],
            marker="D",
            s=48,
            color="#374151",
            label="100-tree mixtures",
            zorder=4,
        )
        for row in mixtures:
            ax.annotate(
                _mixture_annotation(row),
                (row["mean_fit_time_s"], row["mean_accuracy"]),
                textcoords="offset points",
                xytext=(5, -11),
                fontsize=8,
                color="#374151",
            )

    ax.set_xscale("log")
    ax.set_xlabel("Mean fit time (s, log scale)")
    ax.set_ylabel("Mean accuracy")
    ax.set_title(f"Forest size, sight depth, and mixed forests (n={completed_datasets})")
    ax.grid(axis="both", color="#dddddd", linewidth=0.8, which="both")
    ax.legend(frameon=False, fontsize=9)
    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"sighted_forest_tradeoff.{suffix}", dpi=220)
    for suffix in ["pdf", "png"]:
        fig.savefig(ROOT / "amai_submission" / f"Fig2_forest_size.{suffix}", dpi=220)
    plt.close(fig)


def make_forest_size_tradeoff_figure() -> None:
    grid_rows = _read_mixed_forest_grid_results()
    if grid_rows:
        _make_mixed_forest_grid_tradeoff_figure(grid_rows)
        return

    mixed_rows = _read_mixed_forest_results()
    if mixed_rows:
        _make_mixed_forest_tradeoff_figure(mixed_rows)
        return

    rows = _read_forest_size_small()
    if not rows:
        return
    summary = _forest_size_summary(rows)
    _write_csv(TABLE_DIR / "forest_size_tradeoff_small_summary.csv", summary)
    colors = {1: "#2f6f73", 2: "#b07f2f"}
    markers = {1: "o", 2: "s"}
    fig, ax = plt.subplots(figsize=(6.2, 4.3), constrained_layout=True)
    for depth in [1, 2]:
        subset = [row for row in summary if row["lookahead_depth"] == depth]
        x = [row["mean_fit_time_s"] for row in subset]
        y = [row["mean_accuracy"] for row in subset]
        labels = [row["n_estimators"] for row in subset]
        ax.plot(
            x,
            y,
            marker=markers[depth],
            linewidth=2,
            color=colors[depth],
            label=f"integer k={depth}",
        )
        for xi, yi, label in zip(x, y, labels):
            ax.annotate(
                str(label),
                (xi, yi),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
            )
    ax.set_xscale("log")
    ax.set_xlabel("Mean fit time (s, log scale)")
    ax.set_ylabel("Mean accuracy")
    ax.grid(axis="both", color="#dddddd", linewidth=0.8, which="both")
    ax.legend(frameon=False)
    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"forest_size_tradeoff_small.{suffix}", dpi=220)
    for suffix in ["pdf", "png"]:
        fig.savefig(ROOT / "amai_submission" / f"Fig2_forest_size.{suffix}", dpi=220)
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
    axes[1].set_title("Evaluated sight-depth grid")
    axes[1].text(0.55, 0.86, "sight depth k", ha="center", fontsize=11, color="#555555")
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

    fig.suptitle("PMLB k-sighted benchmark scope", fontsize=14)
    for suffix in ["png", "pdf"]:
        fig.savefig(FIG_DIR / f"lookahead_benchmark_scope.{suffix}", dpi=220)
    plt.close(fig)


def write_summary() -> None:
    lines = [
        "# K-Sighted Tree Letter Assets",
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
        "- figures/sighted_forest_tradeoff.png",
        "- figures/sighted_forest_tradeoff.pdf",
        "- figures/lookahead_benchmark_scope.png",
        "- figures/lookahead_benchmark_scope.pdf",
    ]
    (ROOT / "asset_summary.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(TABLE_DIR / "lookahead_aggregate_results.csv", AGGREGATE_ROWS)
    _write_csv(TABLE_DIR / "lookahead_accuracy_cost_deltas.csv", _delta_rows())
    _write_csv(TABLE_DIR / "lookahead_utility_thresholds.csv", _utility_rows())
    _write_csv(TABLE_DIR / "lookahead_benchmark_accounting.csv", ACCOUNTING_ROWS)
    _write_csv(TABLE_DIR / "lookahead_wins_or_ties.csv", WIN_ROWS)
    make_accuracy_cost_figure()
    make_accuracy_time_tradeoff_figure()
    make_forest_size_tradeoff_figure()
    make_scope_figure()
    write_summary()


if __name__ == "__main__":
    main()
