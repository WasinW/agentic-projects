# 03 - AI Services & Tools

## 1. LLM (Text / Script Generation)

### Cloud APIs

| Model | Provider | Input/1M tokens | Output/1M tokens | Best For |
|-------|----------|-----------------|-------------------|----------|
| **Claude Opus 4** | Anthropic | $15.00 | $75.00 | Nuanced creative writing, emotional scripts |
| **Claude Sonnet 4** | Anthropic | $3.00 | $15.00 | **Recommended** — quality/cost balance |
| **GPT-5.2** | OpenAI | $1.75 | $14.00 | Flagship alternative |
| **GPT-5 Nano** | OpenAI | $0.05 | $0.40 | Budget tasks |
| **Gemini 2.5 Pro** | Google | $1.25 | $5.00 | GCP integration |
| **Gemini 2.0 Flash** | Google | $0.08 | $0.30 | **Cheapest** — high-volume batch |

### Local / Self-Hosted

| Model | Size | VRAM (Q4) | Quality | License |
|-------|------|-----------|---------|---------|
| **Llama 3.1 8B** | 8B | 5-6 GB | Good | Meta (commercial OK) |
| **Qwen 2.5 14B** | 14B | 8-10 GB | Very Good | Apache 2.0 |
| **Qwen 2.5 32B** | 32B | 20-24 GB | Excellent | Apache 2.0 |
| **DeepSeek-R1 32B** | 32B | 20-24 GB | Excellent reasoning | MIT |

### Recommendations by Task

| Task | Recommended Model | Cost/Clip |
|------|-------------------|-----------|
| Script generation | Claude Sonnet 4 (~2K tokens) | ~$0.03 |
| Emotional analysis | Claude Sonnet 4 (~1K tokens) | ~$0.02 |
| Visual prompts | Claude Sonnet 4 (~1K tokens) | ~$0.02 |
| Batch processing (100+ clips) | Gemini 2.0 Flash | ~$0.005 |
| Local dev/testing | Ollama + Llama 3.1 8B | Free |

---

## 2. Image Generation

### Cloud APIs

| Service | Price/Image | Quality | API | Best For |
|---------|-------------|---------|-----|----------|
| **Flux 1.1 Pro** (Black Forest Labs) | $0.03-0.05 | Highest realism | Replicate, fal.ai | **Recommended** — photorealistic |
| **DALL-E 3** (OpenAI) | $0.04 (std), $0.08 (HD) | Very Good | OpenAI API | Text in images, precise prompts |
| **Stable Diffusion 3.5** (Stability) | $0.002-0.035 | Good-Very Good | Stability API | **Cheapest** at volume |
| **Imagen 3** (Google) | Pay-per-use | Very Good | Vertex AI | GCP-native teams |
| **Midjourney** | $10-60/mo subscription | Best aesthetics | No public API | Manual use only |

### Self-Hosted

| Model | VRAM | Speed | Notes |
|-------|------|-------|-------|
| **SDXL** | 6-10 GB | ~5 sec/img | Good quality, huge ecosystem |
| **Flux.1 Schnell** | 8-12 GB | ~3 sec/img | Fast, good quality |
| **Flux.1 Dev** | 10-16 GB | ~10 sec/img | Best self-hosted quality |

**ComfyUI** = recommended for self-hosted pipeline (node-based, API-driven)

---

## 3. Video Generation

### API Comparison

| Service | Model | Resolution | Duration | Cost/sec | API Status |
|---------|-------|-----------|----------|----------|------------|
| **Kling 3.0** | Kuaishou | **4K native** | Up to 20s | **$0.029** | Available |
| **Runway** | Gen-4.5 Turbo | Up to 4K | 5-10s | $0.05-0.15 | REST API (mature) |
| **Sora 2** | OpenAI | 720p-1080p | 5-20s | Free/$0.10-0.50 | Preview (expanding) |
| **Google Veo 3.1** | DeepMind | HD | 5-8s | $0.75 | Vertex AI (GA) |
| **MiniMax Hailuo** | MiniMax | 1080p | Up to 10s | Varies | Third-party wrappers |

### Recommendation

```
Budget-optimized:     Kling 3.0 ($0.029/sec) — best value, 4K
Feature-rich:         Runway Gen-4.5 — most mature API, good documentation
Premium/Enterprise:   Google Veo 3.1 — SLA, HIPAA, GCP integration
Experimental:         Sora 2 — promising but API still in preview
```

### Cost for 60-second Video

