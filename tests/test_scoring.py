"""The quality gate must be arithmetic, not opinion."""

import pytest

from harness.config import AXES, ConfigError, hard_fail_rules
from harness.scoring import evaluate, normalize_scores, weighted_total


def _report(value=8.0, **overrides):
    report = {
        "candidate": "cinematic",
        "scores": {axis: value for axis in AXES},
    }
    report.update(overrides)
    return report


def test_weights_sum_to_one(quality_gate):
    assert sum(quality_gate["weights"].values()) == pytest.approx(1.0)


def test_all_axes_are_weighted(quality_gate):
    assert set(quality_gate["weights"]) == set(AXES)


def test_uniform_scores_yield_that_score(quality_gate):
    result = evaluate(_report(8.0), quality_gate)
    assert result.weighted_total == pytest.approx(8.0)


def test_threshold_decides_the_verdict(quality_gate):
    threshold = quality_gate["threshold"]
    assert evaluate(_report(threshold), quality_gate).verdict == "PASS"
    assert evaluate(_report(threshold - 0.1), quality_gate).verdict == "REVISE"


def test_hard_failure_overrides_a_high_score(quality_gate):
    report = _report(10.0, hard_failures=["broken_scene_continuity"])
    result = evaluate(report, quality_gate)
    assert result.weighted_total == pytest.approx(10.0)
    assert result.verdict == "REVISE"


def test_hard_failures_accept_objects(quality_gate):
    report = _report(9.0, hard_failures=[{"rule": "missing_climax_or_reveal", "panel_id": "P07"}])
    assert "missing_climax_or_reveal" in evaluate(report, quality_gate).hard_failures


def test_unknown_hard_failure_is_flagged(quality_gate):
    result = evaluate(_report(9.0, hard_failures=["made_up_rule"]), quality_gate)
    assert any("unknown rule" in failure for failure in result.hard_failures)


def test_scores_accept_evidence_objects(quality_gate):
    report = {
        "candidate": "emotional",
        "scores": {axis: {"score": 8, "evidence": "P03 carries it."} for axis in AXES},
    }
    assert evaluate(report, quality_gate).weighted_total == pytest.approx(8.0)


def test_top_score_without_evidence_warns(quality_gate):
    result = evaluate(_report(9.5), quality_gate)
    assert result.integrity_warnings
    assert all("evidence" in warning for warning in result.integrity_warnings)


def test_top_score_with_evidence_does_not_warn(quality_gate):
    report = {
        "candidate": "emotional",
        "scores": {axis: {"score": 9.5, "evidence": "P07 earns it."} for axis in AXES},
    }
    assert evaluate(report, quality_gate).integrity_warnings == []


def test_mismatched_reported_total_warns(quality_gate):
    result = evaluate(_report(8.0, weighted_total=9.9), quality_gate)
    assert any("disagrees" in warning for warning in result.integrity_warnings)


def test_missing_axis_is_an_error(quality_gate):
    report = _report()
    report["scores"].pop("continuity")
    with pytest.raises(ConfigError, match="missing scores"):
        evaluate(report, quality_gate)


def test_out_of_range_score_is_rejected():
    with pytest.raises(ConfigError, match="out of range"):
        normalize_scores({"scores": {"narrative_clarity": 11}})


def test_weighted_total_respects_weights(quality_gate):
    scores = {axis: 0.0 for axis in AXES}
    scores["narrative_clarity"] = 10.0
    expected = 10.0 * quality_gate["weights"]["narrative_clarity"]
    assert weighted_total(scores, quality_gate["weights"]) == pytest.approx(expected)


def test_hard_fail_rules_are_named(quality_gate):
    rules = hard_fail_rules(quality_gate)
    assert "broken_scene_continuity" in rules
    assert len(rules) >= 4
