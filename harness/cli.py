"""Console entry points, so the tools work after `pip install -e .` from any directory."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _run(script: str) -> int:
    path = _SCRIPTS / script
    if not path.is_file():  # pragma: no cover - only in a non-source install
        print(f"Script not found: {path}", file=sys.stderr)
        return 2
    sys.argv[0] = str(path)
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


def score() -> int:
    """`wdh-score` — weighted scoring of critic reports."""
    return _run("score_direction.py")


def validate() -> int:
    """`wdh-validate` — schema and vocabulary validation of an episode workspace."""
    return _run("validate_artifacts.py")
