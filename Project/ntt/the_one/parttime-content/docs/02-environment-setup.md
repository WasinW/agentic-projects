# 02 - Environment Setup

## Local Development

### Prerequisites

| Component | Recommended | Minimum |
|-----------|-------------|---------|
| Python | 3.12 | 3.11 |
| Package Manager | **uv** | pip + venv |
| GPU (optional) | RTX 4090 (24GB) / Mac M3 Pro 36GB | RTX 4060 Ti 8GB / Mac M2 16GB |
| RAM | 32 GB | 16 GB |
| Storage | 100 GB SSD (for models) | 50 GB |
| Docker | Docker Desktop / Colima | — |

### Step 1: Python + uv

```bash
# Install uv (replaces pip, pip-tools, virtualenv)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
mkdir rag-content-pipeline && cd rag-content-pipeline
uv init
```

### Step 2: pyproject.toml

```toml
[project]
name = "rag-content-pipeline"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = [
    # Orchestration
    "langchain>=0.3",
    "langgraph>=0.2",
    "llama-index>=0.11",

    # Vector DB
    "chromadb>=0.5",
    "qdrant-client>=1.12",

    # Embeddings
    "sentence-transformers>=3.0",

    # API framework
    "fastapi>=0.115",
    "uvicorn>=0.32",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",

    # Task queue
    "celery>=5.4",
    "redis>=5.0",

    # AI service clients
    "anthropic>=0.40",          # Claude
    "openai>=1.55",             # OpenAI / Sora
    "google-cloud-aiplatform",  # Vertex AI (Veo, Imagen)
    "httpx>=0.27",              # Generic API calls

    # Media processing
    "ffmpeg-python>=0.2",
    "Pillow>=10.0",

    # Storage
    "boto3>=1.35",              # S3-compatible (MinIO)
    "google-cloud-storage",
]

[project.optional-dependencies]
local-llm = [
    "ollama>=0.3",
]
gpu = [
    "torch>=2.4",
    "vllm>=0.6",
]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
    "mypy>=1.13",
    "jupyter>=1.1",
    "ipywidgets>=8.0",
]
```

```bash
# Install all dependencies
uv sync --all-extras
```

### Step 3: Docker Compose (Local Services)

```yaml
# docker-compose.yml
version: "3.9"

services:
  # Vector Database
  qdrant:
    image: qdrant/qdrant:v1.12.1
    ports:
      - "6333:6333"   # REST
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_data:/qdrant/storage

  # Cache + Task Queue
  redis:
    image: redis:7.4-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Metadata Storage
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: rag_pipeline
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: devpassword
    volumes:
      - pg_data:/var/lib/postgresql/data

  # S3-compatible Object Storage
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"   # API
      - "9001:9001"   # Console
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  # Local LLM Server
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # GPU support (NVIDIA)
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      N8N_BASIC_AUTH_ACTIVE: "true"
      N8N_BASIC_AUTH_USER: admin
      N8N_BASIC_AUTH_PASSWORD: admin
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  qdrant_data:
  redis_data:
  pg_data:
  minio_data:
  ollama_data:
  n8n_data:
```

```bash
# Start all services
docker compose up -d

# Pull LLM models
ollama pull llama3.1:8b        # General purpose
ollama pull nomic-embed-text   # Embeddings
ollama pull qwen2.5:14b        # Stronger reasoning (needs 10GB+ VRAM)
```

### Step 4: Local Image Generation (Optional)

สำหรับ generate ภาพ locally ด้วย ComfyUI:

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Setup with uv
uv venv && uv pip install -r requirements.txt

# Download models (place in models/checkpoints/)
# - Stable Diffusion XL: ~6.5 GB
# - Flux.1 Schnell: ~12 GB

