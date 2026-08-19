# Webtoon Director Harness — Project Instructions

## Objective
Improve **direction quality** — what the reader understands, feels, and looks at, and in what
order — not prose quality and not image-prompt quality. A beautiful panel that lands the reveal one
beat too early is a failure of this repository.

## Core principle
**Do not accept the first plausible direction.** A single generative pass converges on the first
competent staging it finds. This harness forces alternatives to exist, reviews them independently,
synthesizes, validates, and only then hands off.

## Mandatory workflow
1. Read `_workspace/<episode>/00_input/`; normalize to `normalized_input.yaml` if absent.
   **Check for panels.** If `normalized_input.yaml` has no `panels[]`, or a scene carries one or two
   lumped descriptions instead of panel-level ones, run **Stage 0.5** (step 1.5) first. If the input
   already arrives as a cut storyboard, skip it — the cut was made upstream. State which branch you took.
1.5. **Stage 0.5 — panel breakdown** (`story-breakdown` skill, conditional): beat sheet →
   three candidate cuts (dense / economical / spacious) → independent review against `breakdown_gate`
   → selection → `panels[]` written into `normalized_input.yaml`. Panel IDs are frozen at the end
   of this step.
2. **narrative-director** → scene objective, reader emotion arc, reveal order, climax, hook.
3. Fan out **three genuinely different candidates** — Emotional, Cinematic, Webtoon-native —
   generated independently, without seeing each other.
4. **direction-critic** reviews each candidate separately, blind to any preference.
5. **showrunner** synthesizes a spine plus grafts, and records every decision.
6. **dialogue-silence-editor** passes over the synthesis.
7. **continuity-supervisor** validates state and contradictions.
8. Quality gate: below threshold or any hard fail → revise the affected panels and re-review.
9. Export to `06_handoff/` and validate.

## Workspace contract
```
_workspace/<episode>/
  00_input/       normalized_input.yaml, source_handoff.md, layouts/
                  beat_sheet.yaml, breakdown/ (Stage 0.5 only)
  01_analysis/    narrative_analysis.yaml
  02_candidates/  emotional.yaml · cinematic.yaml · webtoon_native.yaml
  03_reviews/     critic_<candidate>.yaml · quality_gate_result.yaml
  04_synthesis/   selected_direction.yaml · decision_log.md · dialogue_pass.yaml
  05_continuity/  continuity_state.yaml · continuity_report.yaml
  06_handoff/     direction_bible.md · panel_direction.yaml · continuity_state.yaml
                  critic_report.md · stage2_handoff.md
```
`_workspace/` is gitignored. Never write episode work outside it, and never edit an upstream stage's
artifact in place — revise it and note the loop number.

## Conventions
- **Panel IDs** are assigned once — upstream, or by Stage 0.5 — and never renumbered. Split a panel as `P05a`, `P05b`; a merge keeps the
  lower ID and records the merge in the decision log.
- **Controlled vocabulary** for shot, angle, transition, and beat duration lives in
  `config/direction_vocabulary.yaml`. Do not invent terms when a listed one fits.
- **Artifacts are YAML**; human-facing summaries are Markdown. Both, not one or the other.
- Every artifact names its `episode_id` and, where relevant, its revision `loop`.

## Rules
- Keep specialist roles distinct. Never merge them into one large prompt — the separation is the
  mechanism, not an organizational nicety.
- Prefer panel-level instructions over scene-level advice. "Raise the tension" is not directable.
- Every major visual decision states its creative purpose.
- Preserve character, prop, location, lighting, and knowledge state explicitly.
- A critic score of 9–10 requires panel-level evidence.
- Never lower the threshold to force a pass; change the direction or record an explicit exception.
- Make outputs file-oriented and traceable — an artifact nobody can diff cannot be reviewed.

## Commands
```bash
python scripts/init_episode.py ep01              # create the workspace skeleton
python scripts/score_direction.py <critic.yaml>  # weighted score + PASS/REVISE
python scripts/score_direction.py <critic.yaml> --gate breakdown   # Stage 0.5 gate
python scripts/validate_artifacts.py _workspace/ep01
python scripts/validate_handoff.py _workspace/ep01/06_handoff
pytest                                           # repo structure and scoring tests
```

## Clean-room boundary
This repository interoperates with external tools through documented file inputs and outputs only.
Do not copy third-party skill packages, prompts, or assets into it, and do not hard-code a single
image model in the direction artifacts — handoff files must stay production-neutral.
