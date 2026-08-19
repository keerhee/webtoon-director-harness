# Direction Language

The controlled vocabulary in `config/direction_vocabulary.yaml`. Free-text terms break scoring,
diffing, and downstream production — a direction that says "epic hero shot" cannot be validated,
compared across loops, or executed the same way twice.

Extend the vocabulary deliberately, in the config file, with a definition. Never invent a term
inside an artifact.

## `shot` — how much of the subject is in frame

| Term | Reads as |
|---|---|
| `extreme_wide` | Environment dominates. Place, or isolation. |
| `wide` | Full figure with context. Geography and blocking are readable. |
| `full` | Head to feet, minimal context. Body language is the subject. |
| `medium_full` | Knees up. Action plus some expression. |
| `medium` | Waist up. The default conversational shot — cheap to overuse. |
| `medium_close` | Chest up. Expression leads, context survives. |
| `close` | Head and shoulders. Emotion is the subject. |
| `extreme_close` | A feature or detail. Intensity, or deliberate withholding. |
| `insert` | An object, isolated. Evidence, or a beat carried by a thing. |
| `over_shoulder` | Past a foreground figure. Relationship, and asymmetry of knowledge. |
| `pov` | The camera is a character's eyes. Costs the reader that character's face. |
| `two_shot` | Two figures in one frame. The space between them is the content. |

## `angle` — where the camera sits

`eye_level` (neutral, the absence of comment) · `high` (diminishment, overview) ·
`low` (power, threat, awe) · `birds_eye` (geography, fate, detachment) · `worms_eye` (scale) ·
`dutch` (instability — loses meaning if repeated) · `profile` (formal distance; two profiles read
as opposition) · `back` (the reader shares the character's forward attention).

## `transition` — how one panel becomes the next

`cut` · `match_cut` · `scroll_reveal` · `time_skip` · `scene_change` · `moment_to_moment` ·
`action_to_action` · `subject_to_subject` · `aspect_to_aspect`

Two rules carry most of the weight: a `time_skip` that is not declared reads as a mistake, and
`moment_to_moment` is expensive — it buys slowness with panels, so spend it only where the slowness
is the point.

## `beat_duration` — how long the moment lasts

| Term | Whitespace × | Use |
|---|---:|---|
| `instant` | 0.25 | Impact, interruption, a burst of small panels |
| `short` | 0.5 | Functional continuity between beats |
| `medium` | 1.0 | Default. Ordinary story time |
| `hold` | 1.5 | The reader is made to wait — reactions, dread |
| `long_hold` | 2.5 | Climax, aftermath, the silence before a reveal |

`panel_height` is measured in phone-screen heights (1.0 = one viewport). Above ~2.0 the panel is
read in passes, so design its top and bottom as separate moments.

## `dramatic_function` — what the panel does for the scene

`setup` · `escalate` · `reveal` · `react` · `transition` · `payoff`

Every panel has exactly one. A panel that needs two is usually two panels.

## Composition devices

`rule_of_thirds` · `centered_symmetry` · `negative_space_front` (anticipation) ·
`negative_space_behind` (vulnerability, the unseen) · `frame_within_frame` · `leading_lines` ·
`obstruction` · `reflection` · `silhouette` · `diagonal_dynamism`

## Writing a purpose line

`purpose` is mandatory on every panel and is the field reviewers read first. It must name a
**story, emotion, rhythm, or readability** reason.

| Weak | Strong |
|---|---|
| "Dramatic low angle." | "Low angle keeps the alcove in frame behind her, so the next threat stays present while she is distracted." |
| "Nice composition." | "Bird's-eye collapses the room to a single piece of evidence." |
| "Shows her feelings." | "Cropping to the stopped hand makes the reader supply the face." |

If the only reason for a choice is that it looks good, either cut the choice or find the reason.
