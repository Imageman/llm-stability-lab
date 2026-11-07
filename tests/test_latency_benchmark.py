"""Check latency aggregation and warmup handling without contacting a server."""

from types import SimpleNamespace
from pathlib import Path

import pytest

from llm_stability_lab import latency_benchmark as benchmark
from llm_stability_lab.config import AppConfig
from llm_stability_lab.inference import InferenceResult
from llm_stability_lab.tasks import TASKS


def test_round_medians_exclude_warmups(monkeypatch: pytest.MonkeyPatch) -> None:
    """Select the median of round medians and reject missing measurements."""
    monkeypatch.setattr(benchmark, "MODELS", ("test-model",))
    monkeypatch.setattr(benchmark, "TASKS", TASKS[:1])
    monkeypatch.setattr(benchmark, "LEVELS", (0,))
    monkeypatch.setattr(benchmark, "REPETITIONS", 2)
    rows = []
    for round_number, times in enumerate(((1.0, 3.0), (9.0, 11.0), (3.0, 5.0)), start=1):
        base = {"model": "test-model", "task": TASKS[0].task_id, "noise_target_tokens": 0,
                "round": round_number, "result": {"error_type": None, "raw_response": "66", "finish_reason": "stop"}}
        rows.append(base | {"phase": "warmup", "latency_seconds": 9999.0})
        rows.extend(base | {"phase": "measurement", "latency_seconds": value} for value in times)
    result = benchmark.summarize(rows)
    assert result[0]["median_seconds"] == 4.0
    with pytest.raises(ValueError, match="Incomplete measurements"):
        benchmark.summarize(rows[:-1])


def test_group_records_one_unmeasured_warmup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Save a warmup before each measured group without including its timing."""
    monkeypatch.setattr(benchmark, "REPETITIONS", 2)
    recorded = []
    monkeypatch.setattr(benchmark, "append_jsonl", lambda path, record: recorded.append(record))
    monkeypatch.setattr(benchmark, "prepare_prompt", lambda model, settings, task, target, seed:
                        {"messages": [], "noise_target_tokens": target, "noise_seed": seed})
    result = InferenceResult("1", "stop", 100, 1, {}, {})
    client = SimpleNamespace(config=SimpleNamespace(model_id=benchmark.MODELS[0], max_tokens=100),
                             complete=lambda messages: result)
    progress = SimpleNamespace(update=lambda count: None)
    done: set[benchmark.CaseKey] = set()
    benchmark.measure_group(client, None, AppConfig(), 0, TASKS[0], 1, tmp_path, progress, 42, done)
    assert [row["phase"] for row in recorded] == ["warmup", "measurement", "measurement"]
    assert recorded[0]["latency_seconds"] is None
    assert all(row["latency_seconds"] is not None for row in recorded[1:])
    assert len({row["noise_seed"] for row in recorded}) == 3


def test_resume_partial_group_adds_warmup_and_only_missing_cases(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Preserve completed measurements and warm up again before continuing a partial series."""
    monkeypatch.setattr(benchmark, "REPETITIONS", 2)
    recorded = []
    monkeypatch.setattr(benchmark, "append_jsonl", lambda path, record: recorded.append(record))
    monkeypatch.setattr(benchmark, "prepare_prompt", lambda model, settings, task, target, seed:
                        {"messages": [], "noise_target_tokens": target, "noise_seed": seed})
    result = InferenceResult("1", "stop", 100, 1, {}, {})
    model_id = benchmark.MODELS[0]
    client = SimpleNamespace(config=SimpleNamespace(model_id=model_id, max_tokens=100),
                             complete=lambda messages: result)
    done: set[benchmark.CaseKey] = {(1, model_id, TASKS[0].task_id, 0, 0),
                                    (1, model_id, TASKS[0].task_id, 0, 1)}
    benchmark.measure_group(client, None, AppConfig(), 0, TASKS[0], 1, tmp_path,
                            SimpleNamespace(update=lambda count: None), 42, done)
    assert [row["phase"] for row in recorded] == ["resume_warmup", "measurement"]
    assert [row["repetition"] for row in recorded] == [-1, 2]
    assert len(done) == 3


def test_completed_cases_rejects_duplicates() -> None:
    """Prevent duplicated successful cases from being silently counted again."""
    row = {"round": 1, "model": benchmark.MODELS[0], "task": TASKS[0].task_id, "noise_target_tokens": 0,
           "phase": "measurement", "repetition": 1, "result": {"error_type": None, "prompt_tokens": None}}
    with pytest.raises(ValueError, match="duplicate"):
        benchmark.completed_cases([row, row])


def test_random_noise_precedes_task_and_is_reproducible() -> None:
    """Use distinct seeded noise before the task, with a clean zero-noise baseline."""
    model = SimpleNamespace(tokenize=lambda text: text.split(), apply_prompt_template=lambda chat: "template")
    task = TASKS[0]
    first = benchmark.prepare_prompt(model, AppConfig(), task, 128, 101)
    repeat = benchmark.prepare_prompt(model, AppConfig(), task, 128, 101)
    second = benchmark.prepare_prompt(model, AppConfig(), task, 128, 102)
    clean = benchmark.prepare_prompt(model, AppConfig(), task, 0, 101)
    assert first == repeat
    assert first["messages"] != second["messages"]
    assert first["noise_tokens"] == 128
    assert first["messages"][1]["content"].startswith("Irrelevant context: ")
    assert task.description in first["messages"][1]["content"]
    assert not clean["messages"][1]["content"].startswith("Irrelevant context:")


def test_report_creates_summary_and_chart(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Write a chart and CSV from a complete miniature benchmark."""
    model = benchmark.MODELS[0]
    monkeypatch.setattr(benchmark, "MODELS", (model,))
    monkeypatch.setattr(benchmark, "TASKS", TASKS[:1])
    monkeypatch.setattr(benchmark, "LEVELS", (0,))
    monkeypatch.setattr(benchmark, "REPETITIONS", 1)
    rows = [{"model": model, "task": TASKS[0].task_id, "noise_target_tokens": 0, "round": number,
             "phase": "measurement", "latency_seconds": float(number),
             "result": {"error_type": None, "raw_response": "66", "finish_reason": "stop"}}
            for number in range(1, 4)]
    benchmark.write_report(rows, tmp_path)
    assert (tmp_path / "latency_summary.csv").is_file()
    assert (tmp_path / "latency_oss.png").stat().st_size > 0


def test_summary_counts_invalid_and_incorrect_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Count malformed, truncated and incorrect responses as errors, excluding warmups."""
    monkeypatch.setattr(benchmark, "MODELS", ("test-model",))
    monkeypatch.setattr(benchmark, "TASKS", TASKS[:1])
    monkeypatch.setattr(benchmark, "LEVELS", (0,))
    monkeypatch.setattr(benchmark, "REPETITIONS", 1)
    outcomes = [("66", "stop"), ("wrong", "stop"), ("66", "length")]
    rows = [{"model": "test-model", "task": TASKS[0].task_id, "noise_target_tokens": 0, "round": number,
             "phase": "measurement", "latency_seconds": 1.0,
             "result": {"error_type": None, "raw_response": answer, "finish_reason": finish}}
            for number, (answer, finish) in enumerate(outcomes, start=1)]
    result = benchmark.summarize(rows)[0]
    assert result["error_count"] == 2
    assert result["response_count"] == 3
