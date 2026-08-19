# The Specialist Pool

Nine agents, each with one job. The separation is the mechanism, not an organizational nicety:
a single prompt asked to be narrative, cinematic, emotional, rhythmic, verbal, and continuity-aware
at once will privilege whichever concern it happens to reach first, and quietly drop the rest.

## Role matrix

| Agent | Owns | Reads | Writes | Runs at |
|---|---|---|---|---|
| **showrunner** | Final creative authority, conflict resolution, synthesis | Everything | `04_synthesis/selected_direction.yaml`, `decision_log.md` | Step 4, and again after each loop |
| **breakdown-director** | Panel count, where the cuts fall, what each panel is for | `00_input/source_handoff.md` | `00_input/beat_sheet.yaml`, `00_input/breakdown/*.yaml` | Step 0.5 — only when the input is prose |
| **narrative-director** | Scene objective, beats, reveal order, hook | `00_input/` | `01_analysis/narrative_analysis.yaml` | Step 1 — before any candidate |
| **cinematography-director** | Shot, angle, composition, depth, lighting | `01_analysis/` | `02_candidates/cinematic.yaml` | Step 2 (parallel) |
| **emotion-director** | Emotional beats, reactions, silence, reveal timing | `01_analysis/` | `02_candidates/emotional.yaml` | Step 2 (parallel) |
| **pacing-director** | Timing, panel height, whitespace, scroll rhythm | `01_analysis/` | `02_candidates/webtoon_native.yaml` | Step 2 (parallel) |
| **direction-critic** | Six-axis scoring with evidence, revision requests | One candidate + `01_analysis/` | `03_reviews/critic_<candidate>.yaml` | Step 3, once per candidate |
| **dialogue-silence-editor** | Compression, subtext, balloons, SFX, silence | Candidates, synthesis | `04_synthesis/dialogue_pass.yaml` | Step 4, after synthesis |
| **continuity-supervisor** | State, contradictions, knowledge tracking | `04_synthesis/` | `05_continuity/*.yaml` | Step 5, and after every revision |

## Why these nine

- **The cut is decided before, and separately from, the staging.** Panel count is the most
  irreversible decision in the pipeline - a beat that gets no panel cannot be directed later - so it
  gets its own agent, its own three-way fan-out, and its own gate. The Breakdown Director is
  forbidden from naming a shot, because settling staging there would quietly close the questions the
  direction fan-out exists to open.
- **Narrative before visual.** Anything visual decided before the scene objective exists is a guess
  that later work will be forced to justify.
- **Three leads, not one generator.** Each candidate has an author with a bias. Genuine divergence
  comes from committed positions, not from asking one agent for "three options".
- **The critic is separate from the authors.** A generator scoring its own work grades on effort.
  The critic never drafts, and never learns which candidate the Showrunner prefers.
- **Dialogue is edited last.** Text written before staging exists always ends up doing the image's
  job. The editor's default move is to cut.
- **Continuity is not a taste judgment.** It has a ground truth, so it gets an agent whose output is
  machine-readable state rather than an opinion.
- **The Showrunner decides, and records why.** Synthesis without a decision log is unreviewable, and
  the same argument gets re-litigated next episode.

## Communication rules

Agents communicate through **artifacts**, never through implied shared memory. That is what makes
the pipeline traceable (every decision has a file), debuggable (a bad output localizes to a stage),
reproducible (re-run one stage without re-running the rest), and portable across tools.

- Read upstream artifacts before acting; never assume a prior stage's reasoning.
- Refer to panels by stable IDs (`P01`, `P05a`).
- State assumptions explicitly rather than resolving them silently.
- Every revision note carries: panel ID, problem, severity, concrete fix, owner.

## Adding an agent

Justify it against the existing pool first — most proposed agents are a lens an existing specialist
should already be applying. A new agent is warranted when it owns a distinct **artifact** and a
distinct **failure mode** no current agent is accountable for. Candidates that have earned their
place in other productions: a **layout/lettering** specialist for text-heavy genres, a **world-consistency** agent for long series bibles, and a **cultural-localization** reviewer when the
episode ships in several languages at once.
