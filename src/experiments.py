"""Reproducible case generation for experiments 01 through 05."""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from math import factorial
from typing import Any, Iterable, Sequence

from .perturbations import (
    NOISE_POSITIONS,
    NOISE_SAMPLES,
    Perturbation,
    all_permutations,
    balanced_permutations,
    make_task_perturbations,
)
from .tasks import AnswerChoice, ResearchTask, TASKS, get_task, render_prompt

EXPERIMENT_NAMES = {
    "01": "Determinism",
    "02": "Position Sensitivity",
    "03": "Reasoning Stability",
    "04": "Answer Order Sensitivity",
    "05": "Noise x Answer Order Interaction",
    "06": "Noise Length x Answer Order",
}
MULTIPLE_CHOICE_TASKS = ("task_02_logic", "task_03_traffic")


@dataclass(frozen=True)
class ExperimentCase:
    """A single request with enough information to reproduce its exact prompt."""

    case_id: str
    experiment_id: str
    task_id: str
    repetition: int
    messages: tuple[dict[str, str], ...]
    noise_type: str | None = None
    noise_text: str | None = None
    noise_position: str | None = None
    answer_permutation: tuple[str, ...] = ()
    correct_answer_identity: str = ""
    correct_numeric_answer: int | None = None
    perturbation_id: str | None = None
    perturbation_category: str | None = None
    block_id: str | None = None
    factor_condition: str | None = None
    metadata: dict[str, Any] | None = None


