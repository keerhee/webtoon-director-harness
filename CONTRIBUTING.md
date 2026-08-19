# Contributing

Contributions that improve **direction quality, repeatability, continuity, evaluation, or
interoperability** are welcome. Most of this repository is prompts and contracts, so a change to
`.claude/` is as substantive as a change to `harness/` — and needs the same care.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Before opening a PR

```bash
pytest
python scripts/validate_artifacts.py examples/sample_episode --strict
python scripts/validate_handoff.py examples/sample_episode/06_handoff
```

CI runs the same checks on Python 3.10–3.13.

## Changing an agent or skill

- Keep the frontmatter `name` identical to the filename (agents) or directory (skills). The tests
  check this because a mismatch silently disables the agent.
- Keep roles **distinct**. A change that gives one agent another's job removes the separation that
  makes the harness work.
- Keep the `## Team protocol` section and the panel-ID convention.
- Prompts should be operating instructions — inputs, outputs, method, anti-patterns — not adjectives.

## Changing the vocabulary

Add the term to `config/direction_vocabulary.yaml` **with a definition**, add it to the matching
`enum` in `schemas/panel_direction.schema.yaml`, and document it in `docs/DIRECTION_LANGUAGE.md`.
A test asserts the schema and the vocabulary agree, so a partial change fails CI.

## Changing the quality gate

- Weights must sum to 1.0.
- If you change the threshold, say why in the PR. The high default (8.5) is deliberate: at 7.5 a
  merely competent direction ships, which is the failure this repository exists to prevent.
- New hard-fail rules need a named detector agent.

## Changing the worked example

`examples/sample_episode/` is validated in CI and is the repository's definition of "good enough to
ship". If you change it, keep it internally consistent: the reported scores must match the computed
weighted totals, the handoff must be exported from the synthesis rather than re-authored, and the
three candidates must still genuinely diverge.

## Please do not

- Copy restricted third-party skills, prompts, or assets into this repository — see
  [NOTICE.md](NOTICE.md).
- Hard-code a single image model, art tool, or studio pipeline in the handoff artifacts.
- Collapse the specialist roles into one large prompt.
- Add dependencies without a concrete reason; the runtime deps are PyYAML and jsonschema by design.
