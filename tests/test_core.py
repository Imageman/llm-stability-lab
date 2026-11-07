"""Unit tests for task rendering, case generation, evaluation, and reports."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from llm_stability_lab.evaluation import evaluate_response
from llm_stability_lab.experiments import generate_experiment_cases
from llm_stability_lab.perturbations import (
    NOISE_POSITIONS,
    all_permutations,
    balanced_permutations,
    make_task_perturbations,
)
from llm_stability_lab.reporting import generate_report, summarize_records
from llm_stability_lab.storage import append_jsonl, completed_case_ids, load_jsonl, pending_cases
from llm_stability_lab.tasks import TASKS, get_task, render_prompt


def test_reference_answers_and_numeric_parsing() -> None:
    """Evaluate all three reference answers without an LLM judge."""
    math_task, logic_task, traffic_task = TASKS
    assert evaluate_response(math_task, "66").is_correct is True
    assert evaluate_response(math_task, "67").is_correct is False
    assert evaluate_response(math_task, "Answer: 66").parse_status == "malformed"
    assert evaluate_response(math_task, "").parse_status == "empty"
    assert evaluate_response(math_task, "66", truncated=True).parse_status == "truncated"
    _, logic_correct_number = render_prompt(logic_task)
    _, traffic_correct_number = render_prompt(traffic_task)
    assert logic_correct_number == 3
    assert traffic_correct_number == 1
    assert evaluate_response(logic_task, "3").selected_choice_id == "mixture"
    assert evaluate_response(traffic_task, "1").selected_choice_id == "green"
    assert evaluate_response(traffic_task, "10").parse_status == "out_of_range"


def test_all_logic_permutations_keep_semantic_answer() -> None:
    """Check all 24 logical-task orders retain the stable correct choice ID."""
    task = get_task("task_02_logic")
    permutations = all_permutations(task.choices)
    assert len(permutations) == 24
    for order in permutations:
        _, correct_number = render_prompt(task, choice_order=order)
        assert correct_number is not None
        result = evaluate_response(task, str(correct_number), choice_order=order, correct_number=correct_number)
        assert result.is_correct is True
        assert result.selected_choice_id == task.correct_answer


def test_traffic_permutations_are_balanced_and_repeatable() -> None:
    """Generate deterministic traffic-light permutations balanced over all positions."""
    task = get_task("task_03_traffic")
    first = balanced_permutations(task.choices, task.correct_answer, 90, seed=73)
    second = balanced_permutations(task.choices, task.correct_answer, 90, seed=73)
    assert first == second
    correct_choice = next(choice for choice in task.choices if choice.choice_id == task.correct_answer)
    positions = [order.index(correct_choice) for order in first]
    assert Counter(positions) == Counter({position: 10 for position in range(9)})
    assert len({tuple(choice.choice_id for choice in order) for order in first}) == 90


def test_prompt_noise_placement_and_perturbations_are_reproducible() -> None:
    """Keep the task content intact while placing fixed noise in each requested position."""
    task = get_task("task_02_logic")
    noise = "violet lantern copper meadow"
    prompts = {
        position: render_prompt(task, noise_text=noise, noise_position=position)[0]
        for position in NOISE_POSITIONS
    }
    assert all(task.description in prompt and task.question in prompt for prompt in prompts.values())
    assert prompts["before_task"].index(noise) < prompts["before_task"].index(task.description)
    assert prompts["between_description_question"].index(task.description) < prompts[
        "between_description_question"
    ].index(noise) < prompts["between_description_question"].index(task.question)
    assert prompts["after_question"].index(noise) > prompts["after_question"].index(task.question)
    assert make_task_perturbations(task, 42) == make_task_perturbations(task, 42)
    assert {item.category for item in make_task_perturbations(task, 42)} == {
        "random_words",
        "irrelevant_sentence",
        "neutral_wording",
        "noise_quantity",
    }


def test_experiment_case_counts_and_choice_mapping() -> None:
    """Generate cases for all experiments and preserve the correct semantic mapping."""
    assert len(generate_experiment_cases("01", repetitions=2)) == 6
    assert len(generate_experiment_cases("02")) == 30
    assert len(generate_experiment_cases("03")) == 33
    order_cases = generate_experiment_cases("04")
    assert len(order_cases) == 114
    for case in order_cases:
        task = get_task(case.task_id)
        if task.choices:
            choices = tuple(next(choice for choice in task.choices if choice.choice_id == choice_id)
                            for choice_id in case.answer_permutation)
            _, numeric_answer = render_prompt(task, choice_order=choices)
            assert numeric_answer == case.correct_numeric_answer
    interaction_cases = generate_experiment_cases("05", interaction_blocks=9)
    assert len(interaction_cases) == 72
    assert {case.factor_condition for case in interaction_cases} == {
        "original_clean",
        "shuffled_clean",
        "original_noisy",
        "shuffled_noisy",
    }
    for task_id in ("task_02_logic", "task_03_traffic"):
        shuffled = [
            case
            for case in interaction_cases
            if case.task_id == task_id and case.factor_condition == "shuffled_clean"
        ]
        task = get_task(task_id)
        position_counts = Counter(case.correct_numeric_answer for case in shuffled)
        assert len(position_counts) == len(task.choices)
        assert max(position_counts.values()) - min(position_counts.values()) <= 1


def test_jsonl_persistence_and_resume_ids(tmp_path: Path) -> None:
    """Persist records incrementally and identify them for resume without duplicates."""
    path = tmp_path / "raw" / "sample.jsonl"
    records: list[dict[str, Any]] = [{"case_id": "one", "value": 1}, {"case_id": "two", "value": 2}]
    for record in records:
        append_jsonl(path, record)
    assert load_jsonl(path) == records
    assert completed_case_ids(path) == {"one", "two"}
    cases = generate_experiment_cases("01", repetitions=2)
    saved_case_id = cases[0].case_id
    assert [case.case_id for case in pending_cases(cases, {saved_case_id})] == [
        case.case_id for case in cases[1:]
    ]


def test_summary_and_report_artifacts(tmp_path: Path) -> None:
    """Create task-level metrics and an isolated Markdown/CSV/chart report."""
    records = [
        {
            "run_id": "run",
            "experiment_id": "01",
            "task_id": "task_01_math",
            "is_correct": True,
            "raw_response": "66",
            "normalized_answer": "66",
            "format_compliant": True,
            "response_latency_seconds": 0.2,
            "noise_text": None,
            "noise_position": None,
            "correct_numeric_answer": None,
            "selected_choice_id": None,
            "factor_condition": None,
            "block_id": None,
            "repetition": 1,
            "perturbation_id": None,
            "selected_numeric_option": None,
            "error_type": None,
            "parse_status": "valid",
        }
    ]
    records.extend(
        {
            **records[0],
            "experiment_id": "04",
            "task_id": "task_02_logic",
            "correct_numeric_answer": option_number,
            "selected_numeric_option": option_number,
            "normalized_answer": "mixture",
            "raw_response": str(option_number),
        }
        for option_number in (1, 2)
    )
    summary = summarize_records(records)
    assert summary.iloc[0]["accuracy"] == 1.0
    source = tmp_path / "raw.jsonl"
    for record in records:
        append_jsonl(source, record)
    output_dir = generate_report(source, tmp_path / "report")
    assert (output_dir / "summary.csv").exists()
    assert (output_dir / "report.md").exists()
    assert (output_dir / "records.csv").exists()
    position_csv = (output_dir / "accuracy_by_correct_answer_position.csv").read_text(encoding="utf-8")
    assert position_csv.splitlines()[0] == "task_id,correct_numeric_answer,accuracy,sample_count"
    assert "task_02_logic,1.0,1.0,1" in position_csv


def test_api_failures_are_not_counted_as_answer_or_format_errors() -> None:
    """Exclude failed HTTP requests from answer accuracy and format-violation rates."""
    common = {
        "experiment_id": "01",
        "task_id": "task_01_math",
        "raw_response": None,
        "normalized_answer": None,
        "format_compliant": False,
        "response_latency_seconds": 1.0,
    }
    records = [
        {
            **common,
            "case_id": "success",
            "is_correct": True,
            "error_type": None,
            "raw_response": "66",
            "format_compliant": True,
        },
        {**common, "case_id": "failure", "is_correct": None, "error_type": "APIConnectionError"},
    ]
    summary = summarize_records(records).iloc[0]
    assert summary["accuracy"] == 1.0
    assert summary["evaluated_count"] == 1
    assert summary["failure_count"] == 1
    assert summary["format_violation_rate"] == 0.0
