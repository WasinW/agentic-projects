# LUMORA — Phase 1.A backend (lean, local-first, $0)

An agentic content pipeline for the สายมู creator project. It watches product/trend
signals, **deterministically** ranks `Content × Theme × Media` combos, and surfaces
the top-N for Sin to approve — then (mock-)generates the asset and "publishes". This
slice validates the **agentic loop end-to-end at $0**: orchestrator-first with the
LLM used only as a surgical, mocked call inside generation. No API keys, no model
downloads needed to run the loop.

> Authoritative design: `07_platform_design.md` (orchestrator-first, ⚙️/🤖 boundary,
> adapter seams, the 5 resolved decisions) + `04_tech_backend.md` (SQL data model).

## What's deterministic (⚙️) vs LLM (🤖) vs gen-API (🎨)
- ⚙️ **everything in the pipeline**: scrape → embed → trend z-score → combo scoring
  (the weighted formula `0.30·trend + 0.25·fit + 0.20·lift + 0.10·recency + 0.10·season − fatigue`)
  → write top-N to the approval queue → publish. `$0` token.
- 🤖 **LLM steps** (script / storyboard / caption) and 🎨 **gen-API steps** (image / video)
  live ONLY inside generation — now a **multi-step Content Production pipeline**
  (07 §2.5), and all of it is **mocked** by default. Real Claude/FLUX/Kling sit behind
  env keys + `NotImplementedError` stubs.

## Content Production pipeline (07 §2.5) — the multi-step generator
Generation is no longer one mock step. The `generator` seam is now a **production
recipe** that decomposes into swappable **sub-adapters**, orchestrated per `media_format`:

```
ScriptGen(🤖) · StoryboardGen(🤖) · ImageGen(🎨) · VideoGen(🎨) · CaptionGen(🤖) · Assembler(⚙️)
   └── ProductionRecipe[media_format] (⚙️ orchestrator) picks which run, in order:
       M1 single image : ImageGen(1) → CaptionGen
       M2 carousel     : ImageGen(N) → CaptionGen
       M3 video/reel   : ScriptGen → StoryboardGen → per-shot[ImageGen → VideoGen]
                         → Assembler → CaptionGen
       M5/M6 vlog       : ScriptGen → ImageGen(1) → CaptionGen   (simplified — TODO b-roll)
       M7 fiction       : reuses the reel shape                  (simplified — TODO heavy)
```
Every sub-adapter exposes `est_cost()` (07 §2.5: image ~$0.025 · video clip ~$0.07 ·
LLM step ~$0.01 · assemble $0). The runner sums them into a **`production_cost_estimate`**
so Sin sees ~$/asset BEFORE/after a run (the "gen only approved" cost lever). On approve,
the flow records a per-step **production trace** + cost on the decision.

Mock sub-adapters write fake-but-**structured** stubs to `assets/` (script/shots in the
trace; `*.image.json`, `*.clip.json`, `*.final.json` manifests). $0, no keys, no models.
Real impls (`ClaudeScript`, `ReplicateImage`, `KlingVideo`) raise `NotImplementedError`
behind keys. Code: `app/production/` (`protocols.py`, `mock_subadapters.py`,
`recipes.py`, `runner.py`).

**See the full M3 reel pipeline run end-to-end with mocks:**
```bash
python cli.py produce M3-reel    # script → shots → per-shot image/clip → assemble → caption → $
python cli.py produce M1-image   # the cheap path (1 image + caption, ~$0.035)
```

