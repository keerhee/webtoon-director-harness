# Architecture

## The problem

A single generative pass converges too early. Asked to direct a scene, one model produces the first
staging that is *defensible* — usually competent, usually generic, and almost never the third idea
it would have had. Worse, its own review of that staging grades effort rather than result, because
the reasoning that produced the panels is the same reasoning that evaluates them.

Direction quality is not a prose problem. It fails in ways prose quality checks cannot see: the
reveal that arrives one panel too early, the reaction shot that is missing, the scroll that flatlines,
the character who acts on something they have not been told.

## The response

Separate **generation**, **specialization**, **critique**, **synthesis**, and **validation** into
different agents that communicate only through files.

```text
                    ┌──────────────────┐
                    │   Intake &       │
                    │   Normalize      │
                    └────────┬─────────┘
                             │  does the input have panels?
                    ┌────────▼─────────┐
                    │   Stage 0.5      │  no  → beat sheet, three cuts,
                    │ Panel Breakdown  │        review, select, freeze IDs
                    │  (conditional)   │  yes → skip; the cut was made upstream
                    └────────┬─────────┘
                             │  normalized_input.yaml
                    ┌────────▼─────────┐
                    │    Narrative     │  scene goal · reveal order
                    │    Director      │  climax · hook
                    └────────┬─────────┘
                             │  narrative_analysis.yaml
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐        ┌─────▼────┐         ┌─────▼──────┐
   │ Emotion  │        │ Cinema-  │         │  Pacing    │   fan-out
   │ Director │        │ tography │         │  Director  │   (independent)
   └────┬─────┘        └─────┬────┘         └─────┬──────┘
        │ emotional          │ cinematic          │ webtoon_native
        └────────────────────┼────────────────────┘
                    ┌────────▼─────────┐
                    │ Direction Critic │   scored separately, blind
                    │   (per candidate)│   to any preference
                    └────────┬─────────┘
                    ┌────────▼─────────┐
                    │   Showrunner     │   spine + grafts
                    │   (synthesis)    │   decision log
                    └────────┬─────────┘
                    ┌────────▼─────────┐
                    │ Dialogue Editor  │   cut · compress · silence
                    └────────┬─────────┘
                    ┌────────▼─────────┐
                    │   Continuity     │   state · violations
                    │   Supervisor     │
                    └────────┬─────────┘
                    ┌────────▼─────────┐
                    │  Quality Gate    │──fail──▶ revision tasks ──┐
                    └────────┬─────────┘                          │
                             │ pass                               │
                    ┌────────▼─────────┐                          │
                    │ Production       │◀─────────────────────────┘
                    │ Handoff          │   bounded: max_revision_loops
                    └──────────────────┘
```

## Patterns in use

| Pattern | Where | Why |
|---|---|---|
| **Supervisor** | Showrunner | One agent owns tradeoffs; without it, specialists deadlock or average. |
| **Fan-out / fan-in** | Three cuts, then three directions | Alternatives must exist before a choice can be meaningful — and that applies to the cut as much as to the staging. |
| **Conditional stage** | Stage 0.5 | Prose inputs need a cut; storyboard inputs already have one. The pipeline detects which it received instead of asking. |
| **Expert pool** | Specialist directors | Each concern gets an advocate that will not silently drop it. |
| **Generator / reviewer** | Critic vs. authors | Self-review grades effort. Independence is what makes the score mean anything. |
| **Bounded loop** | Quality gate | Revision without a bound is how a pipeline spends a day polishing panel four. |
| **Pipeline via artifacts** | Every stage | Traceable, debuggable, reproducible, portable. |

## Why artifacts, not conversation

Passing state in a conversation makes the pipeline one long context in which early decisions blur
and late ones dominate. Files give you:

- **Traceability** — every decision has a location, and `decision_log.md` says why.
- **Debuggability** — a weak result localizes to a stage instead of to "the run".
- **Reproducibility** — re-run one stage without regenerating the parts that already worked.
- **Portability** — the handoff is production-neutral, so no downstream tool is baked in.
- **Reviewability** — a human director can diff loop 1 against loop 2.

## Deliberate non-goals

- **Not a script writer.** Stage 0.5 cuts an existing scene into panels. It never invents story,
  and it never names a shot.
- **Not an image generator.** Handoff files name no model, tool, or studio pipeline.
- **Not a script editor.** The dialogue pass serves direction; it does not rewrite the story.
- **Not automatic taste.** The gate catches competent-but-unremarkable work and stops runaway
  revision. It does not replace a human director's judgment, and it is not meant to.
