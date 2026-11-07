"""Repeat latency measurements across models, tasks and model-token noise lengths."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
import traceback
from collections import defaultdict
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import lmstudio as lms
import matplotlib.pyplot as plt
from loguru import logger
from tqdm import tqdm

from .config import AppConfig, load_config
from .evaluation import evaluate_response
from .inference import InferenceClient
from .noise_length import TEMPLATE_TOKEN_MARGIN, _noise_for_tokens
from .storage import append_jsonl
from .tasks import TASKS, ResearchTask, render_prompt

MODELS = ("openai/gpt-oss-20b", "qwen3.5-9b", "google/gemma-4-26b-a4b")
LEVELS = (0, 128, 256, 512, 1024, 2048, 3072, 4096, 6144, 8192)
ROUNDS = 3
REPETITIONS = 5
TASK_LABELS = {"task_01_math": "Математика", "task_02_logic": "Логика", "task_03_traffic": "Светофор"}
MODEL_SLUGS = {MODELS[0]: "oss", MODELS[1]: "qwen", MODELS[2]: "gemma"}
CaseKey = tuple[int, str, str, int, int]


def completed_cases(records: list[dict[str, Any]], context_limit: int = 18000) -> set[CaseKey]:
    """Validate prior records and return successfully recorded planned cases."""
    completed: set[CaseKey] = set()
    for row in records:
        if row["result"]["error_type"]:
            raise ValueError("Prior records contain API errors; inspect them before resuming")
        if row["phase"] == "resume_warmup":
            continue
        repetition = row["repetition"]
        expected_phase = "warmup" if repetition == 0 else "measurement"
        if row["phase"] != expected_phase or repetition not in range(REPETITIONS + 1):
            raise ValueError("Prior records contain an invalid phase or repetition")
        key = (row["round"], row["model"], row["task"], row["noise_target_tokens"], repetition)
        if (row["round"] not in range(1, ROUNDS + 1) or row["model"] not in MODELS
                or row["task"] not in TASK_LABELS or row["noise_target_tokens"] not in LEVELS or key in completed):
            raise ValueError(f"Invalid or duplicate prior case: {key}")
        if row["result"]["prompt_tokens"] is not None and (
            row["result"]["prompt_tokens"] + row["result"]["requested_parameters"]["max_tokens"] > context_limit
        ):
            raise ValueError(f"Prior case exceeds context budget: {key}")
        completed.add(key)
    return completed


def prepare_prompt(model: Any, settings: AppConfig, task: ResearchTask, target: int, seed: int) -> dict[str, Any]:
    """Build a seeded random prompt and verify its model-specific context budget."""
    limit = settings.run.experiment_6_context_limit
    noise, actual = _noise_for_tokens(model, target, variant="random_words", seed=seed)
    content, _ = render_prompt(task, noise_text=noise or None, noise_position="before_task" if noise else None)
    messages = [{"role": "system", "content": task.system_message}, {"role": "user", "content": content}]
    chat = lms.Chat.from_history({"messages": messages})
    prompt_tokens = len(model.tokenize(model.apply_prompt_template(chat)))
    if prompt_tokens + settings.inference.max_tokens + TEMPLATE_TOKEN_MARGIN > limit:
        raise ValueError(f"Context budget exceeded for {task.task_id}, target {target}: {prompt_tokens}")
    return {"noise_target_tokens": target, "noise_tokens": actual, "noise_seed": seed,
            "noise_variant": "random_words", "planned_prompt_tokens": prompt_tokens, "messages": messages}


def measure_model(
    settings: AppConfig, model_id: str, round_number: int, raw_path: Path, seed_base: int, done: set[CaseKey]
) -> None:
    """Measure one model in one round and save each response immediately."""
    host = urlparse(settings.inference.base_url).netloc
    config = settings.inference.model_copy(update={"model_id": model_id})
    with InferenceClient(config) as client:
        client.require_configured_model()
        with lms.Client(host) as sdk:
            model = sdk.llm.model(model_id, config={"contextLength": settings.run.experiment_6_context_limit}, ttl=3600)
            try:
                if model.get_context_length() < settings.run.experiment_6_context_limit:
                    raise ValueError(f"Loaded context is too small for {model_id}")
                total = len(LEVELS) * len(TASKS) * (REPETITIONS + 1)
                with tqdm(total=total, desc=f"Round {round_number}: {model_id}", unit="request") as progress:
                    for level in LEVELS:
                        for task in TASKS:
                            measure_group(client, model, settings, level, task, round_number, raw_path, progress,
                                          seed_base, done)
            finally:
                model.unload()


def measure_group(
    client: InferenceClient,
    model: Any,
    settings: AppConfig,
    target: int,
    task: ResearchTask,
    round_number: int,
    raw_path: Path,
    progress: Any,
    seed_base: int,
    done: set[CaseKey],
) -> None:
    """Measure consecutive repetitions of one model, task, and noise length."""
    def case_key(repetition: int) -> CaseKey:
        """Return the stable key for one planned request."""
        return round_number, client.config.model_id, task.task_id, target, repetition

    pending = [i for i in range(REPETITIONS + 1) if case_key(i) not in done]
    progress.update(REPETITIONS + 1 - len(pending))
    if not pending:
        return
    if 0 not in pending:
        pending.insert(0, -1)
    for repetition in pending:
        group_index = (((round_number - 1) * len(MODELS) + MODELS.index(client.config.model_id)) * len(LEVELS)
                       + LEVELS.index(target)) * len(TASKS) + TASKS.index(task)
        seed_offset = group_index * (REPETITIONS + 1) + repetition
        if repetition == -1:
            seed_offset = ROUNDS * len(MODELS) * len(LEVELS) * len(TASKS) * (REPETITIONS + 1) + group_index
        seed = seed_base + seed_offset
        prompt = prepare_prompt(model, settings, task, target, seed)
        if repetition <= 0:
            result = client.complete(prompt["messages"])
            elapsed = None
        else:
            start = time.perf_counter()
            result = client.complete(prompt["messages"])
            elapsed = time.perf_counter() - start
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "round": round_number,
            "model": client.config.model_id,
            "task": task.task_id,
            "phase": "resume_warmup" if repetition == -1 else ("warmup" if repetition == 0 else "measurement"),
            "repetition": repetition,
            **prompt,
            "latency_seconds": elapsed,
            "result": asdict(result),
        }
        append_jsonl(raw_path, record)
        if repetition != -1:
            progress.update(1)
        if result.error_type:
            raise RuntimeError(f"Inference failed; record saved in {raw_path.resolve()}: {result.error_message}")
        if (result.prompt_tokens is not None
                and result.prompt_tokens + client.config.max_tokens > settings.run.experiment_6_context_limit):
            raise RuntimeError(f"Server token usage exceeds context budget; record saved in {raw_path.resolve()}")
        if repetition != -1:
            done.add(case_key(repetition))


def summarize(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Calculate round medians and count incorrect or invalid responses."""
    groups: dict[tuple[str, str, int, int], list[float]] = defaultdict(list)
    errors: dict[tuple[str, str, int], int] = defaultdict(int)
    task_map = {task.task_id: task for task in TASKS}
    for row in records:
        if row["phase"] == "measurement" and row["result"]["error_type"] is None:
            key = (row["model"], row["task"], row["noise_target_tokens"], row["round"])
            groups[key].append(row["latency_seconds"])
            result = row["result"]
            evaluation = evaluate_response(task_map[row["task"]], result["raw_response"],
                                           truncated=result["finish_reason"] == "length")
            if evaluation.is_correct is not True:
                errors[key[:3]] += 1
    output: list[dict[str, Any]] = []
    for model in MODELS:
        for task in TASKS:
            for level in LEVELS:
                rounds = [groups[model, task.task_id, level, number] for number in range(1, ROUNDS + 1)]
                if any(len(values) != REPETITIONS for values in rounds):
                    raise ValueError(f"Incomplete measurements for {model}, {task.task_id}, level {level}")
                medians = [statistics.median(values) for values in rounds]
                output.append({
                    "model": model, "task": task.task_id, "noise_target_tokens": level,
                    "round_1_median_seconds": medians[0], "round_2_median_seconds": medians[1],
                    "round_3_median_seconds": medians[2], "median_seconds": statistics.median(medians),
                    "error_count": errors[model, task.task_id, level], "response_count": ROUNDS * REPETITIONS,
                })
    return output


