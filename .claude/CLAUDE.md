# Webtoon Director Harness — Project Instructions

## Objective
Improve **direction quality**, not merely prose or image-prompt quality.

## Mandatory workflow
1. Read `_workspace/<episode>/00_input/`.
2. Normalize scene and panel information.
3. Narrative Director defines scene objective, reader emotion arc, reveal order, climax/hook.
4. Generate three genuinely different candidates: Emotional, Cinematic, Webtoon-native.
5. Direction Critic reviews each candidate independently.
6. Showrunner synthesizes the strongest elements into one coherent direction.
7. Continuity Supervisor validates state and contradictions.
8. If score < threshold or a hard-fail triggers, revise and re-review.
9. Export final files to `06_handoff/`.

## Rules
- Keep specialist roles distinct.
- Never select the first plausible direction without alternatives.
- Prefer panel-level instructions over vague advice.
- Every major visual decision should state its creative purpose.
- Preserve character/location/prop state explicitly.
- Make outputs file-oriented and traceable.
