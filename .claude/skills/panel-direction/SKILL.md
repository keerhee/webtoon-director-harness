---
name: panel-direction
description: Converts dramatic intent into precise, production-ready panel-level visual direction with a controlled vocabulary. Use when drafting or revising any candidate, or when a panel description is too vague for an artist or an image model to execute.
---
# Panel Direction

A panel direction is executable when two different artists would produce recognizably the same
staging from it. Anything less is a mood note.

## Required fields per panel

| Field | Meaning |
|---|---|
| `panel_id` | Stable ID (`P01`). Never renumber; split as `P05a`, `P05b`. |
| `dramatic_function` | What this panel does for the scene: setup / escalate / reveal / react / transition / payoff |
| `shot` | From the vocabulary — `wide`, `medium`, `close`, `insert`, `over_shoulder`, … |
| `angle` | `eye_level`, `high`, `low`, `dutch`, `birds_eye`, `worms_eye`, `profile`, `back` |
| `composition` | Where the subject sits in frame, and what the negative space is doing |
| `character_blocking` | Who is where, facing which way, at what distance |
| `gaze` | Where each character looks, and where the reader's eye enters and exits |
| `foreground` / `background` | The other two planes; use them for depth and framing |
| `lighting` | Key direction, contrast, and what the shadow conceals |
| `dialogue_space` | Reserved balloon area, so text never covers the subject |
| `beat_duration` | `instant` · `short` · `medium` · `hold` · `long_hold` |
| `whitespace_before` / `whitespace_after` | Gap multipliers — anticipation and resonance |
| `transition` | How this panel connects to the next |
| `purpose` | One line: the story, emotion, rhythm, or readability reason |

## Rules
1. **Purpose is mandatory.** If the only reason for a choice is that it looks good, cut it or
   replace it with a choice that also carries meaning.
2. **Use the controlled vocabulary** in `config/direction_vocabulary.yaml`. Free-text shot names
   break scoring, diffing, and downstream production.
3. **One idea per panel.** A panel doing two jobs usually needs to be two panels.
4. **Write what is visible.** "She feels betrayed" is not directable; "her hand stops halfway to
   the card" is.
5. **Reserve dialogue space at staging time,** not after composition is final.
6. **Escalation is finite.** The most extreme framing, the longest hold, and the only full-width
   panel belong to the climax. Spend them once.
7. **Name the transition,** especially across a time skip — an unmarked skip reads as an error.

## Validation
```bash
python scripts/validate_artifacts.py _workspace/<episode>
```
Checks required fields, vocabulary conformance, panel ID uniqueness and ordering.

## Worked example
```yaml
- panel_id: P05
  dramatic_function: reveal
  shot: insert
  angle: high
  composition: "Card off-center bottom-right; upper two-thirds empty floor."
  character_blocking: "Mina out of frame; only her shadow reaches the card's edge."
  gaze: "Reader enters top-left along the shadow, exits on the card."
  foreground: "Grain of the floor, slightly out of focus."
  background: "Darkness; no depth cue — the room stops mattering."
  lighting: "Blue pulse from the north alcove, raking across the card's face."
  dialogue_space: "None. Silent panel."
  beat_duration: hold
  whitespace_before: 1.5
  whitespace_after: 2.0
  transition: subject_to_subject
  purpose: "Let the reader recognize the card one beat before Mina does."
```
