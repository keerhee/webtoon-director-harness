"""Turn panel direction into image-generation prompts.

The harness artifacts stay production-neutral; all model-specific wording lives in
`adapters/image-prompt/profiles/*.yaml`. This module is the deterministic bridge:
same direction plus same profile always yields the same prompts and the same seeds,
so a re-render reproduces a panel exactly and a diff shows what actually changed.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from harness.config import ConfigError, find_repo_root, load_yaml


@dataclass
class RenderSection:
    """One generation pass for a panel too tall to render in a single image."""

    index: int
    of: int
    gen_width: int
    gen_height: int
    covers: str


@dataclass
class PanelPrompt:
    panel_id: str
    positive: str
    negative: str
    target_width: int
    target_height: int
    gen_width: int
    gen_height: int
    seed: int
    characters: list[str] = field(default_factory=list)
    location_token: str = ""
    sections: list[RenderSection] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def requires_lettered_prop_text(self) -> bool:
        return any("legible writing" in n for n in self.notes)

    @property
    def upscale(self) -> float:
        return round(self.target_height / self.gen_height, 3) if self.gen_height else 1.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "panel_id": self.panel_id,
            "positive": self.positive,
            "negative": self.negative,
            "target_size": [self.target_width, self.target_height],
            "gen_size": [self.gen_width, self.gen_height],
            "upscale": self.upscale,
            "seed": self.seed,
            "characters": self.characters,
            "location_token": self.location_token,
            "sections": [vars(s) for s in self.sections],
            "notes": self.notes,
        }


def load_profile(name: str = "comfyui", root: Path | None = None) -> dict[str, Any]:
    """Load an image-prompt profile from `adapters/image-prompt/profiles/`."""
    root = root or find_repo_root()
    path = root / "adapters" / "image-prompt" / "profiles" / f"{name}.yaml"
    if not path.is_file():
        raise ConfigError(f"No such profile: {name} (looked in {path.parent})")
    return load_yaml(path)


def stable_seed(episode_id: str, panel_id: str) -> int:
    """A seed that depends only on the panel's identity, never on wall-clock time.

    Re-running the builder must not change seeds; otherwise a re-render of one panel
    silently changes every other panel's output.
    """
    digest = hashlib.sha256(f"{episode_id}:{panel_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % (2**31)


def location_token(location: dict[str, Any] | None) -> str:
    """`LOC_LAB_B3` - injected into every panel of a scene so the background cannot drift."""
    if not location or not location.get("id"):
        return "LOC_UNSPECIFIED"
    return "LOC_" + str(location["id"]).upper().replace(" ", "_").replace("-", "_")


def character_tokens(continuity: dict[str, Any]) -> dict[str, str]:
    """Immutable appearance tokens per character, built from continuity state.

    Everything here is repeated verbatim in every panel the character appears in.
    Identifying marks carry their side, because a mole that swaps cheeks between
    panels reads as a different person.
    """
    tokens: dict[str, str] = {}
    entities = (continuity or {}).get("entities") or {}
    for char in entities.get("characters") or []:
        parts = [str(char.get("id", "character"))]
        if char.get("appearance"):
            parts.append(str(char["appearance"]))
        if char.get("costume"):
            parts.append(str(char["costume"]))
        for mark in char.get("marks") or []:
            if isinstance(mark, dict):
                side = f" on the {mark['side']}" if mark.get("side") else ""
                parts.append(f"{mark.get('mark', 'distinguishing mark')}{side}")
            else:
                parts.append(str(mark))
        for injury in char.get("injuries") or []:
            if isinstance(injury, dict) and injury.get("location"):
                parts.append(f"injury on {injury['location']}")
        held = [str(o) for o in char.get("held_objects") or []]
        if held:
            parts.append("holding " + ", ".join(held))
        cleaned = [str(p).strip().rstrip(".") for p in parts if p and str(p).strip()]
        tokens[str(char.get("id", "character"))] = ", ".join(cleaned)
    return tokens


def _round_to(value: float, step: int) -> int:
    return max(step, int(round(value / step) * step))


def _generation_size(width: int, height: int, canvas: dict[str, Any]) -> tuple[int, int]:
    """Pick a generation size near the model's trained pixel budget, keeping aspect."""
    target_pixels = float(canvas.get("target_pixels", 1_048_576))
    step = int(canvas.get("round_to", 64))
    max_side = int(canvas.get("max_side", 1536))

    scale = math.sqrt(target_pixels / max(width * height, 1))
    gen_w = _round_to(width * scale, step)
    gen_h = _round_to(height * scale, step)

    if max(gen_w, gen_h) > max_side:
        shrink = max_side / max(gen_w, gen_h)
        gen_w = _round_to(gen_w * shrink, step)
        gen_h = _round_to(gen_h * shrink, step)
    return gen_w, gen_h


