"""Config loading for the quality gate, direction modes, and controlled vocabulary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

#: The six direction scoring axes, in report order.
AXES = (
    "narrative_clarity",
    "emotional_impact",
    "visual_composition",
    "pacing_scroll",
    "reading_flow",
    "continuity",
)

#: The four Stage 0.5 panel-breakdown axes, in report order.
BREAKDOWN_AXES = (
    "beat_coverage",
    "reveal_placement",
    "rhythm_potential",
    "production_cost",
)

_MARKER = Path("config") / "quality_gate.yaml"


class ConfigError(RuntimeError):
    """Raised when a config file is missing or internally inconsistent."""


def find_repo_root(start: Path | None = None) -> Path:
    """Walk upward from `start` (default: cwd) until the config directory is found.

    Falls back to the directory containing this package, which is the repo root in
    an editable install.
    """
    for base in (start or Path.cwd(), Path(__file__).resolve().parent.parent):
        base = Path(base).resolve()
        for candidate in (base, *base.parents):
            if (candidate / _MARKER).is_file():
                return candidate
    raise ConfigError(
        f"Could not locate {_MARKER.as_posix()}. Run from inside the repository."
    )


def load_yaml(path: Path) -> Any:
    """Load a YAML file with a useful error message when it is missing or malformed."""
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"Missing file: {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - message formatting only
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc


def _validate_gate(config: dict[str, Any], axes: tuple[str, ...], label: str) -> dict[str, Any]:
    """Shared validation for any gate: complete, known, normalized weights."""
    weights = config.get("weights") or {}
    missing = set(axes) - set(weights)
    unknown = set(weights) - set(axes)
    if missing:
        raise ConfigError(f"{label} is missing weights for: {sorted(missing)}")
    if unknown:
        raise ConfigError(f"{label} has unknown axes: {sorted(unknown)}")

    total = sum(float(v) for v in weights.values())
    if abs(total - 1.0) > 1e-6:
        raise ConfigError(f"{label} weights must sum to 1.0, got {total:.4f}")

    threshold = float(config.get("threshold", 0))
    if not 0 <= threshold <= 10:
        raise ConfigError(f"{label} threshold must be within 0-10, got {threshold}")
    return config


def load_quality_gate(root: Path | None = None) -> dict[str, Any]:
    """Load and validate the direction gate from `config/quality_gate.yaml`.

    Validation is deliberate: a gate whose weights do not sum to 1.0 silently
    rescales every score, which is worse than failing loudly.
    """
    root = root or find_repo_root()
    config = load_yaml(root / "config" / "quality_gate.yaml")
    return _validate_gate(config, AXES, "quality_gate.yaml")


def load_breakdown_gate(root: Path | None = None) -> dict[str, Any]:
    """Load and validate the Stage 0.5 panel-breakdown gate.

    It lives inside `quality_gate.yaml` under `breakdown_gate` so that both gates
    are reviewed in one place, but it is a separate gate with its own axes,
    threshold, and hard-fail rules.
    """
    root = root or find_repo_root()
    config = load_yaml(root / "config" / "quality_gate.yaml")
    gate = config.get("breakdown_gate")
    if not gate:
        raise ConfigError("quality_gate.yaml has no 'breakdown_gate' section")
    gate = dict(gate)
    gate.setdefault("evidence_required_at_or_above", config.get("evidence_required_at_or_above"))
    return _validate_gate(gate, BREAKDOWN_AXES, "breakdown_gate")


def hard_fail_rules(config: dict[str, Any]) -> list[str]:
    """Return hard-fail rule names, accepting either a list or a mapping in the config."""
    rules = config.get("hard_fail_rules") or {}
    if isinstance(rules, dict):
        return sorted(rules)
    return sorted(str(rule) for rule in rules)


def load_direction_modes(root: Path | None = None) -> dict[str, Any]:
    """Load `config/direction_modes.yaml`."""
    root = root or find_repo_root()
    return load_yaml(root / "config" / "direction_modes.yaml")


def load_vocabulary(root: Path | None = None) -> dict[str, Any]:
    """Load `config/direction_vocabulary.yaml`."""
    root = root or find_repo_root()
    return load_yaml(root / "config" / "direction_vocabulary.yaml")
