# 06 - Cost Estimation

## Per-Clip Cost (60-second Video)

### Budget Option (Kling + Fish Audio)

| Component | Service | Est. Cost |
|-----------|---------|-----------|
| Script generation | Claude Sonnet 4 (~2K tokens) | $0.03 |
| RAG retrieval | Qdrant (self-hosted) | ~$0 |
| Emotion analysis | Claude Sonnet 4 (~1K tokens) | $0.02 |
| Visual prompts | Claude Sonnet 4 (~1K tokens) | $0.02 |
| Image gen (5 frames) | Flux 1.1 Pro (via fal.ai) | $0.20 |
| **Video gen (60s)** | **Kling 3.0** | **$1.74** |
| Background music | Suno Pro (amortized) | $0.05 |
| Voiceover (60s) | Fish Audio | $0.10 |
| Thumbnail | Flux 1.1 Pro | $0.04 |
| **Total per clip** | | **~$2.20** |

### Standard Option (Runway + ElevenLabs)

| Component | Service | Est. Cost |
|-----------|---------|-----------|
| Script generation | Claude Sonnet 4 | $0.03 |
| RAG retrieval | Qdrant (self-hosted) | ~$0 |
| Emotion analysis | Claude Sonnet 4 | $0.02 |
| Visual prompts | Claude Sonnet 4 | $0.02 |
| Image gen (5 frames) | Flux 1.1 Pro | $0.20 |
| **Video gen (60s)** | **Runway Gen-4.5** | **$3.00-9.00** |
| Background music | Suno Pro | $0.05 |
| **Voiceover (60s)** | **ElevenLabs** | **$0.30** |
| Thumbnail | DALL-E 3 | $0.08 |
| **Total per clip** | | **~$3.70-9.70** |

### Premium Option (Veo + ElevenLabs)

| Component | Service | Est. Cost |
|-----------|---------|-----------|
| Script generation | Claude Opus 4 | $0.15 |
| RAG retrieval | Vertex AI Vector Search | $0.01 |
| Emotion analysis | Claude Opus 4 | $0.10 |
| Visual prompts | Claude Opus 4 | $0.10 |
| Image gen (5 frames) | Imagen 3 (Vertex AI) | $0.30 |
| **Video gen (60s)** | **Google Veo 3.1** | **$45.00** |
| Background music | Suno Premier | $0.03 |
| Voiceover (60s) | ElevenLabs Scale | $0.30 |
| Thumbnail | Imagen 3 | $0.06 |
| **Total per clip** | | **~$46.05** |

### Ultra-Budget (Self-Hosted + Free Tiers)

| Component | Service | Est. Cost |
|-----------|---------|-----------|
| Script generation | Ollama (Llama 3.1 8B) | $0 (electricity) |
| RAG retrieval | ChromaDB (local) | $0 |
| Emotion analysis | Ollama | $0 |
| Visual prompts | Ollama | $0 |
| Image gen | ComfyUI + SDXL (local) | $0 (electricity) |
| **Video gen (60s)** | **Kling 3.0** | **$1.74** |
| Background music | MusicGen (local) | $0 |
| Voiceover | Bark (local) | $0 |
| **Total per clip** | | **~$1.74** |

**Note:** Ultra-budget ต้องมี GPU (min 8GB VRAM) สำหรับ local inference

---

## Monthly Cost Estimates

### Solo Creator (30 clips/month)

| Tier | Cost/Clip | Monthly | Quality |
|------|-----------|---------|---------|
| Ultra-Budget | $1.74 | **$52** | Basic (local LLM quality) |
| Budget | $2.20 | **$66** | Good (cloud LLM + Kling) |
| Standard | $5.00 | **$150** | Very Good (Runway + ElevenLabs) |
| Premium | $46.00 | **$1,380** | Enterprise (Veo 3.1) |

### Active Creator (100 clips/month)

| Tier | Cost/Clip | Monthly | Quality |
|------|-----------|---------|---------|
| Ultra-Budget | $1.74 | **$174** | Basic |
| Budget | $2.20 | **$220** | Good |
| Standard | $5.00 | **$500** | Very Good |
| Premium | $46.00 | **$4,600** | Enterprise |

### Agency / Team (500 clips/month)

| Tier | Cost/Clip | Monthly | Quality |
|------|-----------|---------|---------|
| Budget | $2.20 | **$1,100** | Good |
| Standard | $5.00 | **$2,500** | Very Good |

---

## Infrastructure Monthly Costs

### Local-First (Recommended Start)

| Service | Cost |
|---------|------|
| Docker services (Qdrant, Redis, etc.) | $0 (local) |
| Ollama (local LLM) | $0 (electricity ~$5-10) |
| n8n (self-hosted) | $0 |
| Cloud API subscriptions | (see per-clip costs) |
| MinIO (local S3) | $0 |
| **Total infra** | **~$5-10/mo** |

### Cloud Deployment (Scaling)

