"""Stage 3 - image prompt construction.

Prompts must be deterministic and must carry every consistency device, because a
prompt defect is discovered only after a GPU has spent minutes on it.
"""

import json
import subprocess
import sys

import pytest

from harness.config import load_yaml
from harness.prompts import (
    build_panel_prompt,
    build_reference_sheets,
    character_tokens,
    load_profile,
    location_token,
    stable_seed,
    style_anchor,
)


@pytest.fixture(scope="module")
def profile(repo_root):
    return load_profile("comfyui", repo_root)


@pytest.fixture(scope="module")
def example(repo_root):
    base = repo_root / "examples" / "sample_episode"
    return (
        load_yaml(base / "06_handoff" / "panel_direction.yaml"),
        load_yaml(base / "06_handoff" / "continuity_state.yaml"),
        base,
    )


def _prompts(example, profile):
    direction, continuity, _ = example
    return [
        build_panel_prompt(p, episode_id=direction["episode_id"], profile=profile,
                           continuity=continuity, tone="tense, restrained")
        for p in direction["panels"]
    ]


def test_profile_covers_the_whole_vocabulary(repo_root, profile):
    """A shot the profile cannot translate would silently vanish from the prompt."""
    vocab = load_yaml(repo_root / "config" / "direction_vocabulary.yaml")
    assert set(profile["shot"]) == set(vocab["shot"])
    assert set(profile["angle"]) == set(vocab["angle"])


def test_seeds_are_stable_and_distinct():
    assert stable_seed("ep01", "P01") == stable_seed("ep01", "P01")
    assert stable_seed("ep01", "P01") != stable_seed("ep01", "P02")
    assert stable_seed("ep01", "P01") != stable_seed("ep02", "P01")


def test_build_is_deterministic(example, profile):
    first = [p.as_dict() for p in _prompts(example, profile)]
    second = [p.as_dict() for p in _prompts(example, profile)]
    assert first == second


def test_every_prompt_carries_the_style_anchor(example, profile):
    anchor = style_anchor(profile, "tense, restrained").split(",")[0].strip()
    for prompt in _prompts(example, profile):
        assert anchor in prompt.positive, prompt.panel_id


def test_every_prompt_carries_the_location_token(example, profile):
    for prompt in _prompts(example, profile):
        assert prompt.location_token.startswith("LOC_")
        assert prompt.location_token in prompt.positive, prompt.panel_id


def test_character_panels_carry_the_appearance_and_mark(example, profile):
    """A mark that swaps sides between panels reads as a different person."""
    with_mina = [p for p in _prompts(example, profile) if "mina" in p.characters]
    assert with_mina
    for prompt in with_mina:
        assert "mole" in prompt.positive
        assert "on the left" in prompt.positive
        assert "black hair" in prompt.positive


def test_insert_panel_has_no_character_tokens(example, profile):
    """P05a is an object insert - Mina is present only as a shadow."""
    p05a = next(p for p in _prompts(example, profile) if p.panel_id == "P05a")
    assert p05a.characters == []
    assert "mina_char" not in p05a.positive


def test_negatives_block_text_everywhere(example, profile):
    for prompt in _prompts(example, profile):
        for banned in ("text", "speech bubble", "watermark"):
            assert banned in prompt.negative, prompt.panel_id


def test_literal_none_never_reaches_the_prompt(example, profile):
    """'None - depth deliberately collapsed' is direction for a human, not a token."""
    for prompt in _prompts(example, profile):
        assert "None" not in prompt.positive, prompt.panel_id


def test_legible_text_conflict_is_flagged_not_silently_dropped(example, profile):
    p05a = next(p for p in _prompts(example, profile) if p.panel_id == "P05a")
    assert p05a.requires_lettered_prop_text
    assert "text" in p05a.negative  # the negative is kept; the conflict is handed to lettering


def test_tall_panels_are_sectioned(example, profile):
    prompts = {p.panel_id: p for p in _prompts(example, profile)}
    assert prompts["P07"].sections, "a 2.6-screen panel cannot be one generation"
    assert len(prompts["P07"].sections) >= 2
    assert not prompts["P01"].sections


def test_generation_size_is_model_friendly(example, profile):
    for prompt in _prompts(example, profile):
        assert prompt.gen_width % 64 == 0 and prompt.gen_height % 64 == 0
        assert max(prompt.gen_width, prompt.gen_height) <= profile["canvas"]["max_side"]


