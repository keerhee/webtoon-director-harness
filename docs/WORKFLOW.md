# Workflow

Nine steps, each producing a file. A step that produces no artifact did not happen.

| # | Step | Agent | Output | Gate before moving on |
|---:|---|---|---|---|
| 0 | Intake & normalize | — | `00_input/normalized_input.yaml` | Panel IDs stable and sequential |
| 1 | Narrative analysis | narrative-director | `01_analysis/narrative_analysis.yaml` | One-sentence scene goal, a single climax panel |
| 2 | Fan-out ×3 | emotion / cinematography / pacing | `02_candidates/*.yaml` | Candidates differ in ≥2 divergence axes |
| 3 | Independent review | direction-critic ×3 | `03_reviews/critic_*.yaml` | Every score has evidence; every problem has a fix and an owner |
| 4 | Synthesis | showrunner | `04_synthesis/selected_direction.yaml`, `decision_log.md` | Every graft recorded with a reason |
| 5 | Dialogue pass | dialogue-silence-editor | `04_synthesis/dialogue_pass.yaml` | Balloon order unambiguous on every panel |
| 6 | Continuity | continuity-supervisor | `05_continuity/*.yaml` | Zero blocking violations |
| 7 | Quality gate | quality-loop | `03_reviews/quality_gate_result.yaml` | Weighted ≥ threshold, no hard failures |
| 8 | Export | showrunner | `06_handoff/` (5 files) | `validate_handoff.py` passes |

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

`examples/sample_episode/` carries a complete run of all nine steps for a seven-panel scene:
three divergent candidates, three independent reviews (7.60 / 7.85 / 8.20 — all `revise`), a
synthesis that grafts from all three and scores 8.85, a continuity pass, and the exported handoff.
Read it before running your first episode; it is the repository's definition of "good enough to ship".
