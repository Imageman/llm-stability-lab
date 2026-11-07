"""Plan matched noise-length experiments using the selected model's tokenizer."""

from __future__ import annotations

import json
import random
import traceback
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse

import lmstudio as lms
from loguru import logger

from .config import AppConfig
from .experiments import ExperimentCase, MULTIPLE_CHOICE_TASKS, _case, _filter_tasks, _interaction_orders, _repeat_cases
from .perturbations import NOISE_POSITIONS

NOISE_WORDS = ("violet", "lantern", "copper", "meadow", "orbit", "velvet", "cinnamon", "telescope")
TEMPLATE_TOKEN_MARGIN = 64
MAX_NOISE_TOKENS = 8192
VOCABULARY = (
    "orchard", "compass", "violet", "pillow", "marble", "island", "copper", "lantern", "harbor", "ribbon",
    "forest", "window", "silver", "garden", "velvet", "pencil", "tunnel", "meadow", "planet", "basket",
    "orange", "winter", "guitar", "pebble", "saddle", "puzzle", "mirror", "cloud", "ticket", "candle",
)
SENTENCES = (
    "A quiet garden has a wooden bench near the northern path.",
    "The blue notebook was placed beside a small ceramic vase.",
    "Several birds gathered near the old stone bridge this morning.",
    "A local workshop repaired a bicycle with a silver bell.",
    "The library has a window overlooking a row of trees.",
    "A painter arranged brushes and colors on a wide table.",
)


def _noise_for_tokens(model: Any, target: int, variant: str = "repeated", seed: int = 1729) -> tuple[str, int]:
    """Make a deterministic noise prefix with at most the target number of tokens."""
    if target == 0:
        return "", 0
    rng = random.Random(seed)
    if variant == "repeated":
        words = list(NOISE_WORDS) * (target + 1)
    elif variant == "random_words":
        words = [rng.choice(VOCABULARY) for _ in range(target * 2)]
    elif variant == "sentences":
        words = " ".join(rng.choice(SENTENCES) for _ in range(target)).split()
    elif variant == "catalog":
        words = " ".join(
            f"Record {index:04d}: {rng.choice(VOCABULARY)} {rng.randrange(100, 10000)} "
            f"{rng.choice(VOCABULARY)}; shelf {rng.randrange(1, 100)}."
            for index in range(target)
        ).split()
    else:
        raise ValueError(f"Unknown noise variant: {variant}")
    low, high = 0, len(words)
    while low < high:
        middle = (low + high + 1) // 2
        if len(model.tokenize(" ".join(words[:middle]))) <= target:
            low = middle
        else:
            high = middle - 1
    text = " ".join(words[:low])
    return text, len(model.tokenize(text))


def _load_frozen_noise(path: Path, levels: list[int], model: Any) -> dict[int, tuple[str, int]]:
    """Read identical saved texts and measure them using the current model tokenizer."""
    try:
        with path.open("r", encoding="utf-8") as noise_file:
            data = json.load(noise_file)
        noises = {target: data[str(target)] for target in levels}
        if any(not isinstance(text, str) for text in noises.values()) or noises[0] != "":
            raise ValueError("Frozen noise must contain strings and an empty baseline")
        measured = {target: (text, len(model.tokenize(text)) if text else 0) for target, text in noises.items()}
        if any(length > MAX_NOISE_TOKENS for _, length in measured.values()):
            raise ValueError(f"Frozen noise exceeds {MAX_NOISE_TOKENS} tokens for the selected model")
        return measured
    except Exception:
        logger.error(f"Could not load or measure noise file {path.resolve()}\n{traceback.format_exc()}")
        raise