| Service | 60 sec cost |
|---------|-------------|
| Kling 3.0 | **$1.74** |
| Runway Gen-4.5 | $3.00-9.00 |
| Sora 2 Pro | $6.00-30.00 |
| Google Veo 3.1 | $45.00 |

### API Example (Runway)

```python
import httpx

async def generate_video(prompt: str, duration: int = 5) -> str:
    """Generate video clip via Runway API."""
    async with httpx.AsyncClient() as client:
        # Create video job
        resp = await client.post(
            "https://api.dev.runwayml.com/v1/videos",
            headers={"Authorization": f"Bearer {RUNWAY_API_KEY}"},
            json={
                "model": "gen4_turbo",
                "prompt": prompt,
                "duration": duration,
                "resolution": "1080p",
            }
        )
        job_id = resp.json()["id"]

        # Poll for completion
        while True:
            status = await client.get(
                f"https://api.dev.runwayml.com/v1/videos/{job_id}",
                headers={"Authorization": f"Bearer {RUNWAY_API_KEY}"},
            )
            data = status.json()
            if data["status"] == "completed":
                return data["download_url"]
            await asyncio.sleep(5)
```

---

## 4. Music / Sound Generation

| Service | Type | Price | API | Best For |
|---------|------|-------|-----|----------|
| **Suno V5** | Full song (vocals + instruments) | $10-30/mo | Third-party wrappers | **Best quality**, commercial rights |
| **Udio** | Full song | Similar to Suno | Third-party wrappers | Alternative to Suno |
| **Stable Audio** | Music + SFX | Stability AI pricing | Official API | Sound effects, ambient |
| **MusicGen** (Meta) | Instrumental music | Free (self-hosted) | HuggingFace | **Free**, full control |
| **Bark** (Suno) | Speech + music + SFX | Free (self-hosted) | Open source (MIT) | Mixed audio, free |

### Suno Pricing

| Plan | Price | Credits/mo | Commercial Use |
|------|-------|------------|---------------|
| Free | $0 | 50 | No |
| Pro | $10/mo | 2,500 | Yes |
| Premier | $30/mo | 10,000 | Yes |

### MusicGen (Self-Hosted, Free)

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration

processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

inputs = processor(
    text=["upbeat electronic music for product showcase"],
    padding=True,
    return_tensors="pt",
)
audio = model.generate(**inputs, max_new_tokens=512)
```

---

## 5. TTS / Voice Generation

| Service | Quality | Thai Support | Price | API | Best For |
|---------|---------|-------------|-------|-----|----------|
| **ElevenLabs** | Best overall | Limited voices | $5-330/mo | REST + WebSocket | **Premium quality** |
| **Fish Audio** | Very Good | Good | 1/12 of ElevenLabs | REST API | **Best value** |
| **Narakeet** | Good | **93 Thai voices** | Pay per minute | REST API | **Thai content** |
| **OpenAI TTS** | Good | Limited | ~$0.015/min | OpenAI API | Simplest integration |
| **Google Cloud TTS** | Good | Multiple Thai | Pay per char | GCP API | GCP integration |
| **Bark** (OSS) | Good (expressive) | 13 languages | Free | Self-hosted | Free, experimental |

### ElevenLabs Pricing

| Plan | Price | Credits | Voice Clone | Best For |
|------|-------|---------|-------------|----------|
| Free | $0 | 10K (~20 min) | No | Testing |
| Starter | $5/mo | — | Instant clone | Personal use |
| Creator | $22/mo | — | Professional clone | Content creators |
| Scale | $330/mo | Millions | Full features | Production |

### Fish Audio — Best Value

```python
import httpx

