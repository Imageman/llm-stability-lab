"""Deterministic parsing and semantic evaluation of model responses."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .tasks import ResearchTask, render_prompt

INTEGER_RESPONSE = re.compile(r"^[+-]?\d+$")


@dataclass(frozen=True)
class Evaluation:
    """Parsed answer fields stored with an inference result."""

    normalized_answer: str | None
    selected_choice_id: str | None
    is_correct: bool | None
    format_compliant: bool
    parse_status: str


def evaluate_response(
    task: ResearchTask,
    raw_response: str | None,
    *,
    choice_order: tuple | None = None,
    correct_number: int | None = None,
    truncated: bool = False,
) -> Evaluation:
    """Parse a response and compare its semantic answer with the task reference."""
    if truncated:
        return Evaluation(None, None, None, False, "truncated")
    if raw_response is None or not raw_response.strip():
        return Evaluation(None, None, None, False, "empty")
    response = raw_response.strip()
    if not INTEGER_RESPONSE.fullmatch(response):
        return Evaluation(None, None, None, False, "malformed")
    numeric_answer = int(response)
    if not task.choices:
        normalized = str(numeric_answer)
        return Evaluation(normalized, None, normalized == task.correct_answer, True, "valid")
    choices = choice_order or task.choices
    if correct_number is None:
        _, correct_number = render_prompt(task, choice_order=choices)
    if not 1 <= numeric_answer <= len(choices):
        return Evaluation(str(numeric_answer), None, False, False, "out_of_range")
    selected_id = choices[numeric_answer - 1].choice_id
    return Evaluation(
        normalized_answer=selected_id,
        selected_choice_id=selected_id,
        is_correct=selected_id == task.correct_answer,
        format_compliant=True,
        parse_status="valid",
    )
