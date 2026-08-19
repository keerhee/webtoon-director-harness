#!/usr/bin/env python3
"""Create the workspace skeleton for an episode.

    python scripts/init_episode.py ep01
    python scripts/init_episode.py ep01 --from-example
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):  # keep output readable on legacy consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


from harness.artifacts import STAGE_DIRS  # noqa: E402
from harness.config import find_repo_root  # noqa: E402

NEXT_STEPS = """# {episode}

Workspace created by `scripts/init_episode.py`.

1. Put the upstream handoff and layout files in `00_input/`.
2. Normalize them to `00_input/normalized_input.yaml`.
3. In Claude Code, run the Director's Room over this episode.

Stage directories are written in pipeline order; never edit an upstream stage in place.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("episode", nargs="?", default="ep01", help="episode id, e.g. ep01")
    parser.add_argument(
        "--from-example",
        action="store_true",
        help="seed 00_input/ from examples/sample_episode/",
    )
    parser.add_argument(
        "--workspace",
        default="_workspace",
        help="workspace root (default: _workspace)",
    )
    args = parser.parse_args(argv)

    root = Path(args.workspace) / args.episode
    for sub in STAGE_DIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(NEXT_STEPS.format(episode=args.episode), encoding="utf-8")

    if args.from_example:
        source = find_repo_root() / "examples" / "sample_episode" / "00_input"
        for item in source.glob("*"):
            if item.is_file():
                shutil.copy2(item, root / "00_input" / item.name)
        print(f"Seeded 00_input from {source}")

    print(f"Created episode workspace: {root}")
    print("Next: place upstream files in 00_input/, then run the Director's Room.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
