# AITOON File Adapter

A file-based interoperability layer only. This folder contains **no third-party skill code, prompts,
or assets** — just the mapping between an upstream tool's outputs and this repository's normalized
input. See [NOTICE.md](../../NOTICE.md).

## Expected upstream files

```text
ep##_인계서.md        # episode handoff / storyboard notes
page#_layout.svg      # per-page panel layout
```

## Normalize to

`_workspace/<episode>/00_input/normalized_input.yaml`:

```yaml
episode_id:
title:
genre:
target_reader:
tone:
characters:
  - name:
    traits: []
scenes:
  - scene_id:
    purpose:
    source_text:
    panels:
      - panel_id:
        source_description:
        source_dialogue:
layout_files: []
```

## Mapping rules

| Upstream | Normalized | Notes |
|---|---|---|
| Handoff heading | `title`, `episode_id` | `episode_id` must be filename-safe (`ep01`, not `EP 01`). |
| Panel bullets | `panels[].source_description` | Assign IDs in reading order: `P01`, `P02`, … Never renumber later. |
| Quoted lines | `panels[].source_dialogue` | Keep the source wording; the dialogue pass edits it downstream, not here. |
| Scene breaks | `scenes[]` | One scene per continuous place and time. |
| `page#_layout.svg` | `layout_files[]` | Reference by path; do not inline SVG into the YAML. |

## Rules

- **Normalize before the pipeline starts.** Unnormalized input propagates into every downstream
  artifact and cannot be diffed across loops.
- **Panel IDs are the join key** for every later artifact. Assign them once, here.
- **Do not interpret while normalizing.** Intake records what the source says; the Narrative
  Director decides what it means. Mixing the two hides the source's gaps.
- **Record what is missing** rather than inventing it — an absent scene purpose is information the
  Narrative Director needs.

## Downstream

The Director's Room exports production-neutral handoff files (`06_handoff/`) that any downstream
system may consume. No image model, art tool, or studio pipeline is named in them by design, so the
same handoff can drive different production stages.

## Writing another adapter

Copy this folder, replace the upstream file list and the mapping table, and keep the output contract
identical — the pipeline only ever reads `normalized_input.yaml`. Review the licenses and terms of
any external tool before publishing or commercializing an integration.
