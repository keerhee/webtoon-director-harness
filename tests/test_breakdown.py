"""Stage 0.5 - panel breakdown.

The cut is the most irreversible decision in the pipeline, so its gate gets the same
arithmetic guarantees as the direction gate.
"""

import pytest
import yaml

from harness.artifacts import schema_for, validate_artifact
from harness.config import BREAKDOWN_AXES, ConfigError, hard_fail_rules, load_breakdown_gate
from harness.config import load_yaml
from harness.scoring import evaluate


@pytest.fixture(scope="module")
def breakdown_gate(repo_root):
    return load_breakdown_gate(repo_root)


@pytest.fixture(scope="module")
def breakdown_dir(repo_root):
    return repo_root / "examples" / "sample_episode" / "00_input" / "breakdown"


def test_breakdown_weights_sum_to_one(breakdown_gate):
    assert sum(breakdown_gate["weights"].values()) == pytest.approx(1.0)
    assert set(breakdown_gate["weights"]) == set(BREAKDOWN_AXES)


def test_breakdown_threshold_is_lower_than_direction(breakdown_gate, quality_gate):
    """The cut must leave room to work, not be polished into a deliverable."""
    assert breakdown_gate["threshold"] < quality_gate["threshold"]


def test_breakdown_hard_fail_rules_are_named(breakdown_gate):
    rules = hard_fail_rules(breakdown_gate)
    assert {"beat_without_panel", "reveal_collision", "no_climax_panel"} <= set(rules)


def test_breakdown_gate_rejects_direction_axes(breakdown_gate):
    report = {"candidate": "x", "scores": {"narrative_clarity": 9, "emotional_impact": 9}}
    with pytest.raises(ConfigError, match="missing scores"):
        evaluate(report, breakdown_gate)


def test_agent_and_skill_exist(repo_root):
    assert (repo_root / ".claude" / "agents" / "breakdown-director.md").is_file()
    assert (repo_root / ".claude" / "skills" / "story-breakdown" / "SKILL.md").is_file()


def test_stage_is_wired_into_the_always_loaded_workflow(repo_root):
    """A stage that only exists as a file is a stage the user has to ask for every time."""
    claude_md = (repo_root / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "story-breakdown" in claude_md
    assert "Stage 0.5" in claude_md

    directors_room = (
        repo_root / ".claude" / "skills" / "directors-room" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "story-breakdown" in directors_room


def test_schema_routing_for_breakdown(breakdown_dir):
    assert schema_for(breakdown_dir / "spacious.yaml") == "panel_breakdown.schema.yaml"
    assert schema_for(breakdown_dir / "critic_spacious.yaml") == "critic_report.schema.yaml"


def test_breakdown_schemas_are_valid(repo_root):
    jsonschema = pytest.importorskip("jsonschema")
    for name in ("panel_breakdown.schema.yaml", "beat_sheet.schema.yaml"):
        schema = yaml.safe_load((repo_root / "schemas" / name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)


def test_beat_sheet_uses_beat_ids_not_panel_ids(repo_root):
    """Panel IDs here would pre-commit the cut the three candidates are supposed to disagree about."""
    sheet = load_yaml(
        repo_root / "examples" / "sample_episode" / "00_input" / "beat_sheet.yaml"
    )
    assert [b["id"] for b in sheet["beats"]] == [f"B{i:02d}" for i in range(1, 8)]
    assert not sheet["climactic_moment"].strip().startswith("P")


def test_example_breakdown_candidates_validate(breakdown_dir):
    problems = []
    for name in ("dense.yaml", "economical.yaml", "spacious.yaml"):
        problems += [
            f"{name}: {issue.message}"
            for issue in validate_artifact(breakdown_dir / name)
            if issue.level == "error"
        ]
    assert not problems, problems


def test_candidates_differ_in_panel_count(breakdown_dir):
    counts = {
        name: len(load_yaml(breakdown_dir / f"{name}.yaml")["panels"])
        for name in ("dense", "economical", "spacious")
    }
    assert len(set(counts.values())) == 3, counts


def test_every_beat_has_a_panel_in_the_selected_cut(repo_root, breakdown_dir):
    sheet = load_yaml(
        repo_root / "examples" / "sample_episode" / "00_input" / "beat_sheet.yaml"
    )
    cut = load_yaml(breakdown_dir / "spacious.yaml")
    covered = {p.get("beat_ref") for p in cut["panels"]}
    assert {b["id"] for b in sheet["beats"]} <= covered


def test_no_panel_carries_two_reveals(breakdown_dir):
    for name in ("dense", "spacious"):
        for panel in load_yaml(breakdown_dir / f"{name}.yaml")["panels"]:
            reveal = panel.get("carries_reveal")
            if reveal:
                assert " and " not in reveal.lower(), f"{name} {panel['panel_id']}: {reveal}"


def test_selected_cut_wins_and_the_others_do_not(breakdown_dir, breakdown_gate):
    results = {
        path.stem: evaluate(load_yaml(path), breakdown_gate)
        for path in breakdown_dir.glob("critic_*.yaml")
    }
    assert results["critic_spacious"].passed
    assert not results["critic_dense"].passed
    assert not results["critic_economical"].passed
    assert "reveal_collision" in results["critic_economical"].hard_failures


def test_breakdown_reviews_have_no_integrity_warnings(breakdown_dir, breakdown_gate):
    for path in breakdown_dir.glob("critic_*.yaml"):
        result = evaluate(load_yaml(path), breakdown_gate)
        assert result.integrity_warnings == [], f"{path.name}: {result.integrity_warnings}"


def test_committed_input_matches_the_selected_cut(repo_root, breakdown_dir):
    """The cut that won must be the cut that ships into normalized_input.yaml."""
    selected = load_yaml(breakdown_dir / "spacious.yaml")
    normalized = load_yaml(
        repo_root / "examples" / "sample_episode" / "00_input" / "normalized_input.yaml"
    )
    committed = [p["panel_id"] for scene in normalized["scenes"] for p in scene["panels"]]
    assert committed == [p["panel_id"] for p in selected["panels"]]
