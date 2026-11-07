"""Canonical research tasks and deterministic prompt rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class AnswerChoice:
    """A multiple-choice answer with a stable semantic identifier."""

    choice_id: str
    text: str


@dataclass(frozen=True)
class ResearchTask:
    """Structured task content used by every experiment."""

    task_id: str
    name: str
    description: str
    question: str
    correct_answer: str
    choices: tuple[AnswerChoice, ...] = ()

    @property
    def system_message(self) -> str:
        """Return the consistent system message for this task."""
        return "Follow the user instructions exactly. Return only the requested answer."

    @property
    def response_instruction(self) -> str:
        """Return the task's output-format instruction."""
        if self.choices:
            return "Return only the number of the correct option. Do not explain."
        return "Return only the integer answer. Do not provide an explanation."


TASKS: tuple[ResearchTask, ...] = (
    ResearchTask(
        task_id="task_01_math",
        name="Mathematics",
        description=(
            "A store has 4 boxes containing 18 bottles of water each. During the morning, 23 bottles are sold. "
            "Later, 2 additional packages containing 12 bottles each are delivered. By the evening, 7 bottles "
            "have been broken."
        ),
        question="How many intact bottles remain in the store?",
        correct_answer="66",
    ),
    ResearchTask(
        task_id="task_02_logic",
        name="Logical Reasoning",
        description=(
            "There are three closed boxes in a warehouse. One contains only tea bags, another contains only "
            "coffee packets, and the third contains a mixture of tea bags and coffee packets. The boxes are "
            "labeled \"Tea\", \"Coffee\", and \"Tea and Coffee\". All three labels are incorrect. A worker "
            "takes one item from the box labeled \"Tea and Coffee\". It is a tea bag."
        ),
        question="What is inside the box labeled \"Coffee\"?",
        correct_answer="mixture",
        choices=(
            AnswerChoice("tea_only", "Tea only"),
            AnswerChoice("coffee_only", "Coffee only"),
            AnswerChoice("mixture", "A mixture of tea and coffee"),
            AnswerChoice("insufficient_information", "Not enough information to determine"),
        ),
    ),
    ResearchTask(
        task_id="task_03_traffic",
        name="Everyday Knowledge",
        description=(
            "You are standing at a pedestrian crossing controlled by a working pedestrian traffic light. The "
            "signal displays exactly one steady color. Assume ordinary pedestrian traffic-light rules, with no "
            "traffic officer or special instructions."
        ),
        question="Which signal color permits a pedestrian to start crossing?",
        correct_answer="green",
        choices=tuple(
            AnswerChoice(choice_id, label)
            for choice_id, label in (
                ("green", "Green"),
                ("red", "Red"),
                ("yellow", "Yellow"),
                ("purple", "Purple"),
                ("white", "White"),
                ("black", "Black"),
                ("blue", "Blue"),
                ("pink", "Pink"),
                ("turquoise", "Turquoise"),
            )
        ),
    ),
)

TASKS_BY_ID = {task.task_id: task for task in TASKS}


def render_prompt(
    task: ResearchTask,
    *,
    question: str | None = None,
    choice_order: Sequence[AnswerChoice] | None = None,
    noise_text: str | None = None,
    noise_position: str | None = None,
) -> tuple[str, int | None]:
    """Render a task prompt and return its correct displayed option number, if any."""
    rendered_question = question or task.question
    choices = tuple(choice_order) if choice_order is not None else task.choices
    choice_lines = [f"{index}. {choice.text}" for index, choice in enumerate(choices, start=1)]
    correct_number = next(
        (index for index, choice in enumerate(choices, start=1) if choice.choice_id == task.correct_answer),
        None,
    )
    question_block = rendered_question
    if choice_lines:
        question_block = f"{question_block}\n\nAnswer choices:\n" + "\n".join(choice_lines)

    if noise_text and noise_position == "before_task":
        content = f"Irrelevant context: {noise_text}\n\n{task.description}\n\n{question_block}"
    elif noise_text and noise_position == "between_description_question":
        content = f"{task.description}\n\nIrrelevant context: {noise_text}\n\n{question_block}"
    elif noise_text and noise_position == "after_question":
        content = f"{task.description}\n\n{question_block}\n\nIrrelevant context: {noise_text}"
    else:
        content = f"{task.description}\n\n{question_block}"
    return f"{content}\n\n{task.response_instruction}", correct_number


def get_task(task_id: str) -> ResearchTask:
    """Return a configured task by ID."""
    try:
        return TASKS_BY_ID[task_id]
    except KeyError as error:
        raise ValueError(f"Unknown task ID: {task_id}") from error
