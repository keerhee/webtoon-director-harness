# Notice
This is an independent clean-room starter scaffold. It may interoperate with third-party tools through documented file inputs/outputs, but it does not redistribute their skill packages, prompts, assets, or source files. Review licenses/terms of external tools before publishing or commercializing integrations.

## Prior art

The Stage 3 image pipeline adopts patterns demonstrated by
[revfactory/webtoon-harness](https://github.com/revfactory/webtoon-harness) — reference sheets
rendered before panels, `LOC_*` location tokens to stop background drift, and a per-panel
validate-and-regenerate loop. Those are design patterns, independently implemented here for a free
local stack; no files, prompts, or assets from that project are copied into this repository.

Model weights used at Stage 3 carry their own licenses. FLUX.1 schnell is Apache-2.0; SDXL base and
community checkpoints vary, and several carry non-commercial terms. Check the license of the
specific checkpoint you download before publishing or selling the output.