def write_report(records: list[dict[str, Any]], output_dir: Path) -> None:
    """Write median statistics and one three-task chart per model."""
    rows = summarize(records)
    csv_path = output_dir / "latency_summary.csv"
    try:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        for model in MODELS:
            fig, axis = plt.subplots(figsize=(9, 5.2), layout="constrained")
            try:
                for task in TASKS:
                    selected = [row for row in rows if row["model"] == model and row["task"] == task.task_id]
                    axis.plot(LEVELS, [row["median_seconds"] for row in selected], marker="o",
                              label=TASK_LABELS[task.task_id])
                    flagged = [row for row in selected if row["error_count"] * 2 > row["response_count"]]
                    if flagged:
                        axis.scatter([row["noise_target_tokens"] for row in flagged],
                                     [row["median_seconds"] for row in flagged], marker="x", color="red",
                                     s=100, linewidths=2.5, zorder=5)
                axis.set_title(model)
                axis.set_xlabel("Целевая длина шума, токены модели")
                axis.set_ylabel("Медиана времени ответа, с")
                axis.set_ylim(bottom=0)
                axis.grid(True, alpha=0.25)
                axis.scatter([], [], marker="x", color="red", s=70, linewidths=2,
                             label="Более 50% ошибок")
                axis.legend()
                fig.savefig(output_dir / f"latency_{MODEL_SLUGS[model]}.png", dpi=160)
            finally:
                plt.close(fig)
    except Exception:
        logger.error(f"Could not write report in {output_dir.resolve()}\n{traceback.format_exc()}")
        raise


