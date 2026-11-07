"""Incremental JSONL storage and resumable run helpers."""

from __future__ import annotations

import json
import traceback
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from loguru import logger

from .experiments import ExperimentCase


def create_run_id() -> str:
    """Create a sortable, unique run identifier."""
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}_{uuid.uuid4().hex[:8]}"


def raw_results_path(results_dir: Path, run_id: str) -> Path:
    """Return the raw JSONL path for a run."""
    return results_dir / "raw" / f"{run_id}.jsonl"


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Append one complete JSON record and flush it before returning."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as output_file:
            output_file.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            output_file.write("\n")
            output_file.flush()
    except Exception:
        logger.error(f"Failed to append JSONL record to {path.resolve()}\n{traceback.format_exc()}")
        raise


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load valid JSON objects from a JSONL result file."""
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    try:
        with path.open("r", encoding="utf-8") as input_file:
            for line_number, line in enumerate(input_file, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid JSON in {path.resolve()} at line {line_number}: {error}") from error
                if not isinstance(record, dict):
                    raise ValueError(f"Expected a JSON object in {path.resolve()} at line {line_number}")
                records.append(record)
    except Exception:
        logger.error(f"Failed to load JSONL results from {path.resolve()}\n{traceback.format_exc()}")
        raise
    return records


def completed_case_ids(path: Path) -> set[str]:
    """Return successful and failed cases already persisted for resume safety."""
    return {str(record["case_id"]) for record in load_jsonl(path) if record.get("case_id")}


def pending_cases(cases: Iterable[ExperimentCase], completed_ids: set[str]) -> list[ExperimentCase]:
    """Return cases without a persisted record, preserving their planned order."""
    return [case for case in cases if case.case_id not in completed_ids]


def write_new_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a new JSON metadata file without overwriting an existing file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as output_file:
            json.dump(payload, output_file, ensure_ascii=False, indent=2)
            output_file.write("\n")
    except Exception:
        logger.error(f"Failed to create metadata file {path.resolve()}\n{traceback.format_exc()}")
        raise


def write_records(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Append a sequence of result records one at a time."""
    for record in records:
        append_jsonl(path, record)
