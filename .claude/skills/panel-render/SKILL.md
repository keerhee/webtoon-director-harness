---
name: panel-render
description: Stage 3 - renders webtoon panels locally and free with ComfyUI. Builds prompts from the approved direction, renders character reference sheets first, generates panels with a validate-and-re-render loop, and produces a text-free strip plus a lettering spec. Use after the handoff package passes, or when the user asks to draw, render, or re-render panels.
---
# Panel Render (Stage 3)

Turns the approved direction into images, entirely on local hardware: no API key, no account, no
per-image cost. Nothing here calls a hosted model.

**Precondition:** `06_handoff/` passes `validate_handoff.py`. Rendering an unapproved direction just
produces images you will throw away.

## 0. Build the prompts

```bash
python scripts/build_image_prompts.py _workspace/<episode>
```

Writes `07_prompts/`. Deterministic — same direction, same prompts, same seeds. Never hand-edit the
output; change the direction or `adapters/image-prompt/profiles/comfyui.yaml` and rebuild.

## 1. Reference sheets FIRST

Render `07_prompts/refs/REFERENCE_SHEETS.md` — a turnaround and an expression sheet per character —
before any panel. Text tokens alone will not hold a face steady across a scene, let alone a series.

Then pick a consistency anchor:

| Method | Setup | Consistency | Use when |
|---|---|---|---|
| **Character LoRA** | Train on 15–30 images derived from the turnaround | Best | A recurring character; a series |
| **IP-Adapter / reference-only** | Point at the turnaround image | Good | A one-off episode, or before the LoRA exists |
| Tokens only | Nothing | Weak | Backgrounds and props, never faces |

Record the LoRA filename in the profile's `character_loras`, then **rebuild the prompts** so the
LoRA tag is injected everywhere.

Reference sheets are a **series asset**. Store them outside the episode directory and reuse them;
only new characters need a new sheet.

## 2. Render panels

Each `07_prompts/panels/P**.txt` carries positive, negative, generation size, seed, and sections.
Render in panel order, and pass every panel to the validator as it lands.

- **Sizes** come from the panel's height in screen-heights. A panel taller than 2× its width is
  rendered in overlapping sections and stitched — a 2.6-screen climax panel is not one image any
  diffusion model was trained to make.
- **Local rendering is VRAM-bound, not rate-limited.** Queue sequentially; parallel jobs on one GPU
  are slower than serial ones. Expect roughly 10–40 s per SDXL panel on a mid-range GPU.
- **Do not change the seed** to fix a prompt problem. Fix the prompt.

## 3. Validate as you go

Invoke **panel-validator** per panel → ACCEPT / REGEN / ACCEPT-FLAG on six axes: character
consistency, location continuity, clean text-free plate with balloon space preserved, direction
fidelity, read flow, technical integrity.

REGEN → **prompt-smith** strengthens one device → re-render that panel only → re-validate.
Cap at 3 attempts per panel, then ACCEPT-FLAG and move on.

After the batch, run the validator's **cross-comparison sweep** — per-panel checks miss gradual
drift, because drift is a property of the set.

## 4. Letter

Art is text-free by design: local models cannot render Korean reliably, and baked-in glyphs cannot
be edited without repainting. Apply `07_prompts/lettering.md` over the finished panels — balloons in
the reserved `dialogue_space`, plus any **Prop text** the direction requires.

This also means a dialogue change costs a lettering pass instead of a re-render.

## 5. Assemble

Stack the panels at the strip width with the whitespace the direction specifies —
`whitespace_before` and `whitespace_after` are gap multipliers, and they are the scene's timing.
Verify against `direction_bible.md`'s rhythm table: the total scroll should match what was designed.

## Free stack

| Piece | Choice | Note |
|---|---|---|
| Runner | ComfyUI | Local, free, no account |
| Model | SDXL-family or FLUX.1 schnell | schnell is Apache-2.0; check any other checkpoint's license before commercial use |
| Consistency | LoRA training, or IP-Adapter | Both local and free |
| Upscale | Any ESRGAN-family model | Panels are generated near 1 MP and upscaled |

Setup, hardware requirements, and licensing: `docs/IMAGE_PIPELINE.md`.

## Reporting
Close with: panels rendered, panels that needed a re-render and why, panels carrying ACCEPT-FLAG
with their known defect, and whether the cross-comparison sweep passed.
