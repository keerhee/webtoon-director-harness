---
name: quality-loop
description: Runs weighted scoring, hard-fail checks, and bounded revision loops against the quality gate config. Use after synthesis and continuity validation, and again after each revision, to decide whether the direction ships or goes back.
---
# Quality Loop

The gate exists to catch directions that are competent but unremarkable, and to stop revision from
running forever. It is a debugging instrument, not a replacement for the Showrunner's judgment.

## Procedure
1. **Load** `config/quality_gate.yaml` — weights, threshold, `max_revision_loops`, hard-fail rules.
2. **Score** the current direction on the six axes, with evidence per axis.
3. **Compute** the weighted total:
   ```bash
   python scripts/score_direction.py _workspace/<episode>/03_reviews/critic_selected.yaml
   ```
4. **Check hard failures.** Any hard failure forces `REVISE` regardless of the weighted total.
   A `blocking` continuity violation is a hard failure.
5. **Decide.**
   - `PASS` → export the handoff package.
   - `REVISE` → step 6.
6. **Create revision tasks.** Each task names: panel IDs, the axis that failed, the concrete change,
   and the owning specialist. Tasks without an owner do not get done.
7. **Re-run only what changed** — the affected candidate sections, then their reviews, then
   continuity. Do not regenerate the whole episode; you will lose the parts that already worked.
8. **Loop**, up to `max_revision_loops`.

## When the loop is exhausted
Do not silently ship. Export the best available direction and record, in `critic_report.md`:
the final score, which axes are still below bar, the specific unresolved problems, and a
recommendation — accept as-is, escalate to a human director, or re-run from the fan-out with a
different creative premise.

## Diminishing returns
If a loop improves the weighted total by less than ~0.2, the problem is usually upstream: the scene
goal, the reveal order, or the choice of spine. Go back to the narrative analysis rather than
polishing panels.

## Score integrity
- Scores of 9–10 require panel-level evidence.
- A score that rises without a corresponding change to the artifact is invalid — re-score.
- Never lower the threshold to make a direction pass. Change the direction, or record the exception
  explicitly in the decision log.

## Output
`03_reviews/quality_gate_result.yaml`:
```yaml
loop: 2
weighted_total: 8.72
threshold: 8.5
hard_failures: []
verdict: PASS
delta_from_previous: 0.41
unresolved: [{panel_id: P06, axis: pacing_scroll, severity: minor, note: "..."}]
```
