"""Validate the complete revision run and derive tables, uncertainty, and plots."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper/array_revision"
SEEDS = (1000, 1001, 1002, 1003, 1004)
DEPTHS = ("3", "6", "None")
MODELS = ("tree_k1", "tree_k2", "greedy20", "mix05_20", "mix10_20",
          "mix25_20", "mix50_20", "sighted2_20", "greedy100", "mix05_100",
          "mix10_100", "mix25_100", "greedy200")
LABELS = {"tree_k1": "Greedy tree", "tree_k2": "Two-sighted tree",
          "greedy20": "Greedy (20)", "mix05_20": "5% two-sighted (20)",
          "mix10_20": "10% two-sighted (20)", "mix25_20": "25% two-sighted (20)",
          "mix50_20": "50% two-sighted (20)", "sighted2_20": "Two-sighted (20)",
          "greedy100": "Greedy (100)", "mix05_100": "5% two-sighted (100)",
          "mix10_100": "10% two-sighted (100)", "mix25_100": "25% two-sighted (100)",
          "greedy200": "Greedy (200)", "cart_tuned": "Tuned CART",
          "rf_tuned": "Tuned random forest"}
LABELS.update({"cart_fixed": "CART tree", "cart_bag100": "CART bagging (100)",
               "cart_bag200": "CART bagging (200)", "cart_mix10_100": "CART + 10% two-sighted (100)",
               "rf_sqrt_fixed": "Random forest (sqrt)"})


def family(name):
    for prefix in ("GAMETES", "monk", "led", "parity5", "analcatdata_cyyoung"):
        if name.startswith(prefix):
            return prefix
    return name


def synthetic(name):
    prefixes = ("GAMETES", "monk", "led", "parity5")
    return name.startswith(prefixes) or name in {
        "prnn_synth", "mux6", "corral", "threeOf9", "mofn_3_7_10", "xd6", "tic_tac_toe"
    }


def ci(values, seed=41):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, (20000, len(values)), replace=True).mean(axis=1)
    return [float(value) for value in np.quantile(samples, [0.025, 0.975])]


def holm(values):
    values = np.asarray(values, dtype=float)
    order = np.argsort(values)
    adjusted = np.maximum.accumulate((len(values) - np.arange(len(values))) * values[order])
    result = np.empty_like(values)
    result[order] = np.minimum(adjusted, 1.0)
    return result


def p_value(differences):
    values = np.round(np.asarray(differences), 12)
    if not np.any(values):
        return 1.0
    return float(wilcoxon(values, zero_method="wilcox", alternative="two-sided",
                          method="auto").pvalue)


def load_results():
    names = pd.read_csv(REPO / "paper/tables/mixed_sighted_dataset_sample.csv")["dataset"].tolist()
    expected = {(name, seed, depth) for name in names for seed in SEEDS for depth in DEPTHS}
    rows, seen, meta = [], set(), []
    for path in sorted((OUT / "raw").glob("*.json")):
        task = json.loads(path.read_text())
        key = task["dataset"], task["seed"], task["max_depth"]
        if key not in expected or key in seen:
            raise ValueError(f"Unexpected or duplicated task: {key}")
        seen.add(key)
        required = set(MODELS) | ({"cart_tuned", "rf_tuned", "majority"} if key[2] == "3" else set())
        ids = [row["model_id"] for row in task["rows"]]
        if set(ids) != required or len(ids) != len(required):
            raise ValueError(f"Incomplete model block: {key}")
        for row in task["rows"]:
            record = {**{k: v for k, v in task.items() if k != "rows"}, **row}
            record["task_depth"] = key[2]
            if not 0 <= record["accuracy"] <= 1 or not 0 <= record["balanced_accuracy"] <= 1:
                raise ValueError(f"Invalid score: {key}")
            if not np.isfinite(record["fit_time_s"]) or record["fit_time_s"] < 0:
                raise ValueError(f"Invalid timing: {key}")
            rows.append(record)
        meta.append({k: task[k] for k in ("dataset", "n_samples", "n_features", "n_classes")})
    if seen != expected:
        missing = sorted(expected - seen)
        raise ValueError(f"Run incomplete: {len(seen)}/{len(expected)} tasks, e.g. {missing[:5]}")
    controls_seen = set()
    for path in sorted((OUT / "raw_cart").glob("*.json")):
        task = json.loads(path.read_text())
        key = task["dataset"], task["seed"], task["max_depth"]
        if key not in expected or key in controls_seen:
            raise ValueError(f"Unexpected or duplicate CART task: {key}")
        controls_seen.add(key)
        original = json.loads((OUT / "raw" / path.name).read_text())
        for index_key in ("train_index_sha256", "test_index_sha256"):
            if task[index_key] != original[index_key]:
                raise ValueError(f"CART control split mismatch: {key}")
        ids = [row["model_id"] for row in task["rows"]]
        required = {"cart_fixed", "cart_bag100", "cart_bag200", "cart_mix10_100", "rf_sqrt_fixed"}
        if set(ids) != required or len(ids) != len(required):
            raise ValueError(f"Incomplete CART model block: {key}")
        for row in task["rows"]:
            record = {**{k: v for k, v in task.items() if k != "rows"}, **row}
            record["task_depth"] = key[2]
            if not 0 <= record["accuracy"] <= 1 or not 0 <= record["balanced_accuracy"] <= 1:
                raise ValueError(f"Invalid CART score: {key}")
            if not np.isfinite(record["fit_time_s"]) or record["fit_time_s"] < 0:
                raise ValueError(f"Invalid CART timing: {key}")
            rows.append(record)
    if controls_seen != expected:
        raise ValueError(f"CART controls incomplete: {len(controls_seen)}/{len(expected)}")
    # Put exact constituent sums on one consistent scale across depths. The
    # direct wall times remain separately available in the raw/result files.
    for record in rows:
        record["fit_cost_s"] = record.get("tree_fit_sum_s", record["fit_time_s"])
    return pd.DataFrame(rows), pd.DataFrame(meta).drop_duplicates("dataset"), len(seen)


def contrast(dataset_means, left, left_depth, right, right_depth, test_family, label):
    a = dataset_means[(dataset_means.model_id == left) & (dataset_means.task_depth == left_depth)].set_index("dataset")
    b = dataset_means[(dataset_means.model_id == right) & (dataset_means.task_depth == right_depth)].set_index("dataset")
    if set(a.index) != set(b.index):
        raise ValueError("Unpaired datasets")
    b = b.loc[a.index]
    delta = a.accuracy - b.accuracy
    low, high = ci(delta)
    grouped = delta.groupby([family(name) for name in delta.index]).mean()
    non_synthetic = delta[[not synthetic(name) for name in delta.index]]
    row = {"label": label, "left": left, "left_depth": left_depth,
           "right": right, "right_depth": right_depth, "test_family": test_family,
           "n_datasets": len(delta), "mean_delta": delta.mean(), "median_delta": delta.median(),
           "ci_low": low, "ci_high": high, "wilcoxon_p": p_value(delta),
           "wins": int((delta > 1e-12).sum()), "ties": int((delta.abs() <= 1e-12).sum()),
           "losses": int((delta < -1e-12).sum()),
           "balanced_accuracy_delta": float((a.balanced_accuracy - b.balanced_accuracy).mean()),
           "mean_time_ratio": float(a.fit_time_s.mean() / b.fit_time_s.mean()),
           "median_paired_time_ratio": float((a.fit_time_s / b.fit_time_s).median()),
           "family_groups": len(grouped), "family_mean_delta": grouped.mean(),
           "family_ci_low": ci(grouped)[0], "family_ci_high": ci(grouped)[1],
           "family_wilcoxon_p": p_value(grouped),
           "non_synthetic_n": len(non_synthetic), "non_synthetic_delta": non_synthetic.mean(),
           "non_synthetic_ci_low": ci(non_synthetic)[0],
           "non_synthetic_ci_high": ci(non_synthetic)[1]}
    values = pd.DataFrame({"dataset": delta.index, "label": label, "delta": delta.values,
                           "family": [family(name) for name in delta.index]})
    return row, values


def latex_p(value):
    return "$<0.001$" if value < 0.001 else f"{value:.3f}"


def make_tables(summary, comparisons):
    lines = []
    for depth in DEPTHS:
        for model in ("cart_fixed", "tree_k2", "cart_bag100", "cart_mix10_100", "rf_sqrt_fixed"):
            r = summary[(summary.task_depth == depth) & (summary.model_id == model)].iloc[0]
            display_depth = r"$\infty$" if depth == "None" else depth
            label = LABELS[model].replace("%", r"\%")
            lines.append(f"{label} & {display_depth} & {r.accuracy:.4f} & "
                         f"{r.balanced_accuracy:.4f} & {r.fit_time_s:.3f} & {r.realized_depth:.1f}" + r" \\")
    for model in ("cart_tuned", "rf_tuned"):
        r = summary[summary.model_id == model].iloc[0]
        lines.append(f"{LABELS[model]} & tuned & {r.accuracy:.4f} & "
                     f"{r.balanced_accuracy:.4f} & {r.fit_time_s:.3f} & --" + r" \\")
    (OUT / "table_performance.tex").write_text("\n".join(lines) + "\n")
    lines = []
    for r in comparisons[comparisons.test_family.isin(["primary", "cart_control"])].itertuples():
        depth = r"$\infty$" if r.left_depth == "None" else r.left_depth
        labels = {"tree_k2": "Two-sighted vs. greedy tree", "sighted2_20": "Two-sighted vs. greedy (20)",
                  "mix10_100": "10\\% mixture vs. greedy (100)",
                  "cart_mix10_100": "CART mixture vs. CART bagging"}
        label = "Two-sighted vs. CART tree" if r.right == "cart_fixed" else labels[r.left]
        lines.append(f"{label} & {depth} & {100*r.mean_delta:.2f} "
                     f"[{100*r.ci_low:.2f}, {100*r.ci_high:.2f}] & {latex_p(r.holm_p)} & "
                     f"{r.wins}/{r.ties}/{r.losses} & {r.mean_time_ratio:.1f}" + r" \\")
    (OUT / "table_comparisons.tex").write_text("\n".join(lines) + "\n")


def make_figures(summary, comparisons):
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.0), constrained_layout=True)
    colors = {"tree_k2": "#176A8A", "sighted2_20": "#BE593B", "cart_mix10_100": "#3B8559"}
    labels = {"tree_k2": "Two-sighted vs CART tree", "sighted2_20": "Two-sighted vs custom greedy (20)",
              "cart_mix10_100": "CART mixture vs CART bagging (100)"}
    for i, model in enumerate(colors):
        target_family = "primary" if model == "sighted2_20" else "cart_control"
        records = comparisons[(comparisons.test_family == target_family) & (comparisons.left == model)].set_index("left_depth").loc[list(DEPTHS)]
        x = np.arange(3) + (i - 1) * .18
        y = 100 * records.mean_delta.to_numpy()
        low, high = 100 * records.ci_low.to_numpy(), 100 * records.ci_high.to_numpy()
        axes[0].errorbar(x, y, yerr=np.array([y-low, high-y]), marker="o", ls="none",
                         capsize=3, color=colors[model], label=labels[model])
        axes[1].plot(np.arange(3), records.mean_time_ratio, "o-", color=colors[model])
    axes[0].axhline(0, color="0.45", lw=.8)
    for ax in axes:
        ax.set_xticks(range(3), ["3", "6", "Unlimited"])
        ax.set_xlabel("Maximum tree depth")
    axes[0].set_ylabel("Accuracy difference (percentage points)")
    axes[0].legend(fontsize=7, loc="best")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Ratio of mean fitting costs")
    axes[0].set_title("(a) Paired accuracy differences")
    axes[1].set_title("(b) Relative fitting cost")
    fig.savefig(OUT / "Fig1_depth_sensitivity.pdf")
    fig.savefig(OUT / "Fig1_depth_sensitivity.png", dpi=240)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(7.1, 3.1), sharey=True, constrained_layout=True)
    curve_colors = ["#727272", "#288868", "#007CBA", "#C45434", "#555AA5"]
    for ax, depth in zip(axes, DEPTHS):
        for model, color in zip(("cart_bag100", "cart_mix10_100", "rf_sqrt_fixed", "mix25_100", "cart_bag200"), curve_colors):
            r = summary[(summary.task_depth == depth) & (summary.model_id == model)].iloc[0]
            ax.errorbar(r.fit_time_s, r.accuracy,
                        yerr=np.array([[r.accuracy-r.accuracy_ci_low], [r.accuracy_ci_high-r.accuracy]]),
                        fmt="o", capsize=2, color=color, label=LABELS[model], markersize=4)
        r = summary[summary.model_id == "rf_tuned"].iloc[0]
        ax.errorbar(r.fit_time_s, r.accuracy,
                    yerr=np.array([[r.accuracy-r.accuracy_ci_low], [r.accuracy_ci_high-r.accuracy]]),
                    fmt="*", markersize=10, capsize=2, color="#242424", label=LABELS["rf_tuned"], zorder=5)
        ax.set_xscale("log")
        ax.set_xlabel("Mean fitting cost (s)")
        ax.set_title("Depth " + ("unlimited" if depth == "None" else depth))
    axes[0].set_ylabel("Mean test accuracy")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, fontsize=7)
    fig.savefig(OUT / "Fig2_accuracy_cost.pdf")
    fig.savefig(OUT / "Fig2_accuracy_cost.png", dpi=240)
    plt.close(fig)


def main():
    frame, metadata, task_count = load_results()
    OUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT / "revision_results.csv", index=False)
    means = frame.groupby(["dataset", "task_depth", "model_id"], as_index=False).agg(
        accuracy=("accuracy", "mean"), balanced_accuracy=("balanced_accuracy", "mean"),
        fit_time_s=("fit_cost_s", "mean"), realized_depth=("realized_depth", "mean"),
        repeats=("seed", "nunique"))
    if not (means.repeats == len(SEEDS)).all():
        raise ValueError("Unbalanced repeat counts")
    means.to_csv(OUT / "dataset_means.csv", index=False)
    summaries = []
    for (depth, model), group in means.groupby(["task_depth", "model_id"]):
        low, high = ci(group.accuracy)
        summaries.append({"task_depth": depth, "model_id": model,
                          "n_datasets": len(group), "accuracy": group.accuracy.mean(),
                          "accuracy_ci_low": low, "accuracy_ci_high": high,
                          "balanced_accuracy": group.balanced_accuracy.mean(),
                          "fit_time_s": group.fit_time_s.mean(),
                          "median_fit_time_s": group.fit_time_s.median(),
                          "realized_depth": group.realized_depth.mean()})
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "summary.csv", index=False)
    contrasts, deltas = [], []
    for depth in DEPTHS:
        for left, right in (("tree_k2", "tree_k1"), ("sighted2_20", "greedy20"),
                            ("mix10_100", "greedy100")):
            row, values = contrast(means, left, depth, right, depth, "primary", f"{left}-{right}_D{depth}")
            contrasts.append(row)
            deltas.append(values)
        for left, right in (("tree_k2", "cart_tuned"), ("mix10_100", "rf_tuned")):
            row, values = contrast(means, left, depth, right, "3", "tuned_baseline", f"{left}_D{depth}-{right}")
            contrasts.append(row)
            deltas.append(values)
        for left, right in (("tree_k2", "cart_fixed"), ("cart_mix10_100", "cart_bag100")):
            row, values = contrast(means, left, depth, right, depth, "cart_control", f"{left}-{right}_D{depth}")
            contrasts.append(row)
            deltas.append(values)
        row, values = contrast(means, "cart_mix10_100", depth, "rf_tuned", "3",
                               "tuned_baseline", f"cart_mix10_100_D{depth}-rf_tuned")
        contrasts.append(row)
        deltas.append(values)
    for depth in ("6", "None"):
        row, values = contrast(means, "mix10_100", "3", "greedy100", depth,
                               "deep_greedy", f"mix10_D3-greedy_D{depth}")
        contrasts.append(row)
        deltas.append(values)
    comparisons = pd.DataFrame(contrasts)
    for group in comparisons.test_family.unique():
        selected = comparisons.test_family == group
        comparisons.loc[selected, "holm_p"] = holm(comparisons.loc[selected, "wilcoxon_p"])
        comparisons.loc[selected, "family_holm_p"] = holm(comparisons.loc[selected, "family_wilcoxon_p"])
    selected = comparisons.test_family.isin(["primary", "cart_control"])
    comparisons.loc[selected, "holm_p"] = holm(comparisons.loc[selected, "wilcoxon_p"])
    comparisons.loc[selected, "family_holm_p"] = holm(comparisons.loc[selected, "family_wilcoxon_p"])
    comparisons.to_csv(OUT / "paired_comparisons.csv", index=False)
    pd.concat(deltas).to_csv(OUT / "paired_dataset_deltas.csv", index=False)
    metadata["family"] = metadata.dataset.map(family)
    metadata["named_synthetic_sensitivity"] = metadata.dataset.map(synthetic)
    metadata.to_csv(OUT / "dataset_manifest.csv", index=False)
    tuned = frame[frame.model_id.isin(["cart_tuned", "rf_tuned"])]
    tuned[["dataset", "seed", "model_id", "params", "fit_time_s", "selection_fit_time_s"]].to_csv(
        OUT / "tuning_results.csv", index=False)
    validation = {"complete_tasks": task_count, "expected_tasks": len(metadata)*5*3,
                  "complete_cart_control_tasks": task_count,
                  "datasets": len(metadata), "result_rows": len(frame),
                  "known_family_groups": metadata.family.nunique(),
                  "named_non_synthetic_datasets": int((~metadata.named_synthetic_sensitivity).sum()),
                  "all_repeats_balanced": True, "missing_or_duplicate_tasks": 0,
                  "n_samples_range": [int(metadata.n_samples.min()), int(metadata.n_samples.max())],
                  "n_features_range": [int(metadata.n_features.min()), int(metadata.n_features.max())]}
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    make_tables(summary, comparisons)
    make_figures(summary, comparisons)
    print(json.dumps(validation, indent=2))
    print(comparisons[["label", "mean_delta", "ci_low", "ci_high", "holm_p", "mean_time_ratio"]].to_string(index=False))


if __name__ == "__main__":
    main()
