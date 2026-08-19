"""The repository is a prompt artifact as much as a code artifact — verify its shape."""

import pytest

REQUIRED_FILES = [
    ".claude/CLAUDE.md",
    "config/quality_gate.yaml",
    "config/direction_modes.yaml",
    "config/direction_vocabulary.yaml",
    "schemas/panel_direction.schema.yaml",
    "schemas/critic_report.schema.yaml",
    "schemas/narrative_analysis.schema.yaml",
    "schemas/continuity_state.schema.yaml",
    "templates/direction_bible.md",
    "templates/critic_report.md",
    "templates/stage2_handoff.md",
    "scripts/init_episode.py",
    "scripts/score_direction.py",
    "scripts/validate_artifacts.py",
    "scripts/validate_handoff.py",
    "docs/ARCHITECTURE.md",
    "docs/WORKFLOW.md",
    "docs/SCORING.md",
    "docs/AGENTS.md",
    "docs/DIRECTION_LANGUAGE.md",
    "README.md",
    "LICENSE",
    "NOTICE.md",
]

REQUIRED_AGENTS = [
    "showrunner",
    "narrative-director",
    "cinematography-director",
    "emotion-director",
    "pacing-director",
    "dialogue-silence-editor",
    "continuity-supervisor",
    "direction-critic",
]

REQUIRED_SKILLS = ["directors-room", "panel-direction", "continuity-check", "quality-loop"]


@pytest.mark.parametrize("relative", REQUIRED_FILES)
def test_required_project_files_exist(repo_root, relative):
    assert (repo_root / relative).is_file(), relative


@pytest.mark.parametrize("agent", REQUIRED_AGENTS)
def test_agent_file_exists(repo_root, agent):
    assert (repo_root / ".claude" / "agents" / f"{agent}.md").is_file()


@pytest.mark.parametrize("skill", REQUIRED_SKILLS)
def test_skill_file_exists(repo_root, skill):
    assert (repo_root / ".claude" / "skills" / skill / "SKILL.md").is_file()


def test_workspace_is_gitignored_but_kept(repo_root):
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert "_workspace/*" in gitignore
    assert "!_workspace/.gitkeep" in gitignore
    assert (repo_root / "_workspace" / ".gitkeep").exists()