# Run with API
python main.py --listen 0.0.0.0 --port 8188
```

**VRAM ที่ต้องการ:**

| Model | Min VRAM | Recommended |
|-------|----------|-------------|
| SD 1.5 | 4 GB | 6 GB |
| SDXL | 6 GB | 8-10 GB |
| Flux.1 Schnell | 8 GB | 12 GB |
| Flux.1 Dev | 10 GB | 16 GB+ |

### Step 5: Environment Variables

```bash
# .env.example
# === LLM APIs ===
ANTHROPIC_API_KEY=sk-ant-...          # Claude
OPENAI_API_KEY=sk-...                 # GPT / Sora / DALL-E
GOOGLE_CLOUD_PROJECT=your-project-id  # Vertex AI

# === Content Generation ===
ELEVENLABS_API_KEY=...                # TTS
RUNWAY_API_KEY=...                    # Video generation
KLING_API_KEY=...                     # Video generation (alt)
SUNO_API_KEY=...                      # Music generation

# === Infrastructure ===
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://dev:devpassword@localhost:5432/rag_pipeline
MINIO_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
OLLAMA_URL=http://localhost:11434

# === Publishing ===
TIKTOK_ACCESS_TOKEN=...
INSTAGRAM_ACCESS_TOKEN=...
YOUTUBE_REFRESH_TOKEN=...
```

---

## Project Structure

```
rag-content-pipeline/
├── pyproject.toml
├── uv.lock
├── docker-compose.yml
├── Dockerfile
├── .env.example
│
├── src/
│   ├── core/                   # Shared
│   │   ├── config.py           # Pydantic Settings
│   │   ├── models.py           # Domain models
│   │   └── prompts/            # Versioned prompt templates
│   │       ├── ecommerce/
│   │       └── creative/
│   │
│   ├── rag/                    # RAG Layer
│   │   ├── ingestion.py        # Document loading + chunking
│   │   ├── embedder.py         # Embedding model wrapper
│   │   ├── vector_store.py     # Qdrant/ChromaDB abstraction
│   │   └── retriever.py        # Retrieval + reranking
│   │
│   ├── agents/                 # Agentic Layer (LangGraph)
│   │   ├── orchestrator.py     # Main LangGraph workflow
│   │   ├── script_agent.py     # Script generation
│   │   ├── emotion_agent.py    # Emotion analysis
│   │   ├── visual_agent.py     # Visual prompt generation
│   │   ├── audio_agent.py      # Audio planning
│   │   └── assembly_agent.py   # Content assembly
│   │
│   ├── generation/             # Content Generation Services
│   │   ├── llm_client.py       # LLM abstraction (Claude/GPT/Ollama)
│   │   ├── image_gen.py        # Image generation (Flux/DALL-E/SD)
│   │   ├── video_gen.py        # Video generation (Kling/Runway/Sora)
│   │   ├── music_gen.py        # Music generation (Suno/MusicGen)
│   │   └── tts.py              # TTS (ElevenLabs/Fish Audio)
│   │
│   ├── processing/             # Media Processing
│   │   ├── video_editor.py     # FFmpeg wrapper
│   │   ├── repurposer.py       # Long → short-form
│   │   └── format_adapter.py   # Platform-specific formats
│   │
│   ├── publishing/             # Publishing Layer
│   │   ├── tiktok.py           # TikTok Content Posting API
│   │   ├── instagram.py        # Instagram Graph API
│   │   ├── youtube.py          # YouTube Data API v3
│   │   └── scheduler.py        # Posting schedule optimizer
│   │
│   ├── api/                    # FastAPI Application
│   │   ├── app.py
│   │   ├── routes/
│   │   └── deps.py
│   │
│   └── workers/                # Background Tasks
│       ├── celery_app.py
│       └── tasks/
│
├── knowledge_base/             # RAG Documents
│   ├── brand/
│   ├── scripts/
│   ├── emotions/
│   └── trends/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── eval/                   # RAG quality evaluation
│
└── infra/
    ├── terraform/              # Cloud infrastructure
    └── docker/
