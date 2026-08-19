# AITOON File Adapter

File-based interoperability layer only. This folder does **not** contain or reproduce third-party skill code.

## Expected upstream files
Typical examples:
```text
ep##_인계서.md
page#_layout.svg
```

## Normalize to
```yaml
episode_id:
title:
genre:
target_reader:
tone:
characters: []
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

The Director's Room exports neutral handoff files that any downstream production system may consume.
