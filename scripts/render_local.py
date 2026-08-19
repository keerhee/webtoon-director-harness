#!/usr/bin/env python3
"""Render panels from `07_prompts/manifest.json` on local hardware, CPU included.

    python scripts/render_local.py examples/sample_episode --only P01
    python scripts/render_local.py _workspace/ep01 --scale 0.5

A no-GPU fallback runner. ComfyUI is the recommended path when a CUDA GPU exists;
this script exists so the pipeline is verifiable on a laptop with integrated graphics.
Same prompts, same seeds, same manifest - only the executor differs.

Defaults to Stable Diffusion 1.5 with LCM-LoRA (8 steps), which is the only combination
that renders in a sane time on a CPU and still permits commercial use.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from harness.prompts import stable_seed  # noqa: E402

BASE_MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
LCM_LORA = "latent-consistency/lcm-lora-sdv1-5"


def _round64(value: int) -> int:
    return max(256, int(round(value / 64)) * 64)


def load_pipeline(model: str, lcm: bool, threads: int | None):
    import torch
    from diffusers import LCMScheduler, StableDiffusionPipeline

    if threads:
        torch.set_num_threads(threads)

    pipe = StableDiffusionPipeline.from_pretrained(
        model, torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False
    )
    if lcm:
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
        pipe.load_lora_weights(LCM_LORA)
        pipe.fuse_lora()
    pipe.set_progress_bar_config(disable=True)
    pipe.to("cpu")
    # Attention slicing trades a little speed for a much smaller peak footprint,
    # which is what keeps this inside a 6 GB working set.
    pipe.enable_attention_slicing()
    return pipe


def render(pipe, prompt: str, negative: str, width: int, height: int,
           seed: int, steps: int, guidance: float):
    import torch

    generator = torch.Generator(device="cpu").manual_seed(int(seed))
    return pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=generator,
    ).images[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("episode_dir", type=Path)
    parser.add_argument("--out", type=Path, default=None, help="default: <episode>/08_panels")
    parser.add_argument("--model", default=BASE_MODEL)
    parser.add_argument("--no-lcm", action="store_true", help="full sampling instead of LCM 8-step")
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--guidance", type=float, default=1.5, help="LCM wants ~1.0-2.0")
    parser.add_argument("--scale", type=float, default=0.5,
                        help="fraction of the manifest generation size (CPU default: 0.5)")
    parser.add_argument("--only", nargs="*", default=None, help="panel ids, or 'refs'")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--full-prompt", action="store_true",
                        help="use the full prompt instead of the 77-token compact one "
                             "(diffusers truncates, so this loses the panel direction)")
    args = parser.parse_args(argv)

    manifest_path = args.episode_dir / "07_prompts" / "manifest.json"
    if not manifest_path.is_file():
        print(f"No manifest at {manifest_path} - run build_image_prompts.py first", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    out = args.out or (args.episode_dir / "08_panels")
    out.mkdir(parents=True, exist_ok=True)

    jobs: list[tuple[str, str, str, int, int, int]] = []
    wanted = set(args.only or [])

    if not wanted or "refs" in wanted:
        for char_id, sheet in (manifest.get("reference_sheets") or {}).items():
            for kind in ("turnaround", "expressions"):
                key = kind if args.full_prompt else f"{kind}_compact"
                jobs.append((f"REF_{char_id}_{kind}", sheet.get(key, sheet[kind]),
                             sheet["negative"], 704, 448,
                             stable_seed(manifest.get("episode_id", "ep"), f"REF_{char_id}_{kind}")))

    for panel in manifest.get("panels", []):
        if wanted and panel["panel_id"] not in wanted:
            continue
        text = panel["positive"] if args.full_prompt else panel.get(
            "positive_compact", panel["positive"])
        gen_w, gen_h = panel["gen_size"]
        w = _round64(int(gen_w * args.scale))
        h = _round64(int(gen_h * args.scale))
        if panel.get("sections"):
            for section in panel["sections"]:
                jobs.append((f"{panel['panel_id']}_s{section['index']}",
                             text + f", {section['covers']}",
                             panel["negative"], w, h, panel["seed"] + section["index"]))
        else:
            jobs.append((panel["panel_id"], text, panel["negative"],
                         w, h, panel["seed"]))

    if args.skip_existing:
        jobs = [j for j in jobs if not (out / f"{j[0]}.png").exists()]

    if not jobs:
        print("Nothing to render.")
        return 0

    print(f"Model   : {args.model}{'' if args.no_lcm else ' + LCM-LoRA'}")
    print(f"Steps   : {args.steps}   guidance {args.guidance}   scale {args.scale}")
    print(f"Jobs    : {len(jobs)} -> {out}")
    print("Loading pipeline (first run downloads the model)...", flush=True)

    started = time.time()
    pipe = load_pipeline(args.model, not args.no_lcm, int(os.cpu_count() or 4))
    print(f"Pipeline ready in {time.time() - started:.0f}s", flush=True)

    for index, (name, positive, negative, width, height, seed) in enumerate(jobs, 1):
        t0 = time.time()
        image = render(pipe, positive, negative, width, height, seed, args.steps, args.guidance)
        path = out / f"{name}.png"
        image.save(path)
        print(f"[{index}/{len(jobs)}] {name}  {width}x{height}  seed {seed}  "
              f"{time.time() - t0:.0f}s  -> {path.name}", flush=True)

    print(f"Done in {(time.time() - started) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
