---
name: story-breakdown
description: Stage 0.5 - turns a prose scene, synopsis, or script into a panel breakdown by generating three candidate cuts, scoring them independently, and writing the winner into normalized_input.yaml. Runs automatically when the input has no panels; skipped when a cut storyboard already exists.
---
# Story Breakdown (Stage 0.5)

Converts prose into a panel cut. This is the only stage that decides **how many panels exist** —
everything downstream decides what happens inside them.

## Trigger — check before running

Read `00_input/normalized_input.yaml` (or the source handoff if it does not exist yet):

| Input state | Action |
|---|---|
| No `panels[]` at all | **Run this skill.** |
| A scene carries 1–2 lumped descriptions for a whole sequence | **Run this skill** for that scene. |
| Every scene has panel-level descriptions with IDs | **Skip.** The cut was made upstream; do not redo it. |

Say which branch you took and why. Silently skipping is how a prose input ends up with an
unreviewed cut.

## 1. Beat sheet
Invoke **breakdown-director** → `00_input/beat_sheet.yaml`.

Beats are `B01`, `B02` — never panel IDs. The sheet names the scene goal, each beat's function and
weight, what each reveals and to whom, and the **climactic moment in words**.

Gate: at least two beats, a one-sentence scene goal, and a climactic moment that is not phrased as
a panel ID. Source dialogue is carried over unedited.

## 2. Three candidate cuts
Invoke **breakdown-director** → `00_input/breakdown/dense.yaml`, `economical.yaml`, `spacious.yaml`.

Gate: the three must differ in **panel count** and in **where the reveals land**. Three cuts that
produce the same panel count with different wording are one cut written three times.

## 3. Independent review
Invoke **direction-critic** once per candidate → `00_input/breakdown/critic_<approach>.yaml`,
scored against `breakdown_gate` in `config/quality_gate.yaml` — four axes, threshold 8.0:

| Axis | Weight | Question |
|---|---:|---|
| `beat_coverage` | 30% | Does every beat in the sheet have a panel? Is any beat smeared across so many panels it loses shape? |
| `reveal_placement` | 30% | Does each reveal get its own panel, in the intended order? Is the reader-ahead-of-character offset preserved where it exists? |
| `rhythm_potential` | 25% | Does this cut leave room for holds, bursts, and one uncontested climax panel? |
| `production_cost` | 15% | Is the panel count proportionate to what this scene is worth in the episode? |

Hard failures: `beat_without_panel`, `reveal_collision`, `no_climax_panel`.

```bash
python scripts/score_direction.py _workspace/<episode>/00_input/breakdown/critic_*.yaml --gate breakdown
```

## 4. Selection
Invoke **showrunner** → `00_input/breakdown/selection.md`.

Select a cut and graft from the others panel by panel, exactly as in the direction synthesis —
a `spacious` spine that borrows one split from `dense` is a normal and good outcome. Record what
was taken and what was rejected.

## 5. Commit the cut
Write the selected panels into `00_input/normalized_input.yaml` as `panels[]`, keeping
`source_description` and `source_dialogue` per panel.

```bash
python scripts/validate_artifacts.py _workspace/<episode>
```

**Panel IDs are now frozen.** Later stages may split a panel (`P05a`, `P05b`) or merge two, but
never renumber. From here the standard pipeline runs unchanged.

## Why this stage is scored separately

The four axes are structural, and the threshold is lower (8.0) on purpose. A breakdown does not need
to be beautiful — it needs to leave every later stage room to work. Over-tuning the cut spends
revision budget that the direction stages need more, which is why `max_revision_loops` here is 1.

## Reporting
Close with: which approach was selected, the panel count and how it compares to the alternatives,
which grafts were taken, and any beat you were unable to give its own panel.