## Run the mock loop WITHOUT docker (fastest — in-memory repo)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # or just pydantic+pydantic-settings for the CLI
python cli.py demo                        # seed -> cycle -> queue -> approve -> publish
```
`demo` prints the full state transition: `suggested → approved → asset_ready → published`.
Step-by-step:
```bash
python cli.py cycle          # ⚙️ run one pipeline cycle (writes ranked suggestions)
python cli.py queue          # list suggested combos (ranked by score)
python cli.py approve <id>   # 🤖🎨⚙️ run production recipe -> asset_ready (+trace +cost)
python cli.py publish <id>   # -> published
python cli.py produce M3-reel  # 🤖🎨⚙️ print the FULL production trace for a media
```
`demo` auto-approves an **M3 reel** so you see the whole multi-step trace (script →
shots → per-shot image/clip → assemble → caption → total est cost).

## Run with docker (Postgres + pgvector, still $0)
```bash
docker compose up --build
# app on http://localhost:8000 , db on :5432 , schema auto-migrates on first boot
```
Then drive the API:
```bash
curl -X POST localhost:8000/cycle
curl localhost:8000/queue
curl -X POST localhost:8000/decisions/<id>/approve     # -> asset_ready (+caption)
curl -X POST localhost:8000/decisions/<id>/revise -d '{"theme":"Cozy-home"}' -H 'content-type: application/json'
curl -X POST localhost:8000/decisions/<id>/reject -d '{"reason_tag":"off_trend"}' -H 'content-type: application/json'
curl -X POST localhost:8000/decisions/<id>/archive     # idea bank (no hard delete)
curl -X POST localhost:8000/metrics -d '{"post_id":"p1","views":1000}' -H 'content-type: application/json'
```

## The 5 resolved decisions, baked in
1. **Metrics = service/API** → `POST /metrics` + `performance` table (not manual paste).
2. **Approve per-combo + revise** → `/approve`, `/revise`, `/reject`, `/archive`.
3. **Vector(1024)** (bge-m3) → schema + embedder dim.
4. **No hard delete → archive** → `archived` status (idea bank), enforced by the state machine.
5. **Reject = fixed tags** → `reject_reasons` lookup + validated `reason_tag`.

## Where real adapters / keys plug in (the seams)
Four extensible seams live in `app/core/adapters.py` (Protocols + registry). Adding a
platform = write one class + `register(...)`, no core changes:
- **SourceAdapter** — `app/adapters/mock_source.py` → add TikTok/Shopee/Lazada.
- **GeneratorAdapter** — now the **Content Production pipeline** (`app/production/`):
  `RecipeGenerator` runs a per-`media_format` recipe of sub-adapters (`ScriptGen`,
  `StoryboardGen`, `ImageGen`, `VideoGen`, `CaptionGen`, `Assembler`). Swap a model =
  swap one sub-adapter. The legacy 1-step generator stays at `generator/single`
  (`app/adapters/mock_generator.py`); real stubs behind `GENERATOR=real` + keys.
- **PublisherAdapter** — `app/adapters/mock_publisher.py` → add TikTok/Reels/IG.
- **Scorer** — `app/services/scorer.py` → swap formula for an ML ranker later.
- **Embedder** — `app/adapters/embedder.py`: `MockEmbedder` (default) vs `Bge_M3Embedder` (`EMBEDDER=bge-m3`, needs `sentence-transformers`).

## Migrate-to-cloud note (Phase 1.B+)
Same shape, swap backends: **pgvector → Supabase** (Postgres+pgvector+RLS),
**local fs assets → Cloudflare R2** (uncomment MinIO to rehearse the S3 swap),
**the deterministic flow → Inngest** steps (cron/queue/retry), API → CF Workers.
`brand_id` is already on every table, so Phase 2 (client brands) = INSERT, not migrate.

## Layout
```
db/migrations/001_init.sql     schema (VECTOR 1024, brand_id, state machine, fixed reject tags)
app/core/models.py             domain types + state machine (transitions enforced)
app/core/adapters.py           4 seam Protocols + registry
app/core/repo.py               InMemoryRepo (default) | PgRepo (DATABASE_URL set)
app/core/settings.py           env-driven config (all mock by default)
app/adapters/                  mock_source, embedder, mock_generator, mock_publisher
app/production/                Content Production pipeline (07 §2.5):
  protocols.py                   sub-adapter Protocols + structured I/O + trace
  mock_subadapters.py            🤖/🎨/⚙️ mocks ($0) + real stubs (NotImplementedError)
  recipes.py                     media_format -> ordered steps (M1/M2/M3/M5/M6/M7)
  runner.py                      ⚙️ orchestrator + RecipeGenerator (the generator seam)
app/services/trend.py          ⚙️ z-score
app/services/scorer.py         ⚙️ weighted combo formula
app/flow/pipeline.py           ⚙️ orchestrator-first cycle (🤖 only inside generate)
app/main.py                    FastAPI: /cycle /queue /decisions/* /metrics
cli.py                         drive the full loop with no UI
```
