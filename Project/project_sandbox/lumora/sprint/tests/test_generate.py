"""Tests for the image-generation seam — the ONE external adapter.

Nothing here touches the network: the stub is real, and the Replicate path is exercised
through a fake client so the input mapping and the >4 batching loop are covered offline.
"""
from __future__ import annotations

import pytest
from PIL import Image

from lumora_sprint.config import EngineConfig, GeneratorCfg, load_engine
from lumora_sprint.generate import (
    DEFAULT_BASE_NAME,
    ImageGenerator,
    generate_for_spec,
    get_generator,
    merge_params,
)
from lumora_sprint.generate.replicate_flux import (
    MAX_NUM_OUTPUTS,
    ReplicateFlux,
    build_flux_input,
)
from lumora_sprint.generate.stub import StubGenerator, size_for_aspect
from lumora_sprint.models import ImageSpec, PostSpec

ENGINE_DEFAULTS = {
    "aspect_ratio": "9:16",
    "num_inference_steps": 28,
    "guidance": 3.5,
    "output_format": "png",
    "output_quality": 90,
}


@pytest.fixture(autouse=True)
def _no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test starts key-less; tests that need a token set one explicitly."""
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)


def _spec(**kw) -> ImageSpec:
    base = {
        "prompt": "Three ethereal oracle cards floating above open palms, cosmic nebula style",
        "aspect_ratio": "9:16",
        "seed": 10101,
    }
    base.update(kw)
    return ImageSpec(**base)


def _engine(**gen) -> EngineConfig:
    cfg = {"provider": "stub", "model": "black-forest-labs/flux-dev", "defaults": dict(ENGINE_DEFAULTS)}
    cfg.update(gen)
    return EngineConfig(generator=GeneratorCfg(**cfg))


# ── stub ───────────────────────────────────────────────────────────────────


def test_stub_writes_n_files_at_9x16(tmp_path):
    images = StubGenerator().generate(_spec(count=3), tmp_path, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))

    assert len(images) == 3
    for i, img in enumerate(images, start=1):
        path = tmp_path / f"image_{i}.png"
        assert path.exists() and path.stat().st_size > 0
        assert img.path == str(path)
        with Image.open(path) as opened:
            assert opened.size == (1080, 1920)
        assert img.provider == "stub"
        assert img.est_cost_usd == 0.0          # empty beats fake
        assert img.seed == 10101 + (i - 1)      # carousel walks the seed, like the batch spec


@pytest.mark.parametrize(
    ("aspect", "size"),
    [("9:16", (1080, 1920)), ("1:1", (1080, 1080)), ("16:9", (1920, 1080)), ("4:5", (1080, 1350))],
)
def test_size_for_aspect(aspect, size):
    assert size_for_aspect(aspect) == size


def test_size_for_aspect_falls_back_on_garbage():
    assert size_for_aspect("portrait") == (1080, 1920)


def test_stub_honours_aspect_ratio_on_disk(tmp_path):
    StubGenerator().generate(_spec(aspect_ratio="1:1"), tmp_path, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))
    with Image.open(tmp_path / "image_1.png") as opened:
        assert opened.size == (1080, 1080)


def test_stub_is_deterministic(tmp_path):
    # same packet dir name under two roots — the overlay prints the dir name, so it must match
    a, b = tmp_path / "run1" / "L1-D01", tmp_path / "run2" / "L1-D01"
    StubGenerator().generate(_spec(), a, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))
    StubGenerator().generate(_spec(), b, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))
    assert (a / "image_1.png").read_bytes() == (b / "image_1.png").read_bytes()


def test_stub_without_seed_is_still_stable(tmp_path):
    a, b = tmp_path / "run1" / "L1-D01", tmp_path / "run2" / "L1-D01"
    StubGenerator().generate(_spec(seed=None), a, DEFAULT_BASE_NAME, {})
    StubGenerator().generate(_spec(seed=None), b, DEFAULT_BASE_NAME, {})
    assert (a / "image_1.png").read_bytes() == (b / "image_1.png").read_bytes()


def test_stub_palette_varies_with_seed(tmp_path):
    a, b = tmp_path / "run1" / "L1-D01", tmp_path / "run2" / "L1-D01"
    StubGenerator().generate(_spec(seed=1), a, DEFAULT_BASE_NAME, {})
    StubGenerator().generate(_spec(seed=2), b, DEFAULT_BASE_NAME, {})
    assert (a / "image_1.png").read_bytes() != (b / "image_1.png").read_bytes()


def test_stub_satisfies_the_protocol():
    assert isinstance(StubGenerator(), ImageGenerator)


# ── merge_params ───────────────────────────────────────────────────────────


def test_merge_params_spec_overrides_defaults():
    merged = merge_params(_spec(steps=32, guidance=4.0, aspect_ratio="1:1"), ENGINE_DEFAULTS)
    assert merged["num_inference_steps"] == 32
    assert merged["guidance"] == 4.0
    assert merged["aspect_ratio"] == "1:1"
    assert merged["output_quality"] == 90         # untouched default passes through


def test_merge_params_keeps_defaults_when_spec_is_silent():
    merged = merge_params(_spec(steps=None, guidance=None), ENGINE_DEFAULTS)
    assert merged["num_inference_steps"] == 28
    assert merged["guidance"] == 3.5


# ── get_generator ──────────────────────────────────────────────────────────


def test_auto_picks_stub_without_token(monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    assert isinstance(get_generator(_engine(provider="auto")), StubGenerator)


def test_auto_picks_replicate_with_token(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "r8_faketoken")
    generator = get_generator(_engine(provider="auto"))
    assert isinstance(generator, ReplicateFlux)
    assert generator.model == "black-forest-labs/flux-dev"


def test_explicit_stub_wins_over_a_present_token(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_TOKEN", "r8_faketoken")
    assert isinstance(get_generator(_engine(provider="stub")), StubGenerator)


def test_explicit_replicate_without_token_raises(monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="REPLICATE_API_TOKEN"):
        get_generator(_engine(provider="replicate"))


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="unknown generator.provider"):
        get_generator(_engine(provider="midjourney"))


def test_real_engine_yaml_resolves_to_stub_offline(monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    assert isinstance(get_generator(load_engine()), StubGenerator)


# ── generate_for_spec ──────────────────────────────────────────────────────


def _post(image: ImageSpec | None, **kw) -> PostSpec:
    base = {
        "post_id": "L1-D01",
        "day": 1,
        "week": 1,
        "content_pillar": "C2",
        "theme": "Cosmic",
        "media": "M11",
        "hook_type": "curiosity-choice",
        "image": image,
    }
    base.update(kw)
    return PostSpec(**base)


def test_generate_for_spec_names_files_image_n(tmp_path):
    images = generate_for_spec(_post(_spec(count=2)), _engine(), tmp_path / "L1-D01")

    assert [p.name for p in sorted((tmp_path / "L1-D01").glob("image_*.png"))] == [
        "image_1.png",
        "image_2.png",
    ]
    assert len(images) == 2
    assert all(img.provider == "stub" and img.model == "stub" for img in images)


def test_generate_for_spec_creates_the_packet_dir(tmp_path):
    target = tmp_path / "out" / "L1-D03"
    generate_for_spec(_post(_spec()), _engine(), target)
    assert (target / "image_1.png").exists()


def test_generate_for_spec_rejects_outline_rows(tmp_path):
    with pytest.raises(ValueError, match="no image spec"):
        generate_for_spec(_post(None, full_spec=False), _engine(), tmp_path)


# ── replicate input mapping (no network) ───────────────────────────────────


def test_replicate_module_imports():
    import lumora_sprint.generate.replicate_flux as mod

    assert mod.MAX_NUM_OUTPUTS == 4
    assert callable(mod.build_flux_input)


def test_build_flux_input_maps_the_common_set():
    payload = build_flux_input(_spec(steps=32, guidance=4.0), ENGINE_DEFAULTS, num_outputs=1)

    assert payload["prompt"].startswith("Three ethereal oracle cards")
    assert payload["aspect_ratio"] == "9:16"
    assert payload["num_inference_steps"] == 32
    assert payload["guidance"] == 4.0
    assert payload["seed"] == 10101
    assert payload["num_outputs"] == 1
    assert payload["output_format"] == "png"
    assert payload["output_quality"] == 90


def test_build_flux_input_folds_negative_into_the_prompt():
    payload = build_flux_input(_spec(negative="text, watermark, extra fingers"), ENGINE_DEFAULTS)

    # flux-dev has no negative_prompt input — sending one is a 422.
    assert "negative_prompt" not in payload
    assert "negative" not in payload
    assert payload["prompt"].endswith("Avoid: text, watermark, extra fingers")


def test_build_flux_input_omits_the_avoid_clause_when_negative_is_empty():
    assert "Avoid:" not in build_flux_input(_spec(negative=""), ENGINE_DEFAULTS)["prompt"]


def test_build_flux_input_drops_unset_seed():
    assert "seed" not in build_flux_input(_spec(seed=None), ENGINE_DEFAULTS)


def test_build_flux_input_offsets_and_clamps():
    payload = build_flux_input(
        _spec(steps=99, guidance=42.0), ENGINE_DEFAULTS, num_outputs=9, seed_offset=4
    )
    assert payload["num_outputs"] == MAX_NUM_OUTPUTS
    assert payload["num_inference_steps"] == 50
    assert payload["guidance"] == 10.0
    assert payload["seed"] == 10105


def test_build_flux_input_never_leaks_our_own_vocabulary():
    payload = build_flux_input(_spec(count=5, variation="vary palette per card"), ENGINE_DEFAULTS)
    assert "count" not in payload and "variation" not in payload and "steps" not in payload


# ── replicate generate loop with a fake client ─────────────────────────────


class _FakeFileOutput:
    """Stands in for replicate.helpers.FileOutput (`.read() -> bytes`)."""

    def __init__(self, blob: bytes) -> None:
        self._blob = blob

    def read(self) -> bytes:
        return self._blob


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run(self, ref, input):
        self.calls.append({"ref": ref, "input": dict(input)})
        n = input["num_outputs"]
        return [_FakeFileOutput(f"png-bytes-{len(self.calls)}-{i}".encode()) for i in range(n)]


def _fake_flux(monkeypatch) -> tuple[ReplicateFlux, _FakeClient]:
    generator = ReplicateFlux(est_cost_usd_per_image=0.025, timeout_s=180, api_token="r8_faketoken")
    fake = _FakeClient()
    monkeypatch.setattr(ReplicateFlux, "_client", lambda self: fake)
    return generator, fake


def test_replicate_generate_writes_files_and_costs(tmp_path, monkeypatch):
    generator, fake = _fake_flux(monkeypatch)
    images = generator.generate(_spec(count=2), tmp_path, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))

    assert len(fake.calls) == 1 and fake.calls[0]["ref"] == "black-forest-labs/flux-dev"
    assert [p.name for p in sorted(tmp_path.glob("image_*"))] == ["image_1.png", "image_2.png"]
    assert [img.est_cost_usd for img in images] == [0.025, 0.025]
    assert all(img.provider == "replicate" and img.seed == 10101 for img in images)


def test_replicate_batches_carousels_over_four(tmp_path, monkeypatch):
    generator, fake = _fake_flux(monkeypatch)
    images = generator.generate(_spec(count=6), tmp_path, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))

    assert len(images) == 6
    assert [c["input"]["num_outputs"] for c in fake.calls] == [4, 2]
    assert [c["input"]["seed"] for c in fake.calls] == [10101, 10105]   # reserved seed ranges
    assert sorted(p.name for p in tmp_path.glob("image_*")) == [f"image_{i}.png" for i in range(1, 7)]
    assert len({p.read_bytes() for p in tmp_path.glob("image_*")}) == 6


def test_replicate_extension_follows_output_format(tmp_path, monkeypatch):
    generator, _ = _fake_flux(monkeypatch)
    generator.generate(_spec(), tmp_path, DEFAULT_BASE_NAME, {**ENGINE_DEFAULTS, "output_format": "webp"})
    assert (tmp_path / "image_1.webp").exists()


def test_replicate_wraps_api_errors_with_the_model_slug(tmp_path, monkeypatch):
    generator = ReplicateFlux(api_token="r8_faketoken")

    class _Boom:
        def run(self, ref, input):
            raise ConnectionError("connection reset")

    monkeypatch.setattr(ReplicateFlux, "_client", lambda self: _Boom())
    with pytest.raises(RuntimeError, match="black-forest-labs/flux-dev"):
        generator.generate(_spec(), tmp_path, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))


def test_replicate_raises_on_empty_output(tmp_path, monkeypatch):
    generator = ReplicateFlux(api_token="r8_faketoken")

    class _Empty:
        def run(self, ref, input):
            return []

    monkeypatch.setattr(ReplicateFlux, "_client", lambda self: _Empty())
    with pytest.raises(RuntimeError, match="returned no images"):
        generator.generate(_spec(), tmp_path, DEFAULT_BASE_NAME, dict(ENGINE_DEFAULTS))


def test_replicate_client_without_token_raises(monkeypatch):
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="REPLICATE_API_TOKEN"):
        ReplicateFlux()._client()
