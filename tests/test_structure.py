from pathlib import Path

def test_required_project_files_exist():
    required=[".claude/CLAUDE.md",".claude/agents/showrunner.md",".claude/agents/direction-critic.md",".claude/skills/directors-room/SKILL.md","config/quality_gate.yaml","templates/direction_bible.md","scripts/init_episode.py"]
    for item in required: assert Path(item).exists(), item
