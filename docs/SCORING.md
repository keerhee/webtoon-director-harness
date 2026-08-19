# Direction Scoring

Six axes, weighted, on a 0–10 scale. The score is a **quality gate and a debugging instrument**,
not a replacement for creative judgment. Its two real jobs are to catch work that is competent but
unremarkable, and to stop revision from running forever.

## Axes and weights

| Axis | Weight | The question it asks |
|---|---:|---|
| Narrative clarity | 20% | Can a first-time reader say what changed, and in what order they learned it? |
| Emotional impact | 20% | Does the sequence *produce* the intended arc, or only describe it? |
| Visual composition | 20% | Are shot, angle, blocking, depth, and hierarchy purposeful and varied? |
| Pacing / scroll | 15% | Is time controlled through panel size and whitespace, or accidental? |
| Continuity | 15% | Are characters, props, geography, lighting, timeline, and knowledge coherent? |
| Reading flow | 10% | Do gaze path, balloon order, and transitions survive a fast mobile scroll? |

Weights sum to 1.0 — enforced by `harness.config.load_quality_gate` and by the test suite, because
a gate whose weights drift silently rescales every score.

**Pass threshold: 8.5 / 10.** Set deliberately high. At 7.5 a merely competent direction ships,
which is the exact failure this repository exists to prevent.

## Anchors

| Score | Meaning |
|---:|---|
| 9–10 | Exemplary. Would teach this sequence as a reference. **Requires panel-level evidence.** |
| 7–8 | Professional. Works, with identifiable missed opportunities. |
| 5–6 | Functional but generic. A competent default; no authored choice visible. |
| 3–4 | Actively weakens the scene — confusion, flat rhythm, wasted beats. |
| 0–2 | Broken. The scene fails to communicate. |

A 9 or 10 without a cited panel ID is invalid. `score_direction.py` flags it, and the reviewer
re-scores.

## Hard failures

Any of these forces `REVISE` regardless of the weighted total:

| Rule | Detected by |
|---|---|
| `broken_scene_continuity` | continuity-supervisor (a `blocking` violation) |
| `unreadable_dialogue_order` | dialogue-silence-editor |
| `character_identity_mismatch` | continuity-supervisor |
| `missing_climax_or_reveal` | direction-critic |

A perfect score with an open hard failure is still a revision. This is deliberate: the axes are
averages, and an average can hide a scene the reader cannot follow.

## Computing a score

```bash
python scripts/score_direction.py _workspace/ep01/03_reviews/critic_cinematic.yaml
python scripts/score_direction.py _workspace/ep01/03_reviews/critic_*.yaml --json
```

Exit code 0 when every report passes, 1 when any needs revision — usable in CI or a pre-handoff hook.
The tool also reports **integrity warnings**: unevidenced top scores, and a `weighted_total` in the
report that disagrees with the computed value by more than 0.05.

## Reading the numbers honestly

- **Compare candidates, not episodes.** The scale is calibrated within a review round; cross-episode
  comparison mostly measures how strict that round's critic was.
- **A rising total with no artifact change is invalid.** Re-score.
- **Never lower the threshold to force a pass.** Change the direction, or record an explicit
  exception in the decision log — an unrecorded exception becomes next episode's default.
- **Watch the delta, not the level.** Under `min_improvement_per_loop` (default 0.2), the problem is
  upstream: the scene goal, the reveal order, or the choice of spine.
- **A perfect score means the rubric ran out of resolution,** not that the scene cannot be better.

## The Stage 0.5 gate

Panel breakdown is scored separately, on four structural axes with a lower threshold (8.0) and a
single revision loop.

| Axis | Weight | The question it asks |
|---|---:|---|
| Beat coverage | 30% | Does every beat have a panel? Is any beat smeared across so many panels it loses shape? |
| Reveal placement | 30% | Does each reveal get its own panel, in the intended order? |
| Rhythm potential | 25% | Does the cut leave room for holds, bursts, and one uncontested climax panel? |
| Production cost | 15% | Is the panel count proportionate to what the scene is worth? |

Hard failures: `beat_without_panel`, `reveal_collision`, `no_climax_panel`.

```bash
python scripts/score_direction.py <critic.yaml> --gate breakdown
```

The threshold is lower on purpose. A breakdown does not need to be beautiful - it needs to leave
every later stage room to work, and revision budget spent here is budget the direction stages lose.

From `examples/sample_episode/00_input/breakdown/`:

| Cut | Panels | Coverage | Reveals | Rhythm | Cost | Weighted | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| dense | 11 | 9 | 9 | 7 | 4 | **7.75** | revise |
| economical | 5 | 7 | 4 | 5 | 10 | **6.05** | revise - `reveal_collision` |
| spacious | 7 | 9 | 9 | 8 | 8 | **8.60** | pass |

`economical` scores highest on cost and still loses, which is the gate working: merging the card
with its recognition destroys a beat no downstream staging can recover.

## Worked numbers

From `examples/sample_episode/`:

| Candidate | NC | EI | VC | PS | RF | Cont | Weighted | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| emotional | 8 | 9 | 7 | 7 | 8 | 8 | **7.85** | revise |
| cinematic | 9 | 7 | 9 | 7 | 8 | 9 | **8.20** | revise |
| webtoon_native | 7 | 8 | 7 | 9 | 8 | 7 | **7.60** | revise |
| synthesis | 9 | 9 | 9 | 8 | 9 | 9 | **8.85** | pass |

The synthesis beats every candidate on every axis it grafted from, which is the outcome the
architecture is built to produce. If synthesis ever scores below its best candidate, the Showrunner
blended instead of selecting.
