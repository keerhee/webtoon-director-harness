"""Artifact discovery and validation for an episode workspace."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from harness.config import find_repo_root, load_yaml, load_vocabulary

#: Files the downstream production stage is entitled to expect.
REQUIRED_HANDOFF_FILES = (
    "direction_bible.md",
    "panel_direction.yaml",
    "continuity_state.yaml",
    "critic_report.md",
    "stage2_handoff.md",
)

#: Workspace stage directories, in pipeline order.
STAGE_DIRS = (
    "00_input/layouts",
    "00_input/breakdown",
    "01_analysis",
    "02_candidates",
    "03_reviews",
    "04_synthesis",
    "05_continuity",
    "06_handoff",
)

#: Artifact filename -> schema filename.
SCHEMA_MAP = {
    "beat_sheet.yaml": "beat_sheet.schema.yaml",
    "narrative_analysis.yaml": "narrative_analysis.schema.yaml",
    "emotional.yaml": "panel_direction.schema.yaml",
    "cinematic.yaml": "panel_direction.schema.yaml",
    "webtoon_native.yaml": "panel_direction.schema.yaml",
    "selected_direction.yaml": "panel_direction.schema.yaml",
    "panel_direction.yaml": "panel_direction.schema.yaml",
    "continuity_state.yaml": "continuity_state.schema.yaml",
}

PANEL_ID_RE = re.compile(r"^P(\d{2,3})([a-z]?)$")


@dataclass
class Issue:
    """A single validation problem, addressed to a file."""

    path: Path
    message: str
    level: str = "error"

    def __str__(self) -> str:  # pragma: no cover - formatting only
        mark = "ERROR" if self.level == "error" else "warn "
        return f"  [{mark}] {self.path.name}: {self.message}"


def load_schema(name: str, root: Path | None = None) -> dict[str, Any]:
    root = root or find_repo_root()
    return load_yaml(root / "schemas" / name)


def schema_for(path: Path) -> str | None:
    """Return the schema filename for an artifact, or None when it is unschema'd."""
    if path.suffix in {".yaml", ".yml"}:
        if path.name.startswith("critic_"):
            return "critic_report.schema.yaml"
        # Stage 0.5 candidates are named by approach and live in a breakdown/ directory.
        if path.parent.name == "breakdown":
            return "panel_breakdown.schema.yaml"
    return SCHEMA_MAP.get(path.name)


def validate_against_schema(data: Any, schema: dict[str, Any], path: Path) -> list[Issue]:
    """Validate with jsonschema when available; degrade to required-key checks when not."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        required = schema.get("required", [])
        if isinstance(data, dict):
            return [
                Issue(path, f"missing required key '{key}'")
                for key in required
                if key not in data
            ]
        return [Issue(path, "expected a mapping at the top level")]

    validator = Draft202012Validator(schema)
    issues = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        location = "/".join(str(p) for p in error.path) or "<root>"
        issues.append(Issue(path, f"{location}: {error.message}"))
    return issues


def check_panel_ids(data: Any, path: Path) -> list[Issue]:
    """Panel IDs must be unique and non-decreasing — they key every other artifact."""
    if not isinstance(data, dict) or not isinstance(data.get("panels"), list):
        return []

    issues: list[Issue] = []
    seen: set[str] = set()
    previous = -1
    for panel in data["panels"]:
        if not isinstance(panel, dict):
            continue
        panel_id = str(panel.get("panel_id", ""))
        match = PANEL_ID_RE.match(panel_id)
        if not match:
            issues.append(Issue(path, f"malformed panel_id '{panel_id}' (expected P01, P05a)"))
            continue
        if panel_id in seen:
            issues.append(Issue(path, f"duplicate panel_id '{panel_id}'"))
        seen.add(panel_id)
        number = int(match.group(1))
        if number < previous:
            issues.append(
                Issue(path, f"panel_id '{panel_id}' is out of order", level="warning")
            )
        previous = max(previous, number)
    return issues


def check_vocabulary(data: Any, path: Path, root: Path | None = None) -> list[Issue]:
    """Flag free-text terms where the controlled vocabulary has a listed value."""
    if not isinstance(data, dict) or not isinstance(data.get("panels"), list):
        return []

    vocab = load_vocabulary(root)
    allowed = {
        "shot": set(vocab.get("shot") or {}),
        "angle": set(vocab.get("angle") or {}),
        "transition": set(vocab.get("transition") or {}),
        "beat_duration": set(vocab.get("beat_duration") or {}),
        "dramatic_function": set(vocab.get("dramatic_function") or []),
    }

    issues = []
    for panel in data["panels"]:
        if not isinstance(panel, dict):
            continue
        panel_id = panel.get("panel_id", "?")
        for field, values in allowed.items():
            value = panel.get(field)
            if value and values and value not in values:
                issues.append(
                    Issue(path, f"{panel_id}: {field}='{value}' is not in the vocabulary")
                )
        if not str(panel.get("purpose", "")).strip():
            issues.append(Issue(path, f"{panel_id}: missing purpose"))
    return issues


def validate_artifact(path: Path, root: Path | None = None) -> list[Issue]:
    """Validate one artifact file against its schema, panel IDs, and vocabulary."""
    schema_name = schema_for(path)
    if schema_name is None:
        return []
    data = load_yaml(path)
    issues = validate_against_schema(data, load_schema(schema_name, root), path)
    if schema_name in {"panel_direction.schema.yaml", "panel_breakdown.schema.yaml"}:
        issues += check_panel_ids(data, path)
    if schema_name == "panel_direction.schema.yaml":
        issues += check_vocabulary(data, path, root)
    return issues


def iter_artifacts(episode_dir: Path) -> Iterable[Path]:
    """Yield every schema-backed artifact under an episode workspace."""
    for path in sorted(Path(episode_dir).rglob("*.y*ml")):
        if schema_for(path):
            yield path


def missing_handoff_files(handoff_dir: Path) -> list[str]:
    """Required handoff files that are absent or empty."""
    handoff_dir = Path(handoff_dir)
    missing = []
    for name in REQUIRED_HANDOFF_FILES:
        target = handoff_dir / name
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(name)
    return missing
