"""OpenAI-compatible LM Studio client with explicit failure records."""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any, Sequence

from loguru import logger
from openai import OpenAI

from .config import InferenceConfig


@dataclass(frozen=True)
class InferenceResult:
    """Response data and requested settings from one independent API call."""

    raw_response: str | None
    finish_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    requested_parameters: dict[str, Any]
    response_metadata: dict[str, Any]
    error_type: str | None = None
    error_message: str | None = None
    error_traceback: str | None = None


class InferenceClient:
    """Small reusable client for an OpenAI-compatible local inference server."""

    def __init__(self, config: InferenceConfig) -> None:
        """Create a client without making a network request."""
        self.config = config
        self._client = OpenAI(
            base_url=config.base_url,
            api_key="lm-studio",
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
        )

    def __enter__(self) -> InferenceClient:
        """Return this client for use in a context manager."""
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback_info: Any) -> None:
        """Close the underlying client when leaving a context manager."""
        self.close()

    def list_models(self) -> list[str]:
        """Return model IDs currently exposed by the configured endpoint."""
        try:
            return [model.id for model in self._client.models.list().data]
        except Exception as error:
            logger.exception(f"Model discovery failed at {self.config.base_url}/models")
            raise ConnectionError(
                f"Could not list models from {self.config.base_url}/models: {error}"
            ) from error

    def require_configured_model(self) -> list[str]:
        """Check the selected model exists without substituting another model ID."""
        models = self.list_models()
        if self.config.model_id not in models:
            raise ValueError(
                f"Configured model {self.config.model_id!r} is not exposed by the server. "
                f"Available IDs: {', '.join(models) if models else '(none)'}"
            )
        return models

    def complete(self, messages: Sequence[dict[str, str]]) -> InferenceResult:
        """Send one stateless chat completion and preserve response metadata."""
        parameters: dict[str, Any] = {
            "model": self.config.model_id,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False,
        }
        if self.config.seed is not None:
            parameters["seed"] = self.config.seed
        if self.config.reasoning_effort is not None:
            parameters["extra_body"] = {"reasoning_effort": self.config.reasoning_effort}
        try:
            response = self._client.chat.completions.create(messages=list(messages), **parameters)
            choice = response.choices[0] if response.choices else None
            message = choice.message if choice is not None else None
            raw_response = message.content if message is not None else None
            if isinstance(raw_response, list):
                raw_response = "".join(
                    str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in raw_response
                )
            usage = response.usage
            return InferenceResult(
                raw_response=str(raw_response) if raw_response is not None else None,
                finish_reason=choice.finish_reason if choice is not None else None,
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                requested_parameters=self._requested_parameters(parameters),
                response_metadata={
                    "response_id": response.id,
                    "model": response.model,
                    "created": response.created,
                    "system_fingerprint": getattr(response, "system_fingerprint", None),
                    "reasoning_content": getattr(message, "reasoning", None) if message is not None else None,
                },
            )
        except Exception as error:
            trace = traceback.format_exc()
            logger.error(
                f"Inference failed for model {self.config.model_id!r} at {self.config.base_url}: "
                f"{type(error).__name__}: {error}\n{trace}"
            )
            return InferenceResult(
                raw_response=None,
                finish_reason=None,
                prompt_tokens=None,
                completion_tokens=None,
                requested_parameters=self._requested_parameters(parameters),
                response_metadata={},
                error_type=type(error).__name__,
                error_message=str(error),
                error_traceback=trace,
            )

    def _requested_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Record API parameters and client-side execution settings."""
        return (
            {key: value for key, value in parameters.items() if key != "extra_body"}
            | parameters.get("extra_body", {})
            | {
                "reasoning_effort": self.config.reasoning_effort,
                "seed": self.config.seed,
                "timeout_seconds": self.config.timeout_seconds,
                "max_retries": self.config.max_retries,
                "concurrency": 1,
            }
        )

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._client.close()
