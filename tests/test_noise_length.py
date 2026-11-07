"""Tests for matched noise-length planning and context limits."""

from __future__ import annotations

from typing import Any

import pytest

from llm_stability_lab.config import AppConfig, InferenceConfig, RunConfig
from llm_stability_lab.noise_length import _load_frozen_noise, _noise_for_tokens, generate_length_cases
from llm_stability_lab.evaluation import evaluate_response
from llm_stability_lab.tasks import get_task


class FakeModel:
    """A deterministic word tokenizer for planning tests."""

    def tokenize(self, text: str) -> list[str]:
        """Return one synthetic token per whitespace-separated word."""
        return text.split()

    def apply_prompt_template(self, chat: dict[str, Any]) -> str:
        """Render fake chat messages as plain text."""
        return " ".join(message["content"] for message in chat["messages"])

    def get_context_length(self) -> int:
        """Return the model's fake available context."""
        return 18000


class FakeClient:
    """Context manager exposing a fake LM Studio model."""

    def __init__(self, host: str) -> None:
        """Initialize the fake model namespace."""
        self.llm = self

    def __enter__(self) -> FakeClient:
        """Enter the client context."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the client context."""

    def model(self, *args: Any, **kwargs: Any) -> FakeModel:
        """Return the fake model without a network request."""
        return FakeModel()


class FakeChat:
    """Build plain fake chat history for the tokenizer test."""

    @staticmethod
    def from_history(history: dict[str, Any]) -> dict[str, Any]:
        """Return the history unchanged."""
        return history


def test_length_cases_are_matched_and_keep_context_reserve(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep task, answer order, and position matched while increasing noise length."""
    monkeypatch.setattr("llm_stability_lab.noise_length.lms.Client", FakeClient)
    monkeypatch.setattr("llm_stability_lab.noise_length.lms.Chat", FakeChat)
    config = AppConfig(run=RunConfig(experiment_6_noise_levels=[0, 8, 16]))
    cases = generate_length_cases(config, ["task_02_logic"], 2, 42)
    assert len(cases) == 12
    for block in {case.block_id for case in cases}:
        block_cases = [case for case in cases if case.block_id == block]
        assert len(block_cases) == 6
        assert len({case.metadata["noise_position_planned"] for case in block_cases}) == 1
        for order in ("original", "shuffled"):
            orders = {case.answer_permutation for case in block_cases if case.metadata["answer_order"] == order}
            assert len(orders) == 1
        for level in (0, 8, 16):
            matching = [case for case in block_cases if case.metadata["noise_tokens"] == level]
            assert {case.metadata["answer_order"] for case in matching} == {"original", "shuffled"}
            assert all(case.metadata["planned_prompt_tokens"] + 64 + 2048 <= 18000 for case in matching)


def test_invalid_context_budget_and_truncated_empty_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject unsafe settings and classify empty truncated responses explicitly."""
    monkeypatch.setattr("llm_stability_lab.noise_length.lms.Client", FakeClient)
    monkeypatch.setattr("llm_stability_lab.noise_length.lms.Chat", FakeChat)
    config = AppConfig(
        inference=InferenceConfig(max_tokens=90),
        run=RunConfig(experiment_6_context_limit=100, experiment_6_noise_levels=[0, 8]),
    )
    with pytest.raises(ValueError, match="exceeds context budget"):
        generate_length_cases(config, ["task_02_logic"], 1, 42)
    assert evaluate_response(get_task("task_02_logic"), "", truncated=True).parse_status == "truncated"


def test_three_blocks_cover_noise_positions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover both tasks, three noise placements, two orders, and every configured length."""
    monkeypatch.setattr("llm_stability_lab.noise_length.lms.Client", FakeClient)
    monkeypatch.setattr("llm_stability_lab.noise_length.lms.Chat", FakeChat)
    cases = generate_length_cases(AppConfig(), None, 3, 1729)
    assert len(cases) == 60
    for task_id in ("task_02_logic", "task_03_traffic"):
        task_cases = [case for case in cases if case.task_id == task_id]
        assert {case.metadata["noise_position_planned"] for case in task_cases} == {
            "before_task", "between_description_question", "after_question"
        }
        assert {case.metadata["noise_tokens"] for case in task_cases} == {0, 256, 1024, 4096, 8192}


def test_noise_variants_and_frozen_text(tmp_path: Any) -> None:
    """Generate repeatable distinct noise and preserve frozen text across tokenizers."""
    import json

    model = FakeModel()
    variants = {name: _noise_for_tokens(model, 30, name, 42)[0]
                for name in ("random_words", "sentences", "catalog")}
    assert len(set(variants.values())) == 3
    assert variants["random_words"] == _noise_for_tokens(model, 30, "random_words", 42)[0]
    path = tmp_path / "noise.json"
    path.write_text(json.dumps({"0": "", "30": variants["sentences"]}), encoding="utf-8")
    result = _load_frozen_noise(path, [0, 30], model)
    assert result[30][0] == variants["sentences"]
    assert result[30][1] == 30
