"""Command-line interface for planning and running reproducible experiments."""

from __future__ import annotations

import hashlib
import json
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer
from loguru import logger
from tqdm import tqdm

from .config import AppConfig, config_dict, configure_logging, load_config
from .evaluation import evaluate_response
from .experiments import EXPERIMENT_NAMES, ExperimentCase, generate_experiment_cases
from .inference import InferenceClient
from .reporting import generate_report
from .storage import append_jsonl, completed_case_ids, create_run_id, pending_cases, raw_results_path, write_new_json
from .tasks import get_task, render_prompt

app = typer.Typer(no_args_is_help=True, help="Reproducible LLM answer-stability experiments.")
DEFAULT_CONFIG_PATH = Path("configs/default.yaml")


def _read_config(config_path: Path, *, verbose: bool = False) -> AppConfig:
    """Read configuration and set up console logging."""
    config = load_config(config_path)
    configure_logging(verbose=verbose)
    return config


def _planned_experiments(experiment: str | None) -> list[str]:
    """Resolve the selected experiment or all five experiments."""
    if experiment is None:
        return [key for key in EXPERIMENT_NAMES if key != "06"]
    if experiment not in EXPERIMENT_NAMES:
        raise ValueError(f"Unknown experiment {experiment!r}; choose from {', '.join(EXPERIMENT_NAMES)}")
    return [experiment]


def _repetition_count(config: AppConfig, experiment_id: str, override: int | None) -> int:
    """Resolve per-experiment repetition defaults without multiplying all run sizes."""
    if override is not None:
        if override <= 0:
            raise ValueError("Repetition count must be positive")
        return override
    return config.run.repetitions if experiment_id == "01" else 1


def _generate_cases(
    config: AppConfig,
    experiment_ids: list[str],
    task_ids: list[str] | None,
    repetitions_override: int | None,
    permutation_count: int,
    interaction_blocks: int | None,
    random_seed: int | None,
) -> list[ExperimentCase]:
    """Generate cases using configuration defaults and explicit CLI overrides."""
    cases: list[ExperimentCase] = []
    block_count = interaction_blocks or config.run.experiment_5_blocks
    seed = config.run.random_seed if random_seed is None else random_seed
    for experiment_id in experiment_ids:
        if experiment_id == "06":
            from .noise_length import generate_length_cases

            cases.extend(generate_length_cases(
                config, task_ids, block_count, seed, _repetition_count(config, experiment_id, repetitions_override)
            ))
            continue
        cases.extend(
            generate_experiment_cases(
                experiment_id,
                task_ids=task_ids,
                repetitions=_repetition_count(config, experiment_id, repetitions_override),
                random_seed=seed,
                permutation_count=permutation_count,
                interaction_blocks=block_count,
            )
        )
    return cases


def _plan_hash(cases: list[ExperimentCase]) -> str:
    """Hash the ordered case IDs to prevent accidental mismatched resumes."""
    return hashlib.sha256("\n".join(case.case_id for case in cases).encode("utf-8")).hexdigest()


def _run_metadata_path(results_dir: Path, run_id: str) -> Path:
    """Return the run metadata JSON path."""
    return results_dir / "runs" / f"{run_id}.json"


def _check_resume(
    metadata_path: Path,
    config: AppConfig,
    plan_hash: str,
    experiment_ids: list[str],
) -> dict[str, Any]:
    """Validate a saved run's settings and plan before resuming it."""
    try:
        with metadata_path.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
    except Exception:
        logger.error(f"Could not read resume metadata at {metadata_path.resolve()}\n{traceback.format_exc()}")
        raise
    if metadata.get("inference_config") != config_dict(config)["inference"]:
        raise ValueError("Resume configuration differs from the original run's inference settings")
    if metadata.get("plan_hash") != plan_hash or metadata.get("experiment_ids") != experiment_ids:
        raise ValueError("Resume plan differs from the original run; use the original experiments and options")
    return metadata


