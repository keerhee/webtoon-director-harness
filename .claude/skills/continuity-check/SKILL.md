---
name: continuity-check
description: Validates panel-to-panel character, costume, prop, geography, lighting, timeline, camera-axis, and knowledge state, and reports violations with severity and fixes. Use after synthesis, after every revision loop, and before any handoff export.
---
# Continuity Check

Continuity is the cheapest quality axis to verify and the most expensive to fix after art is drawn.
Run it before the handoff, every time.

## Procedure
1. **Build forward state.** Start at the first panel and construct the scene state. Never revise the
   state backwards to make a later panel legal — that is how contradictions get laundered.
2. **Diff each panel against the previous one.** Every change must be caused by a shown action or by
   an ellipsis the direction explicitly declares.
3. **Classify every difference** using the taxonomy below.
4. **Assign severity** — `blocking`, `major`, `minor`.
5. **Write both outputs**: machine-readable state, and a report of violations with concrete fixes
   addressed to the owning specialist.
6. **Re-run after every revision.** Fixes routinely introduce new violations.

## Taxonomy
| Type | Checks |
|---|---|
| `identity` | Is each character unambiguously recognizable in every panel they appear in? |
| `costume` | Clothing, accessories, lanyards, bandages — including damage acquired mid-scene |
| `prop` | Where each object is, who holds it, when it moved |
| `geography` | Room layout, door and exit positions, relative distances |
| `action_direction` | Movement vector consistency across cuts |
| `eyeline` | Who looks at whom, and whether the eyelines match across a cut |
| `camera_axis` | The 180-degree line; unannounced crossings |
| `lighting` | Source direction and intensity versus the named source |
| `timeline` | Elapsed time consistent with the pacing labels and with stated clock times |
| `knowledge_state` | No character acts on information they have not yet received |

## Severity
- **blocking** — the reader cannot form a coherent picture, or a character is unidentifiable.
  Triggers the `broken_scene_continuity` / `character_identity_mismatch` hard fail.
- **major** — an attentive reader is pulled out of the scene.
- **minor** — production can silently correct it.

## Output
`05_continuity/continuity_state.yaml` and `05_continuity/continuity_report.yaml`, plus a short human
summary: counts by severity, the single most dangerous violation, and any assumption you had to make
because the source was silent.

## Common misses
- Knowledge state — checked last, if at all, and the most damaging when wrong.
- Light direction after a new source is introduced mid-scene.
- Props that appear in a reaction shot but were never established in a wide.
- Elapsed time contradicted by a `long_hold` on an instantaneous action.
