"""Packet tests — the loop must stop at an approved folder on disk, and refuse to skip the gate."""
from __future__ import annotations

import json

import pytest

from lumora_sprint.compliance import run_compliance
from lumora_sprint.config import load_account, load_engine
from lumora_sprint.models import GeneratedImage, ImageSpec, PacketStatus, PostSpec
from lumora_sprint.packet import (
    CAPTION_FILE,
    CHECKLIST_FILE,
    HASHTAGS_FILE,
    META_FILE,
    PacketRefused,
    approve_packet,
    build_packet,
    load_packet,
    mark_published,
    write_packet,
)

# Day-1 of the real batch (01-batch-30day.md) — kept local so the two test modules stay independent.
DAY1_HOOK = "การ์ดใบแรกของช่องนี้ — เลือกใบที่ตาไปหยุดก่อน 🌌"
DAY1_CAPTION = (
    "การ์ดใบแรกของช่องนี้ — เลือกใบที่ตาไปหยุดก่อน 🌌\n"
    "ซ้าย = เริ่มใหม่ · กลาง = อยู่กับปัจจุบัน · ขวา = ปล่อยของเก่า\n"
    "เราไม่ได้มาทำนายว่าพรุ่งนี้จะเป็นไง — แค่ชวนถามตัวเองว่า *วันนี้* อยากถือแสงแบบไหนไป\n"
    "เซฟใบที่ใช่ไว้ แล้วคอมเมนต์เลขที่เลือกมาให้ดูหน่อย"
)
DAY1_HASHTAGS = ["#การ์ดวันนี้", "#สายมู", "#มูมีแสง", "#ไพ่ออราเคิล", "#cosmic", "#AIart"]


def make_spec(**over) -> PostSpec:
    base: dict = {
        "post_id": "L1-D01",
        "day": 1,
        "week": 1,
        "content_pillar": "C2",
        "theme": "Cosmic",
        "media": "M11",
        "funnel_stage": "Hub",
        "jtbd": "ช่วยให้รู้สึกสงบ + ตั้งต้นวันได้",
        "hook_type": "curiosity-choice",
        "concept": "การ์ดเปิดช่อง แสงแรก",
        "hook": DAY1_HOOK,
        "caption": DAY1_CAPTION,
        "hashtags": list(DAY1_HASHTAGS),
        "affiliate_angle": "none",
        "ai_visual": True,
        "homage_watch": False,
        "image": ImageSpec(prompt="Three ethereal oracle cards floating above open palms, cosmic nebula"),
        "full_spec": True,
    }
    base.update(over)
    return PostSpec(**base)


@pytest.fixture
def account():
    return load_account()


@pytest.fixture
def engine():
    cfg = load_engine()
    cfg.llm.enabled = False
    return cfg


def make_image(tmp_path, name: str = "L1-D01-1.png") -> GeneratedImage:
    src = tmp_path / name
    src.write_bytes(b"\x89PNG\r\n\x1a\n fake")
    return GeneratedImage(
        path=str(src),
        provider="stub",
        model="stub-placeholder",
        seed=10101,
        prompt="Three ethereal oracle cards",
        est_cost_usd=0.0,
    )


# ── build + write + load ───────────────────────────────────────────────────