def generate_length_cases(
    config: AppConfig, task_ids: Sequence[str] | None, blocks: int, seed: int, repetitions: int = 1
) -> list[ExperimentCase]:
    """Plan matched answer orders and noise lengths with a real LM Studio tokenizer."""
    if blocks < 1 or repetitions < 1:
        raise ValueError("Blocks and repetitions must be positive")
    host = urlparse(config.inference.base_url).netloc
    if not host:
        raise ValueError("The inference base URL must include a host and port")
    context_limit = config.run.experiment_6_context_limit
    if config.inference.max_tokens >= context_limit:
        raise ValueError("The generation reserve must be smaller than the context limit")
    if config.run.experiment_6_noise_levels[-1] >= context_limit - config.inference.max_tokens:
        raise ValueError("A noise target leaves no room for the task and generation reserve")
    try:
        with lms.Client(host) as client:
            model = client.llm.model(
                config.inference.model_id, config={"contextLength": context_limit}, ttl=3600
            )
            actual_context = model.get_context_length()
            if actual_context < context_limit:
                raise ValueError(f"Loaded model context {actual_context} is smaller than {context_limit}")
            if config.run.experiment_6_noise_file:
                noises = _load_frozen_noise(
                    config.run.experiment_6_noise_file, config.run.experiment_6_noise_levels, model
                )
            else:
                noises = {
                    target: _noise_for_tokens(
                        model, target, config.run.experiment_6_noise_variant,
                        config.run.experiment_6_noise_seed if config.run.experiment_6_noise_seed is not None else seed,
                    )
                    for target in config.run.experiment_6_noise_levels
                }
                if any(length > MAX_NOISE_TOKENS for _, length in noises.values()):
                    raise ValueError(f"Noise exceeds {MAX_NOISE_TOKENS} tokens")
            templates: list[ExperimentCase] = []
            for task in _filter_tasks(task_ids):
                if task.task_id not in MULTIPLE_CHOICE_TASKS:
                    continue
                orders = _interaction_orders(task, blocks, seed)
                for block_index, order in enumerate(orders, start=1):
                    position = NOISE_POSITIONS[(block_index - 1) % len(NOISE_POSITIONS)]
                    for target, (noise, actual_noise_tokens) in noises.items():
                        for order_name, choices in (("original", task.choices), ("shuffled", order)):
                            case = _case(
                                "06", task, 1, choice_order=choices,
                                noise_type="length_prefix" if noise else None,
                                noise_text=noise or None,
                                noise_position=position if noise else None,
                                block_id=f"{task.task_id}_block_{block_index:03d}",
                                factor_condition=f"{order_name}_{'noisy' if noise else 'clean'}",
                                metadata={"noise_target_tokens": target, "noise_tokens": actual_noise_tokens,
                                          "noise_position_planned": position, "answer_order": order_name,
                                          "noise_variant": config.run.experiment_6_noise_variant,
                                          "noise_seed": config.run.experiment_6_noise_seed
                                          if config.run.experiment_6_noise_seed is not None else seed},
                            )
                            chat = lms.Chat.from_history({"messages": list(case.messages)})
                            prompt_tokens = len(model.tokenize(model.apply_prompt_template(chat)))
                            if prompt_tokens + TEMPLATE_TOKEN_MARGIN + config.inference.max_tokens > context_limit:
                                raise ValueError(
                                    f"Case {case.case_id} exceeds context budget: prompt={prompt_tokens}, "
                                    f"margin={TEMPLATE_TOKEN_MARGIN}, reserve={config.inference.max_tokens}, "
                                    f"limit={context_limit}"
                                )
                            assert case.metadata is not None
                            case.metadata.update({"planned_prompt_tokens": prompt_tokens,
                                                  "context_limit": context_limit,
                                                  "template_token_margin": TEMPLATE_TOKEN_MARGIN,
                                                  "generation_reserve": config.inference.max_tokens,
                                                  "loaded_model_context": actual_context})
                            templates.append(case)
            logger.info(f"Experiment 06 planned using tokenizer for {config.inference.model_id}")
            return _repeat_cases(templates, repetitions)
    except Exception:
        logger.error(f"Experiment 06 tokenizer or planning failed at {host}\n{traceback.format_exc()}")
        raise