def _build_result_record(
    run_id: str,
    case: ExperimentCase,
    result: Any,
    inference_config: dict[str, Any],
    exposed_models: list[str],
    latency: float,
    experimental_seed: int,
) -> dict[str, Any]:
    """Combine the planned case and API response into an auditable record."""
    task = get_task(case.task_id)
    choice_order = tuple(
        choice for choice in task.choices if choice.choice_id in case.answer_permutation
    )
    choice_order = tuple(sorted(choice_order, key=lambda choice: case.answer_permutation.index(choice.choice_id)))
    evaluation = evaluate_response(
        task,
        result.raw_response,
        choice_order=choice_order,
        correct_number=case.correct_numeric_answer,
        truncated=result.finish_reason == "length",
    )
    return {
        "run_id": run_id,
        "case_id": case.case_id,
        "experiment_id": case.experiment_id,
        "experiment_name": EXPERIMENT_NAMES.get(case.experiment_id, "Smoke Test"),
        "task_id": case.task_id,
        "task_name": task.name,
        "model_id": inference_config["model_id"],
        "timestamp": datetime.now(UTC).isoformat(),
        "repetition": case.repetition,
        "experimental_random_seed": experimental_seed,
        "messages": list(case.messages),
        "noise_type": case.noise_type,
        "noise_text": case.noise_text,
        "noise_position": case.noise_position,
        "answer_permutation": list(case.answer_permutation),
        "correct_answer_identity": case.correct_answer_identity,
        "correct_numeric_answer": case.correct_numeric_answer,
        "requested_parameters": result.requested_parameters,
        "raw_response": result.raw_response,
        "normalized_answer": evaluation.normalized_answer,
        "selected_choice_id": evaluation.selected_choice_id,
        "selected_numeric_option": case.answer_permutation.index(evaluation.selected_choice_id) + 1
        if evaluation.selected_choice_id is not None
        else None,
        "is_correct": evaluation.is_correct,
        "format_compliant": evaluation.format_compliant,
        "parse_status": evaluation.parse_status,
        "finish_reason": result.finish_reason,
        "response_latency_seconds": latency,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "error_type": result.error_type,
        "error_message": result.error_message,
        "error_traceback": result.error_traceback,
        "configuration_valid": not (result.error_type and "BadRequest" in result.error_type),
        "backend_audit": {
            "base_url": inference_config["base_url"],
            "configured_model_id": inference_config["model_id"],
            "exposed_model_ids": exposed_models,
            "response": result.response_metadata,
        },
        "experiment_metadata": case.metadata,
        "perturbation_id": case.perturbation_id,
        "perturbation_category": case.perturbation_category,
        "block_id": case.block_id,
        "factor_condition": case.factor_condition,
    }


