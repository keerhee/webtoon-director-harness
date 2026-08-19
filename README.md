# Webtoon Director Harness

**English** · [한국어](README.ko.md)

[![CI](https://github.com/keerhee/webtoon-director-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/keerhee/webtoon-director-harness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

A **Director's Room** for webtoon and comic production: a multi-agent harness that sits between an
upstream storyboard stage and a downstream art/production stage, and improves the *direction* —
what the reader understands, feels, and looks at, and in what order.

> Clean-room scaffold. No third-party skill files, prompts, or assets are copied into this
> repository; interoperability is file-based. See [NOTICE.md](NOTICE.md).

## Why

A single generative pass converges too early. Asked to direct a scene, one model produces the first
staging that is *defensible* — competent, generic, and never the third idea it would have had. Then
it reviews its own work, which grades effort rather than result.

Direction fails in ways a prose check cannot see: the reveal that lands one panel early, the missing
reaction shot, the scroll that flatlines on a phone, the character who acts on something they were
never told. This repository separates **generation, specialization, critique, synthesis, and
validation** into different agents that communicate only through files.

**Core principle: do not accept the first plausible direction.**

## Workflow

```text
Upstream story, script, or storyboard / Stage 1
        │
        ▼
  Intake & Normalize
        │
        ├── no panels? ──▶ Stage 0.5  Panel Breakdown      ← conditional
        │                  beat sheet ▸ 3 cuts ▸ review ▸ select ▸ freeze IDs
        ▼
  Narrative Analysis
                              │
              ┌───────────────┼───────────────┐
         Emotional        Cinematic      Webtoon-native      ← independent fan-out
              └───────────────┼───────────────┘
                              ▼
                   Multi-Critic Review        ← blind, evidence-based, one per candidate
                              ▼
                   Director Synthesis         ← spine + grafts + decision log
                              ▼
                  Dialogue & Silence Pass
                              ▼
              Continuity + Quality Gate ──fail──▶ bounded revision loop
                              │ pass
                              ▼
                Production Handoff / Stage 2
                              │
                              ▼   (optional, on request)
                Stage 3  Panel Render — local ComfyUI, free
                refs first ▸ render ▸ validate ▸ regen ▸ letter
```

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/WORKFLOW.md](docs/WORKFLOW.md)

## Agents

| Agent | Owns |
|---|---|
| **Showrunner** | Final creative authority, conflict resolution, synthesis |
| **Breakdown Director** | Panel count and where the cuts fall — Stage 0.5, prose input only |
| **Narrative Director** | Scene objective, dramatic beats, reveal order, hook |
| **Cinematography Director** | Shot, angle, composition, depth, lighting, visual reveal |
| **Emotion Director** | Emotional beats, reactions, silence, anticipation |
| **Pacing Director** | Panel timing, scroll rhythm, whitespace, panel height |
| **Dialogue & Silence Editor** | Compression, subtext, balloon order, SFX, silence |
| **Continuity Supervisor** | Characters, props, geography, lighting, timeline, knowledge state |
| **Direction Critic** | Six-axis scoring with evidence, revision requests |
| **Prompt Smith** | Image prompts, consistency tokens, negatives — Stage 3 |
| **Panel Validator** | Six-axis render check with a bounded re-render loop — Stage 3 |

Role matrix and rationale: [docs/AGENTS.md](docs/AGENTS.md)

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

python scripts/init_episode.py ep01
```

Put the upstream handoff and layout files in `_workspace/ep01/00_input/`, then in Claude Code:

```text
이 프로젝트의 Director's Room을 실행해줘.
_workspace/ep01/00_input을 읽고 Emotional / Cinematic / Webtoon-native
세 연출안을 병렬 생성한 뒤 multi-critic review와 synthesis를 수행하고,
quality gate를 통과할 때까지 수정한 후 06_handoff에 최종 산출물을 만들어줘.
```

To see the target quality first, seed an episode from the worked example:

```bash
python scripts/init_episode.py demo --from-example
```

## Input: story, or storyboard?

Both work. The harness detects which one it received.

| You have | What happens |
|---|---|
| A **cut storyboard** (panel-level descriptions) | Stage 0.5 is skipped — the cut was made upstream and is not re-litigated |
| **Prose**: a scene, synopsis, or script | Stage 0.5 runs: a beat sheet, then three candidate cuts (`dense` / `economical` / `spacious`), independently reviewed against a four-axis gate, selected and grafted, then committed as `panels[]` |

You never have to ask for it. The check happens at intake, and the pipeline says which branch it took.

Panel art, layouts, and thumbnails are **not** required at any level — `layout_files` is optional,
and the worked example completes with it empty.

## Worked example

[`examples/sample_episode/`](examples/sample_episode) is a complete run over a seven-panel scene:
three divergent candidates, three independent reviews (7.60 / 7.85 / 8.20 — all `revise`), a
synthesis that grafts from all three and scores **8.85**, a continuity pass, and the exported
handoff package. Start with
[`06_handoff/direction_bible.md`](examples/sample_episode/06_handoff/direction_bible.md) and
[`04_synthesis/decision_log.md`](examples/sample_episode/04_synthesis/decision_log.md).

## Images: free and local (Stage 3)

The handoff is text, and production-neutral by design — it names no image model. When you want
pictures, Stage 3 renders them **on your own machine at zero cost**: ComfyUI plus an SDXL-family or
FLUX.1 schnell checkpoint. No API key, no account, nothing leaves the computer.

```bash
python scripts/build_image_prompts.py _workspace/ep01
```

That writes `07_prompts/` — style anchor, negatives, immutable character tokens, `LOC_*` location
tokens, reference-sheet prompts, one prompt per panel with a deterministic seed, and a lettering
spec. Then the `panel-render` skill renders reference sheets first, generates panels with a
per-panel validate-and-re-render loop, and hands off to lettering.

Three things the builder does that hand-written prompts usually miss:

- **Consistency is engineered, not hoped for.** Character tokens carry identifying marks *with their
  side*; location tokens keep the background from drifting mid-scene; seeds are derived from
  `episode_id:panel_id`, so a re-render is reproducible and a diff shows what your edit changed.
- **Tall panels are sectioned.** A 2.6-screen climax panel is rendered in overlapping passes rather
  than squashed into a square.
- **The art is text-free.** Local models cannot render Korean reliably, so panels are clean plates
  and text is lettered into the balloon space the direction reserved. A dialogue change then costs a
  lettering pass instead of a re-render.

Setup, hardware, consistency methods, and checkpoint licensing: [docs/IMAGE_PIPELINE.md](docs/IMAGE_PIPELINE.md).

## Inputs and outputs

```text
_workspace/<episode>/
  00_input/       normalized_input.yaml, source_handoff.md, layouts/
                  beat_sheet.yaml, breakdown/   (Stage 0.5 only)
  01_analysis/    narrative_analysis.yaml
  02_candidates/  emotional.yaml · cinematic.yaml · webtoon_native.yaml
  03_reviews/     critic_<candidate>.yaml · quality_gate_result.yaml
  04_synthesis/   selected_direction.yaml · decision_log.md · dialogue_pass.yaml
  05_continuity/  continuity_state.yaml · continuity_report.yaml
  06_handoff/     direction_bible.md · panel_direction.yaml · continuity_state.yaml
                  critic_report.md · stage2_handoff.md
  07_prompts/     image prompts, reference sheets, lettering spec   (Stage 3)
  08_panels/      rendered PNGs + validation.md                     (Stage 3)
```

Handoff files are **production-neutral** — no image model, art tool, or studio pipeline is assumed.

## Quality gate

| Axis | Weight |
|---|---:|
| Narrative clarity | 20% |
| Emotional impact | 20% |
| Visual composition | 20% |
| Pacing / scroll | 15% |
| Continuity | 15% |
| Reading flow | 10% |

Pass threshold **8.5 / 10**, at most 3 revision loops. Scores of 9–10 require panel-level evidence,
and any hard failure (broken continuity, unreadable balloon order, identity mismatch, missing climax)
forces a revision regardless of the total. See [docs/SCORING.md](docs/SCORING.md) and
[`config/quality_gate.yaml`](config/quality_gate.yaml).

```bash
python scripts/score_direction.py _workspace/ep01/03_reviews/critic_*.yaml
python scripts/score_direction.py _workspace/ep01/00_input/breakdown/critic_*.yaml --gate breakdown
python scripts/validate_artifacts.py _workspace/ep01     # schema + vocabulary + panel IDs
python scripts/validate_handoff.py _workspace/ep01/06_handoff
pytest
```

## Direction language

Shot, angle, transition, beat duration, and dramatic function come from a controlled vocabulary in
[`config/direction_vocabulary.yaml`](config/direction_vocabulary.yaml), enforced by the panel
schema and the validator. Free-text terms break scoring, diffing, and production.
Reference: [docs/DIRECTION_LANGUAGE.md](docs/DIRECTION_LANGUAGE.md)

## Repository layout

```text
.claude/          11 agents + 6 skills + project instructions (the creative core)
harness/          scoring, config loading, artifact validation (the deterministic core)
config/           quality gate, direction modes, controlled vocabulary
schemas/          JSON Schema for every structured artifact
scripts/          init_episode · score_direction · validate_artifacts · validate_handoff
templates/        direction bible · critic report · stage 2 handoff
docs/             architecture · workflow · scoring · agents · direction language
examples/         a fully worked episode, validated in CI
adapters/         upstream file adapters, and image-prompt profiles per generator
tests/            structure, prompt, schema, scoring, and worked-example tests
```

## License

MIT — see [LICENSE](LICENSE). See also [NOTICE.md](NOTICE.md) for third-party interoperability terms.