def test_build_write_load_roundtrip(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec()
    report = run_compliance(spec, account, engine)
    packet = build_packet(spec, account, engine, [make_image(tmp_path)], report)

    assert packet.status is PacketStatus.draft
    assert packet.brand_id == account.brand_id
    assert packet.account_handle == account.account_handle
    assert packet.ai_labeled_reminder is True

    pdir = write_packet(packet, out)
    assert pdir == out / "L1-D01"
    for name in (META_FILE, CAPTION_FILE, HASHTAGS_FILE, CHECKLIST_FILE):
        assert (pdir / name).is_file(), f"missing {name}"

    reloaded = load_packet(out, "L1-D01")
    assert reloaded.post_id == packet.post_id
    assert reloaded.status is PacketStatus.draft
    assert reloaded.spec.caption == DAY1_CAPTION
    assert reloaded.compliance is not None
    assert reloaded.images[0].seed == 10101

    meta = json.loads((pdir / META_FILE).read_text(encoding="utf-8"))
    assert meta["brand_id"] == account.brand_id  # brand_id on every row, from day 1


def test_caption_file_appends_hashtags(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec()
    packet = build_packet(spec, account, engine, [], run_compliance(spec, account, engine))
    pdir = write_packet(packet, out)

    caption = (pdir / CAPTION_FILE).read_text(encoding="utf-8")
    assert caption.startswith(DAY1_CAPTION.rstrip()[:20])
    assert "\n\n" + " ".join(DAY1_HASHTAGS) in caption
    assert (pdir / HASHTAGS_FILE).read_text(encoding="utf-8").strip() == " ".join(DAY1_HASHTAGS)


def test_caption_final_overrides_spec_caption(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec()
    packet = build_packet(spec, account, engine, [], run_compliance(spec, account, engine))
    packet.caption_final = "caption ที่ Sin แก้เอง"
    pdir = write_packet(packet, out)
    assert (pdir / CAPTION_FILE).read_text(encoding="utf-8").startswith("caption ที่ Sin แก้เอง")


def test_checklist_has_the_human_steps(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec(homage_watch=True, affiliate_angle="จี้ท่านท้าวเวสฯ (ปักตะกร้า)")
    packet = build_packet(spec, account, engine, [make_image(tmp_path)], run_compliance(spec, account, engine))
    text = (write_packet(packet, out) / CHECKLIST_FILE).read_text(encoding="utf-8")

    assert "AI label toggle: ON" in text
    assert "C2 × Cosmic × M11" in text
    assert spec.hook in text
    assert "จี้ท่านท้าวเวสฯ" in text
    assert "homage-watch" in text
    assert "R-3.6" in text
    assert "lumora log L1-D01 --url <URL>" in text
    assert "L1-D01-1.png" in text


def test_stray_image_is_copied_into_the_packet_dir(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec()
    img = make_image(tmp_path, "stray.png")
    packet = build_packet(spec, account, engine, [img], run_compliance(spec, account, engine))
    pdir = write_packet(packet, out)

    assert (pdir / "stray.png").is_file()
    assert packet.images[0].path == str(pdir / "stray.png")
    # rewriting is idempotent — the image is already in place
    write_packet(packet, out)
    assert packet.images[0].path == str(pdir / "stray.png")


def test_load_packet_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_packet(tmp_path / "out", "L9-D99")


# ── the human gate ─────────────────────────────────────────────────────────


def test_blocked_packet_cannot_be_approved(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec(caption=DAY1_CAPTION + "\nขอแล้วได้ 100% การันตี")
    report = run_compliance(spec, account, engine)
    packet = build_packet(spec, account, engine, [], report)

    assert report.ok is False
    assert packet.status is PacketStatus.blocked
    write_packet(packet, out)

    with pytest.raises(PacketRefused):
        approve_packet(packet, out, engine)
    assert load_packet(out, "L1-D01").status is PacketStatus.blocked


def test_approve_refuses_when_llm_qa_required_but_skipped(tmp_path, account, engine):
    out = tmp_path / "out"
    engine.compliance.require_llm_qa_before_approve = True
    spec = make_spec()
    packet = build_packet(spec, account, engine, [], run_compliance(spec, account, engine))
    write_packet(packet, out)

    with pytest.raises(PacketRefused, match="require_llm_qa_before_approve"):
        approve_packet(packet, out, engine)


def test_approve_then_publish(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec()
    packet = build_packet(spec, account, engine, [make_image(tmp_path)], run_compliance(spec, account, engine))
    write_packet(packet, out)

    approved = approve_packet(packet, out, engine)
    assert approved.status is PacketStatus.approved
    assert approved.approved_at is not None
    on_disk = load_packet(out, "L1-D01")
    assert on_disk.status is PacketStatus.approved
    assert on_disk.approved_at is not None

    published = mark_published(on_disk, out)
    assert published.status is PacketStatus.published
    assert load_packet(out, "L1-D01").status is PacketStatus.published


def test_mark_published_refuses_blocked(tmp_path, account, engine):
    out = tmp_path / "out"
    spec = make_spec(caption="รับรองว่ารวยแน่ 100%")
    packet = build_packet(spec, account, engine, [], run_compliance(spec, account, engine))
    write_packet(packet, out)
    with pytest.raises(PacketRefused):
        mark_published(packet, out)
