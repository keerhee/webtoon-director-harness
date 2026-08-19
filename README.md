# Webtoon Director Harness

Independent **Director's Room** repository for improving webtoon/comic direction between an upstream storyboard stage and a downstream image/production stage.

> Clean-room scaffold: no third-party skill files, prompts, or assets are copied into this repository. Interoperability is file-based.

## Workflow

```text
Upstream Storyboard / Stage 1
        |
        v
  Intake & Normalize
        |
        v
  Narrative Analysis
        |
        v
  Direction Fan-out
   /       |        \
Emotional Cinematic Webtoon-native
   \       |        /
        v
   Multi-Critic Review
        |
        v
   Director Synthesis
        |
        v
 Continuity + Quality Gate
        |
   pass? -- no --> revise loop
        |
       yes
        v
  Production Handoff / Stage 2
```

## Agents

- **Showrunner** — supervisor and final creative authority
- **Narrative Director** — scene objective, dramatic beats, reveal order
- **Cinematography Director** — shot, angle, composition, visual hierarchy
- **Emotion Director** — emotional beats, silence, reactions, anticipation
- **Pacing Director** — panel timing, scroll rhythm, whitespace
- **Dialogue & Silence Editor** — compression, subtext, SFX, silence
- **Continuity Supervisor** — characters, props, geography, lighting, timeline
- **Direction Critic** — multi-axis scoring and revision requests

## Inputs

Typical upstream files:

```text
episode_handoff.md
page1_layout.svg
page2_layout.svg
```

Normalize them to `_workspace/<episode>/00_input/normalized_input.yaml`.

## Outputs

```text
_workspace/<episode>/06_handoff/
├── direction_bible.md
├── panel_direction.yaml
├── continuity_state.yaml
├── critic_report.md
└── stage2_handoff.md
```

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e .
python scripts/init_episode.py ep01
```

Put upstream files in `_workspace/ep01/00_input/`, then in Claude Code:

```text
이 프로젝트의 Director's Room을 실행해줘.
_workspace/ep01/00_input을 읽고 Emotional / Cinematic / Webtoon-native
세 연출안을 병렬 생성한 뒤 multi-critic review와 synthesis를 수행하고,
quality gate를 통과할 때까지 수정한 후 06_handoff에 최종 산출물을 만들어줘.
```

## Default quality gate

- Narrative clarity: 20%
- Emotional impact: 20%
- Visual composition: 20%
- Pacing / scroll: 15%
- Reading flow: 10%
- Continuity: 15%
- Pass threshold: **8.5 / 10**

See `config/quality_gate.yaml`.

## Core design principle

**Do not accept the first plausible direction.** Generate alternatives, review independently, synthesize, validate, and only then hand off to production.

## License

MIT — see [LICENSE](LICENSE). See also [NOTICE.md](NOTICE.md) for third-party interoperability terms.