@app.command()
def models(config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", "-c")) -> None:
    """List model IDs exposed by the configured server."""
    settings = _read_config(config)
    with InferenceClient(settings.inference) as client:
        for model_id in client.list_models():
            logger.info(f"Model ID: {model_id}")


@app.command()
def plan(
    experiment: str | None = typer.Option(None, "--experiment", "-e", help="Experiment ID 01-06; default: 01-05."),
    tasks: list[str] | None = typer.Option(None, "--task", help="Task ID; repeat to select multiple tasks."),
    repetitions: int | None = typer.Option(None, "--repetitions", min=1),
    permutation_count: int = typer.Option(90, "--permutation-count", min=1),
    interaction_blocks: int | None = typer.Option(None, "--interaction-blocks", min=1),
    seed: int | None = typer.Option(None, "--seed", help="Override the experimental random seed."),
    model: str | None = typer.Option(None, "--model", help="Override the configured model ID."),
    preview_all: bool = typer.Option(False, "--preview-all", help="Log every planned prompt."),
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", "-c"),
) -> None:
    """Preview planned requests and estimate inference-call counts."""
    settings = _read_config(config)
    if model:
        settings.inference.model_id = model
    experiment_ids = _planned_experiments(experiment)
    cases = _generate_cases(settings, experiment_ids, tasks, repetitions, permutation_count, interaction_blocks, seed)
    logger.info(f"Planned inference calls: {len(cases)}")
    for experiment_id in experiment_ids:
        count = sum(case.experiment_id == experiment_id for case in cases)
        logger.info(f"Experiment {experiment_id} ({EXPERIMENT_NAMES[experiment_id]}): {count} calls")
    if "06" in experiment_ids:
        length_cases = [case for case in cases if case.experiment_id == "06" and case.metadata]
        if length_cases:
            levels = sorted(
                {(case.metadata["noise_target_tokens"], case.metadata["noise_tokens"]) for case in length_cases}
            )
            maximum = max(case.metadata["planned_prompt_tokens"] for case in length_cases)
            logger.info(f"Noise token targets and measured lengths: {levels}")
            logger.info(
                f"Maximum planned prompt: {maximum} tokens; generation reserve: {settings.inference.max_tokens}; "
                f"context limit: {settings.run.experiment_6_context_limit}"
            )
    preview_cases = cases if preview_all else cases[:5]
    for case in preview_cases:
        logger.info(
            f"Preview {case.experiment_id}/{case.task_id} case={case.case_id}: "
            f"{case.messages[-1]['content'][:220].replace(chr(10), ' ')}"
        )
    if len(cases) > len(preview_cases):
        logger.info(f"Preview omitted {len(cases) - len(preview_cases)} additional requests; use --preview-all")


@app.command()
def run(
    experiment: str | None = typer.Option(None, "--experiment", "-e", help="Experiment ID 01-06; default: 01-05."),
    tasks: list[str] | None = typer.Option(None, "--task", help="Task ID; repeat to select multiple tasks."),
    repetitions: int | None = typer.Option(None, "--repetitions", min=1),
    permutation_count: int = typer.Option(90, "--permutation-count", min=1),
    interaction_blocks: int | None = typer.Option(None, "--interaction-blocks", min=1),
    seed: int | None = typer.Option(None, "--seed", help="Override the experimental random seed."),
    model: str | None = typer.Option(None, "--model", help="Override the configured model ID."),
    resume: str | None = typer.Option(None, "--resume", help="Resume an existing run ID."),
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose"),
) -> None:
    """Execute selected experiments; invoking without an experiment runs all five."""
    settings = load_config(config)
    if model:
        settings.inference.model_id = model
    experiment_ids = _planned_experiments(experiment)
    cases = _generate_cases(settings, experiment_ids, tasks, repetitions, permutation_count, interaction_blocks, seed)
    if not cases:
        raise ValueError("The selected experiment and tasks produced no inference cases")
    run_id = resume or create_run_id()
    results_dir = settings.run.results_dir
    data_path = raw_results_path(results_dir, run_id)
    metadata_path = _run_metadata_path(results_dir, run_id)
    configure_logging(results_dir / "logs" / f"{run_id}.log", verbose=verbose)
    plan_hash = _plan_hash(cases)
    if resume:
        _check_resume(metadata_path, settings, plan_hash, experiment_ids)
    else:
        write_new_json(
            metadata_path,
            {
                "run_id": run_id,
                "started_at": datetime.now(UTC).isoformat(),
                "experiment_ids": experiment_ids,
                "task_ids": tasks,
                "plan_hash": plan_hash,
                "planned_case_count": len(cases),
                "inference_config": config_dict(settings)["inference"],
                "run_config": config_dict(settings)["run"],
                "random_seed": settings.run.random_seed if seed is None else seed,
            },
        )
    client = InferenceClient(settings.inference)
    try:
        exposed_models = client.require_configured_model()
        completed = completed_case_ids(data_path)
        pending = pending_cases(cases, completed)
        logger.info(
            f"Run {run_id}: {len(pending)} pending of {len(cases)} planned cases; "
            f"model={settings.inference.model_id}"
        )
        case_iterator = tqdm(pending, desc="Inference cases", unit="case") if len(pending) >= 20 else pending
        invalid_parameter_errors = 0
        for case in case_iterator:
            started = time.perf_counter()
            result = client.complete(case.messages)
            latency = time.perf_counter() - started
            record = _build_result_record(
                run_id,
                case,
                result,
                config_dict(settings)["inference"],
                exposed_models,
                latency,
                settings.run.random_seed if seed is None else seed,
            )
            if case.experiment_id == "06" and case.metadata is not None:
                reported = result.prompt_tokens
                record["prompt_token_difference"] = (
                    reported - case.metadata["planned_prompt_tokens"] if reported is not None else None
                )
                record["context_budget_verified"] = (
                    reported + settings.inference.max_tokens <= case.metadata["context_limit"]
                    if reported is not None else None
                )
            append_jsonl(data_path, record)
            if record.get("context_budget_verified") is False:
                raise ValueError("Server-reported prompt plus generation reserve exceeds the context limit")
            if not record["configuration_valid"]:
                invalid_parameter_errors += 1
        if invalid_parameter_errors:
            logger.error(
                f"{invalid_parameter_errors} requests were rejected as invalid API requests; "
                "review stored error records before interpreting this run."
            )
        logger.info(f"Run {run_id} saved to {data_path.resolve()}")
    except KeyboardInterrupt:
        logger.warning(f"Run {run_id} interrupted; completed records remain resumable")
        raise
    finally:
        client.close()


@app.command()
def smoke(
    task: str = typer.Option("task_01_math", "--task"),
    model: str | None = typer.Option(None, "--model", help="Override the configured model ID."),
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", "-c"),
) -> None:
    """Check connectivity, selected model availability, and one minimal inference."""
    settings = _read_config(config)
    if model:
        settings.inference.model_id = model
    task_data = get_task(task)
    user_message, correct_number = render_prompt(task_data)
    case = ExperimentCase(
        case_id=f"smoke_{task_data.task_id}",
        experiment_id="00",
        task_id=task_data.task_id,
        repetition=1,
        messages=(
            {"role": "system", "content": task_data.system_message},
            {"role": "user", "content": user_message},
        ),
        correct_answer_identity=task_data.correct_answer,
        correct_numeric_answer=correct_number,
        answer_permutation=tuple(choice.choice_id for choice in task_data.choices),
    )
    run_id = create_run_id()
    data_path = raw_results_path(settings.run.results_dir, run_id)
    client = InferenceClient(settings.inference)
    configure_logging(settings.run.results_dir / "logs" / f"{run_id}.log")
    try:
        exposed_models = client.require_configured_model()
        started = time.perf_counter()
        result = client.complete(case.messages)
        latency = time.perf_counter() - started
        record = _build_result_record(
            run_id,
            case,
            result,
            config_dict(settings)["inference"],
            exposed_models,
            latency,
            settings.run.random_seed,
        )
        append_jsonl(data_path, record)
        logger.info(
            f"Smoke test result: status={result.error_type or 'completed'}, "
            f"answer={record['normalized_answer']}, correct={record['is_correct']}"
        )
        logger.info(f"Smoke record saved to {data_path.resolve()}")
    finally:
        client.close()


@app.command()
def report(
    run_id: str = typer.Argument(..., help="Run ID or path to a JSONL result file."),
    config: Path = typer.Option(DEFAULT_CONFIG_PATH, "--config", "-c"),
) -> None:
    """Generate CSV, Markdown, and PNG reports from saved raw results."""
    settings = _read_config(config)
    supplied_path = Path(run_id)
    input_path = supplied_path if supplied_path.is_file() else raw_results_path(settings.run.results_dir, run_id)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_dir = settings.run.results_dir / "reports" / f"{input_path.stem}_{stamp}"
    generate_report(input_path, report_dir)


if __name__ == "__main__":
    app()
