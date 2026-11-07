"""Mocked API and resume validation tests that do not need LM Studio."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from llm_stability_lab.config import AppConfig, InferenceConfig, RunConfig, config_dict
from llm_stability_lab.experiments import generate_experiment_cases
from llm_stability_lab.inference import InferenceClient, InferenceResult
from llm_stability_lab.storage import completed_case_ids, load_jsonl, write_new_json
from llm_stability_lab.cli import _check_resume, _plan_hash, raw_results_path, run


class FakeOpenAIClient:
    """Minimal SDK-compatible fake for deterministic unit tests."""

    def __init__(self, **_: Any) -> None:
        """Create fake model and completion endpoints."""
        self.models = Mock()
        self.models.list.return_value.data = [Mock(id="openai/gpt-oss-20b")]
        self.chat = Mock()
        self.chat.completions = Mock()
        response = Mock()
        response.choices = [
            Mock(message=Mock(content="66", reasoning=None), finish_reason="stop")
        ]
        response.usage = Mock(prompt_tokens=10, completion_tokens=1)
        response.id = "response-1"
        response.model = "openai/gpt-oss-20b"
        response.created = 1
        response.system_fingerprint = "fingerprint"
        self.chat.completions.create.return_value = response
        self.close = Mock()


def test_mocked_inference_and_model_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Call the wrapper using a fake SDK and check requested parameters and metadata."""
    fake_client = FakeOpenAIClient()
    monkeypatch.setattr("llm_stability_lab.inference.OpenAI", lambda **_: fake_client)
    settings = InferenceConfig()
    with InferenceClient(settings) as client:
        assert client.require_configured_model() == [settings.model_id]
        result = client.complete([{"role": "user", "content": "Return 66."}])
    assert result.raw_response == "66"
    assert result.prompt_tokens == 10
    assert result.requested_parameters["temperature"] == 0
    assert result.requested_parameters["max_tokens"] == 2048
    assert result.error_type is None
    fake_client.close.assert_called_once()


def test_resume_requires_same_settings_and_case_plan(tmp_path: Path) -> None:
    """Reject resume attempts whose saved plan or inference configuration changed."""
    config = AppConfig()
    cases = generate_experiment_cases("01", repetitions=2)
    metadata_path = tmp_path / "run.json"
    write_new_json(
        metadata_path,
        {
            "inference_config": config_dict(config)["inference"],
            "plan_hash": _plan_hash(cases),
            "experiment_ids": ["01"],
        },
    )
    assert _check_resume(metadata_path, config, _plan_hash(cases), ["01"])
    with pytest.raises(ValueError, match="Resume plan differs"):
        _check_resume(metadata_path, config, _plan_hash(cases[:-1]), ["01"])
    changed_config = AppConfig(inference=InferenceConfig(model_id="different-model"))
    with pytest.raises(ValueError, match="inference settings"):
        _check_resume(metadata_path, changed_config, _plan_hash(cases), ["01"])


def test_run_resume_skips_already_recorded_cases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute a mocked small run and verify resume does not duplicate records."""
    settings = AppConfig(run=RunConfig(results_dir=tmp_path, repetitions=2))
    monkeypatch.setattr("llm_stability_lab.cli.load_config", lambda _: settings)

    class FakeInferenceClient:
        """Fake sequential client used by the CLI run test."""

        def __init__(self, _: InferenceConfig) -> None:
            """Initialize call tracking."""
            self.call_count = 0

        def require_configured_model(self) -> list[str]:
            """Return the configured model ID without a network call."""
            return [settings.inference.model_id]

        def complete(self, _: list[dict[str, str]]) -> InferenceResult:
            """Return the mathematical reference answer."""
            self.call_count += 1
            return InferenceResult(
                raw_response="66",
                finish_reason="stop",
                prompt_tokens=10,
                completion_tokens=1,
                requested_parameters={"temperature": 0},
                response_metadata={},
            )

        def close(self) -> None:
            """Release no resources for this fake client."""

    fake_client = FakeInferenceClient(settings.inference)
    monkeypatch.setattr("llm_stability_lab.cli.InferenceClient", lambda _: fake_client)
    arguments = {
        "experiment": "01",
        "tasks": ["task_01_math"],
        "repetitions": 2,
        "permutation_count": 90,
        "interaction_blocks": None,
        "seed": None,
        "model": None,
        "resume": None,
        "config": Path("unused.yaml"),
        "verbose": False,
    }
    run(**arguments)
    run_id = next((tmp_path / "runs").glob("*.json")).stem
    records_path = raw_results_path(tmp_path, run_id)
    assert fake_client.call_count == 2
    assert len(load_jsonl(records_path)) == 2
    run(**{**arguments, "resume": run_id})
    assert fake_client.call_count == 2
    assert len(load_jsonl(records_path)) == 2
    assert completed_case_ids(records_path) == {case["case_id"] for case in load_jsonl(records_path)}
