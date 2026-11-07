"""Optional live LM Studio integration test, disabled unless explicitly enabled."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from llm_stability_lab.config import load_config
from llm_stability_lab.evaluation import evaluate_response
from llm_stability_lab.inference import InferenceClient
from llm_stability_lab.tasks import get_task, render_prompt

pytestmark = pytest.mark.skipif(
    os.environ.get("LLM_STABILITY_LAB_INTEGRATION") != "1",
    reason="Set LLM_STABILITY_LAB_INTEGRATION=1 to call the configured LM Studio endpoint.",
)


def test_live_lm_studio_smoke() -> None:
    """Discover the configured model and send one answerable request."""
    config = load_config(Path("configs/default.yaml"))
    task = get_task("task_01_math")
    user_message, _ = render_prompt(task)
    with InferenceClient(config.inference) as client:
        client.require_configured_model()
        result = client.complete(
            [
                {"role": "system", "content": task.system_message},
                {"role": "user", "content": user_message},
            ]
        )
    assert result.error_type is None, result.error_message
    assert evaluate_response(task, result.raw_response).is_correct is True
