# Webtoon Director Harness

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
Upstream Storyboard / Stage 1
        │
        ▼
  Intake & Normalize ──▶ Narrative Analysis
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
```

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · [docs/WORKFLOW.md](docs/WORKFLOW.md)

## Agents

| Agent | Owns |
|---|---|
| **Showrunner** | Final creative authority, conflict resolution, synthesis |
| **Narrative Director** | Scene objective, dramatic beats, reveal order, hook |
| **Cinematography Director** | Shot, angle, composition, depth, lighting, visual reveal |
| **Emotion Director** | Emotional beats, reactions, silence, anticipation |
| **Pacing Director** | Panel timing, scroll rhythm, whitespace, panel height |
| **Dialogue & Silence Editor** | Compression, subtext, balloon order, SFX, silence |
| **Continuity Supervisor** | Characters, props, geography, lighting, timeline, knowledge state |
| **Direction Critic** | Six-axis scoring with evidence, revision requests |

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

## Worked example

[`examples/sample_episode/`](examples/sample_episode) is a complete run over a seven-panel scene:
three divergent candidates, three independent reviews (7.60 / 7.85 / 8.20 — all `revise`), a
synthesis that grafts from all three and scores **8.85**, a continuity pass, and the exported
handoff package. Start with
[`06_handoff/direction_bible.md`](examples/sample_episode/06_handoff/direction_bible.md) and
[`04_synthesis/decision_log.md`](examples/sample_episode/04_synthesis/decision_log.md).

## Inputs and outputs

```text
_workspace/<episode>/
  00_input/       normalized_input.yaml, source_handoff.md, layouts/
  01_analysis/    narrative_analysis.yaml
  02_candidates/  emotional.yaml · cinematic.yaml · webtoon_native.yaml
  03_reviews/     critic_<candidate>.yaml · quality_gate_result.yaml
  04_synthesis/   selected_direction.yaml · decision_log.md · dialogue_pass.yaml
  05_continuity/  continuity_state.yaml · continuity_report.yaml
  06_handoff/     direction_bible.md · panel_direction.yaml · continuity_state.yaml
                  critic_report.md · stage2_handoff.md
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
.claude/          8 agents + 4 skills + project instructions (the creative core)
harness/          scoring, config loading, artifact validation (the deterministic core)
config/           quality gate, direction modes, controlled vocabulary
schemas/          JSON Schema for every structured artifact
scripts/          init_episode · score_direction · validate_artifacts · validate_handoff
templates/        direction bible · critic report · stage 2 handoff
docs/             architecture · workflow · scoring · agents · direction language
examples/         a fully worked episode, validated in CI
adapters/         file-based interoperability notes for upstream tools
tests/            structure, prompt, schema, scoring, and worked-example tests
```

## License

MIT — see [LICENSE](LICENSE). See also [NOTICE.md](NOTICE.md) for third-party interoperability terms.
