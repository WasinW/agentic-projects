"""Publisher seam. MockPublisher just logs "published". Real publishers
(TikTok/Reels/IG) implement the same .publish() seam — add one class to extend.
"""
from __future__ import annotations

import logging

from app.core.models import Decision

log = logging.getLogger("lumora.publisher")


class MockPublisher:
    platform = "mock"

    def publish(self, decision: Decision) -> str:
        ext_id = f"mock-post-{decision.decision_id[:8]}"
        log.info("published %s -> %s (asset=%s)", decision.decision_id, ext_id, decision.asset_url)
        return ext_id
