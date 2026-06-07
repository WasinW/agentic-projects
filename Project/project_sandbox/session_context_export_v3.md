# Session Context Export — DE Career & Creator Business Roadmap

> **Purpose:** Complete context handoff สำหรับ Claude Code
> **Session date:** 1 มิถุนายน 2026
> **User:** Sin
> **Final version:** v4 — Integrated marketing frameworks + finalized 3-axis library + multi-account strategy
> **Key meta-principle:** Sin's creative thinking = divergent + library-based + multi-direction. Future Claude should expand options, not force convergence.

---

## 📑 TABLE OF CONTENTS

1. User Memory (Work + Personal)
2. Session Part 1 — DE Q&A จิปาถะ (Detailed)
3. Session Part 2 — Career Strategy in Agentic AI Era
4. Session Part 3 — Side Business Exploration
5. Session Part 4 — Refined Roadmap (Sin's Plan)
6. Session Part 5 — Content Niche Discovery
7. Session Part 6 — IG References Aesthetic Calibration
8. **Marketing Frameworks Research**
9. **FINAL Framework: Library + Account-Level Tags** ⭐
10. **Theme Clusters (Open-Ended, Expandable)**
11. **Multi-Account Strategy**
12. Monetization Map
13. Tech Backend Architecture
14. Channel Strategy
15. Warnings & Risks
16. How to Use This Framework (Step-by-Step)
17. Open Items & Next Steps
18. Resume Prompt + Style Notes

---

## 1. 🧑‍💻 USER MEMORY

### Work Context
- **Role:** Data Engineer ที่ The1 (Central Group Thailand)
- **Stack หลัก:** Apache Beam/Dataflow (Python), BigQuery, Bigtable, Pub/Sub, Cloud Composer (Airflow), Apache Iceberg, BigLake
- **Cross-cloud:** AWS (S3, RDS), Confluent Kafka with Schema Registry
- **Infrastructure:** GitLab CI/CD, Terraform, VPC Service Controls
- **Framework ที่สร้าง:** `dataflow_common` — shared wheel + Docker image

### Current Projects
- **"Insight" project:** Customer profile realtime pipeline
- Kafka consumer pipelines (`loyalty.members.upgraded/downgraded`)
- Iceberg/BigLake managed tables
- `WriteToBigQueryCDC` + `TransformSchemasDoFn` + `WriteToBigLakeIcebergStreaming`
- GCP Professional Data Engineer cert prep

### Long-term Background
- Multi-year AWS → GCP migration (The1/Central Group)
- Siebel CRM/Oracle on AWS → GCP BigQuery/Dataflow
- Multi-phase migration: batch → streaming → pure streaming
- CDC at scale (10M records/sec target)
- Scala/Spark, Delta Lake (earlier phases)
- BigTable vs BigQuery, Storage Write API modes, Iceberg vs Delta Lake

### Personal Interests
- อาหาร, ของกิน
- เรื่องตลก, standup comedy
- Anime
- Art (consume + want to create)
- Tech
- **ของมูเตลู, ความเชื่อ** ⭐ (strongest signal)
- ที่ไหว้เจ้า

### Communication Style
- ไทยผสม English technical terms
- Practical, direct, specific
- Push back ต่อ misanalysis (3 ครั้งใน session)
- **Creative thinking:** divergent, library-based, mix-and-match
- ชอบ honest take, ไม่ชอบ over-elaboration
- Mobile-friendly preferred
- **Wants frameworks grounded in established theory, not made up**

---

## 2. 📚 SESSION PART 1 — DE Q&A จิปาถะ (Detailed)

### 2.1 ADF Ingestion Capabilities

**Q:** ADF ingest Postgres, Mongo, REST API ได้มั้ย?

**A:** ได้หมด

**Postgres:**
- Azure Database for PostgreSQL (managed)
- PostgreSQL generic (on-prem / AWS RDS)
- Self-hosted IR สำหรับ private network

**MongoDB:**
- MongoDB generic, Atlas connector, Cosmos DB for MongoDB

**REST API:**
- REST connector (JSON, pagination, OAuth2, API key)
- HTTP connector (generic, non-JSON)
- OData connector

**Caveats:**
- Cursor-based pagination แบบ non-standard → Web Activity + ForEach
- Postgres CDC ผ่าน Mapping Data Flow แต่ไม่ native เท่า Debezium
- Self-hosted IR จำเป็นถ้า source private

---

### 2.2 Spark Streaming Internals

**Q:** เขียนยังไง, micro-batch จริงมั้ย, ack ยังไง?

**A:** Structured Streaming (current) — default = micro-batch

```python
df = (spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "orders")
    .option("startingOffsets", "latest").load())

agg = (parsed
    .withWatermark("event_time", "10 minutes")
    .groupBy(window("event_time", "5 minutes"), "user_id")
    .count())

query = (agg.writeStream
    .format("parquet")
    .outputMode("append")
    .option("checkpointLocation", "gs://bucket/checkpoint")
    .trigger(processingTime="30 seconds")
    .start())
```

**Trigger types:**
- `processingTime="30 seconds"` — fixed interval
- `trigger(availableNow=True)` — process all then stop (batch-style streaming)
- Continuous mode — experimental, ~1ms latency, limited ops

**Offset tracking (WAL pattern):**
```
checkpoint/
  ├── offsets/   # planned offsets per batch N
  ├── commits/   # confirmation batch N done
  ├── sources/   # source metadata
  └── state/     # state store for stateful ops
```

**Recovery:** has offsets/N + no commits/N → reprocess; both exist → skip to N+1

**Caveats:**
- Kafka consumer group ใน UI = placeholder (don't trust lag)
- Don't move checkpoint between deploys
- RocksDB state store (Spark 3.2+) > HDFS-backed for heavy stateful

---

### 2.3 Data Mesh

**A:** Architectural paradigm โดย Zhamak Dehghani (2019) — org + tech, ไม่ใช่ tech อย่างเดียว

**4 หลักการ:**
1. Domain-oriented ownership
2. Data as a product
3. Self-serve data platform
4. Federated computational governance

**vs Centralized DW:** ownership domain teams, distributed architecture, org+tech scope

**Caveats:** Overkill for small org, tooling immature, often "Data Mesh-inspired" hybrid

---

### 2.4 Incremental Load vs CDC

| | Incremental | CDC |
|---|---|---|
| Source | Table state | Transaction log |
| DELETE | ❌ | ✅ |
| Every state | ❌ | ✅ |
| Latency | min-hr | sec-ms |
| Source load | High | Low |
| Setup | Easy | Complex |

**Incremental:** append-only OK, latency OK, simple

**CDC:** real-time, need DELETE/history, multi-consumer, no `updated_at`

**Tools:** Debezium, AWS DMS, Datastream, Fivetran (some log-based, some query-based)

**Pattern:** SCD Type 2 + CDC for history, BigQuery Storage Write API `_CHANGE_TYPE`, hybrid (snapshot → CDC stream)

**Warning:** Fivetran/Airbyte บางตัวเป็น query-based ไม่ใช่ log-based CDC จริง

---

### 2.5 Microsoft Purview

**A:** Multi-cloud data governance + Information Protection

**2 ขา:**
1. Data Governance (Data Map, Catalog, lineage, DQ, classification)
2. Information Protection (DLP, sensitivity labels, AI governance)

**GCP equivalent:** Dataplex Catalog + Lineage + DQ + Cloud DLP

**Pricing:** DGPU model — $15/Basic DGPU

**Pros:** Multi-cloud, M365 integration, AI governance first-class
**Cons:** Setup complex, UI ไม่ดีที่สุด

**สำหรับ The1:** GCP-heavy → Dataplex น่าจะ fit กว่า

---

## 3. 💼 SESSION PART 2 — Career in Agentic AI Era

### Reality
- AI agents augment ไม่แทน DE wholesale
- "Data plumber" หาย, architect/framework builder value มากขึ้น
- **Sin อยู่ฝั่ง builder** = ไม่ใช่กลุ่มเสี่ยง

### 5 Career Paths
1. **AI-Augmented Data Platform Engineer** ⭐ ใกล้สุด (Vector DB, embedding, RAG infra)
2. AI Agent / RAG Engineer (application layer, LangGraph)
3. Analytics/Decision Engineer with AI (NL→SQL, conversational BI)
4. AI Solutions Architect (system level)
5. **Founder / IC Specialist** ← Sin's chosen direction

### Skills Roadmap
- **Now:** Vector DB, embedding models, RAG patterns, LLM APIs
- **This quarter:** 1 agent framework deep (LangGraph), function calling, observability
- **6 months:** Evaluation, fine-tuning basics, cost engineering, guardrails

### The1 AI Use Cases (sandbox)
1. Conversational analytics (NL→SQL on BQ)
2. Hyper-personalization (real-time recommendation)
3. AI customer service (Thai, grounded)
4. Campaign optimization (agent A/B loop)
5. Voice of Customer intelligence
6. Internal data assistant Slack bot

### Strategic Principles
- Use The1 as sandbox
- Build in public ภาษาไทย (gap)
- Don't chase quarterly hype
- DE + AI literate ในไทย = scarce + premium

---

## 4. 🚀 SESSION PART 3 — Side Business Exploration

### Sin's Motivation
- ยังทำงานประจำ "อยากหนีงานประจำ"
- Want freelance/part-time, creative, monetizable
- Use existing DE+DS+AI knowledge

### Reality Check
- 70% of business = sales+marketing+ops (not tech)
- AI hype doesn't make sales easy
- Financial pressure kills creativity

### "หนีงาน" Progression
```
ขั้น 0: ประจำ (now)
ขั้น 1: ประจำ + side project
ขั้น 2: ประจำ + side income (real customers)
ขั้น 3: ประจำ part-time + business 60%
ขั้น 4: Business full-time (revenue ≥ salary × 1.5, 6 เดือนต่อเนื่อง)
```
**ห้ามกระโดดข้ามขั้น**

### Data Fabric (Architectural Concept) — NOT Microsoft Fabric

4 pillars: Active metadata + Data virtualization + Knowledge graph + AI/ML automation

vs Data Mesh: Fabric = tech-led centralized metadata; Mesh = org-led decentralized

**Sin's application idea:** Multi-platform aggregation tool (Shopee/Lazada/TikTok Shop) = Data Fabric pattern for creator economy

---

## 5. 🗺️ SESSION PART 4 — Refined Roadmap (Sin's Actual Plan)

```
Phase 1 (NOW):
  Content + Multi-channel + Online selling (creator business)
  + Internal tech backend (own tool, NOT for sale yet)
  
Phase 2 (Later):
  Productize backend → serve SME/B2B
```

**Pattern:** Build creator empire → invisible tooling moat → productize later
(Pieter Levels, Justin Welsh, Marc Lou model)

### Sin's 4 Questions
1. Content niche? (need creative)
2. Channels? (all of them)
3. Internal backend tech (own use)
4. Future productization (premature now)

---

## 6. 🎯 SESSION PART 5 — Content Niche Discovery

### Sin's 3 Discovery Q&A
- **Q1 (เวลา/เงิน):** อาหาร, ตลก, anime, art, tech, **ของมู**, ที่ไหว้เจ้า
- **Q2 (เพื่อนถาม):** ตลก, tech, **ของมู**, ที่ไหว้เจ้า
- **Q3 (ดูไม่เบื่อ):** Standup, anime, **art, อยากทำ art สายมู**, tech

### Convergence
**Theme:** Spiritual/Mystical (สายมู) ⭐ — broad theme, not narrow positioning

---

## 7. 🎨 SESSION PART 6 — IG References (Aesthetic Calibration)

### @odysseyml (360K)
AI lab, epic fantasy/sci-fi worldbuilding, cinematic single frames

### @hellopersonality (2.5M) ⭐
AI ANIMATIONS, first-person POV motion, vaporwave/anime/cyberpunk
- Patreon monetization
- Secondary account: @hellothoughtpalace

### @abeastinside (110K)
REAL photography (not AI), Chongqing cyberpunk, blue neon, lone figure
- Side accounts: @ejay_portrait, @ejaytrip

### @metronovon (185K, verified) ⭐
Japan sci-fi artist, quiet human-centered futures, contemplative
- Shopify shop monetization
- Highlights: Archives, Silent Futures, Inner signals, Outer codes, Prototypes

### Aesthetic Pattern Sin Likes
- Cinematic + atmospheric
- Moody lighting (neon + dark, lantern + mist)
- Lone figure in vast world
- Sci-fi + fantasy fusion
- Anime/manga DNA (Akira, Ghost in the Shell, Ghibli)
- Cool palette dominant

**IMPORTANT:** Sin ชอบ **multiple aesthetics** ไม่ใช่อันเดียว — ไม่ converge เป็น "Cyber-Spiritual" alone

---

## 8. 📊 MARKETING FRAMEWORKS RESEARCH

> Searched & analyzed established marketing frameworks to validate Sin's library structure

### Top Frameworks Used in Industry

| Framework | What it covers | Used by |
|---|---|---|
| **Content Pillars** | 3-5 core topical buckets | Modern social media (Cloud Campaign, HubSpot) |
| **Brand Voice + Archetype** | 12 Jungian archetypes (Visionary, Sage, Jester, etc.) | Sprout Social, enterprise brands |
| **Brand Persona** | Character derived from archetype | Sprout's "Luminary" pattern |
| **JTBD (Jobs To Be Done)** | "What job is content hired for" | Christensen, CMI, modern marketers |
| **Audience Persona** | Fictional character of target audience | Universal best practice |
| **Hero/Hub/Hygiene (HHH)** | Production cadence per funnel stage | Google/YouTube, content agencies |
| **STP** | Segment-Target-Position | Kotler classic, pre-strategy |
| **AIDA** | Attention-Interest-Desire-Action | Sales funnel, per-post tactical |
| **Brand Pyramid** | Attributes→Benefits→Values→Personality→Essence | Brand strategy consultancies |
| **Golden Circle** | Why→How→What | Simon Sinek |

### Mapping to Sin's Framework

| Sin's axis | Industry equivalent | Status |
|---|---|---|
| Content | Content Pillars | ✅ Aligned with standard |
| Theme | (Sin's unique angle — visual creator specific) | ✅ Strong addition |
| Media | Format mix / Channel | ✅ Aligned |
| Voice | Brand Voice + Archetype | ✅ Industry best practice |
| **(Missing)** | **Audience Persona** | ⚠️ Added (account-level) |
| **(Missing)** | **JTBD / Intent** | ⚠️ Added (optional per-post) |
| (Skipped) | HHH funnel stage | 🟡 Optional |

### Key Quotes from Research
- "Content pillars are overarching themes or topics you consistently create content around — foundational categories that support entire content strategy" (Cloud Campaign 2025)
- "Sprout's brand voice uses archetypes and personas — Visionary archetype + Luminary persona inform voice, tone, language" (Sprout Social)
- "JTBD theory specifies a consumer's 'job' — they 'hire' content to complete jobs" (CMI / Christensen)
- "Companies with documented content strategy report 46% higher conversion rates" (HubSpot 2025)

---

## 9. ⭐ FINAL FRAMEWORK: Library + Account-Level Tags

```
═══════════════════════════════════════════════════
  ACCOUNT-LEVEL (fixed per channel, define ครั้งเดียว)
═══════════════════════════════════════════════════
  🎭 Voice           — brand archetype + persona
  👥 Audience Persona — who is this account for
  🎯 Niche scope     — broad / narrow positioning

═══════════════════════════════════════════════════
  POST-LEVEL (vary per post, the "Library" axes)
═══════════════════════════════════════════════════
  💎 Content     — what to sell + topic (Pillar)
  🌍 Theme       — world/setting/era
  📹 Media       — format / production type

  Optional tags:
  🎯 JTBD/Intent — what job this post does for audience
  📊 Funnel Stage — Hero/Hub/Hygiene (optional)
═══════════════════════════════════════════════════
```

### 💎 Content (Pillar) — สิ่งที่ขาย + topic

| Code | Pillar | Products/Affiliate |
|---|---|---|
| C1 | สายมู — เทพเจ้า | เครื่องราง, จี้, รูป |
| C2 | สายมู — ดวง/oracle | Card deck, course, app |
| C3 | สายมู — ยันต์/คาถา | ยันต์, ตะกรุด |
| C4 | สายมู — ที่ไหว้เจ้า/pilgrimage | Travel package, hotel |
| C5 | สายมู — พิธีกรรม/ritual | ธูป, เทียน, ผง, น้ำมัน |
| C6 | Art product — original | Art print, wallpaper, NFT |
| C7 | Art product — commission | Custom art service |
| C8 | Education — process/tutorial | Course, e-book |
| C9 | Comedy/skit | Audience build, brand collab |
| C10 | อื่นๆ (expandable) | — |

### 🌍 Theme — see Section 10 (Theme Clusters)

### 📹 Media — format/production type

| Code | Media | Effort |
|---|---|---|
| M1 | Single AI image | Low |
| M2 | AI image carousel (5-10) | Medium |
| M3 | AI animation reel (Runway/Kling/Luma) | High |
| M4 | Real photography (mobile/camera) | Medium |
| M5 | Vlog (real footage + storytelling) | High |
| M6 | Talking head + b-roll | High |
| M7 | แต่งเรื่อง (fiction narrative + AI) — "movie feel" | Very high |
| M8 | First-person POV walk | Medium |
| M9 | Process / time-lapse | Low-medium |
| M10 | Tutorial / explainer | Medium |
| M11 | Interactive (oracle, quiz, poll) | Low |
| M12 | Mixed media | Variable |

### 🎯 JTBD / Intent (Optional, per-post)

Examples of jobs audience "hires" content for:
- "Help me feel calm before work" → contemplative content
- "Help me know what to buy" → product recommendation
- "Help me feel cool about my beliefs" → aesthetic art
- "Help me laugh at myself" → comedy
- "Help me find sacred sites" → travel
- "Help me understand traditions" → educational
- "Help me look intellectual" → deep/cultural content
- "Help me decorate my space" → wallpaper/art
- "Help me explore new aesthetics" → art exploration

**Tag format:** "When [situation], help me [outcome] so I can [reason]"

### 📊 Funnel Stage (Optional, HHH model)

- **Hero (5%):** Tentpole content, viral push, brand awareness — high effort, rare
- **Hub (35%):** Regular series, recurring format, audience retention — medium effort
- **Hygiene (60%):** Search/educational, evergreen, always-on — high volume

---

## 10. 🌍 THEME CLUSTERS (Open-Ended, Expandable)

> Theme is **NOT a fixed list** — Sin can add new themes anytime as creativity dictates
> Clusters serve as navigation/categorization, not constraint

```
🌆 Future-tech         → cyberpunk, AI era, neon, holographic, vaporwave
🏚️ Post-apocalyptic    → Wall-E, Mad Max, abandoned worlds, decay
🌀 Liminal/Surreal     → backroom, dreamcore, weirdcore, uncanny
👽 Retro sci-fi        → Dr Who, 80s sci-fi, atompunk, dieselpunk
🏰 Fantasy             → medieval, magical realism, Ghibli soft
🌌 Multiverse/Time     → Loki, parallel reality, time-bending
⏳ Historical          → ancient India, China, Thai, Egypt, lost civilizations
🏙️ Contemporary        → modern Bangkok, daily life, photoreal
🌾 Pastoral            → countryside shrine, nature, Studio Ghibli rural
🌠 Cosmic              → space, celestial, nebula, astrology
🎮 Game/Anime worlds   → specific IP-inspired (careful w/ copyright)
🎨 Pure abstract       → no setting, art-focused, geometric
[+] Expandable          → add new themes anytime
```

**Theme value:**
- Audience targeting (different clusters attract different demographics)
- Algorithm tagging (TikTok/IG algo understands clusters)
- Content variety (rotate to prevent monotone)
- Affiliate matching (Future-tech theme → cyber products; Historical → traditional มู products)

---

## 11. 🌐 MULTI-ACCOUNT STRATEGY

### Why Multi-Account?

**Pros:**
- Algorithm favors clear positioning
- Audience targeting precise
- Test parallel directions
- Risk diversification
- Each account = different monetization angle

**Cons:**
- Effort multiplied
- Slower individual growth
- Cross-promote algorithm-unfriendly

### Reference Patterns

| Main account | Side accounts | Logic |
|---|---|---|
| @hellopersonality | @hellothoughtpalace | Main vs secondary |
| @abeastinside | @ejay_portrait, @ejaytrip | Vertical split |

### 4 Strategy Options

**Option A: Single brand, multi-aesthetic mix**
- Pros: Concentrated effort
- Cons: Algo signals mixed

**Option B: Multi-account parallel (day 1)**
- Pros: Clear positioning each
- Cons: 3x effort

**Option C: Hub + Spoke**
- Pros: Best of both
- Cons: Most complex

**Option D: Sequential expansion** ⭐ RECOMMENDED for Sin
- Start 1 account → validate → 5-10K followers → open 2nd → repeat
- **Reason:** Sustainable for part-time + learning per stage
- Compatible with full-time job

### 3 Split Patterns for Sin

**Pattern 1: By Aesthetic Family**
- Account 1: Cyber-spiritual (Theme = Future-tech)
- Account 2: Traditional (Theme = Historical / Contemporary)
- Account 3: Photography travel (Theme = real + pilgrimage)

**Pattern 2: By Content Pillar**
- Account 1: Deities (C1+C3)
- Account 2: Oracle/daily reading (C2)
- Account 3: Temple travel (C4)

**Pattern 3: By Media Format**
- Account 1: Art portfolio (M1+M2)
- Account 2: Reels/animation (M3+M8)
- Account 3: Educational/face (M5+M6)

### Recommended Path for Sin

```
Month 1-3:   ONE account, validate library
Month 4-6:   If 3-5K followers → open 2nd account
Month 7-12:  Scale based on traction; consider 3rd
```

**Backend implication:** Build for multi-account from day 1 (shared prompt library + per-account scheduling)

---

## 12. 💰 MONETIZATION MAP

### Affiliate (ปักตะกร้า) — Day 1
- เครื่องราง, จี้, สร้อย — 5-15%
- ยันต์, ตะกรุด — 5-10%
- น้ำมัน, ผง, เครื่องหอม — 8-15%
- Crystal, หิน — 10-15%
- Oracle deck, tarot, หนังสือ — 5-10%

### Digital Products (Month 3-6+)
- AI art prints — $5-15 mass, $20-80 premium
- Custom oracle deck PDF — $20-50
- Daily journal template — $10-30
- Personalized AI art commission (birth/zodiac) — $30-100
- Wallpaper pack subscription
- Course — $50-200

### Subscription (Month 6+, need audience)
- Patreon: daily oracle + exclusive — 99-299/month
- Discord community

### Brand Partnership (50K+)
- ร้านเครื่องราง, crystal brand, ของมู online
- Hotel/restaurant near sacred sites
- Fashion/streetwear (aesthetic crossover)
- Gaming/anime brand

### Cross-Aesthetic Upside
- Traditional theme → traditional มู (large audience, lower AOV)
- Future-tech theme → premium art print, brand collab (smaller, higher AOV)
- Comedy → viral, broad
- Photography → travel affiliate

**Multi-account = multi-monetization vehicle**

---

## 13. 🛠️ TECH BACKEND ARCHITECTURE

### Design Principle
Build once, serve multiple accounts. Backend = Sin's unfair advantage.

### Phase 1 (Month 1-2): MVP
- **AI Art Pipeline:** FLUX.1 / SDXL / Midjourney / Replicate API
  - 30-50 images/day, auto-categorize by Content/Theme tags
  - Metadata stored in BigQuery
- **Prompt Library:** Database per (Content × Theme × style)
  - Versioned, searchable, performance-tracked
- **Content Calendar:** Notion + automation
  - Per-account schedule, caption templates, hashtag library

### Phase 2 (Month 3-6): Automation
- **Trending detection:** Scrape TikTok Shop ของมู → notification
- **Personalization engine:** Input วันเกิด → custom AI art (future paid)
- **AI animation pipeline:** Image → Runway/Kling/Luma → reel
- **Caption AI:** Claude API generates variants tagged with Content+Theme+JTBD
- **Multi-account router:** Asset routing to correct account

### Phase 3 (Month 6+): Scale & Productize
- API service for others (productize)
- Newsletter automation per account
- Affiliate tracking cross-platform
- Cohort analytics per (Content × Theme × Media)

### Stack
- Backend: Python + GCP Cloud Run / Cloudflare Workers
- Data: BigQuery + Cloudflare D1
- AI Image: FLUX.1 on Replicate/RunPod, Midjourney
- AI Animation: Runway Gen-3/4, Kling, Luma
- AI Text: Claude API, GPT-4
- Scraping: Playwright + Apify
- Automation: Notion API, Make.com, n8n
- Tracking: PostHog, Plausible
- Storage: Cloudflare R2 / GCS

### Cost (Phase 1)
- AI generation: $30-80/month
- Animation: $20-50/month
- Infra: $10-20/month
- **Total: ~$60-150/month**

### Prompt Template Example
```
"[Subject from Content pillar] in [Theme description] style,
volumetric atmospheric lighting,
[Color palette per Theme],
[Composition: lone figure, wide shot, POV, etc.],
[Mood per JTBD/intent],
shot on 35mm, [Color grade reference],
inspired by [Artist/Film reference]"
```

Example (C1 × Future-tech × M1):
```
"Phra Phrom (Brahma) in Cyberpunk Neo-Bangkok,
volumetric neon lighting with atmospheric mist,
deep blue and violet palette with gold sacred accents,
lone figure silhouette small in foreground,
contemplative mysterious mood,
shot on 35mm, Blade Runner color grade,
inspired by Akira, Ghost in the Shell"
```

---

## 14. 📺 CHANNEL STRATEGY

### Per-Account Priority (Phase 1)
- **TikTok + Reels** = 70% primary
- **YouTube Shorts** = repurpose 0% extra effort
- **LinkedIn** = repurpose text 10% (B2B future)
- **Long-form YouTube** = 1/month, 20% (SEO)

### Skip Until Audience Built
- Facebook page (algo dead)
- IG feed only (use Reels)
- Twitter/X (low ROI visual TH)

### Multi-Platform Linkage
- IG and Meta linked (auto-cross-post Reels)
- TikTok separate
- YouTube separate

### Naming Strategy (TBD)
- Umbrella brand + per-account variants
- Or creator name + suffix
- Memorable in Thai market

---

## 15. ⚠️ WARNINGS & RISKS

1. **Respect > satire** — comedy ของมู ต้อง self-deprecating ไม่ใช่เยาะคนอื่น
2. **AI art + sacred imagery** — "respectful homage" not "casual remix"
3. **Don't be a guru** — "fellow explorer" framing safer
4. **Avoid prediction/medical claims** — legal risk + scammy
5. **Cross-aesthetic balance** — multi-account แก้ปัญหานี้
6. **Voice consistency > aesthetic consistency** — caption/tone unifies
7. **The1 IP boundary** — pattern OK, no proprietary code/data
8. **TikTok Shop commission ลด** (2025) — diversify, don't rely on one platform
9. **AI image of real deities** — culturally sensitive, watch reactions
10. **Algorithm sensitivity to "religion"** — some platforms shadow-ban, test carefully

---

## 16. 📖 HOW TO USE THIS FRAMEWORK (Step-by-Step)

### Step 1: Define Account-Level (do once per account)
1. Pick **Voice / Archetype** (e.g., Magician + Explorer)
2. Define **Audience Persona** (1-2 personas, e.g., "GenZ มู สาย aesthetic, 22-32, Bangkok working pro")
3. Set **Niche Scope** (broad vs narrow)

### Step 2: Plan Content Mix
1. Choose 2-4 **Content Pillars** for this account
2. Pick 2-4 **Theme Clusters** to focus
3. List **Media formats** Sin can produce sustainably

### Step 3: Create Post (per piece)
1. **Content:** which pillar?
2. **Theme:** which world/setting?
3. **Media:** which format?
4. (Optional) **JTBD:** what job does this post do?
5. (Optional) **Funnel stage:** Hero / Hub / Hygiene?

### Step 4: Tag Everything for Analytics
Each post tagged with all dimensions → backend tracks which combos perform best

### Step 5: Iterate
- Weekly review: which (Content × Theme × Media) drove engagement?
- Monthly: adjust pillar/theme mix
- Quarterly: revisit Audience Persona based on actual followers

---

## 17. 🎬 OPEN ITEMS & NEXT STEPS

### Decisions Made ✅
- **Theme:** Spiritual/Mystical (broad)
- **Approach:** Library framework + account-level tags
- **Account strategy:** Sequential expansion (Option D)
- **Phase structure:** Creator first → productize later
- **Platform priority:** TikTok-first, multi-channel repurpose
- **Added:** Audience Persona (account-level), JTBD (optional per-post)
- **HHH:** Optional, can skip phase 1
- **Theme list:** Open-ended, 12 clusters as starter

### Pending Decisions 🔄
1. **First account brand archetype** — Magician? Explorer? Sage? Jester? (need to pick)
2. **First account Audience Persona** — define 1-2 personas
3. **First account Content Pillars** — which 2-4?
4. **First account Theme Clusters** — which 2-4 to focus first?
5. **Channel naming + brand identity** (logo, color, typography)
6. **Show face or stay behind?**
7. **Affiliate-first vs digital product day 1?**

### Immediate Next Steps 📋
1. Pick first account's archetype + persona
2. Define Sin's voice (3-5 sample captions to test)
3. Choose first batch focus (2-3 combos)
4. Brainstorm channel/brand name (10 candidates)
5. Setup minimum tech backend (1 prompt → 1 image working)
6. Create 10 sample posts in different combos
7. Soft launch with friends/family feedback

### Future Phases (Not Active)
- Phase 2: Audience 10K+ → open account #2
- Phase 3: Digital products + subscription
- Phase 4: Productize backend for SME/B2B

---

## 18. 📞 RESUME PROMPT + STYLE NOTES

### Style Notes for Next Claude

- Sin สื่อสารภาษาไทย + English technical terms
- ชอบ practical, specific, mobile-friendly
- **Push back ถ้าหลงประเด็น** — เกิด 3 ครั้งใน session:
  1. ตอบเรื่อง Microsoft Fabric แทน Data Fabric concept
  2. ลุยลึก B2B strategy เมื่อต้องการ content niche basics
  3. Force convergence "Cyber-Spiritual only" ขณะที่ต้องการ multi-direction
- **Creative thinking:** divergent, library-based, NOT premature convergence
- ชอบ honest take, ไม่ชอบ over-positive
- ใช้ table/structured comparison เมื่อช่วย clarity
- หลีกเลี่ยง over-formatting, excessive emoji
- **Wants frameworks grounded in established theory** — verify with research

### Key Meta-Lessons for Future Claude

1. **Don't converge prematurely** — Sin prefers breadth
2. **Multi-direction > single-direction**
3. **Verify framework against established theory** before proposing
4. **Confirm understanding before deep-dive**
5. **Library mindset** — keep options expandable

### Resume Prompt for Claude Code

```
สวัสดีครับ ผม Sin DE ที่ The1 — continue session จาก mobile

Context สรุป:
- Theme: Spiritual/Mystical (สายมู) — broad, multi-aesthetic
- Framework: Library (3 axes: Content × Theme × Media) 
  + Account-level (Voice/Archetype + Audience Persona + Niche scope)
  + Optional per-post tags (JTBD, HHH funnel)
- Account strategy: Multi-account, sequential expansion (start 1 → 2-3)
- Roadmap: Creator first → tech backend invisible moat → productize later
- Still working full-time, Phase 1 side hustle

Pending decisions:
- First account: archetype, persona, content pillars (2-4), theme clusters (2-4)
- Channel/brand naming
- Show face or not?
- Affiliate vs digital product day 1?

Tech backend: minimum viable AI art pipeline + multi-account ready

อยากต่อจาก [topic]
```

### References

- Anthropic's "Building Effective Agents" — for AI work
- Creator references:
  - @hellopersonality (Patreon, 2.5M)
  - @metronovon (Shopify, 185K, verified)
  - @odysseyml (360K, AI worldbuilding)
  - @abeastinside (110K, real cyberpunk photography, multi-account)
- Founder/creator models: Pieter Levels, Justin Welsh, Marc Lou, Sahil Bloom
- Marketing frameworks: Content Pillars, Brand Archetypes, JTBD (Christensen), HHH (Google), STP (Kotler), Audience Persona

---

**End of Context Export v4 — Final**

> **Session takeaway:** Sin's framework (Content × Theme × Media) aligns with industry standard (Content Pillars + format mix). Added missing dimensions (Audience Persona, JTBD) grounded in established marketing theory. Theme dimension intentionally open-ended for creative freedom. Multi-account sequential expansion = sustainable path for part-time creator.
