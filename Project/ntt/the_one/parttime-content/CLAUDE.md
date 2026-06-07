# RAG Agentic AI — Content Clip Generator

## Project Overview
ระบบ AI สำหรับสร้าง content clips อัตโนมัติ (scripts, emotional prompts, situations, sound, video/music/article)

### Use Cases
1. **E-Commerce Content** — เปิดช่อง TikTok/IG/YouTube ขายของออนไลน์
2. **Creative / Artist** — สร้างผลงานศิลปะ, music video, storytelling content

## Documentation (อ่านก่อนทำงาน)
- `docs/01-architecture-overview.md` — System architecture, LangGraph agent design, pipeline flow
- `docs/02-environment-setup.md` — Local dev + Cloud deployment + project structure
- `docs/03-ai-services-and-tools.md` — ทุก AI service/API พร้อม pricing
- `docs/04-content-pipeline.md` — Pipeline implementation (n8n + FastAPI + Celery)
- `docs/05-thai-market-strategy.md` — Thai TTS, platform ranking, TikTok Shop strategy
- `docs/06-cost-estimation.md` — Per-clip cost, monthly estimates

## Tech Stack
```
Orchestration:  LangGraph (state machine) + LlamaIndex (RAG)
LLM:            Claude Sonnet 4 / GPT-5.2 / Gemini 2.0 Flash
Image:          Flux 1.1 Pro / DALL-E 3 / Stable Diffusion
Video:          Kling 3.0 / Runway Gen-4.5 / Sora 2
Music:          Suno V5 / MusicGen (self-hosted)
TTS:            ElevenLabs / Fish Audio / Narakeet (Thai — 93 voices)
Vector DB:      ChromaDB (dev) → Qdrant (prod)
Automation:     n8n (self-hosted)
Cloud:          GCP (Vertex AI + Cloud Run + GCS)
```

## Architecture
```
RAG Knowledge Base → LangGraph Orchestrator → Content Generation Services
                          │
                    ┌─────┼─────┐
                    │     │     │
              Script  Emotion  Visual/Audio
              Agent   Agent    Agents
                    │     │     │
                    └─────┼─────┘
                          │
                    Assembly → Post-Process → Publish (TikTok/IG/YouTube)
```

## Pipeline Flow
```
Input (topic/product URL) → RAG Retrieval → Script Gen → Emotion Mapping
→ Visual+Audio Prompts → [Parallel] Video + Music + TTS → Assembly → Publish
```

## Cost Per 60-sec Clip
- Budget (Kling + Fish Audio): ~$2.20 (~76 บาท)
- Standard (Runway + ElevenLabs): ~$5.00 (~173 บาท)
- Ultra-Budget (self-hosted + Kling): ~$1.74 (~60 บาท)

## Project Rules
- ใช้ภาษาไทยในการสื่อสาร (code เป็น English)
- ใช้ uv เป็น package manager
- ใช้ ruff + mypy สำหรับ linting/type checking
- ใช้ pytest สำหรับ testing
- No git commands (no branch, add, commit, push) — ผมจัดการเอง

## Local Dev Requirements
- Python 3.12, uv, Docker Desktop, FFmpeg (ต้องมี)
- Ollama (แนะนำ — local LLM)
- ComfyUI (optional — ต้อง GPU 8GB+)

## Thai Market Focus
- TikTok + TikTok Shop = priority #1 (แซง Lazada แล้ว)
- Thai TTS: Narakeet (93 voices) เป็นตัวเลือกหลัก
- UGC-style content ทำงานดีกว่า polished ads
- Hook ใน 3 วินาทีแรกสำคัญมาก
