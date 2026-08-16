"""Tests for the batch layer + the four converted batch/*.yaml files.

These double as the loader check the task asks for: every yaml in batch/ must validate against
models.Batch, and the 30 rows must reconstruct the 30-day plan (days 1-30, unique ids, W1 full spec).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from lumora_sprint.batch import (
    expand_outline_hint,
    fatigue_check,
    find_post,
    load_all,
    load_batch,
    next_unposted,
    validate_spec,
)
from lumora_sprint.config import FatigueCfg, load_account, load_engine
from lumora_sprint.models import Batch, ImageSpec, PostSpec

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "batch"

# The single deliberate spec-vs-config conflict carried over verbatim from 01-batch-30day.md:
# the day-29 Hero is written as C2 x Historical x M2, which breaks both the oracle-theme rule and
# the C2 media allowlist. It is kept (not silently rewritten) so validate_spec surfaces it.
KNOWN_CONFLICT_ID = "L4-D29"


@pytest.fixture(scope="module")
def account():
    return load_account()


@pytest.fixture(scope="module")
def engine():
    return load_engine()


@pytest.fixture(scope="module")
def batches():
    return load_all(BATCH_DIR)


# ── the yaml files themselves ──────────────────────────────────────────────


def test_all_four_yaml_files_load_into_batch():
    files = sorted(BATCH_DIR.glob("*.yaml"))
    assert [f.name for f in files] == [
        "2026-07-w1.yaml",
        "2026-07-w2.yaml",
        "2026-07-w3.yaml",
        "2026-07-w4.yaml",
    ]
    for f in files:
        b = load_batch(f)
        assert isinstance(b, Batch)
        assert b.batch_id == f.stem
        assert b.account_handle == "@มูมีแสง"
        assert b.posts, f"{f.name} has no posts"


def test_load_all_is_sorted_and_covers_30_days(batches):
    assert [b.batch_id for b in batches] == [
        "2026-07-w1",
        "2026-07-w2",
        "2026-07-w3",
        "2026-07-w4",
    ]
    posts = [p for b in batches for p in b.posts]
    assert len(posts) == 30
    assert sorted(p.day for p in posts) == list(range(1, 31))
    assert len({p.post_id for p in posts}) == 30


def test_post_id_encodes_week_and_day(batches):
    for b in batches:
        for p in b.posts:
            assert p.post_id == f"L{p.week}-D{p.day:02d}"
            assert b.batch_id.endswith(f"w{p.week}")


def test_week1_is_full_spec_and_weeks_2_to_4_are_outlines(batches):
    by_week = {b.batch_id[-2:]: b for b in batches}
    for p in by_week["w1"].posts:
        assert p.full_spec is True
        assert p.caption.strip(), f"{p.post_id} full spec needs a caption"
        assert p.hashtags, f"{p.post_id} full spec needs hashtags"
        assert p.image is not None and p.image.prompt.strip()
        assert p.affiliate_angle
    for key in ("w2", "w3", "w4"):
        for p in by_week[key].posts:
            assert p.full_spec is False
            assert p.caption == ""          # empty beats fake
            assert p.image is None
            assert p.concept and p.hook     # outline still carries combo + concept + hook


def test_day1_is_the_launch_oracle(batches):
    d1 = find_post(batches, "L1-D01")
    assert (d1.content_pillar, d1.theme, d1.media) == ("C2", "Cosmic", "M11")
    assert d1.hook_type == "curiosity-choice"
    assert d1.funnel_stage == "Hub"
    assert d1.day == 1 and d1.week == 1
    assert d1.image is not None and d1.image.seed == 10101 and d1.image.count == 1
    assert "การ์ดใบแรกของช่องนี้" in d1.caption


def test_carousel_days_ask_for_five_cards(batches):
    d6 = find_post(batches, 6)
    assert d6.media == "M2"
    assert d6.image is not None and d6.image.count == 5


def test_aesthetic_week_map_and_fixed_oracle_look(batches, account):
    """Art engine rotates per aesthetic_weeks; the oracle holds one look (spec §Aesthetic-week map)."""
    for b in batches:
        for p in b.posts:
            if p.content_pillar in {"C1", "C6"}:
                assert p.theme == account.aesthetic_weeks[p.week], p.post_id
            elif p.content_pillar == "C2" and p.post_id != KNOWN_CONFLICT_ID:
                assert p.theme == account.oracle_theme, p.post_id


def test_the_single_hero_is_day_29(batches):
    heroes = [p for b in batches for p in b.posts if p.funnel_stage == "Hero"]
    assert [p.post_id for p in heroes] == [KNOWN_CONFLICT_ID]


def test_sacred_imagery_rows_carry_homage_watch(batches):
    for b in batches:
        for p in b.posts:
            if p.content_pillar == "C1":
                assert p.homage_watch is True, f"{p.post_id} is deity imagery — needs homage_watch"


# ── find_post ──────────────────────────────────────────────────────────────


def test_find_post_by_id_day_int_and_day_string(batches):
    assert find_post(batches, "L2-D09").day == 9
    assert find_post(batches, 9).post_id == "L2-D09"
    assert find_post(batches, "9").post_id == "L2-D09"
    assert find_post(batches, "D09").post_id == "L2-D09"
    with pytest.raises(KeyError):
        find_post(batches, "L9-D99")


# ── validate_spec ──────────────────────────────────────────────────────────


def test_validate_day1_has_no_problems(batches, account):
    assert validate_spec(find_post(batches, 1), account) == []


def test_validate_whole_batch_flags_only_the_known_day29_conflict(batches, account):
    flagged = {p.post_id: validate_spec(p, account) for b in batches for p in b.posts}
    bad = {pid: probs for pid, probs in flagged.items() if probs}
    assert list(bad) == [KNOWN_CONFLICT_ID]
    joined = " ".join(bad[KNOWN_CONFLICT_ID])
    assert "legality" in joined and "oracle theme" in joined


def _spec(**over) -> PostSpec:
    """A minimal legal C2 oracle spec; pass keyword overrides to break exactly one rule."""
    base: dict = {
        "post_id": "L1-D01",
        "day": 1,
        "week": 1,
        "content_pillar": "C2",
        "theme": "Cosmic",
        "media": "M11",
        "image": ImageSpec(prompt="x"),
    }
    base.update(over)
    return PostSpec(**base)


def test_parked_pillar_c4_fails_legality(account):
    fake = _spec(post_id="L1-D02", day=2, content_pillar="C4", theme="Pastoral", media="M1")
    problems = validate_spec(fake, account)
    assert problems, "C4 travelogue is parked — must not validate"
    assert any(p.startswith("legality:") for p in problems)
    assert any("parked pillar" in p for p in problems)


def test_oracle_theme_rule(account):
    problems = validate_spec(_spec(theme="Pastoral"), account)
    assert any("oracle theme" in p for p in problems)


def test_media_not_allowed_for_pillar(account):
    # C2's allowlist is [M11, M1]; M2 is legal for the account but not for the oracle pillar.
    problems = validate_spec(_spec(media="M2"), account)
    assert any("media M2 not allowed for C2" in p for p in problems)


def test_full_spec_ai_visual_without_image_is_a_problem(account):
    problems = validate_spec(_spec(image=None, full_spec=True, ai_visual=True), account)
    assert any(p.startswith("image:") for p in problems)
    # an outline row is allowed to have no image yet
    assert validate_spec(_spec(image=None, full_spec=False), account) == []


def test_bad_hook_type_is_rejected_by_the_contract():
    with pytest.raises(ValueError):
        _spec(hook_type="ชวนเลือก")


# ── fatigue_check ──────────────────────────────────────────────────────────


def test_fatigue_detects_same_c_m_consecutive(engine):
    spec = _spec(post_id="L2-D13", day=13, week=2, content_pillar="C6", theme="Historical", media="M2")
    recent = [("C6", "Future-tech", "M2"), ("C2", "Cosmic", "M1")]   # recent[0] = the post just before
    warnings = fatigue_check(spec, recent, engine.fatigue)
    assert any("same C+M as the previous post" in w for w in warnings)


def test_fatigue_detects_exact_combo_inside_the_window(engine):
    assert engine.fatigue.same_combo_window_posts == 3
    spec = _spec(post_id="L1-D06", day=6, week=1, content_pillar="C6", theme="Future-tech", media="M2")
    recent = [("C1", "Future-tech", "M1"), ("C9", "Contemporary", "M1"), ("C6", "Future-tech", "M2")]
    warnings = fatigue_check(spec, recent, engine.fatigue)
    assert any("exact combo" in w for w in warnings)
    # …and not when the repeat falls outside the window
    assert fatigue_check(spec, recent[:2] + [("C2", "Cosmic", "M1")] * 2, engine.fatigue) == []


def test_fatigue_exempts_the_oracle_anchor(engine):
    assert "C2" in engine.fatigue.exempt_pillars
    spec = _spec()  # C2 x Cosmic x M11
    assert fatigue_check(spec, [("C2", "Cosmic", "M11")], engine.fatigue) == []


def test_fatigue_no_warnings_on_an_empty_history(engine):
    spec = _spec(content_pillar="C1", theme="Future-tech", media="M1")
    assert fatigue_check(spec, [], engine.fatigue) == []


def test_fatigue_respects_the_config_toggles():
    off = FatigueCfg(no_same_c_m_consecutive=False, same_combo_window_posts=0)
    spec = _spec(content_pillar="C1", theme="Future-tech", media="M1")
    assert fatigue_check(spec, [("C1", "Future-tech", "M1")], off) == []


def test_planned_batch_has_no_consecutive_c_m_repeats(batches, engine):
    """The 30-day plan itself should be clean under the configured fatigue rules."""
    posts = sorted((p for b in batches for p in b.posts), key=lambda p: p.day)
    recent: list[tuple[str, str, str]] = []
    for p in posts:
        assert fatigue_check(p, recent, engine.fatigue) == [], p.post_id
        recent.insert(0, (p.content_pillar, p.theme, p.media))


# ── next_unposted ──────────────────────────────────────────────────────────


def test_next_unposted_walks_the_days_in_order(batches):
    assert next_unposted(batches, set()).post_id == "L1-D01"
    assert next_unposted(batches, {"L1-D01"}).post_id == "L1-D02"
    assert next_unposted(batches, {"L1-D02"}).post_id == "L1-D01"   # gaps are skipped, lowest day wins
    published = {p.post_id for b in batches for p in b.posts if p.day <= 7}
    assert next_unposted(batches, published).post_id == "L2-D08"


def test_next_unposted_returns_none_when_the_batch_is_done(batches):
    everything = {p.post_id for b in batches for p in b.posts}
    assert next_unposted(batches, everything) is None


# ── expand_outline_hint ────────────────────────────────────────────────────


def test_expand_outline_hint_prepares_the_ask_for_an_outline_row(batches):
    spec = find_post(batches, "L2-D09")
    hint = expand_outline_hint(spec)
    assert "lumora-content-batch" in hint
    assert "L2-D09" in hint
    assert "C1 x Historical x M1" in hint
    assert spec.hook in hint and spec.concept in hint
    assert "2026-07-w2.yaml" in hint
    assert "homage_watch" in hint          # sacred-imagery row carries the reminder
    assert "full_spec: true" in hint


def test_expand_outline_hint_flags_carousel_count(batches):
    hint = expand_outline_hint(find_post(batches, 13))
    assert "5 — carousel" in hint


def test_expand_outline_hint_is_a_noop_for_full_spec_rows(batches):
    hint = expand_outline_hint(find_post(batches, 1))
    assert hint == "L1-D01 is already full_spec — nothing to expand."


# ── loader edge cases ──────────────────────────────────────────────────────


def test_load_all_on_a_missing_dir_is_empty(tmp_path):
    assert load_all(tmp_path / "nope") == []


def test_load_batch_rejects_a_broken_row(tmp_path):
    bad = tmp_path / "2026-07-w9.yaml"
    bad.write_text(
        "batch_id: 2026-07-w9\naccount_handle: '@x'\nposts:\n  - post_id: nope\n    day: 1\n"
        "    week: 9\n    content_pillar: C2\n    theme: Cosmic\n    media: M11\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_batch(bad)
