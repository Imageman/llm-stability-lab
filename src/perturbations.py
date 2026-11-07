"""Deterministic prompt perturbations and answer-order generation."""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import factorial
from typing import Sequence

from .tasks import AnswerChoice, ResearchTask

NOISE_POSITIONS = ("before_task", "between_description_question", "after_question")
NOISE_SAMPLES = (
    "violet lantern copper meadow orbit velvet cinnamon telescope",
    "silver mountain umbrella lemon compass winter violin",
    "amber notebook quiet river marble orchard paper kite",
)
IRRELEVANT_SENTENCES = (
    "A nearby shop recently purchased nineteen oranges.",
    "The warehouse manager prefers blue delivery trucks.",
    "A small garden received a new wooden bench last Tuesday.",
)
WORD_NOISE = (
    "violet lantern copper meadow orbit velvet cinnamon telescope",
    "silver mountain umbrella lemon compass winter violin",
    "amber notebook quiet river marble orchard paper kite",
)
NOISE_LENGTHS = (4, 8, 16)
NOISE_WORDS = ("violet", "lantern", "copper", "meadow", "orbit", "velvet", "cinnamon", "telescope")


@dataclass(frozen=True)
class Perturbation:
    """A named, reproducible change to a prompt."""

    perturbation_id: str
    category: str
    text: str | None = None
    question: str | None = None
    noise_position: str | None = None


def make_task_perturbations(task: ResearchTask, seed: int) -> tuple[Perturbation, ...]:
    """Create fixed perturbation categories while preserving task answers."""
    rng = random.Random(seed)
    variants: list[Perturbation] = []
    for index, text in enumerate(WORD_NOISE, start=1):
        variants.append(Perturbation(f"words_{index}", "random_words", text=text, noise_position="after_question"))
    for index, text in enumerate(IRRELEVANT_SENTENCES, start=1):
        variants.append(
            Perturbation(f"sentence_{index}", "irrelevant_sentence", text=text, noise_position="after_question")
        )
    wording = {
        "task_01_math": "At closing time, how many unbroken bottles of water are still in the store?",
        "task_02_logic": "Which contents are in the box labeled \"Coffee\"?",
        "task_03_traffic": "Which steady light color allows a pedestrian to begin crossing?",
    }[task.task_id]
    variants.append(Perturbation("wording_neutral", "neutral_wording", question=wording))
    for length in NOISE_LENGTHS:
        words = [rng.choice(NOISE_WORDS) for _ in range(length)]
        variants.append(
            Perturbation(
                f"quantity_{length}",
                "noise_quantity",
                text=" ".join(words),
                noise_position="after_question",
            )
        )
    return tuple(variants)


def balanced_permutations(
    choices: Sequence[AnswerChoice], correct_choice_id: str, count: int, seed: int
) -> tuple[tuple[AnswerChoice, ...], ...]:
    """Generate deterministic permutations with balanced correct-choice positions."""
    if count <= 0:
        raise ValueError("Permutation count must be positive")
    choice_ids = {choice.choice_id for choice in choices}
    if correct_choice_id not in choice_ids:
        raise ValueError(f"Correct choice ID {correct_choice_id!r} is not present")
    rng = random.Random(seed)
    correct_choice = next(choice for choice in choices if choice.choice_id == correct_choice_id)
    distractors = [choice for choice in choices if choice.choice_id != correct_choice_id]
    selected: list[tuple[AnswerChoice, ...]] = []
    seen_by_position: list[set[tuple[str, ...]]] = [set() for _ in choices]
    needed_per_position = (count + len(choices) - 1) // len(choices)
    if needed_per_position > factorial(len(distractors)):
        raise ValueError("Requested count exceeds the number of unique permutations per correct-answer position")
    for index in range(count):
        position = index % len(choices)
        while True:
            candidate = list(rng.sample(distractors, len(distractors)))
            candidate.insert(position, correct_choice)
            permutation = tuple(candidate)
            signature = tuple(choice.choice_id for choice in permutation)
            if signature not in seen_by_position[position]:
                seen_by_position[position].add(signature)
                selected.append(permutation)
                break
    rng.shuffle(selected)
    return tuple(selected)


def all_permutations(choices: Sequence[AnswerChoice]) -> tuple[tuple[AnswerChoice, ...], ...]:
    """Return all permutations in stable iteration order."""
    from itertools import permutations

    return tuple(permutations(choices))