def test_panel_height_drives_target_size(example, profile):
    prompts = {p.panel_id: p for p in _prompts(example, profile)}
    assert prompts["P07"].target_height > prompts["P01"].target_height * 4


def test_reference_sheets_exist_for_every_character(example, profile):
    _, continuity, _ = example
    sheets = build_reference_sheets(continuity, profile, "tense")
    assert set(sheets) == set(character_tokens(continuity))
    for sheet in sheets.values():
        assert "reference sheet" in sheet["turnaround"]
        assert "back view" in sheet["turnaround"]
        assert "expression" in sheet["expressions"]


def test_location_token_formatting():
    assert location_token({"id": "lab b3"}) == "LOC_LAB_B3"
    assert location_token(None) == "LOC_UNSPECIFIED"


def test_committed_example_output_is_up_to_date(repo_root, tmp_path):
    """The committed 07_prompts/ must match a fresh build, or it is documentation of a lie."""
    example_dir = repo_root / "examples" / "sample_episode"
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "build_image_prompts.py"),
         str(example_dir), "--out", str(tmp_path)],
        capture_output=True, text=True, cwd=repo_root,
    )
    assert result.returncode == 0, result.stderr

    fresh = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    committed = json.loads(
        (example_dir / "07_prompts" / "manifest.json").read_text(encoding="utf-8")
    )
    assert fresh == committed, "run scripts/build_image_prompts.py examples/sample_episode"


def test_lettering_spec_lists_the_only_line(repo_root):
    text = (repo_root / "examples" / "sample_episode" / "07_prompts" / "lettering.md").read_text(
        encoding="utf-8"
    )
    assert "P05b" in text
    assert "Prop text" in text
    assert "P05a" in text


# --- 77-token CLIP budget -------------------------------------------------
# Found by actually rendering: a 224-token prompt was truncated by SD 1.5 to its
# first 77 tokens, which were all style and character tags. P02 - an insert of a
# door latch - came back as two portraits, because every word of direction had
# been silently discarded.


def test_compact_prompt_fits_the_clip_budget(example, profile):
    from harness.prompts import estimate_clip_tokens

    budget = profile["token_budget"]
    for prompt in _prompts(example, profile):
        assert estimate_clip_tokens(prompt.positive_compact) <= budget, prompt.panel_id


def test_full_prompt_is_kept_for_chunking_runners(example, profile):
    """ComfyUI chunks past 77 tokens, so the full prompt still has a consumer."""
    for prompt in _prompts(example, profile):
        assert len(prompt.positive) > len(prompt.positive_compact)


def test_compact_prompt_leads_with_style_then_shot(example, profile):
    prompts = {p.panel_id: p for p in _prompts(example, profile)}
    compact = prompts["P01"].positive_compact
    assert compact.startswith("korean webtoon style")
    assert "extreme wide shot" in compact.split(",")[3]


def test_insert_panels_do_not_spend_the_budget_on_faces(example, profile):
    """The bug that produced portraits for a door latch."""
    p02 = next(p for p in _prompts(example, profile) if p.panel_id == "P02")
    assert "extreme close-up of a single object" in p02.positive_compact
    assert "Latch plate" in p02.positive_compact
    assert "black hair" not in p02.positive_compact


def test_character_panels_still_carry_identity_in_compact(example, profile):
    p03 = next(p for p in _prompts(example, profile) if p.panel_id == "P03")
    assert "mina_char" in p03.positive_compact
    assert "black hair" in p03.positive_compact
    assert "mole" in p03.positive_compact


def test_compact_never_truncates_mid_phrase(example, profile):
    """"the object fills the" costs tokens and reads as noise. Cut at a comma."""
    for prompt in _prompts(example, profile):
        for tag in prompt.positive_compact.split(","):
            assert not tag.strip().endswith((" the", " a", " of", " and", " with")), prompt.panel_id


def test_compact_drops_literal_none(example, profile):
    for prompt in _prompts(example, profile):
        assert "None" not in prompt.positive_compact, prompt.panel_id


def test_token_estimate_is_conservative():
    from harness.prompts import estimate_clip_tokens

    assert estimate_clip_tokens("a b c") >= 3
    assert estimate_clip_tokens("") == 2
