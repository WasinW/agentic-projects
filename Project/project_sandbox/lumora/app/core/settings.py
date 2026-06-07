"""Runtime config. ALL external deps default to mock => runs at $0 with no keys."""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # adapter selection — mock by default (no keys, no model downloads)
    embedder: str = "mock"            # mock | bge-m3
    generator: str = "mock"           # mock | real
    source: str = "mock"              # mock | <future platform>
    publisher: str = "mock"           # mock | <future platform>

    # optional real-impl credentials (only needed when *=real)
    anthropic_api_key: str | None = None
    replicate_api_token: str | None = None

    # storage: Phase 1.A = local fs (R2 later)
    assets_dir: str = os.path.join(os.path.dirname(__file__), "..", "..", "assets")

    # db — optional. If unset, the pipeline uses an in-memory store (sqlite-less)
    # so the loop runs WITHOUT docker/postgres.
    database_url: str | None = None   # e.g. postgresql://lumora:lumora@db:5432/lumora

    embedding_dim: int = 1024         # decision #3: bge-m3
    top_n: int = 5                    # how many combos to surface per cycle


@lru_cache
def get_settings() -> Settings:
    return Settings()
