from pathlib import Path
import sys
REQUIRED=["direction_bible.md","panel_direction.yaml","continuity_state.yaml","critic_report.md","stage2_handoff.md"]
target=Path(sys.argv[1]) if len(sys.argv)>1 else Path("_workspace/ep01/06_handoff")
missing=[x for x in REQUIRED if not (target/x).exists()]
if missing:
    print("Handoff validation: FAIL")
    [print("  missing:",x) for x in missing]
    raise SystemExit(1)
print("Handoff validation: PASS")
