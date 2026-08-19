# Workflow

Ten steps, each producing a file. A step that produces no artifact did not happen.
Step 0.5 is conditional; every other step always runs.

| # | Step | Agent | Output | Gate before moving on |
|---:|---|---|---|---|
| 0 | Intake & normalize | — | `00_input/normalized_input.yaml` | Panel IDs stable and sequential |
| 0.5 | **Panel breakdown** *(only if the input is prose)* | breakdown-director | `00_input/beat_sheet.yaml`, `00_input/breakdown/` | Selected cut committed as `panels[]`; IDs frozen |
| 1 | Narrative analysis | narrative-director | `01_analysis/narrative_analysis.yaml` | One-sentence scene goal, a single climax panel |
| 2 | Fan-out ×3 | emotion / cinematography / pacing | `02_candidates/*.yaml` | Candidates differ in ≥2 divergence axes |
| 3 | Independent review | direction-critic ×3 | `03_reviews/critic_*.yaml` | Every score has evidence; every problem has a fix and an owner |
| 4 | Synthesis | showrunner | `04_synthesis/selected_direction.yaml`, `decision_log.md` | Every graft recorded with a reason |
| 5 | Dialogue pass | dialogue-silence-editor | `04_synthesis/dialogue_pass.yaml` | Balloon order unambiguous on every panel |
| 6 | Continuity | continuity-supervisor | `05_continuity/*.yaml` | Zero blocking violations |
| 7 | Quality gate | quality-loop | `03_reviews/quality_gate_result.yaml` | Weighted ≥ threshold, no hard failures |
| 8 | Export | showrunner | `06_handoff/` (5 files) | `validate_handoff.py` passes |

## Stage 0.5 - when it runs

Checked at intake, automatically:

| Input state | Action |
|---|---|
| No `panels[]` | Run Stage 0.5 |
| A scene carries 1-2 lumped descriptions for a whole sequence | Run Stage 0.5 for that scene |
| Every scene has panel-level descriptions | Skip - the cut was made upstream |

The stage generates three cuts (`dense` / `economical` / `spacious`), reviews each against the
four-axis `breakdown_gate` (threshold 8.0, one revision loop), selects and grafts, then writes
`panels[]` into `normalized_input.yaml`. Panel IDs are frozen at the end of it.

```bash
python scripts/score_direction.py _workspace/ep01/00_input/breakdown/critic_*.yaml --gate breakdown
```

Why a separate, lower gate: a breakdown does not need to be beautiful, it needs to leave every later
stage room to work. Over-tuning the cut spends revision budget the direction stages need more.

## Divergence check (after step 2)

Compare the three candidates on `reveal_order`, `climactic_image`, and `rhythm_profile`. At least
two axes must differ. Candidates that agree on all three are one candidate written three ways —
discard them and re-run with the mode constraints in `config/direction_modes.yaml` applied harder.

## Revision loop (steps 6–7)

```text
gate fails ──▶ revision tasks (panel IDs + axis + fix + owner)
           ──▶ re-run ONLY the affected candidate sections
           ──▶ re-review those sections
           ──▶ re-run continuity
           ──▶ gate again        (max_revision_loops, default 3)
```

Never regenerate the whole episode to fix three panels; you will lose the parts that already worked.
If a loop improves the weighted total by less than `min_improvement_per_loop`, the problem is
upstream — go back to the narrative analysis rather than polishing panels.

## Commands

```bash
python scripts/init_episode.py ep01                       # workspace skeleton
python scripts/init_episode.py demo --from-example        # seeded from the sample episode
python scripts/score_direction.py _workspace/ep01/03_reviews/critic_*.yaml
python scripts/validate_artifacts.py _workspace/ep01
python scripts/validate_handoff.py _workspace/ep01/06_handoff
```

## Worked example

`examples/sample_episode/` carries a complete run of all ten steps for a seven-panel scene.
Stage 0.5 lives in `00_input/`: a seven-beat sheet, three cuts at 11 / 5 / 7 panels
(7.75 / 6.05 / 8.60 - `economical` hard-fails on `reveal_collision`), and the selection note.
Then the direction stages:
three divergent candidates, three independent reviews (7.60 / 7.85 / 8.20 — all `revise`), a
synthesis that grafts from all three and scores 8.85, a continuity pass, and the exported handoff.
Read it before running your first episode; it is the repository's definition of "good enough to ship".
