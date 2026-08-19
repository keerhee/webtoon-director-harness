from pathlib import Path
import sys
SUBDIRS = ["00_input/layouts","01_analysis","02_candidates","03_reviews","04_synthesis","05_continuity","06_handoff"]
episode = sys.argv[1] if len(sys.argv)>1 else "ep01"
root = Path("_workspace") / episode
for sub in SUBDIRS: (root/sub).mkdir(parents=True, exist_ok=True)
print(f"Created episode workspace: {root}")
