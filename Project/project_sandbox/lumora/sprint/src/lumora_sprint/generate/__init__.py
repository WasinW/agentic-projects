"""Image-generation seam — the ONE external adapter this sprint tool is allowed to open.

ADR-0001 keeps the loop orchestrator-first and human-gated: there is no publisher, no
scheduler, no platform API. The only outbound call in the whole tool is text -> image, and
even that sits behind a Protocol with an offline stub, so `plan -> generate -> packet ->
approve -> log` runs end-to-end with NO API keys at all.

Public API
----------
ImageGenerator      Protocol every adapter satisfies.
get_generator()     Pick the adapter from EngineConfig (auto / replicate / stub).
generate_for_spec() Convenience: PostSpec + EngineConfig + post_dir -> files on disk.
merge_params()      engine.generator.defaults <- ImageSpec overrides (shared by adapters).
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from ..config import EngineConfig
from ..models import GeneratedImage, ImageSpec, PostSpec

__all__ = [
    "DEFAULT_BASE_NAME",
    "ImageGenerator",
    "ReplicateFlux",
    "StubGenerator",
    "generate_for_spec",
    "get_generator",
    "merge_params",
]

#: Packet convention — out/<post_id>/image_1.png, image_2.png, ...
DEFAULT_BASE_NAME = "image"


@runtime_checkable
class ImageGenerator(Protocol):
    """One text-to-image call. Implementations must be side-effect-free beyond `out_dir`."""

    def generate(
        self,
        spec: ImageSpec,
        out_dir: Path,
        base_name: str,
        defaults: dict[str, Any],
    ) -> list[GeneratedImage]:
        """Render `spec.count` images into `out_dir` as `<base_name>_<n>.<ext>` (n starts at 1).

        Args:
            spec: the post's image spec (prompt, negative, aspect_ratio, seed, steps, ...).
            out_dir: directory to write into; created by the adapter if missing.
            base_name: filename stem, usually ``DEFAULT_BASE_NAME``.
            defaults: engine.generator.defaults — provider-level knobs the spec may override.

        Returns:
            One GeneratedImage per file written, in filename order.
        """
        ...


def merge_params(spec: ImageSpec, defaults: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Merge engine defaults with the per-post ImageSpec — the spec always wins.

    Field names are normalised onto the FLUX input vocabulary (`num_inference_steps`,
    `guidance`, `aspect_ratio`, `seed`) so adapters share one merged dict. Keys the spec
    leaves as None fall through to `defaults`; keys neither side sets are simply absent.

    Note: `spec.negative` is NOT merged here — FLUX has no negative-prompt input, so each
    adapter decides how to express it (see replicate_flux.build_flux_input).
    """
    params: dict[str, Any] = dict(defaults or {})
    params["prompt"] = spec.prompt
    if spec.aspect_ratio:
        params["aspect_ratio"] = spec.aspect_ratio
    if spec.seed is not None:
        params["seed"] = spec.seed
    if spec.steps is not None:
        params["num_inference_steps"] = spec.steps
    if spec.guidance is not None:
        params["guidance"] = spec.guidance
    return params


def get_generator(engine: EngineConfig) -> ImageGenerator:
    """Resolve `engine.generator.provider` into a concrete adapter.

    * ``auto``      -> ReplicateFlux when REPLICATE_API_TOKEN is set, else the stub.
    * ``replicate`` -> ReplicateFlux; raises if the token is missing (explicit means explicit).
    * ``stub``      -> StubGenerator, even when a token is present (cheap dry runs).

    Raises:
        RuntimeError: provider is 'replicate' but no REPLICATE_API_TOKEN in the environment.
        ValueError: unknown provider string.
    """
    provider = (engine.generator.provider or "auto").strip().lower()
    token = (os.environ.get("REPLICATE_API_TOKEN") or "").strip()

    if provider == "auto":
        provider = "replicate" if token else "stub"

    if provider == "stub":
        from .stub import StubGenerator

        return StubGenerator()

    if provider == "replicate":
        if not token:
            raise RuntimeError(
                "config/engine.yaml has generator.provider: replicate but REPLICATE_API_TOKEN "
                "is not set. Either `export REPLICATE_API_TOKEN=...` or set "
                "generator.provider: stub (offline placeholders) / auto (stub when no token)."
            )
        from .replicate_flux import ReplicateFlux

        return ReplicateFlux(
            model=engine.generator.model,
            est_cost_usd_per_image=engine.generator.est_cost_usd_per_image,
            timeout_s=engine.generator.timeout_s,
            api_token=token,
        )

    raise ValueError(
        f"unknown generator.provider {engine.generator.provider!r} — expected auto | replicate | stub"
    )


def generate_for_spec(
    spec: PostSpec,
    engine: EngineConfig,
    post_dir: Path,
) -> list[GeneratedImage]:
    """Generate every image for one planned post into its packet directory.

    Merges `engine.generator.defaults` with `spec.image` (spec overrides), renders
    `spec.image.count` files named `image_1.<ext> ... image_N.<ext>`, and returns the
    GeneratedImage rows the packet/log layers record (provider, model, seed, cost, duration).

    Raises:
        ValueError: the post has no image spec (outline rows, `full_spec: false`, carry none).
    """
    if spec.image is None:
        raise ValueError(
            f"{spec.post_id}: no image spec — expand the outline row (full_spec: false) with a "
            "prompt from lumora-art-prompt before generating."
        )
    if spec.image.count < 1:
        raise ValueError(f"{spec.post_id}: image.count must be >= 1, got {spec.image.count}")

    out_dir = Path(post_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    generator = get_generator(engine)
    return generator.generate(
        spec.image,
        out_dir,
        DEFAULT_BASE_NAME,
        dict(engine.generator.defaults),
    )


def __getattr__(name: str) -> Any:
    """Lazy adapter re-export (PEP 562) — keeps `replicate`/`PIL` off the import hot path."""
    if name == "StubGenerator":
        from .stub import StubGenerator

        return StubGenerator
    if name == "ReplicateFlux":
        from .replicate_flux import ReplicateFlux

        return ReplicateFlux
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
