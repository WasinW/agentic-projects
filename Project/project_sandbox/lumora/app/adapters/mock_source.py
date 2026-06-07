"""MockSource — returns a few fake product listings so the loop runs with no network.
Real Source adapters (TikTok/Shopee/Lazada) implement the same .scrape() seam.
"""
from __future__ import annotations

# hardcoded สายมู-flavoured catalog (Phase 1 = Sin's own brand)
_FAKE = [
    {"external_id": "tt-001", "platform": "tiktok_shop", "canonical_name": "Moonstone bracelet (มูนสโตน)",
     "category": "มู", "price": 290, "commission_pct": 12, "rating": 4.8, "reviews_count": 1320},
    {"external_id": "tt-002", "platform": "tiktok_shop", "canonical_name": "Palo Santo smudge stick",
     "category": "มู", "price": 150, "commission_pct": 15, "rating": 4.6, "reviews_count": 540},
    {"external_id": "sh-010", "platform": "shopee", "canonical_name": "Oracle card deck (ไพ่ออราเคิล)",
     "category": "art", "price": 690, "commission_pct": 10, "rating": 4.9, "reviews_count": 880},
    {"external_id": "sh-011", "platform": "shopee", "canonical_name": "Clear quartz tower (หินควอตซ์)",
     "category": "มู", "price": 450, "commission_pct": 11, "rating": 4.7, "reviews_count": 410},
    {"external_id": "lz-020", "platform": "lazada", "canonical_name": "Brass incense holder",
     "category": "art", "price": 320, "commission_pct": 9, "rating": 4.5, "reviews_count": 205},
]


class MockSource:
    platform = "mock"

    def scrape(self, brand_id: str) -> list[dict]:
        return [{**row, "brand_id": brand_id, "url": f"https://mock/{row['external_id']}"} for row in _FAKE]
