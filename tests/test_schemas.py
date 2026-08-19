"""Schemas are the contract between stages — they must themselves be valid."""

import pytest
import yaml

from harness.artifacts import check_panel_ids, check_vocabulary, schema_for
from harness.config import load_vocabulary

SCHEMA_FILES = [
    "panel_direction.schema.yaml",
    "critic_report.schema.yaml",
    "narrative_analysis.schema.yaml",
    "continuity_state.schema.yaml",
]


@pytest.mark.parametrize("name", SCHEMA_FILES)
def test_schema_is_valid_json_schema(repo_root, name):
    jsonschema = pytest.importorskip("jsonschema")
    schema = yaml.safe_load((repo_root / "schemas" / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def test_schema_routing():
    from pathlib import Path

    assert schema_for(Path("cinematic.yaml")) == "panel_direction.schema.yaml"
    assert schema_for(Path("critic_emotional.yaml")) == "critic_report.schema.yaml"
    assert schema_for(Path("decision_log.md")) is None


def test_panel_schema_matches_vocabulary(repo_root):
    """A term allowed by the schema but absent from the vocabulary would be unusable."""
    schema = yaml.safe_load(
        (repo_root / "schemas" / "panel_direction.schema.yaml").read_text(encoding="utf-8")
    )
    panel = schema["properties"]["panels"]["items"]["properties"]
    vocab = load_vocabulary(repo_root)

    assert set(panel["shot"]["enum"]) == set(vocab["shot"])
    assert set(panel["angle"]["enum"]) == set(vocab["angle"])
    assert set(panel["transition"]["enum"]) == set(vocab["transition"])
    assert set(panel["beat_duration"]["enum"]) == set(vocab["beat_duration"])
    assert set(panel["dramatic_function"]["enum"]) == set(vocab["dramatic_function"])


def test_duplicate_panel_ids_are_caught(tmp_path):
    data = {"panels": [{"panel_id": "P01"}, {"panel_id": "P01"}]}
    issues = check_panel_ids(data, tmp_path / "x.yaml")
    assert any("duplicate" in issue.message for issue in issues)


def test_malformed_panel_id_is_caught(tmp_path):
    issues = check_panel_ids({"panels": [{"panel_id": "panel-1"}]}, tmp_path / "x.yaml")
    assert any("malformed" in issue.message for issue in issues)


def test_free_text_shot_is_caught(repo_root, tmp_path):
    data = {"panels": [{"panel_id": "P01", "shot": "epic_hero_shot", "purpose": "x" * 10}]}
    issues = check_vocabulary(data, tmp_path / "x.yaml", repo_root)
    assert any("not in the vocabulary" in issue.message for issue in issues)


def test_missing_purpose_is_caught(repo_root, tmp_path):
    data = {"panels": [{"panel_id": "P01", "shot": "wide"}]}
    issues = check_vocabulary(data, tmp_path / "x.yaml", repo_root)
    assert any("missing purpose" in issue.message for issue in issues)
