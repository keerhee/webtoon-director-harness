# Image Pipeline (Stage 3) — free, local, no account

The direction stages produce text. This stage turns that text into panels on your own machine:
**no API key, no account, no per-image cost**, and nothing leaves the computer.

```text
06_handoff/  ──▶ build_image_prompts.py ──▶ 07_prompts/
                                              │
                              ┌───────────────┴────────────────┐
                              ▼                                ▼
                     refs/ (render FIRST)              panels/ P01…P07
                     turnaround + expressions          render ▸ validate ▸ regen
                              │                                │
                     LoRA / IP-Adapter ─────anchors───────────▶│
                                                               ▼
                                                    text-free plates
                                                               │
                                        lettering.md ──────────▶ balloons + prop text
                                                               ▼
                                                  assembled vertical strip
```

## What you install

| Piece | What | Cost |
|---|---|---|
| **ComfyUI** | Node-based local runner for Stable Diffusion | Free, open source |
| **Checkpoint** | SDXL-family, or FLUX.1 schnell | Free download |
| **LoRA trainer** | Any local trainer (kohya-style), for character consistency | Free |
| **IP-Adapter** *(alternative)* | Reference-image conditioning, no training | Free |
| **Upscaler** | An ESRGAN-family model | Free |

Nothing above requires a subscription or an online account. Model weights are downloaded once.

### Hardware, honestly

- **8 GB VRAM** — SDXL works with the usual memory optimizations. This is the practical floor.
- **12 GB+** — comfortable SDXL, and FLUX.1 schnell in reduced precision.
- **No GPU** — CPU generation is minutes per image, not seconds. Technically free, practically painful.
- Roughly 10–40 s per SDXL panel on a mid-range GPU. A 7-panel scene is minutes; a 60-panel episode
  is an evening.

### Licensing

FLUX.1 **schnell** is Apache-2.0, which is the cleanest option if the work will be commercial.
SDXL base ships under CreativeML Open RAIL++-M, and community checkpoints vary widely — several
popular anime checkpoints carry non-commercial terms. **Check the license of the specific checkpoint
you download** before publishing or selling. Terms change; verify at download time rather than
trusting this table.

## Consistency is the whole problem

Panel quality is not the hard part; making panel 40 show the same person as panel 3 is. Three
devices, in order of strength:

1. **Character LoRA** *(best)* — render the turnaround sheet, derive a small training set from it,
   train a LoRA per recurring character. Then every prompt carries `<lora:mina_v1:0.8>` and the face
   holds across an entire series. Record the filename in the profile and rebuild the prompts.
2. **IP-Adapter / reference-only** *(no training)* — condition on the turnaround image directly.
   Good, and immediate. Weaker than a LoRA over long sequences.
3. **Text tokens alone** *(insufficient for faces)* — the harness injects immutable appearance
   tokens including identifying marks *with their side*, but tokens alone will not hold a face.

Two more devices the harness handles for you:

- **Location tokens** — `LOC_LAB_B3` plus identical geography wording in every panel of a scene, so
  the background cannot drift mid-scene.
- **Deterministic seeds** — derived from `episode_id:panel_id`. Re-running the builder never changes
  a seed, so a re-render is reproducible and a diff shows exactly what your edit did.

## Why the art is rendered text-free

Local diffusion models cannot render Korean reliably — they produce glyph-shaped noise. So this
pipeline renders **clean plates** and letters afterwards, into the `dialogue_space` the direction
reserved at staging time.

This is a deliberate divergence from pipelines built on hosted image models that *can* draw legible
text and therefore bake it in. On a local stack the tradeoff runs the other way, and it pays:

- A dialogue change costs a lettering pass, not a re-render.
- Translation is a lettering pass.
- No garbled-glyph failures, which are the single most common defect in text-baking pipelines.

Panels whose direction needs readable writing inside the art — a name on a dropped access card —
are flagged under **Prop text** in `lettering.md`. The plate is rendered blank; the writing is added
with the balloons.

## The validate-and-regenerate loop

Validate **each panel as it lands**, never at the end. Six axes — character consistency, location
continuity, clean text-free plate with balloon space intact, direction fidelity, read flow,
technical integrity (zero-byte, corruption, md5 duplicates).

Failures go back to prompt-smith, which strengthens **one** device and re-renders that panel only,
keeping the seed. Cap at three attempts, then accept the best version with its defect recorded.

Finish with a cross-comparison sweep across all accepted panels: per-panel checks systematically
miss gradual drift, because drift is a property of the set, not of any single image.

## Commands

```bash
python scripts/build_image_prompts.py _workspace/ep01
python scripts/build_image_prompts.py examples/sample_episode --profile comfyui
```

Then in Claude Code: "ep01 패널 렌더링해줘" invokes the `panel-render` skill.

## Targeting a different generator

Everything model-specific lives in `adapters/image-prompt/profiles/comfyui.yaml` — style anchor,
shot and angle wording, negatives, canvas sizing, LoRA table. Add a sibling profile to target
another generator; the harness artifacts do not change, because they never named a model.

## Prior art

The reference-sheet-first ordering, `LOC_*` location tokens, and the per-panel validate-and-regenerate
loop are patterns demonstrated by [revfactory/webtoon-harness](https://github.com/revfactory/webtoon-harness),
which runs a full webtoon production on hosted image generation. This repository implements those
patterns independently for a free local stack, and inverts the text decision for the reason given
above. No files, prompts, or assets from that project are copied here — see [NOTICE.md](../NOTICE.md).
