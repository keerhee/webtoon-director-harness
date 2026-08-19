---
name: quality-loop
description: Runs weighted scoring, hard-fail checks, and bounded revision loops.
---
# Quality Loop
1. Load quality-gate config.
2. Compute weighted score.
3. Check hard fails.
4. Pass -> export.
5. Fail -> create revision tasks, assign specialists, re-review changed artifacts.
6. Stop at `max_revision_loops`.
