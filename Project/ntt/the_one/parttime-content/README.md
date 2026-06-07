# RAG Agentic AI — Content Clip Generator

ระบบ AI สำหรับสร้าง content clips อัตโนมัติ ครอบคลุม scripts, emotional prompts, situations, sound, video/music/article

## Use Cases
1. **E-Commerce Content** — เปิดช่อง TikTok/IG/YouTube ขายของออนไลน์
2. **Creative / Artist** — สร้างผลงานศิลปะ, music video, storytelling content

## Documentation

| Doc | เนื้อหา |
|-----|---------|
| [01 - Architecture Overview](docs/01-architecture-overview.md) | System architecture, pipeline flow, agent design |
| [02 - Environment Setup](docs/02-environment-setup.md) | Local dev + Cloud deployment setup |
| [03 - AI Services & Tools](docs/03-ai-services-and-tools.md) | ทุก AI service/API ที่ใช้ พร้อม pricing |
| [04 - Content Pipeline](docs/04-content-pipeline.md) | Pipeline design, automation, publishing |
| [05 - Thai Market Strategy](docs/05-thai-market-strategy.md) | Thai TTS, trends, platform preferences |
| [06 - Cost Estimation](docs/06-cost-estimation.md) | Cost breakdown per clip + monthly estimate |

## Quick Start (Local Dev)

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create project
uv init rag-content-pipeline
cd rag-content-pipeline

# 3. Install dependencies
uv add langchain langgraph chromadb sentence-transformers fastapi pydantic

# 4. Start local services
docker compose up -d  # Qdrant, Redis, Ollama, MinIO

# 5. Pull local LLM
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

## Tech Stack Summary

```
Orchestration:  LangGraph (state machine) + LlamaIndex (RAG)
LLM:            Claude Sonnet 4 / GPT-5.2 / Gemini 2.0 Flash
Image:          Flux 1.1 Pro / DALL-E 3 / Stable Diffusion
Video:          Kling 3.0 / Runway Gen-4.5 / Sora 2
Music:          Suno V5 / MusicGen (self-hosted)
TTS:            ElevenLabs / Fish Audio / Narakeet (Thai)
Vector DB:      ChromaDB (dev) → Qdrant (prod)
Automation:     n8n (self-hosted)
Cloud:          GCP (Vertex AI + Cloud Run + GCS)
```