def main() -> None:
    """Run three sequential model rounds and generate a reproducible latency report."""
    try:
        parser = argparse.ArgumentParser(description="Run or resume a latency benchmark")
        parser.add_argument("--resume", type=Path, help="Existing benchmark directory to resume")
        args = parser.parse_args()
        if args.resume:
            output_dir = args.resume
            metadata_path = output_dir / "settings.json"
            with metadata_path.open(encoding="utf-8") as source:
                metadata = json.load(source)
            if (metadata["models"] != list(MODELS) or metadata["levels"] != list(LEVELS)
                    or metadata["rounds"] != ROUNDS or metadata["repetitions"] != REPETITIONS
                    or metadata["warmups_per_group"] != 1 or metadata["noise_variant"] != "random_words"):
                raise ValueError(f"Saved benchmark plan does not match current code: {metadata_path.resolve()}")
            settings = AppConfig.model_validate(metadata["config"])
            seed_base = metadata["noise_seed_base"]
        else:
            settings = load_config(Path("configs/default.yaml"))
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            output_dir = settings.run.results_dir / "latency_benchmark" / f"{stamp}_{uuid4().hex[:8]}"
            output_dir.mkdir(parents=True, exist_ok=False)
            metadata_path = output_dir / "settings.json"
            seed_base = uuid4().int
            with metadata_path.open("w", encoding="utf-8") as output:
                json.dump({"config": settings.model_dump(mode="json"), "models": MODELS, "levels": LEVELS,
                           "rounds": ROUNDS, "repetitions": REPETITIONS, "warmups_per_group": 1,
                           "noise_seed_base": seed_base, "noise_variant": "random_words"}, output, indent=2)
        raw_path = output_dir / "records.jsonl"
        records = []
        if args.resume:
            with raw_path.open(encoding="utf-8") as source:
                records = [json.loads(line) for line in source if line.strip()]
        done = completed_cases(records, settings.run.experiment_6_context_limit)
        logger.info(f"Results directory: {output_dir.resolve()}")
        measured = ROUNDS * len(MODELS) * len(LEVELS) * len(TASKS) * REPETITIONS
        warmups = ROUNDS * len(MODELS) * len(LEVELS) * len(TASKS)
        logger.info(f"Planned requests: {measured} measurements and {warmups} warmups")
        logger.info(f"Previously completed planned requests: {len(done)}")
        for round_number in range(1, ROUNDS + 1):
            for model_id in MODELS:
                case_count = sum(1 for key in done if key[0] == round_number and key[1] == model_id)
                if case_count == len(LEVELS) * len(TASKS) * (REPETITIONS + 1):
                    logger.info(f"Skipping completed round {round_number} for model {model_id}")
                    continue
                logger.info(f"Starting round {round_number} for model {model_id}")
                measure_model(settings, model_id, round_number, raw_path, seed_base, done)
        with raw_path.open(encoding="utf-8") as source:
            records = [json.loads(line) for line in source if line.strip()]
        write_report(records, output_dir)
        logger.info(f"Benchmark complete: {output_dir.resolve()}")
    except Exception:
        logger.error(f"Latency benchmark failed\n{traceback.format_exc()}")
        raise


if __name__ == "__main__":
    main()