def _sections(panel: dict[str, Any], width: int, height: int,
              canvas: dict[str, Any]) -> list[RenderSection]:
    """Split a very tall panel into overlapping passes.

    A 2.6-screen panel is not one image any diffusion model was trained to make.
    Rendering it in sections preserves the scroll reveal instead of squashing it.
    """
    split_at = float(canvas.get("section_split_ratio", 2.0))
    ratio = height / max(width, 1)
    if ratio < split_at:
        return []

    count = math.ceil(ratio / 1.5)
    section_height = int(height / count * (1 + float(canvas.get("section_overlap", 0.15))))
    gen_w, gen_h = _generation_size(width, section_height, canvas)
    covers = ["upper", "middle", "lower"] if count == 3 else None
    out = []
    for i in range(count):
        if covers:
            where = covers[i]
        else:
            where = "upper" if i == 0 else ("lower" if i == count - 1 else f"middle {i}")
        out.append(RenderSection(index=i + 1, of=count, gen_width=gen_w, gen_height=gen_h,
                                 covers=f"{where} portion of the panel"))
    return out


def style_anchor(profile: dict[str, Any], tone: str | None = None) -> str:
    anchor = profile.get("style_anchor") or {}
    parts = [anchor.get("base", "")]
    tone_map = anchor.get("tone_map") or {}
    for word in (tone or "").replace(",", " ").split():
        if word.strip() in tone_map:
            parts.append(tone_map[word.strip()])
    parts.append(anchor.get("quality", ""))
    return ", ".join(p for p in parts if p)


def _lora_fragment(char_id: str, profile: dict[str, Any]) -> str:
    entry = (profile.get("character_loras") or {}).get(char_id) or {}
    fragments = []
    if entry.get("lora"):
        fragments.append(f"<lora:{entry['lora']}:{entry.get('weight', 0.8)}>")
    if entry.get("trigger"):
        fragments.append(str(entry["trigger"]))
    return ", ".join(fragments)


def _requires_legible_text(panel: dict[str, Any], profile: dict[str, Any]) -> str:
    """Detect direction that asks for readable writing inside the image.

    A panel whose beat depends on the reader recognizing a name conflicts with the
    text negatives. Flag it rather than silently dropping one side of the conflict.
    """
    keywords = profile.get("text_in_art_keywords") or ["legible", "readable", "name visible"]
    for key in ("composition", "foreground", "background", "lighting", "purpose"):
        raw = str(panel.get(key, ""))
        lowered = raw.lower()
        for word in keywords:
            if str(word).lower() in lowered:
                # Quote the clause itself, so the letterer knows what must be readable.
                for clause in raw.replace(";", ".").split("."):
                    if str(word).lower() in clause.lower():
                        return clause.strip()
                return raw.strip()
    return ""


def _panel_characters(panel: dict[str, Any], continuity: dict[str, Any]) -> list[str]:
    """Which characters are in this panel, per the continuity state's panel_states."""
    for state in (continuity or {}).get("panel_states") or []:
        if state.get("panel_id") == panel.get("panel_id"):
            return [str(c) for c in state.get("characters_present") or []]
    return []


