"""Task-aware summaries, paired metrics, CSV exports, and pilot-study charts."""

from __future__ import annotations

import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger
from matplotlib.figure import Figure
from tabulate import tabulate

from .experiments import EXPERIMENT_NAMES
from .storage import load_jsonl

PILOT_LIMITATION = (
    "This is a small pilot study using up to three hand-written tasks. Repeated requests and perturbations of the same "
    "task are not independent reasoning problems; results describe these prompts and this backend only."
)


def summarize_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Aggregate task-level accuracy, variability, format, and latency metrics."""
    if not records:
        return pd.DataFrame()
    frame = pd.DataFrame(records)
    evaluated = frame[frame["is_correct"].notna()].copy()
    rows: list[dict[str, Any]] = []
    group_columns = [column for column in ("experiment_id", "task_id") if column in frame]
    for keys, group in frame.groupby(group_columns, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        key_values = dict(zip(group_columns, keys, strict=False))
        valid = group[group["is_correct"].notna()]
        outputs = group["raw_response"].dropna().astype(str)
        answers = group["normalized_answer"].dropna().astype(str)
        latencies = pd.to_numeric(group.get("response_latency_seconds", pd.Series(dtype=float)), errors="coerce")
        latencies = latencies.dropna()
        answer_counts = answers.value_counts()
        rows.append(
            {
                **key_values,
                "experiment_name": EXPERIMENT_NAMES.get(
                    str(key_values.get("experiment_id", "")),
                    "Smoke Test" if key_values.get("experiment_id") == "00" else "Unknown",
                ),
                "sample_count": len(group),
                "evaluated_count": len(valid),
                "failure_count": int(group.get("error_type", pd.Series(index=group.index)).notna().sum()),
                "accuracy": float(valid["is_correct"].astype(bool).mean()) if len(valid) else np.nan,
                "distinct_raw_outputs": int(outputs.nunique()),
                "distinct_normalized_answers": int(answers.nunique()),
                "most_frequent_answer": answer_counts.index[0] if len(answer_counts) else None,
                "most_frequent_answer_count": int(answer_counts.iloc[0]) if len(answer_counts) else 0,
                "format_violation_rate": _format_violation_rate(group)
                if len(group)
                else np.nan,
                "raw_response_length_std": float(outputs.str.len().std(ddof=0)) if len(outputs) else np.nan,
                "latency_p50_seconds": float(latencies.quantile(0.50)) if len(latencies) else np.nan,
                "latency_p90_seconds": float(latencies.quantile(0.90)) if len(latencies) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def _format_violation_rate(group: pd.DataFrame) -> float:
    """Calculate output-format violations among completed API responses only."""
    responses = group[group["error_type"].isna()] if "error_type" in group else group
    if responses.empty:
        return np.nan
    return float((~responses["format_compliant"].fillna(False).astype(bool)).mean())


def paired_condition_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate paired flips and noise/order interaction using matched records."""
    frame = pd.DataFrame(records)
    result: dict[str, Any] = {"paired_comparisons": [], "interaction_effect": []}
    if frame.empty:
        return result
    if {"experiment_id", "task_id", "repetition", "factor_condition"}.issubset(frame.columns):
        interaction = frame[frame["experiment_id"] == "05"]
        for task_id, task_rows in interaction.groupby("task_id", sort=True):
            pivot = task_rows.pivot_table(
                index=["block_id", "repetition"],
                columns="factor_condition",
                values="is_correct",
                aggfunc="first",
            )
            required = {"original_clean", "shuffled_clean", "original_noisy", "shuffled_noisy"}
            if not required.issubset(pivot.columns):
                continue
            matched = pivot[sorted(required)].dropna().astype(float)
            if matched.empty:
                continue
            delta = (matched["shuffled_noisy"] - matched["original_noisy"]) - (
                matched["shuffled_clean"] - matched["original_clean"]
            )
            result["interaction_effect"].append(
                {"task_id": task_id, "matched_blocks": len(delta), "accuracy_interaction": float(delta.mean())}
            )
    for experiment_id in ("02", "03"):
        subset = frame[frame["experiment_id"] == experiment_id]
        if subset.empty:
            continue
        baseline = subset[subset.get("perturbation_id").isna() & subset.get("noise_position").isna()]
        for task_id, task_rows in subset.groupby("task_id", sort=True):
            task_baseline = baseline[baseline["task_id"] == task_id]
            if task_baseline.empty:
                continue
            for condition_key in ("noise_position", "perturbation_id"):
                if condition_key not in task_rows:
                    continue
                conditions = task_rows[task_rows[condition_key].notna()]
                for condition, condition_rows in conditions.groupby(condition_key, sort=True):
                    if condition_key == "noise_position":
                        match_keys = ["repetition"]
                    else:
                        match_keys = ["repetition"]
                    left = task_baseline.set_index(match_keys)
                    right = condition_rows.set_index(match_keys)
                    paired = left[["normalized_answer", "is_correct"]].join(
                        right[["normalized_answer", "is_correct"]],
                        how="inner",
                        lsuffix="_clean",
                        rsuffix="_condition",
                    ).dropna(subset=["is_correct_clean", "is_correct_condition"])
                    if paired.empty:
                        continue
                    result["paired_comparisons"].append(
                        {
                            "experiment_id": experiment_id,
                            "task_id": task_id,
                            "condition_type": condition_key,
                            "condition": str(condition),
                            "matched_count": len(paired),
                            "answer_flip_rate": float(
                                (paired["normalized_answer_clean"] != paired["normalized_answer_condition"]).mean()
                            ),
                            "correct_to_wrong_rate": (
                                float(
                                    (
                                        paired["is_correct_clean"].astype(bool)
                                        & ~paired["is_correct_condition"].astype(bool)
                                    ).sum()
                                    / int(paired["is_correct_clean"].astype(bool).sum())
                                )
                                if paired["is_correct_clean"].astype(bool).any()
                                else None
                            ),
                            "accuracy_degradation": float(
                                paired["is_correct_clean"].astype(bool).mean()
                                - paired["is_correct_condition"].astype(bool).mean()
                            ),
                        }
                    )
    return result