def _case(
    experiment_id: str,
    task: ResearchTask,
    repetition: int,
    *,
    noise_type: str | None = None,
    noise_text: str | None = None,
    noise_position: str | None = None,
    choice_order: Sequence[AnswerChoice] | None = None,
    question: str | None = None,
    perturbation_id: str | None = None,
    perturbation_category: str | None = None,
    block_id: str | None = None,
    factor_condition: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ExperimentCase:
    """Build one stable, fully specified experiment case."""
    order = tuple(choice_order) if choice_order is not None else task.choices
    user_message, correct_number = render_prompt(
        task,
        question=question,
        choice_order=order,
        noise_text=noise_text,
        noise_position=noise_position,
    )
    messages = (
        {"role": "system", "content": task.system_message},
        {"role": "user", "content": user_message},
    )
    identity = {
        "experiment_id": experiment_id,
        "task_id": task.task_id,
        "repetition": repetition,
        "messages": messages,
        "noise_type": noise_type,
        "noise_text": noise_text,
        "noise_position": noise_position,
        "answer_permutation": [choice.choice_id for choice in order],
        "perturbation_id": perturbation_id,
        "block_id": block_id,
        "factor_condition": factor_condition,
    }
    serialized = json.dumps(identity, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    case_id = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]
    return ExperimentCase(
        case_id=case_id,
        experiment_id=experiment_id,
        task_id=task.task_id,
        repetition=repetition,
        messages=messages,
        noise_type=noise_type,
        noise_text=noise_text,
        noise_position=noise_position,
        answer_permutation=tuple(choice.choice_id for choice in order),
        correct_answer_identity=task.correct_answer,
        correct_numeric_answer=correct_number,
        perturbation_id=perturbation_id,
        perturbation_category=perturbation_category,
        block_id=block_id,
        factor_condition=factor_condition,
        metadata=metadata,
    )


def _repeat_cases(cases: Iterable[ExperimentCase], repetitions: int) -> list[ExperimentCase]:
    """Expand prompt conditions into independently identified repetitions."""
    return [
        _case_from_template(case, repetition)
        for case in cases
        for repetition in range(1, repetitions + 1)
    ]


def _case_from_template(case: ExperimentCase, repetition: int) -> ExperimentCase:
    """Copy a case with a new repetition number and stable ID."""
    identity = {
        "template": case.case_id,
        "repetition": repetition,
    }
    case_id = hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()[:24]
    return ExperimentCase(**{**asdict(case), "case_id": case_id, "repetition": repetition})


def _filter_tasks(task_ids: Sequence[str] | None) -> tuple[ResearchTask, ...]:
    """Return selected tasks, defaulting to the complete task set."""
    if not task_ids:
        return TASKS
    unknown = sorted(set(task_ids) - {task.task_id for task in TASKS})
    if unknown:
        raise ValueError(f"Unknown task IDs: {', '.join(unknown)}")
    return tuple(get_task(task_id) for task_id in task_ids)


def _choices_for_ids(task: ResearchTask, ids: tuple[str, ...]) -> tuple[AnswerChoice, ...]:
    """Resolve a recorded sequence of stable choice IDs to choice records."""
    by_id = {choice.choice_id: choice for choice in task.choices}
    return tuple(by_id[choice_id] for choice_id in ids)


def generate_experiment_cases(
    experiment_id: str,
    *,
    task_ids: Sequence[str] | None = None,
    repetitions: int = 1,
    random_seed: int = 1729,
    permutation_count: int = 90,
    interaction_blocks: int = 18,
) -> list[ExperimentCase]:
    """Generate all request cases for one independently executable experiment."""
    if experiment_id not in EXPERIMENT_NAMES:
        raise ValueError(f"Unknown experiment ID {experiment_id!r}; choose from 01 through 06")
    if experiment_id == "06":
        raise ValueError("Experiment 06 requires model tokenization; use generate_length_cases")
    if repetitions <= 0:
        raise ValueError("Repetition count must be positive")
    tasks = _filter_tasks(task_ids)

    if experiment_id == "01":
        templates = [_case(experiment_id, task, 1) for task in tasks]
        return _repeat_cases(templates, repetitions)

    if experiment_id == "02":
        templates: list[ExperimentCase] = []
        for task in tasks:
            templates.append(_case(experiment_id, task, 1, metadata={"condition": "clean"}))
            for noise_index, text in enumerate(NOISE_SAMPLES, start=1):
                for position in NOISE_POSITIONS:
                    templates.append(
                        _case(
                            experiment_id,
                            task,
                            1,
                            noise_type="fixed_words",
                            noise_text=text,
                            noise_position=position,
                            metadata={"noise_sample": noise_index},
                        )
                    )
        return _repeat_cases(templates, repetitions)

    if experiment_id == "03":
        templates = []
        for task in tasks:
            templates.append(_case(experiment_id, task, 1, metadata={"condition": "clean"}))
            for perturbation in make_task_perturbations(task, random_seed):
                templates.append(_perturbed_case(experiment_id, task, perturbation))
        return _repeat_cases(templates, repetitions)

    if experiment_id == "04":
        templates = []
        for task in tasks:
            if task.task_id not in MULTIPLE_CHOICE_TASKS:
                continue
            if task.task_id == "task_02_logic":
                permutations = all_permutations(task.choices)
            else:
                permutations = balanced_permutations(task.choices, task.correct_answer, permutation_count, random_seed)
            for permutation_index, order in enumerate(permutations, start=1):
                templates.append(
                    _case(
                        experiment_id,
                        task,
                        1,
                        choice_order=order,
                        metadata={"permutation_index": permutation_index},
                    )
                )
        return _repeat_cases(templates, repetitions)

    templates = []
    for task in tasks:
        if task.task_id not in MULTIPLE_CHOICE_TASKS:
            continue
        orders = _interaction_orders(task, interaction_blocks, random_seed)
        for block_index, order in enumerate(orders, start=1):
            noise_index = (block_index - 1) % len(NOISE_SAMPLES)
            position = NOISE_POSITIONS[(block_index - 1) % len(NOISE_POSITIONS)]
            block_id = f"{task.task_id}_block_{block_index:03d}"
            for condition in ("original_clean", "shuffled_clean", "original_noisy", "shuffled_noisy"):
                is_noisy = condition.endswith("noisy")
                is_shuffled = condition.startswith("shuffled")
                active_order = order if is_shuffled else task.choices
                templates.append(
                    _case(
                        experiment_id,
                        task,
                        1,
                        noise_type="fixed_words" if is_noisy else None,
                        noise_text=NOISE_SAMPLES[noise_index] if is_noisy else None,
                        noise_position=position if is_noisy else None,
                        choice_order=active_order,
                        block_id=block_id,
                        factor_condition=condition,
                        metadata={"noise_sample": noise_index + 1, "shuffle_index": block_index},
                    )
                )
    return _repeat_cases(templates, repetitions)


def _perturbed_case(experiment_id: str, task: ResearchTask, perturbation: Perturbation) -> ExperimentCase:
    """Convert a perturbation specification into a prompt case."""
    return _case(
        experiment_id,
        task,
        1,
        noise_type=perturbation.category if perturbation.text else None,
        noise_text=perturbation.text,
        noise_position=perturbation.noise_position,
        question=perturbation.question,
        perturbation_id=perturbation.perturbation_id,
        perturbation_category=perturbation.category,
    )


def _interaction_orders(task: ResearchTask, count: int, seed: int) -> tuple[tuple[AnswerChoice, ...], ...]:
    """Build a balanced, reproducible set of non-original orders for interaction blocks."""
    original_ids = tuple(choice.choice_id for choice in task.choices)
    position_count = (count + len(task.choices) - 1) // len(task.choices)
    if position_count > factorial(len(task.choices) - 1):
        raise ValueError(f"Too many interaction blocks for unique orders in {task.task_id}")
    rng = random.Random(seed)
    correct = next(choice for choice in task.choices if choice.choice_id == task.correct_answer)
    distractors = [choice for choice in task.choices if choice.choice_id != task.correct_answer]
    orders: list[tuple[AnswerChoice, ...]] = []
    seen: set[tuple[str, ...]] = {original_ids}
    for index in range(count):
        position = index % len(task.choices)
        while True:
            candidate = rng.sample(distractors, len(distractors))
            candidate.insert(position, correct)
            order = tuple(candidate)
            order_ids = tuple(choice.choice_id for choice in order)
            if order_ids not in seen:
                seen.add(order_ids)
                orders.append(order)
                break
    rng.shuffle(orders)
    return tuple(orders)


def count_cases_for_all_experiments(
    *, repetitions: int = 1, random_seed: int = 1729, permutation_count: int = 90, interaction_blocks: int = 18
) -> dict[str, int]:
    """Return default planned call counts for all five experiments."""
    return {
        experiment_id: len(
            generate_experiment_cases(
                experiment_id,
                repetitions=repetitions,
                random_seed=random_seed,
                permutation_count=permutation_count,
                interaction_blocks=interaction_blocks,
            )
        )
        for experiment_id in EXPERIMENT_NAMES if experiment_id != "06"
    }
