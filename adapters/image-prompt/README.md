# Image Prompt Adapter

The bridge between production-neutral direction and a specific image generator. Everything
model-specific lives in `profiles/*.yaml`; the harness artifacts never name a model, which is what
lets the same episode drive a different generator next year.

```bash
python scripts/build_image_prompts.py _workspace/ep01 --profile comfyui
```

## Profiles

| Profile | Target | Cost |
|---|---|---|
| `comfyui.yaml` | Local ComfyUI with an SDXL-family or FLUX.1 schnell checkpoint | Free — no key, no account, fully offline |

## What a profile owns

| Key | Purpose |
|---|---|
| `prompt_style` | `tag` (comma-separated) or `prose`, depending on what the model parses well |
| `canvas` | Strip width, viewport height, generation pixel budget, rounding, section-split ratio |
| `style_anchor` | Base style, quality tags, and a tone map keyed to `normalized_input.yaml` |
| `negative` | Shared negative prompt |
| `shot` / `angle` | One phrase per controlled-vocabulary term — must cover the vocabulary completely |
| `text_in_art_keywords` | Direction phrases that ask for readable writing, flagged for lettering |
| `character_loras` | Per-character LoRA file, weight, and trigger word |
| `sampler_defaults` | Steps, CFG, sampler per model family |

A test asserts `shot` and `angle` cover `config/direction_vocabulary.yaml` completely — a term the
profile cannot translate would silently vanish from the prompt.

## Adding a profile

Copy `comfyui.yaml`, change the wording, keep every key. Two things to think about rather than copy:

- **Text.** A generator that renders your language legibly can bake balloons into the art; one that
  cannot must render clean plates and letter afterwards. The `comfyui` profile takes the second
  path because local diffusion models produce glyph-shaped noise for Korean. Set the negatives to
  match whichever choice the model supports.
- **Canvas.** `target_pixels` should sit at the model's trained resolution. Generating far outside
  it degrades quality faster than any prompt wording can recover.

## What the adapter does not do

It does not call a model, ship weights, or assume a runner. It writes prompt files, sizes, and
seeds; rendering is done by whatever tool you point at them.
