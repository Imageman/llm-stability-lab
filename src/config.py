"""Validated application configuration and logging setup."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

import yaml
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_validator


class InferenceConfig(BaseModel):
    """Settings sent to the OpenAI-compatible inference API."""

    model_config = ConfigDict(extra="forbid")

    base_url: str = "http://192.168.0.109:1234/v1"
    model_id: str = "openai/gpt-oss-20b"
    timeout_seconds: float = Field(default=120, gt=0)
    temperature: float = Field(default=0, ge=0)
    max_tokens: int = Field(default=2048, gt=0)
    reasoning_effort: str | None = None
    seed: int | None = None
    max_retries: int = Field(default=0, ge=0)


class RunConfig(BaseModel):
    """Defaults for experiment execution and result storage."""

    model_config = ConfigDict(extra="forbid")

    results_dir: Path = Path("results")
    repetitions: int = Field(default=100, gt=0)
    experiment_5_blocks: int = Field(default=18, gt=0)
    experiment_6_context_limit: int = Field(default=18000, gt=0, le=18000)
    experiment_6_noise_levels: list[int] = Field(default_factory=lambda: [0, 256, 1024, 4096, 8192])
    experiment_6_noise_variant: Literal["repeated", "random_words", "sentences", "catalog"] = "repeated"
    experiment_6_noise_seed: int | None = None
    experiment_6_noise_file: Path | None = None
    random_seed: int = 1729

    @field_validator("experiment_6_noise_levels")
    @classmethod
    def validate_noise_levels(cls, levels: list[int]) -> list[int]:
        """Require a clean baseline and strictly increasing nonnegative targets."""
        if not levels or levels[0] != 0 or levels != sorted(set(levels)) or any(level < 0 for level in levels):
            raise ValueError("Noise levels must start at zero and be strictly increasing")
        return levels


class AppConfig(BaseModel):
    """Complete application configuration."""

    model_config = ConfigDict(extra="forbid")

    inference: InferenceConfig = Field(default_factory=InferenceConfig)
    run: RunConfig = Field(default_factory=RunConfig)


def load_config(path: Path) -> AppConfig:
    """Load and validate YAML configuration from ``path``."""
    try:
        with path.open("r", encoding="utf-8") as config_file:
            raw_config: Any = yaml.safe_load(config_file) or {}
        return AppConfig.model_validate(raw_config)
    except Exception:
        logger.exception(f"Failed to load configuration file {path.resolve()}")
        raise


def configure_logging(log_path: Path | None = None, verbose: bool = False) -> None:
    """Configure readable console logging and optional persistent file logging."""
    logger.remove()
    logger.add(
        sink=sys.stderr,
        level="DEBUG" if verbose else "INFO",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )
    if log_path is not None:
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            logger.add(
                log_path,
                level="DEBUG",
                encoding="utf-8",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
            )
        except Exception:
            logger.exception(f"Failed to configure log file {log_path.resolve()}")
            raise


def config_dict(config: AppConfig) -> dict[str, Any]:
    """Return a JSON-serializable configuration snapshot."""
    return config.model_dump(mode="json")
