"""Offline placeholder generator — the reason this tool needs zero API keys to run.

Draws a deterministic gradient card at the real post dimensions with the post id, the head
of the prompt and a big STUB watermark, so every downstream step (packet assembly, the
approve gate, post_log, the weekly review) can be exercised and reviewed before a single
satang is spent on Replicate. Cost is honestly 0.0 — never a made-up number.

Deterministic by construction: seed -> palette, no RNG anywhere. The same spec renders
byte-identical files on every run, which is what makes the tests meaningful.
"""
from __future__ import annotations

import textwrap
import zlib
from pathlib import Path
from time import perf_counter
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from ..models import GeneratedImage, ImageSpec
from . import merge_params

#: Short-form base edge. 9:16 -> 1080x1920, 1:1 -> 1080x1080, 16:9 -> 1920x1080.
BASE_EDGE = 1080
FALLBACK_SIZE = (1080, 1920)

#: (top, bottom, ink) — dark cosmic grounds with a light accent, close to the account's aesthetic weeks.
_PALETTES: tuple[tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]], ...] = (
    ((26, 20, 66), (86, 44, 120), (240, 214, 132)),   # cosmic indigo -> violet, gold ink
    ((10, 34, 58), (18, 92, 96), (226, 232, 214)),    # deep teal
    ((48, 18, 40), (122, 46, 62), (245, 200, 160)),   # dusk plum
    ((18, 26, 30), (58, 84, 74), (232, 220, 176)),    # pastoral green
    ((36, 22, 12), (120, 74, 30), (246, 226, 170)),   # temple gold-brown
    ((14, 16, 40), (60, 30, 96), (198, 226, 246)),    # night sky
)

_FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)

PROMPT_PREVIEW_CHARS = 60


def size_for_aspect(aspect_ratio: str) -> tuple[int, int]:
    """Map an 'W:H' aspect ratio onto pixel dimensions with a 1080px short edge.

    9:16 -> (1080, 1920), 1:1 -> (1080, 1080), 16:9 -> (1920, 1080), 4:5 -> (1080, 1350).
    Anything unparseable falls back to the short-form default so a bad string never
    crashes a dry run.
    """
    try:
        w_s, h_s = str(aspect_ratio).replace(" ", "").split(":", 1)
        w, h = float(w_s), float(h_s)
        if w <= 0 or h <= 0:
            return FALLBACK_SIZE
    except (ValueError, AttributeError):
        return FALLBACK_SIZE
    if w <= h:
        return BASE_EDGE, max(1, round(BASE_EDGE * h / w))
    return max(1, round(BASE_EDGE * w / h)), BASE_EDGE


def _stable_seed(text: str) -> int:
    """Process-stable pseudo-seed for specs that declare none (hash() is salted, crc32 is not)."""
    return int(zlib.crc32(text.encode("utf-8")))


def _font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Best available truetype face, falling back to PIL's bundled bitmap font."""
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:      # very old Pillow: load_default() takes no size
        return ImageFont.load_default()


def _gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    """Vertical linear gradient, built 1px wide then stretched (per-pixel loops are too slow at 1080p)."""
    w, h = size
    column = Image.new("RGB", (1, h))
    px = column.load()
    span = max(h - 1, 1)
    for y in range(h):
        t = y / span
        px[0, y] = (
            round(top[0] + (bottom[0] - top[0]) * t),
            round(top[1] + (bottom[1] - top[1]) * t),
            round(top[2] + (bottom[2] - top[2]) * t),
        )
    return column.resize((w, h), Image.Resampling.BILINEAR)


def _safe_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, **kw: Any) -> None:
    """Draw text, swallowing font/glyph errors — the overlay is cosmetic, it must never
    fail a dry run (e.g. a bitmap fallback font with no Thai glyphs)."""
    try:
        draw.text(xy, text, **kw)
    except (OSError, ValueError):   # missing glyph / unrenderable font — skip the line, keep the image
        return


class StubGenerator:
    """ImageGenerator that writes PIL placeholders. No network, no key, no cost."""

    provider = "stub"

    def __init__(self, model: str = "stub") -> None:
        """Args: model — recorded as GeneratedImage.model / post_log.gen_model."""
        self.model = model

    def generate(
        self,
        spec: ImageSpec,
        out_dir: Path,
        base_name: str,
        defaults: dict[str, Any] | None = None,
    ) -> list[GeneratedImage]:
        """Render `spec.count` placeholder PNGs into `out_dir`.

        Always PNG regardless of `defaults['output_format']` — the stub is a review artefact,
        not a deliverable. Each image in a carousel gets `base_seed + i` so the set is visibly
        distinct, mirroring how the batch spec walks seeds (60300-60304) for a 5-card set.
        """
        params = merge_params(spec, defaults)
        aspect = str(params.get("aspect_ratio") or spec.aspect_ratio or "9:16")
        size = size_for_aspect(aspect)
        base_seed = params.get("seed")
        if base_seed is None:
            base_seed = _stable_seed(f"{base_name}|{spec.prompt}")

        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        images: list[GeneratedImage] = []
        for i in range(max(1, int(spec.count))):
            started = perf_counter()
            seed = int(base_seed) + i
            path = out_dir / f"{base_name}_{i + 1}.png"
            self._render(path, size, seed, out_dir.name, f"{base_name}_{i + 1}", spec, aspect)
            images.append(
                GeneratedImage(
                    path=str(path),
                    provider=self.provider,
                    model=self.model,
                    seed=seed,
                    prompt=spec.prompt,
                    est_cost_usd=0.0,          # honest zero — the stub costs nothing
                    duration_s=perf_counter() - started,
                )
            )
        return images

    def _render(
        self,
        path: Path,
        size: tuple[int, int],
        seed: int,
        post_label: str,
        file_label: str,
        spec: ImageSpec,
        aspect: str,
    ) -> None:
        """Paint one placeholder: gradient ground, accent frame, labels, STUB watermark."""
        top, bottom, ink = _PALETTES[seed % len(_PALETTES)]
        img = _gradient(size, top, bottom)
        draw = ImageDraw.Draw(img)
        w, h = size
        pad = round(min(w, h) * 0.06)
        unit = min(w, h) / 1080          # scale text with the canvas

        draw.rectangle([pad, pad, w - pad, h - pad], outline=ink, width=max(1, round(3 * unit)))

        _safe_text(draw, (pad * 2, pad * 2), post_label or "packet", font=_font(round(56 * unit)), fill=ink)
        _safe_text(
            draw,
            (pad * 2, pad * 2 + round(74 * unit)),
            file_label,
            font=_font(round(36 * unit)),
            fill=ink,
        )

        preview = " ".join(spec.prompt.split())[:PROMPT_PREVIEW_CHARS]
        body = _font(round(40 * unit))
        y = round(h * 0.34)
        for line in textwrap.wrap(preview, width=30) or ["(no prompt)"]:
            _safe_text(draw, (pad * 2, y), line, font=body, fill=ink)
            y += round(54 * unit)

        _safe_text(draw, (pad * 2, round(h * 0.52)), "STUB", font=_font(round(150 * unit)), fill=ink)

        footer = f"{aspect} · {w}x{h} · seed {seed}"
        _safe_text(draw, (pad * 2, h - pad * 2 - round(40 * unit)), footer, font=_font(round(32 * unit)), fill=ink)

        img.save(path, format="PNG")