async def generate_tts(text: str, voice_id: str) -> bytes:
    """Fish Audio TTS — ~1/12 cost of ElevenLabs."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.fish.audio/v1/tts",
            headers={"Authorization": f"Bearer {FISH_API_KEY}"},
            json={
                "text": text,
                "reference_id": voice_id,
                # Emotion tags: (angry), (sad), (happy), (in a hurry)
            }
        )
        return resp.content
```

### Narakeet — Best for Thai

- **93 Thai voices** (largest selection)
- Natural sounding, multiple gender/age variants
- API available for programmatic use
- Best choice specifically for Thai language content

---

## 6. Vector Database (RAG)

| Database | Type | Free Tier | Prod Pricing | Best For |
|----------|------|-----------|-------------|----------|
| **ChromaDB** | Embedded OSS | Free forever | Self-host | **Prototyping**, dev |
| **Qdrant** | OSS + Cloud | Yes | ~$102/mo | **Production** — recommended |
| **Pinecone** | Managed SaaS | Yes (limited) | ~$25+/mo | Zero-ops, simplest |
| **pgvector** | Postgres ext | Free | Existing PG | Small datasets, ACID |
| **Weaviate** | OSS + Cloud | Yes | Pay-per-use | Hybrid search |

### Recommendation

```
Development:   ChromaDB (zero cost, instant setup, in-process)
Production:    Qdrant Cloud or self-hosted on GKE
GCP-native:    Vertex AI Vector Search (managed ANN)
AWS-native:    Amazon S3 Vectors (new, 90% cheaper than OpenSearch)
```

---

## 7. Automation & Orchestration

### Agentic Frameworks

| Framework | Architecture | Best For | Status (2026) |
|-----------|-------------|----------|---------------|
| **LangGraph** | Graph-based state machine | **Production** — complex pipelines | Active, recommended |
| **CrewAI** | Role-based multi-agent | Quick prototyping | Active |
| **LlamaIndex** | RAG-first agent | **RAG layer** — combine with LangGraph | Active |
| **AutoGen** (MS) | Conversational | Multi-party dialogues | Maintenance mode |
| **OpenAI Agents SDK** | Managed runtime | OpenAI ecosystem | Active (vendor lock-in) |

### Workflow Automation

| Tool | Integrations | Self-Host | AI Nodes | Best For |
|------|-------------|-----------|----------|----------|
| **n8n** | 400+ | Yes (free) | 70 AI nodes + LangChain | **Developers** — recommended |
| **Make** | 1,500+ | No | Good | Visual workflows, mid-budget |
| **Zapier** | 7,000+ | No | Good | Non-technical users |

### Content Pipeline Tools

| Tool | Function | Type |
|------|----------|------|
| **Opus Clip** | Long → short-form repurposing | Cloud service ($15-29/mo) |
| **Remotion** | Programmatic video (React-based) | Open source (license for >3 employees) |
| **Shotstack** | Cloud video rendering API | Pay-per-render |
| **Creatomate** | Template-based video rendering | Pay-per-render |
| **FFmpeg** | Video processing backbone | Free (CLI/library) |
| **MoviePy** | Python video editing | Free (wraps FFmpeg) |

---

## 8. Publishing APIs

### Platform APIs

| Platform | API | Key Limits | Notes |
|----------|-----|-----------|-------|
| **TikTok** | Content Posting API | Must pass compliance audit for public posts | `video.publish` scope |
| **Instagram** | Graph API | 200 req/hour, token refresh every 50-55 days | Reels, Stories, Carousels |
| **YouTube** | Data API v3 | 10K units/day (~6 uploads/day) | OAuth 2.0 required |
| **Shopee** | Seller API | Rate limits vary | Via middleware (CedCommerce) |
| **TikTok Shop** | RESTful API | Product/order/inventory | Growing fast in TH |

---

## 9. AI Product Content Tools (E-Commerce)

| Tool | Function | Price |
|------|----------|-------|
| **Creatify** | URL → product video (3 min), 700+ AI avatars | ~$59/mo Pro |
| **Photoroom** | AI product photography + background removal | ~$10-30/mo |
| **Claid.ai** | E-commerce photo enhancement | Subscription |
| **Bunu** | Shopify-native UGC-style product videos | Shopify app |
| **Opus Clip** | Long → short clips, virality scoring | $15-29/mo |

---

## Service Selection Summary

### Recommended Stack

```
Content Type        | Service              | Cost Level
────────────────────┼──────────────────────┼──────────
Script/Text         | Claude Sonnet 4      | $$
Emotion analysis    | Claude Sonnet 4      | $$
Image generation    | Flux 1.1 Pro         | $
Video generation    | Kling 3.0            | $$ (best value)
Background music    | Suno V5 Pro          | $
TTS (Thai)          | Narakeet             | $
TTS (English/other) | Fish Audio           | $
Vector DB           | ChromaDB → Qdrant    | Free → $$
Orchestration       | LangGraph + n8n      | Free (OSS)
Publishing          | Platform APIs via n8n | Free (API)
```

### Alternative: All-Google Stack

```
LLM:        Gemini 2.5 Pro (Vertex AI)
Image:      Imagen 3 (Vertex AI)
Video:      Veo 3.1 (Vertex AI)
TTS:        Google Cloud TTS Chirp 3 HD
Vector DB:  Vertex AI Vector Search
Infra:      Cloud Run + GCS + BigQuery
```

ข้อดี: single billing, integrated APIs, enterprise SLA
ข้อเสีย: แพงกว่า (โดยเฉพาะ Veo $0.75/sec vs Kling $0.029/sec)
