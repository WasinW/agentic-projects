"""Replicate FLUX adapter — the only code in this tool that talks to the internet.

Verified against replicate-python 1.0.7 as installed in .venv (not guessed):
`Client.run(ref, input={...})` -> `replicate.run.run()` -> creates a prediction, blocks,
raises `ModelError` on failure, and (use_file_output=True, the default) returns the output
with every URL wrapped in `replicate.helpers.FileOutput`, which exposes `.read() -> bytes`
and `str(...) -> url`. flux-dev's output schema is an array, so we normalise to a list.

FLUX.1 dev input vocabulary (black-forest-labs/flux-dev):
    prompt, aspect_ratio, num_outputs (1-4), num_inference_steps (1-50), guidance,
    seed, output_format (png|jpg|webp), output_quality, megapixels, go_fast,
    disable_safety_checker, prompt_strength, image/mask (img2img).

NEGATIVE PROMPTS: flux-dev has NO `negative_prompt` input — the T5/CLIP conditioning has no
CFG negative branch to hang one on. Sending the key is a 422. So when `spec.negative` is
non-empty we fold it into the prompt as a trailing `Avoid: ...` clause. FLUX only partially
honours this (it is a suggestion inside the positive prompt, not a true negative), which is
why prompts in the batch spec do the heavy lifting positively — the negative list is a hint.

COST: Replicate bills per generated image; we record `est_cost_usd_per_image` from
config/engine.yaml per file. It is an *estimate* (hence the field name) and is what the
accountability layer sums in post_log.cost_usd.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx

from ..models import GeneratedImage, ImageSpec
from . import merge_params

#: flux-dev accepts at most 4 images per prediction; larger carousels loop.
MAX_NUM_OUTPUTS = 4
#: flux-dev clamps.
STEPS_RANGE = (1, 50)
GUIDANCE_RANGE = (0.0, 10.0)

#: Keys that must never reach the API: our own vocabulary, or inputs flux-dev rejects.
_DROP_KEYS = frozenset(
    {"negative", "negative_prompt", "count", "variation", "provider", "model", "steps"}
)

_EXT_BY_FORMAT = {"png": "png", "jpg": "jpg", "jpeg": "jpg", "webp": "webp"}


def build_flux_input(
    spec: ImageSpec,
    defaults: Mapping[str, Any] | None = None,
    num_outputs: int = 1,
    seed_offset: int = 0,
) -> dict[str, Any]:
    """Build the `input={...}` payload for one flux-dev prediction. Pure — no network.

    Merges engine defaults with the spec (spec wins), folds `spec.negative` into the prompt,
    clamps the values flux-dev validates, and drops keys the model would reject.

    Args:
        spec: the post's image spec.
        defaults: engine.generator.defaults, passed through except for dropped keys.
        num_outputs: images in THIS prediction; clamped to 1..MAX_NUM_OUTPUTS.
        seed_offset: added to the seed so each batch of a >4 carousel occupies its own
            seed range (batch 2 starts at seed+4) instead of repeating batch 1.

    Returns:
        A JSON-ready dict. `seed` is absent when neither spec nor defaults set one — an
        absent seed means "let the model pick", which is honest; we never invent one.
    """
    params = merge_params(spec, defaults)

    prompt = str(params.get("prompt") or "").strip()
    negative = (spec.negative or "").strip()
    if negative:
        # flux-dev has no negative_prompt input — see module docstring.
        prompt = f"{prompt} Avoid: {negative}"
    params["prompt"] = prompt

    params["num_outputs"] = max(1, min(MAX_NUM_OUTPUTS, int(num_outputs)))

    if params.get("seed") is not None:
        params["seed"] = int(params["seed"]) + int(seed_offset)

    if params.get("num_inference_steps") is not None:
        lo, hi = STEPS_RANGE
        params["num_inference_steps"] = max(lo, min(hi, int(params["num_inference_steps"])))

    if params.get("guidance") is not None:
        lo, hi = GUIDANCE_RANGE
        params["guidance"] = max(lo, min(hi, float(params["guidance"])))

    return {k: v for k, v in params.items() if k not in _DROP_KEYS and v is not None}


def _extension(payload: Mapping[str, Any]) -> str:
    """File extension matching the requested output_format (engine.yaml default: png)."""
    fmt = str(payload.get("output_format") or "png").lower()
    return _EXT_BY_FORMAT.get(fmt, "png")


def _as_list(output: Any) -> list[Any]:
    """flux-dev returns an array; tolerate a bare item or a generator without guessing further."""
    if output is None:
        return []
    if isinstance(output, (str, bytes)) or hasattr(output, "read"):
        return [output]
    if isinstance(output, (list, tuple)):
        return list(output)
    try:
        return list(output)          # iterator-typed outputs
    except TypeError:
        return [output]


class ReplicateFlux:
    """ImageGenerator backed by Replicate (default model: black-forest-labs/flux-dev)."""

    provider = "replicate"

    def __init__(
        self,
        model: str = "black-forest-labs/flux-dev",
        est_cost_usd_per_image: float = 0.025,
        timeout_s: int = 180,
        api_token: str | None = None,
    ) -> None:
        """Args mirror engine.generator; `api_token` defaults to $REPLICATE_API_TOKEN."""
        self.model = model
        self.est_cost_usd_per_image = float(est_cost_usd_per_image)
        self.timeout_s = int(timeout_s)
        self.api_token = api_token

    # ── client ────────────────────────────────────────────────────────────

    def _token(self) -> str:
        token = (self.api_token or os.environ.get("REPLICATE_API_TOKEN") or "").strip()
        if not token:
            raise RuntimeError(
                f"cannot call {self.model!r}: REPLICATE_API_TOKEN is not set. "
                "`export REPLICATE_API_TOKEN=...` or set generator.provider: stub in config/engine.yaml."
            )
        return token

    def _client(self) -> Any:
        """Build a Replicate client. Imported lazily so the stub path never needs the SDK."""
        import replicate

        return replicate.Client(
            api_token=self._token(),
            timeout=httpx.Timeout(float(self.timeout_s), connect=10.0),
        )

    # ── generation ────────────────────────────────────────────────────────

    def generate(
        self,
        spec: ImageSpec,
        out_dir: Path,
        base_name: str,
        defaults: dict[str, Any] | None = None,
    ) -> list[GeneratedImage]:
        """Render `spec.count` images, batching 4 per prediction (flux-dev's num_outputs cap).

        Raises:
            RuntimeError: any API/download failure, wrapped with the model slug and the
                token hint — Replicate's own errors do not say which model was called.
        """
        count = max(1, int(spec.count))
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        client = self._client()

        images: list[GeneratedImage] = []
        produced = 0
        while produced < count:
            want = min(MAX_NUM_OUTPUTS, count - produced)
            payload = build_flux_input(spec, defaults, num_outputs=want, seed_offset=produced)
            ext = _extension(payload)

            started = perf_counter()
            try:
                output = client.run(self.model, input=payload)
            except Exception as exc:
                raise RuntimeError(
                    f"replicate run failed for model {self.model!r}: {exc.__class__.__name__}: {exc}. "
                    "Check REPLICATE_API_TOKEN (valid? billing enabled?), the model slug in "
                    "config/engine.yaml, and the input keys flux-dev accepts."
                ) from exc

            items = _as_list(output)[:want]
            if not items:
                raise RuntimeError(
                    f"replicate model {self.model!r} returned no images for prompt "
                    f"{payload.get('prompt', '')[:80]!r} — nothing to write, aborting."
                )
            elapsed = perf_counter() - started

            for item in items:
                path = out_dir / f"{base_name}_{len(images) + 1}.{ext}"
                try:
                    path.write_bytes(self._read_bytes(item))
                except Exception as exc:
                    raise RuntimeError(
                        f"replicate model {self.model!r} produced output that could not be "
                        f"downloaded to {path}: {exc.__class__.__name__}: {exc}"
                    ) from exc
                images.append(
                    GeneratedImage(
                        path=str(path),
                        provider=self.provider,
                        model=self.model,
                        # the seed sent for this prediction; with num_outputs>1 the model
                        # derives per-image seeds from it, which is why batches step by 4.
                        seed=payload.get("seed"),
                        prompt=payload["prompt"],
                        est_cost_usd=self.est_cost_usd_per_image,
                        duration_s=elapsed / len(items),
                    )
                )
            produced += len(items)

        return images

    def _read_bytes(self, item: Any) -> bytes:
        """Pull bytes from a FileOutput (`.read()`) or, failing that, a plain URL string."""
        reader = getattr(item, "read", None)
        if callable(reader):
            return reader()
        url = str(item)
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"unexpected output item {url[:80]!r} — expected a FileOutput or an http(s) URL")
        with httpx.Client(timeout=httpx.Timeout(float(self.timeout_s), connect=10.0)) as client:
            response = client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.content
