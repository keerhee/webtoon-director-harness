"""Agent and skill files are loaded by frontmatter — a typo there silently disables them."""

import re

import pytest
import yaml

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _load(path):
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    assert match, f"{path.name} has no YAML frontmatter"
    return yaml.safe_load(match.group(1)), text[match.end():]


def _agent_files(repo_root):
    return sorted((repo_root / ".claude" / "agents").glob("*.md"))


def _skill_files(repo_root):
    return sorted((repo_root / ".claude" / "skills").glob("*/SKILL.md"))


def test_agents_are_discovered(repo_root):
    assert len(_agent_files(repo_root)) == 9


def test_agent_frontmatter_is_valid(repo_root):
    for path in _agent_files(repo_root):
        meta, body = _load(path)
        assert meta.get("name") == path.stem, f"{path.name}: name must match the filename"
        description = meta.get("description", "")
        assert len(description) >= 40, f"{path.name}: description is too thin to route on"
        assert len(body.split()) >= 120, f"{path.name}: body is a stub, not an operating prompt"


def test_agents_share_the_team_protocol(repo_root):
    for path in _agent_files(repo_root):
        body = path.read_text(encoding="utf-8")
        assert "## Team protocol" in body, path.name
        assert "P01" in body, f"{path.name}: must state the panel ID convention"


def test_skill_frontmatter_is_valid(repo_root):
    for path in _skill_files(repo_root):
        meta, body = _load(path)
        assert meta.get("name") == path.parent.name, f"{path}: name must match the directory"
        assert len(meta.get("description", "")) >= 40, f"{path}: description is too thin"
        assert len(body.split()) >= 100, f"{path}: body is a stub"


@pytest.mark.parametrize(
    "term", ["shot", "angle", "transition", "beat_duration", "dramatic_function"]
)
def test_vocabulary_terms_are_documented(repo_root, term):
    doc = (repo_root / "docs" / "DIRECTION_LANGUAGE.md").read_text(encoding="utf-8")
    assert term in doc
