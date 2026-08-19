#!/usr/bin/env python3
"""Validate every schema-backed artifact in an episode workspace.

    python scripts/validate_artifacts.py _workspace/ep01
    python scripts/validate_artifacts.py examples/sample_episode --strict

Checks JSON Schema conformance, panel ID uniqueness and ordering, controlled-vocabulary
use, and the presence of a purpose on every panel.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):  # keep output readable on legacy consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


from harness.artifacts import iter_artifacts, validate_artifact  # noqa: E402
from harness.config import ConfigError  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("episode_dir", type=Path, help="episode workspace directory")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)

    if not args.episode_dir.is_dir():
        print(f"Not a directory: {args.episode_dir}", file=sys.stderr)
        return 2

    artifacts = list(iter_artifacts(args.episode_dir))
    if not artifacts:
        print(f"No schema-backed artifacts found under {args.episode_dir}")
        return 0

    errors = warnings = 0
    for path in artifacts:
        try:
            issues = validate_artifact(path)
        except ConfigError as exc:
            print(f"  [ERROR] {path}: {exc}")
            errors += 1
            continue

        rel = path.relative_to(args.episode_dir)
        if not issues:
            print(f"  [ok]    {rel}")
            continue
        print(f"  [FAIL]  {rel}")
        for issue in issues:
            print(f"          {issue.level}: {issue.message}")
            if issue.level == "error":
                errors += 1
            else:
                warnings += 1

    print(f"\n{len(artifacts)} artifact(s) checked - {errors} error(s), {warnings} warning(s)")
    if errors or (args.strict and warnings):
        print("Artifact validation: FAIL")
        return 1
    print("Artifact validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
