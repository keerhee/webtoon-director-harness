#!/usr/bin/env python3
"""Score one or more critic reports against the quality gate.

    python scripts/score_direction.py _workspace/ep01/03_reviews/critic_cinematic.yaml
    python scripts/score_direction.py _workspace/ep01/03_reviews/critic_*.yaml --json
    python scripts/score_direction.py _workspace/ep01/00_input/breakdown/critic_*.yaml --gate breakdown

Exit code is 0 when every report passes, 1 when any report needs revision.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):  # keep output readable on legacy consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


from harness.config import (  # noqa: E402
    ConfigError,
    load_breakdown_gate,
    load_quality_gate,
    load_yaml,
)
from harness.scoring import evaluate  # noqa: E402


def _render(result, path: Path, axes) -> None:
    print(f"\n{path.name}  -  candidate: {result.candidate}")
    print("-" * 60)
    for axis in axes:
        score = result.scores.get(axis)
        if score is None:
            continue
        bar = "#" * int(round(score))
        print(f"  {axis:<20} {score:>5.1f}  {bar}")
    print("-" * 60)
    print(f"  weighted total       {result.weighted_total:>5.2f}   (threshold {result.threshold:.2f})")
    if result.hard_failures:
        print("  hard failures:")
        for failure in result.hard_failures:
            print(f"    - {failure}")
    for warning in result.integrity_warnings:
        print(f"  ! {warning}")
    print(f"  verdict: {result.verdict}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("reports", nargs="+", type=Path, help="critic report YAML files")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--quiet", action="store_true", help="print only the verdict line")
    parser.add_argument(
        "--gate",
        choices=["direction", "breakdown"],
        default="direction",
        help="which gate to score against (default: direction; breakdown = Stage 0.5)",
    )
    args = parser.parse_args(argv)

    try:
        config = load_breakdown_gate() if args.gate == "breakdown" else load_quality_gate()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    results = []
    for path in args.reports:
        try:
            result = evaluate(load_yaml(path), config)
        except ConfigError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            return 2
        results.append((path, result))

    if args.json:
        print(json.dumps([r.as_dict() | {"file": str(p)} for p, r in results], indent=2))
    elif args.quiet:
        for path, result in results:
            print(f"{result.weighted_total:.2f} {result.verdict} {path.name}")
    else:
        axes = list(config["weights"])
        for path, result in results:
            _render(result, path, axes)
        if len(results) > 1:
            best = max(results, key=lambda item: item[1].weighted_total)
            print(f"\nHighest scoring candidate: {best[1].candidate} ({best[1].weighted_total:.2f})")

    return 0 if all(result.passed for _, result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
