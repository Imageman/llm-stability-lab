"""Reproducible experiments for studying LLM answer stability."""

import os
from pathlib import Path

__version__ = "0.1.0"

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parent.parent / "tmp" / "matplotlib"),
)
