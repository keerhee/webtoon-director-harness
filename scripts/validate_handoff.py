#!/usr/bin/env python3
"""Verify a handoff package is complete before declaring an episode done.

    python scripts/validate_handoff.py _workspace/ep01/06_handoff

Files must exist, be non-empty, and - for YAML artifacts - parse and conform to schema.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):  # keep output readable on legacy consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


from harness.artifacts import (  # noqa: E402
    REQUIRED_HANDOFF_FILES,
    missing_handoff_files,
    validate_artifact,
)
from harness.config import ConfigError  # noqa: E402

TEMPLATE_MARKER = "{{episode_id}}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "handoff_dir",
        nargs="?",
        default=Path("_workspace/ep01/06_handoff"),
        type=Path,
        help="handoff directory (default: _workspace/ep01/06_handoff)",
    )
    args = parser.parse_args(argv)

    missing = missing_handoff_files(args.handoff_dir)
    problems = [f"missing or empty: {name}" for name in missing]

    for name in REQUIRED_HANDOFF_FILES:
        path = args.handoff_dir / name
        if name in missing or not path.is_file():
            continue
        if path.suffix == ".md" and TEMPLATE_MARKER in path.read_text(encoding="utf-8"):
            problems.append(f"unfilled template placeholder in {name}")
        if path.suffix in {".yaml", ".yml"}:
            try:
                for issue in validate_artifact(path):
                    if issue.level == "error":
                        problems.append(f"{name}: {issue.message}")
            except ConfigError as exc:
                problems.append(f"{name}: {exc}")

    if problems:
        print("Handoff validation: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"Handoff validation: PASS ({len(REQUIRED_HANDOFF_FILES)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