| Service | GCP Pricing | Monthly Est. |
|---------|------------|-------------|
| Cloud Run (API) | $0.00002400/vCPU-sec | ~$20-50 |
| Qdrant on GKE | e2-standard-2 | ~$50-70 |
| Cloud SQL (PostgreSQL) | db-f1-micro | ~$10 |
| Memorystore (Redis) | 1 GB Basic | ~$35 |
| Cloud Storage (50 GB) | $0.020/GB | ~$1 |
| BigQuery (analytics) | $5/TB scanned | ~$5-10 |
| **Total cloud infra** | | **~$120-175/mo** |

### SaaS Tools

| Tool | Monthly | Required? |
|------|---------|-----------|
| Opus Clip (repurposing) | $15-29 | Nice to have |
| Creatify (e-commerce video) | $59 | For e-commerce focus |
| Photoroom (product photos) | $10-30 | For e-commerce focus |
| n8n Cloud (if not self-hosting) | $20-50 | Alternative to self-host |
| **Total SaaS** | **$0-168/mo** | Depends on needs |

---

## Cost Comparison: AI vs Traditional

### Traditional Content Production (per 60-sec video)

| Item | Cost |
|------|------|
| Scriptwriter | $50-200 |
| Videographer | $100-500 |
| Video editor | $50-200 |
| Voiceover artist | $30-100 |
| Music license | $10-50 |
| **Total** | **$240-1,050** |

### AI Pipeline (per 60-sec video)

| Tier | Cost | vs Traditional |
|------|------|---------------|
| Ultra-Budget | $1.74 | **99% cheaper** |
| Budget | $2.20 | **99% cheaper** |
| Standard | $5.00 | **98% cheaper** |
| Premium | $46.00 | **81-96% cheaper** |

### Volume Advantage

```
Traditional: 1 video/day = $7,200-31,500/month
AI Budget:   3 videos/day = $198/month (90 clips)
AI Standard: 3 videos/day = $450/month (90 clips)

→ AI ถูกกว่า 15-160x แถม produce ได้มากกว่า 3x
```

---

## API Pricing Quick Reference

### LLM

| API | Input/1M | Output/1M |
|-----|----------|-----------|
| Claude Sonnet 4 | $3.00 | $15.00 |
| GPT-5.2 | $1.75 | $14.00 |
| Gemini 2.0 Flash | $0.08 | $0.30 |

### Video

| API | Cost/sec |
|-----|----------|
| Kling 3.0 | $0.029 |
| Runway Gen-4.5 | $0.05-0.15 |
| Sora 2 Standard | Free (limited) |
| Sora 2 Pro | $0.10-0.50 |
| Veo 3.1 | $0.75 |

### Image

| API | Cost/image |
|-----|-----------|
| Flux 1.1 Pro | $0.03-0.05 |
| DALL-E 3 HD | $0.08 |
| SD 3.5 | $0.035 |
| SDXL | $0.002-0.006 |

### TTS

| API | Cost Model |
|-----|-----------|
| ElevenLabs Starter | $5/mo |
| Fish Audio | ~$0.10/min |
| Narakeet | Pay per minute |
| OpenAI TTS | $0.015/min |

### Music

| API | Cost Model |
|-----|-----------|
| Suno Pro | $10/mo (2,500 credits) |
| Suno Premier | $30/mo (10,000 credits) |
| MusicGen | Free (self-hosted) |

---

## Optimization Tips

### 1. LLM Cost Optimization

```
• ใช้ prompt caching (Claude/GPT) — save 50-90% on repeated system prompts
• Batch similar requests — Gemini 2.0 Flash for bulk processing
• Cache semantic-similar queries — avoid re-generating similar content
• Use smaller models for simple tasks (emotion tagging → GPT-5 Nano)
```

### 2. Video Cost Optimization

```
• ใช้ image-to-video แทน text-to-video เมื่อเป็นไปได้ (ถูกกว่า)
• Generate 5-10 sec clips แล้ว stitch ด้วย FFmpeg (ไม่ต้อง gen ยาว)
• Cache identical scenes — product B-roll reuse across clips
• ใช้ Kling (cheapest) สำหรับ standard quality
• Reserve Runway/Veo สำหรับ hero content เท่านั้น
```

### 3. TTS Cost Optimization

```
• ใช้ Fish Audio แทน ElevenLabs สำหรับ volume work (1/12 ราคา)
• Self-host Bark สำหรับ experimental/draft content
• Cache common phrases (greetings, CTAs, transitions)
• Batch TTS requests — generate all voiceovers in one session
```

### 4. Infrastructure Optimization

```
• Start local → cloud เมื่อ scale
• Use spot/preemptible instances for batch work (60-90% cheaper)
• Scale-to-zero for APIs (Cloud Run)
• Compress generated content before storage (FFmpeg -crf)
• Clean up old generated assets (retention policy)
```

---

## Break-Even Analysis

### When does AI content pipeline pay for itself?

```
Assumption: Hiring a content team costs ~$2,000-5,000/month

AI Pipeline (Budget tier, 90 clips/month):
  Per-clip costs: $198/month
  Infrastructure:  $10/month
  Total:          $208/month

Savings: $1,792-4,792/month

Break-even: Immediately (month 1)
ROI: 9-24x return on investment

If including initial setup time (~40 hours × your hourly rate):
  Setup cost: ~$2,000-4,000 (one-time)
  Break-even: Month 2-3
```
