---
name: directors-room
description: Orchestrates the full direction workflow from storyboard intake to production handoff — normalize, analyze, fan out three candidates, critique independently, synthesize, validate continuity, run the quality gate, and export. Use when the user asks to run the Director's Room, direct an episode, or produce a Stage 2 handoff.
---
# Directors Room

The end-to-end pipeline. Run it whole; skipping the fan-out or the independent review defeats the
purpose of the harness.

## 0. Intake
- Read everything in `_workspace/<episode>/00_input/`.
- If `normalized_input.yaml` is missing, build it from the source handoff and layout files, then
  write it before continuing. Never carry unnormalized input into the pipeline.
- Confirm the panel IDs are stable and sequential (`P01`, `P02`, …). All later artifacts key on them.

**If there are no panels**, the input is prose and the cut has not been made. Run the
`story-breakdown` skill (Stage 0.5) before step 1: beat sheet → three candidate cuts → independent
review against `breakdown_gate` → selection → `panels[]` committed to `normalized_input.yaml`.
Same test applies to a scene carrying one or two lumped descriptions instead of panel-level ones.
If the input already arrives as a cut storyboard, skip Stage 0.5 — the decision was made upstream
and is not yours to redo. Say which branch you took.

## 1. Narrative analysis
Invoke **narrative-director** → `01_analysis/narrative_analysis.yaml`.
Gate: the file must name a single `climax_panel` and a one-sentence `scene_goal`.
Everything downstream is measured against this file, so do not proceed on a vague analysis.

## 2. Fan-out — three candidates
Run the three leads **in parallel and independently**. Do not let one candidate see another; shared
context here is how three options collapse into one.

| Candidate | Lead | Priorities |
|---|---|---|
| `emotional.yaml` | emotion-director | reaction, silence, anticipation, reveal timing |
| `cinematic.yaml` | cinematography-director | shot progression, composition, depth, lighting |
| `webtoon_native.yaml` | pacing-director | scroll rhythm, whitespace, panel height, full-width beats |

Gate: the three must differ in **reveal order, climactic image, or rhythm** — not merely in wording.
If they do not, discard and re-run with sharper mode constraints from `config/direction_modes.yaml`.

## 3. Independent review
Invoke **direction-critic** once per candidate → `03_reviews/critic_<candidate>.yaml`.
Each review is blind to the others and to any preference of the Showrunner.
Gate: every score carries evidence; every problem carries a concrete revision and an owner.

## 4. Synthesis
Invoke **showrunner** → `04_synthesis/selected_direction.yaml` + `decision_log.md`.
Pick a spine, graft the strongest panels from the alternates, and record every graft with its reason.
Then invoke **dialogue-silence-editor** → `04_synthesis/dialogue_pass.yaml` and apply its cuts.

## 5. Continuity validation
Invoke **continuity-supervisor** → `05_continuity/continuity_state.yaml` + `continuity_report.yaml`.
Any `blocking` violation is an automatic hard fail — do not compute a score around it.

## 6. Quality gate
Run the `quality-loop` skill against `config/quality_gate.yaml`.
- **Pass** (weighted >= threshold, no hard failures) → step 7.
- **Fail** → create revision tasks addressed to the owning specialist, re-run only the affected
  artifacts and their reviews, and re-enter this step. Stop at `max_revision_loops` and export the
  best result with its open problems recorded in `critic_report.md`.

```bash
python scripts/score_direction.py _workspace/<episode>/03_reviews/critic_*.yaml
```

## 7. Export
Write to `_workspace/<episode>/06_handoff/`:

| File | Source |
|---|---|
| `direction_bible.md` | `templates/direction_bible.md` filled from synthesis |
| `panel_direction.yaml` | `selected_direction.yaml` conformed to the schema |
| `continuity_state.yaml` | copied from `05_continuity/` |
| `critic_report.md` | `templates/critic_report.md` filled from the final review |
| `stage2_handoff.md` | `templates/stage2_handoff.md` |

Validate before declaring completion:

```bash
python scripts/validate_handoff.py _workspace/<episode>/06_handoff
python scripts/validate_artifacts.py _workspace/<episode>
```

## 8. Optional — Stage 3 render
The handoff is production-neutral and complete on its own. If the user wants images, the
`panel-render` skill renders them locally and free with ComfyUI: prompts, reference sheets first,
then panels with a validate-and-re-render loop, then lettering. Offer it; do not start it
unprompted, because it costs GPU hours.

## Reporting
Close with: selected approach and why, weighted score and loop count, grafts from alternate
candidates, unresolved continuity items, and the top production risk.
