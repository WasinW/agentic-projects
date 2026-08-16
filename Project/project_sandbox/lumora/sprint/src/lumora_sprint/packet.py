"""Publish packet — where the loop STOPS.

ADR-0001 rule 5: publishing is Sin's thumb. This module produces a folder Sin opens and uploads
by hand; nothing here talks to TikTok, schedules, or posts. The state machine ends at
``approved`` (human gate) and only becomes ``published`` after Sin says it happened.

Layout written per post::

    out/<post_id>/
        meta.json      # the Packet contract, indent=2 — the reload source of truth
        caption.txt    # caption + blank line + hashtags — copy-paste straight into the app
        hashtags.txt   # hashtags alone, one paste
        checklist.md   # the human upload checklist (AI label, combo, compliance, log command)
        *.png          # images already generated into the folder (kept; strays are copied in)
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from .compliance import RULE_LLM_QA_ERROR, RULE_LLM_QA_SKIPPED, blocking_findings, has_rule
from .config import AccountConfig, EngineConfig
from .models import ComplianceReport, GeneratedImage, Packet, PacketStatus, PostSpec

META_FILE = "meta.json"
CAPTION_FILE = "caption.txt"
HASHTAGS_FILE = "hashtags.txt"
CHECKLIST_FILE = "checklist.md"


class PacketRefused(ValueError):
    """A gate said no (blocked packet, or QA required before approve). Subclasses ValueError."""


# ── build / render ─────────────────────────────────────────────────────────


def default_out_dir(engine: EngineConfig) -> Path:
    """The configured ``out/`` root (engine.paths.out_dir, resolved against sprint/)."""
    return engine.resolve(engine.paths.out_dir)


def packet_dir(out_dir: str | Path, post_id: str) -> Path:
    """``<out_dir>/<post_id>`` — one folder per post, named by the batch id."""
    return Path(out_dir) / post_id


def build_packet(
    spec: PostSpec,
    account: AccountConfig,
    engine: EngineConfig,
    images: list[GeneratedImage],
    report: ComplianceReport,
) -> Packet:
    """Assemble the packet in memory. Status is ``blocked`` iff a block finding survives the engine flag.

    ``caption_final`` starts empty: it only gets filled when Sin accepts a rewording (``lumora
    caption``), and every renderer falls back to ``spec.caption``. This function builds from the
    spec alone, so a caller re-running it over an existing packet must carry the accepted value
    forward itself — ``cli._write_state`` does.
    """
    blocks = blocking_findings(report)
    if not engine.compliance.block_on_banned_phrase:
        blocks = [f for f in blocks if f.rule != "banned_phrase"]
    status = PacketStatus.blocked if blocks else PacketStatus.draft

    return Packet(
        post_id=spec.post_id,
        brand_id=account.brand_id,
        account_handle=account.account_handle,
        status=status,
        spec=spec,
        images=list(images),
        compliance=report,
        ai_labeled_reminder=spec.ai_visual and account.compliance.ai_label_every_ai_visual,
    )


def render_caption(packet: Packet) -> str:
    """Caption body (accepted rewording wins) + blank line + hashtags — one paste, one field."""
    body = (packet.caption_final or packet.spec.caption or "").rstrip()
    tags = render_hashtags(packet).strip()
    return f"{body}\n\n{tags}\n" if tags else f"{body}\n"


def render_hashtags(packet: Packet) -> str:
    """Hashtags on one line, space separated (how the app wants them)."""
    return " ".join(packet.spec.hashtags) + ("\n" if packet.spec.hashtags else "")


def render_checklist(packet: Packet) -> str:
    """The human upload checklist. Everything Sin must do by hand, in posting order."""
    spec = packet.spec
    report = packet.compliance
    blocks = blocking_findings(report)
    warns = [f for f in (report.findings if report else []) if f.severity == "warn"]

    lines = [
        f"# Upload checklist — {packet.post_id}",
        "",
        f"**{packet.account_handle}** · brand_id `{packet.brand_id}` · status **{packet.status.value}**",
        (
            f"combo `{spec.content_pillar} × {spec.theme} × {spec.media}` · funnel {spec.funnel_stage}"
            f" · hook_type `{spec.hook_type}`"
        ),
        "",
        "## ก่อนโพสต์",
        "",
    ]

    if packet.ai_labeled_reminder:
        lines.append("- [ ] เปิด **AI label toggle: ON** (โพสต์นี้มี AI visual — R-3.7 ตั้งแต่โพสต์ #1)")
    lines += [
        (
            f"- [ ] combo ตรงตาม batch: `{spec.content_pillar} × {spec.theme} × {spec.media}`"
            f" ({spec.funnel_stage})"
        ),
        f"- [ ] hook เป็นบรรทัดแรกจริง: “{spec.hook or '(ยังไม่มี hook)'}”",
        f"- [ ] affiliate angle: {spec.affiliate_angle or '(ไม่ขายโพสต์นี้)'}",
    ]
    if spec.homage_watch:
        lines.append(
            "- [ ] **homage-watch** (R-3.6): เฝ้า reaction 24 ชม.แรก พร้อมดึงโพสต์ออก — บันทึกไว้ใน log"
        )

    status_word = "❌ BLOCKED" if blocks else ("⚠️ ผ่าน (มี warn)" if warns else "✅ ผ่าน")
    lines.append(f"- [ ] compliance: {status_word}")
    for finding in blocks + warns:
        mark = "🚫" if finding.severity == "block" else "⚠️"
        lines.append(f"    - {mark} `{finding.rule}` ({finding.source}) — {finding.detail}")
    if report is not None and report.voice_test_pass is not None:
        lines.append(f"    - voice test: {'ผ่าน' if report.voice_test_pass else 'ไม่ผ่าน — ปรับ caption'}")
    if report is not None and report.suggested_caption:
        lines += [
            "- [ ] พิจารณา caption ที่ LLM เสนอ (รับหรือไม่รับก็ได้ — เสียงเป็นของ Sin):",
            "",
            "  > " + report.suggested_caption.replace("\n", "\n  > "),
            "",
        ]

    lines += [
        "",
        "## โพสต์",
        "",
        "- [ ] โพสต์เอง (manual only — ไม่มี auto-publisher, R-3.9)",
        f"- [ ] หลังโพสต์ รันคำสั่งนี้: `lumora log {packet.post_id} --url <URL>`",
        "",
        "## ไฟล์ในโฟลเดอร์นี้",
        "",
        f"- `{CAPTION_FILE}` — caption + hashtags (คัดลอกทั้งไฟล์)",
        f"- `{HASHTAGS_FILE}` — hashtags อย่างเดียว",
        f"- `{META_FILE}` — packet contract (เครื่องอ่าน อย่าแก้มือ)",
    ]
    for img in packet.images:
        name = Path(img.path).name
        lines.append(f"- `{name}` — {img.provider}/{img.model}" + (f" seed {img.seed}" if img.seed else ""))
    if not packet.images:
        lines.append("- (ยังไม่มีรูป — รัน generate ก่อน)")
    lines.append("")
    return "\n".join(lines)


# ── disk I/O ───────────────────────────────────────────────────────────────


def _keep_image_with_packet(img: GeneratedImage, pdir: Path) -> GeneratedImage:
    """Images generated into the packet dir stay put; strays are copied in so the folder is complete."""
    src = Path(img.path)
    if not src.exists():
        return img
    if src.parent.resolve() == pdir.resolve():
        return img
    dest = pdir / src.name
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return img.model_copy(update={"path": str(dest)})


def write_packet(packet: Packet, out_dir: str | Path) -> Path:
    """Write ``out/<post_id>/`` and return the folder. Idempotent — safe to re-run after an edit."""
    pdir = packet_dir(out_dir, packet.post_id)
    pdir.mkdir(parents=True, exist_ok=True)

    packet.images = [_keep_image_with_packet(img, pdir) for img in packet.images]
    # naive local time on purpose — matches models.py default_factory=datetime.now and post_log dates
    packet.updated_at = datetime.now()  # noqa: DTZ005

    (pdir / CAPTION_FILE).write_text(render_caption(packet), encoding="utf-8")
    (pdir / HASHTAGS_FILE).write_text(render_hashtags(packet), encoding="utf-8")
    (pdir / CHECKLIST_FILE).write_text(render_checklist(packet), encoding="utf-8")
    # meta last: a folder with meta.json is a folder whose renders are already on disk
    (pdir / META_FILE).write_text(packet.model_dump_json(indent=2), encoding="utf-8")
    return pdir


def load_packet(out_dir: str | Path, post_id: str) -> Packet:
    """Reload a packet from ``out/<post_id>/meta.json``."""
    meta = packet_dir(out_dir, post_id) / META_FILE
    if not meta.is_file():
        raise FileNotFoundError(f"ไม่พบ packet: {meta}")
    return Packet.model_validate_json(meta.read_text(encoding="utf-8"))


# ── state machine (human gate) ─────────────────────────────────────────────


def approve_packet(packet: Packet, out_dir: str | Path, engine: EngineConfig) -> Packet:
    """The human gate. Sin approves; the tool only records it. Raises :class:`PacketRefused` if:

    * the packet is ``blocked`` or still carries a block finding — edit the caption and re-run, or
    * ``engine.compliance.require_llm_qa_before_approve`` is on and no LLM verdict exists.

    "No verdict" covers both ways the pass can come back empty: ``llm_qa_skipped`` (never called)
    and ``llm_qa_error`` (called and failed — rate limit, 5xx, refusal). A flag whose whole job is
    "refuse to approve without QA" must not fail open in exactly the case where QA is broken.
    """
    if packet.status is PacketStatus.blocked:
        raise PacketRefused(
            f"{packet.post_id}: packet ถูก block โดย compliance — แก้ caption แล้วรัน packet ใหม่ก่อน approve"
        )
    blocks = blocking_findings(packet.compliance)
    if blocks:
        rules = ", ".join(f.rule for f in blocks)
        raise PacketRefused(f"{packet.post_id}: ยังมี block finding ({rules}) — approve ไม่ได้")

    qa_missing = (
        packet.compliance is None
        or has_rule(packet.compliance, RULE_LLM_QA_SKIPPED)
        or has_rule(packet.compliance, RULE_LLM_QA_ERROR)
    )
    if engine.compliance.require_llm_qa_before_approve and qa_missing:
        raise PacketRefused(
            f"{packet.post_id}: require_llm_qa_before_approve=true แต่ยังไม่มีผล LLM QA "
            "(ข้ามไป หรือเรียกแล้วล้มเหลว) — ตั้ง ANTHROPIC credentials + engine.llm.enabled=true "
            "แล้วรัน packet ใหม่"
        )

    packet.status = PacketStatus.approved
    packet.approved_at = datetime.now()  # noqa: DTZ005 - see write_packet
    write_packet(packet, out_dir)
    return packet


def mark_published(packet: Packet, out_dir: str | Path) -> Packet:
    """Sin posted it by hand — record that fact. Refuses a blocked packet, nothing more."""
    if packet.status is PacketStatus.blocked:
        raise PacketRefused(f"{packet.post_id}: packet ยัง blocked — ไม่ควรมีอยู่บนแพลตฟอร์ม")
    packet.status = PacketStatus.published
    write_packet(packet, out_dir)
    return packet