```

---

## Cloud Deployment

### Option A: GCP (Recommended)

```
                    ┌─────────────────────────────┐
                    │      Cloud Run (API)         │
                    │   FastAPI + LangGraph        │
                    └──────────┬──────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                   │
            ▼                  ▼                   ▼
   ┌────────────────┐  ┌──────────────┐  ┌────────────────┐
   │ Vertex AI      │  │ Cloud Run    │  │ Qdrant on GKE  │
   │                │  │ Jobs         │  │ (Vector DB)     │
   │ • Gemini (LLM) │  │ (async gen)  │  └────────────────┘
   │ • Veo (Video)  │  │              │
   │ • Imagen (Img) │  └──────┬───────┘
   └────────────────┘         │
                               ▼
                    ┌─────────────────────┐
                    │ GCS (content store)  │
                    │ BigQuery (analytics) │
                    │ Cloud SQL (metadata) │
                    │ Memorystore (Redis)  │
                    └─────────────────────┘
```

**GCP Services Used:**

| Service | Purpose | Pricing Model |
|---------|---------|---------------|
| **Cloud Run** | API + async processing | Per-request, scales to zero |
| **Vertex AI** | LLM, Video, Image gen | Per-token / per-second |
| **GKE Autopilot** | Qdrant, persistent services | Per-pod resources |
| **Cloud Storage** | Generated content | Per-GB stored + egress |
| **Cloud SQL** | Metadata, user data | Per-instance-hour |
| **Memorystore** | Redis cache + queue | Per-GB-hour |
| **Pub/Sub** | Event-driven processing | Per-message |
| **BigQuery** | Analytics | Per-TB scanned |

### Option B: AWS

| GCP | AWS Equivalent |
|-----|---------------|
| Cloud Run | Lambda + API Gateway / ECS Fargate |
| Vertex AI | Amazon Bedrock |
| GKE | EKS |
| Cloud Storage | S3 |
| Cloud SQL | RDS |
| Memorystore | ElastiCache |
| Pub/Sub | SQS / EventBridge |
| BigQuery | Athena / Redshift |

### Option C: Hybrid (Recommended for Starting)

```
Local Development:
  • Ollama (LLM) + ChromaDB (vector) + Docker services
  • ComfyUI (image gen, optional)

Cloud APIs (pay-per-use):
  • Claude / GPT (script generation)
  • Kling / Runway (video generation)
  • ElevenLabs / Fish Audio (TTS)
  • Suno (music)

Cloud Infrastructure (when scaling):
  • Cloud Run (API hosting)
  • GCS (content storage)
  • n8n Cloud or self-hosted (automation)
```

นี่คือ approach ที่แนะนำ — เริ่มจาก local + cloud APIs ก่อน แล้วค่อยย้าย infra ขึ้น cloud เมื่อ scale

---

## GPU Requirements (Local LLM)

| Model Size | Quantization | VRAM | Example Models | Use Case |
|-----------|-------------|------|----------------|----------|
| 1-3B | Q4_K_M | 2-4 GB | Phi-3 Mini, Gemma 2B | Simple tasks, classification |
| 7-8B | Q4_K_M | 5-6 GB | Llama 3.1 8B, Mistral 7B | General RAG, content gen |
| 7-8B | FP16 | 14-16 GB | Same | Higher quality output |
| 13-14B | Q4_K_M | 8-10 GB | Qwen2.5-14B | Better reasoning |
| 30-34B | Q4_K_M | 20-24 GB | Qwen2.5-32B, DeepSeek-R1-32B | Near GPT-4 quality |
| 70B | Q4_K_M | 40-48 GB | Llama 3.1 70B | Maximum local quality |

**Apple Silicon Note:** Unified memory = ใช้ RAM ทั้งหมดได้ เช่น M3 Max 96GB load 70B Q4 ได้ แต่ inference ช้ากว่า NVIDIA GPU

---

## Dev Tools

| Tool | Purpose |
|------|---------|
| **uv** | Package management (10-100x faster than pip) |
| **Ruff** | Linting + formatting (replaces black+isort+flake8) |
| **mypy** | Type checking |
| **pytest** | Testing |
| **Jupyter Lab** | Experimentation, prompt engineering |
| **Langfuse** (OSS) | LLM observability, tracing |
| **Ragas** | RAG evaluation framework |
| **promptfoo** | Prompt testing and evaluation |