def build_panel_prompt(
    panel: dict[str, Any],
    *,
    episode_id: str,
    profile: dict[str, Any],
    continuity: dict[str, Any] | None = None,
    tone: str | None = None,
) -> PanelPrompt:
    """Compose one panel's positive prompt, negative prompt, size, and seed."""
    continuity = continuity or {}
    canvas = profile.get("canvas") or {}
    panel_id = str(panel.get("panel_id", "P00"))

    width = int(canvas.get("width", 800))
    height = int(round(float(panel.get("panel_height", 1.0)) * int(canvas.get("viewport_height", 1280))))

    present = _panel_characters(panel, continuity)
    tokens = character_tokens(continuity)
    location = ((continuity.get("entities") or {}).get("location")) or {}
    loc_token = location_token(location)

    fragments: list[str] = [style_anchor(profile, tone)]

    for char_id in present:
        lora = _lora_fragment(char_id, profile)
        if lora:
            fragments.append(lora)
        if tokens.get(char_id):
            fragments.append(tokens[char_id])

    fragments.append(f"{loc_token} ({location.get('geography', 'unspecified location')})")

    shot = profile.get("shot", {}).get(panel.get("shot"))
    angle = profile.get("angle", {}).get(panel.get("angle"))
    fragments += [f for f in (shot, angle) if f]

    for key in ("composition", "character_blocking", "gaze", "foreground", "background", "lighting"):
        value = panel.get(key)
        # "None - depth deliberately collapsed" is direction for a human, not a prompt token.
        if value and not str(value).strip().lower().startswith("none"):
            fragments.append(str(value))

    if panel.get("dialogue_space") and "none" not in str(panel["dialogue_space"]).lower():
        fragments.append(profile.get("dialogue_space_tag", ""))
        fragments.append(str(panel["dialogue_space"]))

    positive = ", ".join(f.strip().rstrip(".") for f in fragments if f and str(f).strip())

    gen_w, gen_h = _generation_size(width, height, canvas)
    sections = _sections(panel, width, height, canvas)
    if sections:
        gen_w, gen_h = sections[0].gen_width, sections[0].gen_height

    notes: list[str] = []
    prop_text = _requires_legible_text(panel, profile)
    if prop_text:
        notes.append(
            "Direction requires legible writing in the art (" + prop_text + "). Local diffusion "
            "models cannot render Korean reliably, so the plate stays text-free and the writing is "
            "added at lettering - see lettering.md. Do not remove the text negatives."
        )
    if sections:
        notes.append(
            f"Tall panel ({height}px): render {len(sections)} overlapping sections and stitch. "
            "Keep the payoff at the bottom - the scroll reveal is the beat."
        )
    if panel.get("full_width"):
        notes.append("Full-width panel: no side margin in the strip.")
    if panel.get("dialogue"):
        notes.append("Carries dialogue: art is rendered text-free; balloons are lettered afterwards.")

    return PanelPrompt(
        panel_id=panel_id,
        positive=positive,
        negative=" ".join(str(profile.get("negative", "")).split()),
        target_width=width,
        target_height=height,
        gen_width=gen_w,
        gen_height=gen_h,
        seed=stable_seed(episode_id, panel_id),
        characters=present,
        location_token=loc_token,
        sections=sections,
        notes=notes,
    )


def build_reference_sheets(continuity: dict[str, Any], profile: dict[str, Any],
                           tone: str | None = None) -> dict[str, dict[str, str]]:
    """Turnaround and expression sheets - rendered first, and the anchor for every panel.

    Text tokens alone do not hold a face steady across fifty panels. The sheet is what
    a LoRA is trained on, or what an IP-Adapter references, and what the validator
    compares each panel against.
    """
    anchor = style_anchor(profile, tone)
    sheets = {}
    for char_id, tokens in character_tokens(continuity).items():
        lora = _lora_fragment(char_id, profile)
        head = ", ".join(f for f in (anchor, lora, tokens) if f)
        sheets[char_id] = {
            "turnaround": (
                f"{head}, character reference sheet, model sheet, same character repeated, "
                "front view, three-quarter view, side view, back view, full body, "
                "neutral grey background, even flat lighting, neutral expression, "
                "identifying marks clearly visible and on the correct side"
            ),
            "expressions": (
                f"{head}, character expression sheet, four head-and-shoulders portraits of the same "
                "character, neutral, alarmed, guarded, recognition, neutral grey background, "
                "even flat lighting"
            ),
            "negative": " ".join(str(profile.get("negative", "")).split()),
        }
    return sheets
