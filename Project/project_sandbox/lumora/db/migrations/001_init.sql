-- LUMORA Phase 1.A — schema (synthesized from 04_tech_backend.md + 07 §9 decisions)
-- pgvector/pgvector:pg16. Resolved decisions baked in:
--   #3 VECTOR(1024) (bge-m3, Thai-friendly)
--   #4 no hard delete -> 'archived' status (idea bank)
--   #5 reject_reason = fixed-tag lookup (not free text)
--   #1 metrics ingestion = service/API (POST endpoint writes `performance`)
--   brand_id everywhere (Phase1 -> Phase2 seam, no migration)

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- gen_random_uuid()

-- ── tenant ─────────────────────────────────────────────────────────────
CREATE TABLE brands (
  brand_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              TEXT NOT NULL,
  type              TEXT NOT NULL DEFAULT 'own',   -- 'own' | 'client'
  retainer_amount   DECIMAL DEFAULT 0,
  active_since      DATE DEFAULT CURRENT_DATE
);

-- ── catalog ────────────────────────────────────────────────────────────
CREATE TABLE products (
  product_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  canonical_name    TEXT NOT NULL,
  category          TEXT,                          -- มู / art / etc
  embedding         VECTOR(1024),                  -- decision #3: bge-m3 1024-dim
  created_at        TIMESTAMPTZ DEFAULT now(),
  last_updated      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE product_listings (
  listing_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  product_id        UUID REFERENCES products(product_id),
  platform          TEXT NOT NULL,                 -- tiktok_shop | shopee | lazada
  external_id       TEXT,
  url               TEXT,
  price             DECIMAL,
  commission_pct    DECIMAL,
  rating            DECIMAL,
  reviews_count     INT,
  last_scraped      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE trends (
  trend_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  product_id        UUID REFERENCES products(product_id),
  metric            TEXT,
  value             DECIMAL,
  z_score           DECIMAL,
  ts                TIMESTAMPTZ DEFAULT now()
);

-- ── accounts / posts / performance ────────────────────────────────────
CREATE TABLE accounts (
  account_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  platform          TEXT,                          -- tiktok | ig | youtube
  handle            TEXT,
  archetype         TEXT,                          -- voice
  audience_persona  JSONB,
  active_pillars    TEXT[],                        -- C1, C2...
  active_themes     TEXT[]                         -- Future-tech, Historical...
);

CREATE TABLE posts (
  post_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  account_id        UUID REFERENCES accounts(account_id),
  -- 3-axis tagging (+ jtbd, funnel_stage)
  content_pillar    TEXT,                          -- C1, C2...
  theme             TEXT,
  media_format      TEXT,                          -- M1, M2...
  jtbd              TEXT,
  funnel_stage      TEXT,                          -- Hero | Hub | Hygiene
  product_ids       UUID[],
  posted_at         TIMESTAMPTZ,
  caption           TEXT,
  asset_url         TEXT
);

CREATE TABLE performance (
  perf_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  post_id           UUID REFERENCES posts(post_id),
  views             INT,
  likes             INT,
  shares            INT,
  saves             INT,
  clicks            INT,
  conversions       INT,
  revenue           DECIMAL,
  measured_at       TIMESTAMPTZ DEFAULT now()
);

-- ── reject reasons (decision #5: fixed-tag lookup, NOT free text) ──────
CREATE TABLE reject_reasons (
  reason_tag        TEXT PRIMARY KEY,
  description       TEXT
);
INSERT INTO reject_reasons (reason_tag, description) VALUES
  ('off_brand',        'Does not fit account voice / archetype'),
  ('off_trend',        'Trend has cooled / not relevant'),
  ('low_fit',          'Product-account semantic fit too low'),
  ('fatigued',         'Combo posted too recently / saturated'),
  ('seasonal_miss',    'Wrong season / timing'),
  ('compliance',       'Risk: prediction/medical/financial claim'),
  ('duplicate',        'Near-duplicate of an existing combo'),
  ('other',            'Other (still a fixed bucket, not free text)');

-- ── agent decisions (state machine, decision #4 archive) ──────────────
-- status state machine (enforced in app/core/models.py):
--   suggested -> reviewing -> revised -> approved -> generating -> asset_ready
--             -> scheduled -> published
--   any -> rejected | archived | failed
-- decision #4: no hard delete; stale/rejected combos -> 'archived' (idea bank)
CREATE TABLE agent_decisions (
  decision_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id          UUID NOT NULL REFERENCES brands(brand_id),
  account_id        UUID REFERENCES accounts(account_id),
  trigger_type      TEXT,                          -- trend | scheduled | manual
  status            TEXT NOT NULL DEFAULT 'suggested',
  recommendation    JSONB NOT NULL,                -- the combo (pillar/theme/media/jtbd/funnel/product_id)
  score             DECIMAL,                       -- deterministic combo score
  score_breakdown   JSONB,                         -- trend/fit/lift/recency/season/fatigue
  reject_reason     TEXT REFERENCES reject_reasons(reason_tag),  -- fixed tag only
  approved_by       TEXT,
  asset_url         TEXT,
  caption           TEXT,
  created_at        TIMESTAMPTZ DEFAULT now(),
  updated_at        TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT valid_status CHECK (status IN (
    'suggested','reviewing','revised','approved','rejected',
    'generating','asset_ready','scheduled','published','failed','archived'
  ))
);

CREATE INDEX idx_decisions_status   ON agent_decisions(brand_id, status);
CREATE INDEX idx_listings_product   ON product_listings(product_id);
CREATE INDEX idx_perf_post          ON performance(post_id);
-- vector ANN index (cosine). ivfflat needs data to train; safe to create empty.
CREATE INDEX idx_products_embedding ON products USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
