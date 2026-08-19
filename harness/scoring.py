"""Weighted scoring and the pass/revise decision.

The gate is deliberately simple and deterministic. Its job is not to judge taste but
to make two things impossible to fudge: an unevidenced top score, and a direction that
ships with a hard failure open.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from harness.config import ConfigError, hard_fail_rules


@dataclass
class ScoreResult:
    """Outcome of evaluating one critic report against the quality gate."""

    candidate: str
    scores: dict[str, float]
    weighted_total: float
    threshold: float
    hard_failures: list[str] = field(default_factory=list)
    integrity_warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.weighted_total >= self.threshold and not self.hard_failures

    @property
    def verdict(self) -> str:
        return "PASS" if self.passed else "REVISE"

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate,
            "scores": self.scores,
            "weighted_total": round(self.weighted_total, 3),
            "threshold": self.threshold,
            "hard_failures": self.hard_failures,
            "integrity_warnings": self.integrity_warnings,
            "verdict": self.verdict,
        }


def _axis_value(raw: Any) -> tuple[float, str | None]:
    """Accept either `8` or `{score: 8, evidence: "..."}` and return (score, evidence)."""
    if isinstance(raw, dict):
        if "score" not in raw:
            raise ConfigError(f"Score entry has no 'score' key: {raw!r}")
        return float(raw["score"]), raw.get("evidence")
    return float(raw), None


def normalize_scores(report: dict[str, Any]) -> tuple[dict[str, float], dict[str, str | None]]:
    """Split a report's `scores` block into plain floats and their evidence."""
    raw_scores = report.get("scores") or {}
    if not isinstance(raw_scores, dict):
        raise ConfigError("'scores' must be a mapping of axis -> score")

    scores: dict[str, float] = {}
    evidence: dict[str, str | None] = {}
    for axis, raw in raw_scores.items():
        value, note = _axis_value(raw)
        if not 0 <= value <= 10:
            raise ConfigError(f"Score for '{axis}' out of range 0-10: {value}")
        scores[axis] = value
        evidence[axis] = note
    return scores, evidence


def weighted_total(scores: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted sum over the configured axes. Missing axes are an error, not a zero."""
    missing = set(weights) - set(scores)
    if missing:
        raise ConfigError(f"Report is missing scores for: {sorted(missing)}")
    return sum(scores[axis] * float(weight) for axis, weight in weights.items())


def _normalize_failures(report: dict[str, Any], known: list[str]) -> list[str]:
    failures = []
    for item in report.get("hard_failures") or []:
        rule = item.get("rule") if isinstance(item, dict) else item
        rule = str(rule)
        if known and rule not in known:
            rule = f"{rule} (unknown rule)"
        failures.append(rule)
    return failures


def evaluate(report: dict[str, Any], config: dict[str, Any]) -> ScoreResult:
    """Score one critic report against the gate config."""
    scores, evidence = normalize_scores(report)
    weights = config["weights"]
    total = weighted_total(scores, weights)

    failures = _normalize_failures(report, hard_fail_rules(config))

    warnings: list[str] = []
    evidence_floor = config.get("evidence_required_at_or_above")
    if evidence_floor is not None:
        for axis in weights:
            if scores.get(axis, 0) >= float(evidence_floor) and not evidence.get(axis):
                warnings.append(
                    f"{axis}: score {scores[axis]:g} requires panel-level evidence"
                )

    stated = report.get("weighted_total")
    if stated is not None and abs(float(stated) - total) > 0.05:
        warnings.append(
            f"reported weighted_total {float(stated):.2f} disagrees with computed {total:.2f}"
        )

    return ScoreResult(
        candidate=str(report.get("candidate", "unnamed")),
        scores=scores,
        weighted_total=total,
        threshold=float(config["threshold"]),
        hard_failures=failures,
        integrity_warnings=warnings,
    )
