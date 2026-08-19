"""The worked example is the repository's definition of "good enough to ship".

If it stops validating, either the example rotted or the contract changed — both matter.
"""

import pytest
import yaml

from harness.artifacts import (
    REQUIRED_HANDOFF_FILES,
    iter_artifacts,
    missing_handoff_files,
    validate_artifact,
)
from harness.config import load_yaml
from harness.scoring import evaluate


@pytest.fixture(scope="module")
def example_dir(repo_root):
    return repo_root / "examples" / "sample_episode"


def test_example_covers_every_stage(example_dir):
    for stage in ("01_analysis", "02_candidates", "03_reviews", "04_synthesis",
                  "05_continuity", "06_handoff"):
        assert (example_dir / stage).is_dir(), stage


def test_example_artifacts_validate(example_dir):
    artifacts = list(iter_artifacts(example_dir))
    assert len(artifacts) >= 8
    problems = []
    for path in artifacts:
        problems += [
            f"{path.name}: {issue.message}"
            for issue in validate_artifact(path)
            if issue.level == "error"
        ]
    assert not problems, problems


def test_example_handoff_is_complete(example_dir):
    assert missing_handoff_files(example_dir / "06_handoff") == []


def test_example_handoff_has_no_unfilled_placeholders(example_dir):
    for name in REQUIRED_HANDOFF_FILES:
        text = (example_dir / "06_handoff" / name).read_text(encoding="utf-8")
        assert "{{" not in text, name


def test_three_candidates_exist(example_dir):
    candidates = sorted(p.name for p in (example_dir / "02_candidates").glob("*.yaml"))
    assert candidates == ["cinematic.yaml", "emotional.yaml", "webtoon_native.yaml"]


def test_candidates_actually_diverge(example_dir):
    """The fan-out is worthless if the candidates agree on rhythm."""
    profiles = {}
    for path in (example_dir / "02_candidates").glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        profiles[path.stem] = [p.get("beat_duration") for p in data["panels"]]
    assert len(set(map(tuple, profiles.values()))) == 3, profiles


def test_reported_scores_match_computed(example_dir, quality_gate):
    for path in (example_dir / "03_reviews").glob("critic_*.yaml"):
        result = evaluate(load_yaml(path), quality_gate)
        assert result.integrity_warnings == [], f"{path.name}: {result.integrity_warnings}"


def test_synthesis_passes_and_candidates_did_not(example_dir, quality_gate):
    reviews = {
        path.stem: evaluate(load_yaml(path), quality_gate)
        for path in (example_dir / "03_reviews").glob("critic_*.yaml")
    }
    assert reviews["critic_synthesis"].passed
    for name, result in reviews.items():
        if name != "critic_synthesis":
            assert not result.passed, f"{name} should have needed revision"


def test_synthesis_beats_every_candidate(example_dir, quality_gate):
    reviews = {
        path.stem: evaluate(load_yaml(path), quality_gate).weighted_total
        for path in (example_dir / "03_reviews").glob("critic_*.yaml")
    }
    synthesis = reviews.pop("critic_synthesis")
    assert synthesis > max(reviews.values())


def test_gate_result_matches_the_reviews(example_dir, quality_gate):
    gate = load_yaml(example_dir / "03_reviews" / "quality_gate_result.yaml")
    computed = evaluate(load_yaml(example_dir / "03_reviews" / "critic_synthesis.yaml"), quality_gate)
    assert gate["weighted_total"] == pytest.approx(computed.weighted_total, abs=0.01)
    assert gate["verdict"] == computed.verdict


def test_selected_direction_records_its_grafts(example_dir):
    data = load_yaml(example_dir / "04_synthesis" / "selected_direction.yaml")
    grafts = {p.get("grafted_from") for p in data["panels"]}
    assert grafts >= {"emotional", "cinematic", "webtoon_native"}, (
        "synthesis should take from all three candidates"
    )


def test_handoff_matches_the_synthesis(example_dir):
    synthesis = load_yaml(example_dir / "04_synthesis" / "selected_direction.yaml")
    handoff = load_yaml(example_dir / "06_handoff" / "panel_direction.yaml")
    assert synthesis == handoff, "handoff must be exported from the synthesis, not re-authored"


def test_continuity_report_has_no_blocking_violations(example_dir):
    report = load_yaml(example_dir / "05_continuity" / "continuity_report.yaml")
    assert report["summary"]["blocking"] == 0
    assert report["summary"]["unresolved_major"] == 0