def cluster_bootstrap_accuracy(records: list[dict[str, Any]], seed: int = 1729) -> tuple[float, float] | None:
    """Bootstrap task-level mean accuracy when at least ten task clusters exist."""
    frame = pd.DataFrame(records)
    if frame.empty or not {"task_id", "is_correct"}.issubset(frame.columns):
        return None
    valid = frame[frame["is_correct"].notna()]
    task_accuracies = valid.groupby("task_id")["is_correct"].mean().to_numpy(dtype=float)
    if len(task_accuracies) < 10:
        return None
    rng = np.random.default_rng(seed)
    samples = rng.choice(task_accuracies, size=(5000, len(task_accuracies)), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def generate_report(input_path: Path, output_dir: Path) -> Path:
    """Generate CSV, Markdown, and PNG reports from a saved JSONL run."""
    records = load_jsonl(input_path)
    if not records:
        raise ValueError(f"No result records found in {input_path.resolve()}")
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
        summary = summarize_records(records)
        summary_path = output_dir / "summary.csv"
        _write_csv(summary, summary_path)
        detail = pd.DataFrame(records)
        _write_csv(detail, output_dir / "records.csv")
        _write_condition_tables(output_dir, detail)
        paired = paired_condition_metrics(records)
        _write_markdown(output_dir / "report.md", summary, paired, records)
        _write_charts(output_dir / "charts", detail, summary)
        logger.info(f"Report generated from {input_path.resolve()} at {output_dir.resolve()}")
        return output_dir
    except Exception:
        logger.error(f"Failed to generate report for {input_path.resolve()}\n{traceback.format_exc()}")
        raise


def _write_markdown(path: Path, summary: pd.DataFrame, paired: dict[str, Any], records: list[dict[str, Any]]) -> None:
    """Write a self-contained report with task-level interpretation limits."""
    try:
        with path.open("w", encoding="utf-8", newline="\n") as report_file:
            report_file.write("# LLM Stability Lab Research Report\n\n")
            report_file.write(f"Generated at: {datetime.now(UTC).isoformat()}\n\n")
            report_file.write(f"{PILOT_LIMITATION}\n\n")
            report_file.write("## Task-level results\n\n")
            report_file.write(tabulate(summary.fillna("—"), headers="keys", tablefmt="github", showindex=False))
            report_file.write("\n\n## Paired perturbation results\n\n")
            if paired["paired_comparisons"]:
                report_file.write(
                    tabulate(paired["paired_comparisons"], headers="keys", tablefmt="github", showindex=False)
                )
            else:
                report_file.write("No matched perturbation comparisons are available.\n")
            report_file.write("\n\n## Noise and answer-order interaction\n\n")
            if paired["interaction_effect"]:
                report_file.write(
                    tabulate(paired["interaction_effect"], headers="keys", tablefmt="github", showindex=False)
                )
            else:
                report_file.write("No complete matched factorial blocks are available.\n")
            report_file.write("\n\n## Selected option by correct-answer position\n\n")
            selected_positions = _selected_position_table(pd.DataFrame(records))
            if selected_positions.empty:
                report_file.write("No valid multiple-choice selections are available.\n")
            else:
                report_file.write(
                    tabulate(selected_positions, headers="keys", tablefmt="github", showindex=False)
                )
            length_summary = _noise_length_summary(pd.DataFrame(records))
            if not length_summary.empty:
                report_file.write("\n\n## Noise length and errors\n\n")
                report_file.write(tabulate(length_summary, headers="keys", tablefmt="github", showindex=False))
            report_file.write("\n\n## Uncertainty\n\n")
            interval = cluster_bootstrap_accuracy(records)
            if interval is None:
                report_file.write(
                    "Task-cluster bootstrap confidence intervals are omitted because this run does not contain "
                    "at least ten independent task clusters. Repeated calls are not counted as independent tasks.\n"
                )
            else:
                report_file.write(f"Task-cluster bootstrap 95% interval: {interval[0]:.3f} to {interval[1]:.3f}.\n")
            report_file.write("\n## Limitations\n\n")
            report_file.write(f"- {PILOT_LIMITATION}\n")
            report_file.write("- An accepted request does not prove the backend applied every requested setting.\n")
    except Exception:
        logger.error(f"Failed to write Markdown report {path.resolve()}\n{traceback.format_exc()}")
        raise


def _write_condition_tables(output_dir: Path, records: pd.DataFrame) -> None:
    """Write machine-readable noise-position, answer-position, and answer-choice tables."""
    noise = records[records["experiment_id"] == "02"].copy()
    if not noise.empty:
        noise["noise_position"] = noise["noise_position"].fillna("clean")
        noise_summary = noise.groupby(["task_id", "noise_position"], dropna=False)["is_correct"].agg(
            accuracy="mean", sample_count="count"
        ).reset_index()
        _write_csv(noise_summary, output_dir / "accuracy_by_noise_position.csv")
    positions = records[records["experiment_id"] == "04"].copy()
    if not positions.empty:
        position_summary = positions.groupby(["task_id", "correct_numeric_answer"], dropna=False)["is_correct"].agg(
            accuracy="mean", sample_count="count"
        ).reset_index()
        _write_csv(position_summary, output_dir / "accuracy_by_correct_answer_position.csv")
        _write_csv(_selected_position_table(records), output_dir / "selected_option_distribution.csv")
    length_summary = _noise_length_summary(records)
    if not length_summary.empty:
        _write_csv(length_summary, output_dir / "noise_length_errors.csv")


def _noise_length_summary(records: pd.DataFrame) -> pd.DataFrame:
    """Summarize evaluated answers and failures by measured noise length and condition."""
    if "experiment_id" not in records:
        return pd.DataFrame()
    data = records[records["experiment_id"] == "06"].copy()
    if data.empty:
        return pd.DataFrame()
    for key in ("noise_target_tokens", "noise_tokens", "noise_position_planned", "answer_order"):
        data[key] = data["experiment_metadata"].map(lambda value: (value or {}).get(key))
    data["incorrect"] = data["is_correct"].eq(False)
    data["failed_request"] = data["error_type"].notna()
    data["format_violation"] = ~data["format_compliant"].fillna(False).astype(bool) & ~data["failed_request"]
    data["truncated"] = data["parse_status"].eq("truncated") & ~data["failed_request"]
    result = data.groupby(
        ["task_id", "noise_target_tokens", "noise_tokens", "noise_position_planned", "answer_order"],
        dropna=False,
    ).agg(requests=("case_id", "size"), evaluated=("is_correct", "count"),
          incorrect=("incorrect", "sum"), format_violations=("format_violation", "sum"),
          truncated=("truncated", "sum"), failed_requests=("failed_request", "sum")).reset_index()
    result["error_rate"] = result["incorrect"] / result["evaluated"].replace(0, np.nan)
    return result


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    """Write one UTF-8 CSV file and include its full path in failures."""
    try:
        frame.to_csv(path, index=False, encoding="utf-8")
    except Exception:
        logger.error(f"Failed to write CSV file {path.resolve()}\n{traceback.format_exc()}")
        raise


def _save_figure(figure: Figure, path: Path) -> None:
    """Save and close a chart, logging its full path on failure."""
    try:
        figure.savefig(path, dpi=150)
    except Exception:
        logger.error(f"Failed to save chart file {path.resolve()}\n{traceback.format_exc()}")
        raise
    finally:
        plt.close(figure)


def _write_charts(charts_dir: Path, records: pd.DataFrame, summary: pd.DataFrame) -> None:
    """Generate six compact visual summaries, skipping inapplicable charts."""
    try:
        charts_dir.mkdir(parents=True, exist_ok=True)
        _save_accuracy_chart(charts_dir / "accuracy_by_experiment_task.png", summary)
        _save_noise_position_chart(charts_dir / "accuracy_by_noise_position.png", records)
        _save_correct_position_chart(charts_dir / "accuracy_by_correct_position.png", records)
        _save_answer_distribution(charts_dir / "selected_answers.png", records)
        _save_selected_position_chart(charts_dir / "selected_option_positions.png", records)
        _save_clean_noisy_chart(charts_dir / "clean_vs_noisy.png", records)
        _save_interaction_chart(charts_dir / "noise_order_interaction.png", records)
        _save_noise_length_chart(charts_dir / "noise_length_errors.png", records)
    except Exception:
        logger.error(f"Failed to generate charts in {charts_dir.resolve()}\n{traceback.format_exc()}")
        raise


def _save_accuracy_chart(path: Path, summary: pd.DataFrame) -> None:
    """Plot accuracy for each experiment and task."""
    chart = summary.dropna(subset=["accuracy"])
    if chart.empty:
        return
    pivot = chart.pivot(index="task_id", columns="experiment_id", values="accuracy")
    axis = pivot.plot(kind="bar", figsize=(10, 5), ylim=(0, 1), ylabel="Accuracy", rot=0)
    axis.set_title("Accuracy by experiment and task")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _save_noise_length_chart(path: Path, records: pd.DataFrame) -> None:
    """Plot error rates against measured noise-token lengths for each task and order."""
    summary = _noise_length_summary(records)
    if summary.empty:
        return
    totals = summary.groupby(["task_id", "answer_order", "noise_tokens"], dropna=False)[
        ["incorrect", "evaluated"]
    ].sum().reset_index()
    totals["error_rate"] = totals["incorrect"] / totals["evaluated"].replace(0, np.nan)
    pivot = totals.pivot(index="noise_tokens", columns=["task_id", "answer_order"], values="error_rate")
    axis = pivot.plot(marker="o", figsize=(10, 5), ylim=(0, 1))
    axis.set_xlabel("Noise tokens (selected model tokenizer)")
    axis.set_ylabel("Error rate among evaluated responses")
    axis.set_title("Answer errors by noise length")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _save_noise_position_chart(path: Path, records: pd.DataFrame) -> None:
    """Plot experiment 02 accuracy by noise placement."""
    data = records[records["experiment_id"] == "02"].copy()
    if data.empty or "noise_position" not in data:
        return
    data["position"] = data["noise_position"].fillna("clean")
    grouped = data.groupby(["task_id", "position"], dropna=False)["is_correct"].mean().unstack()
    if grouped.empty:
        return
    axis = grouped.plot(kind="bar", figsize=(10, 5), ylim=(0, 1), ylabel="Accuracy", rot=0)
    axis.set_title("Accuracy by noise position")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _save_correct_position_chart(path: Path, records: pd.DataFrame) -> None:
    """Plot answer-shuffle accuracy against the displayed correct option number."""
    data = records[(records["experiment_id"] == "04") & records["correct_numeric_answer"].notna()]
    if data.empty:
        return
    grouped = data.groupby(["task_id", "correct_numeric_answer"])["is_correct"].mean().unstack()
    axis = grouped.plot(kind="line", marker="o", figsize=(9, 5), ylim=(0, 1), ylabel="Accuracy")
    axis.set_xlabel("Displayed position of correct answer")
    axis.set_title("Accuracy by correct-answer position")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _save_answer_distribution(path: Path, records: pd.DataFrame) -> None:
    """Plot selected semantic answers, retaining malformed responses as a category."""
    data = records[records["experiment_id"] == "04"].copy()
    if "error_type" in data:
        data = data[data["error_type"].isna()]
    if data.empty:
        return
    data["answer"] = data["normalized_answer"].fillna(data["parse_status"].fillna("failed"))
    counts = data.groupby(["task_id", "answer"]).size().unstack(fill_value=0)
    axis = counts.plot(kind="bar", stacked=True, figsize=(10, 5), rot=0)
    axis.set_ylabel("Selections")
    axis.set_title("Selected semantic answers in answer-order experiment")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _save_selected_position_chart(path: Path, records: pd.DataFrame) -> None:
    """Plot selected numeric positions against correct-answer positions."""
    required = {"experiment_id", "correct_numeric_answer", "selected_numeric_option"}
    if not required.issubset(records.columns):
        return
    data = records[(records["experiment_id"] == "04") & records["selected_numeric_option"].notna()]
    if data.empty:
        return
    counts = data.groupby(["correct_numeric_answer", "selected_numeric_option"]).size().unstack(fill_value=0)
    axis = counts.plot(kind="bar", figsize=(10, 5), rot=0)
    axis.set_xlabel("Displayed correct-answer position")
    axis.set_ylabel("Selected-option count")
    axis.set_title("Selected option distribution by correct-answer position")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _selected_position_table(records: pd.DataFrame) -> pd.DataFrame:
    """Return observed selections grouped by correct and selected option positions."""
    required = {"experiment_id", "correct_numeric_answer", "selected_numeric_option"}
    if not required.issubset(records.columns):
        return pd.DataFrame()
    data = records[(records["experiment_id"] == "04") & records["selected_numeric_option"].notna()]
    return (
        data.groupby(["task_id", "correct_numeric_answer", "selected_numeric_option"], dropna=False)
        .size()
        .rename("selection_count")
        .reset_index()
    )


def _save_clean_noisy_chart(path: Path, records: pd.DataFrame) -> None:
    """Compare clean and noisy accuracy for the position experiment."""
    data = records[records["experiment_id"] == "02"].copy()
    if data.empty:
        return
    data["condition"] = np.where(data["noise_text"].notna(), "noisy", "clean")
    grouped = data.groupby(["task_id", "condition"])["is_correct"].mean().unstack()
    if grouped.empty:
        return
    axis = grouped.plot(kind="bar", figsize=(8, 5), ylim=(0, 1), rot=0)
    axis.set_ylabel("Accuracy")
    axis.set_title("Clean versus noisy accuracy")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)


def _save_interaction_chart(path: Path, records: pd.DataFrame) -> None:
    """Plot the factorial noise by answer-order interaction."""
    data = records[records["experiment_id"] == "05"].copy()
    if data.empty or "factor_condition" not in data:
        return
    data["order"] = np.where(data["factor_condition"].str.startswith("shuffled"), "shuffled", "original")
    data["noise"] = np.where(data["factor_condition"].str.endswith("noisy"), "noisy", "clean")
    grouped = data.groupby(["task_id", "order", "noise"])["is_correct"].mean().unstack("noise")
    if grouped.empty:
        return
    axis = grouped.plot(kind="bar", figsize=(9, 5), ylim=(0, 1), rot=0)
    axis.set_ylabel("Accuracy")
    axis.set_title("Accuracy by order and noise condition")
    axis.figure.tight_layout()
    _save_figure(axis.figure, path)
