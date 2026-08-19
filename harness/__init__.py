"""Webtoon Director Harness — shared library for the Director's Room pipeline.

The creative work lives in `.claude/` (agents and skills). This package holds the
deterministic parts: config loading, weighted scoring, and artifact validation, so
that the quality gate is reproducible and testable rather than a matter of opinion.
"""

from harness.config import (
    AXES,
    find_repo_root,
    load_direction_modes,
    load_quality_gate,
    load_vocabulary,
)
from harness.scoring import ScoreResult, evaluate, normalize_scores, weighted_total

__version__ = "0.2.0"

__all__ = [
    "AXES",
    "ScoreResult",
    "evaluate",
    "find_repo_root",
    "load_direction_modes",
    "load_quality_gate",
    "load_vocabulary",
    "normalize_scores",
    "weighted_total",
    "__version__",
]
