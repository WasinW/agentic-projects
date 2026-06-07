# 04 - Content Pipeline Design

## End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Content Generation Pipeline                   │
│                                                                  │
│  INPUT                                                           │
│  ├── Product URL (e-commerce)                                    │
│  ├── Creative Brief (artist)                                     │
│  ├── Topic / Keyword                                             │
│  └── Target Platform(s)                                          │
│                                                                  │
│  STAGE 1: Research & Context                                     │
│  ├── RAG retrieval (brand voice, templates, trends)              │
│  ├── Product info extraction (if URL provided)                   │
│  └── Trend analysis (hashtags, formats, sounds)                  │
│                                                                  │
│  STAGE 2: Script & Planning                                      │
│  ├── Script generation (speaking script, scene descriptions)     │
│  ├── Emotion mapping (per segment: excitement, trust, urgency)   │
│  ├── Visual prompt generation (image/video per scene)            │
│  └── Audio planning (music style, SFX, voice direction)          │
│                                                                  │
│  STAGE 3: Asset Generation (parallel)                            │
│  ├── Video clips (Kling/Runway per scene)                        │
│  ├── Background music (Suno/MusicGen)                            │
│  ├── Voiceover (ElevenLabs/Fish Audio/Narakeet)                  │
│  └── Images/thumbnails (Flux/DALL-E)                             │
│                                                                  │
│  STAGE 4: Assembly                                               │
│  ├── Video composition (FFmpeg/Remotion)                         │
│  ├── Audio mixing (voice + music + SFX)                          │
│  ├── Caption/subtitle generation                                 │
│  └── Thumbnail creation                                          │
│                                                                  │
│  STAGE 5: Post-Processing                                        │
│  ├── Format adaptation (9:16, 16:9, 1:1)                        │
│  ├── Repurposing (long → short clips via Opus Clip)              │
│  └── Quality check (human-in-the-loop optional)                  │
│                                                                  │
│  STAGE 6: Publishing                                             │
│  ├── Schedule optimization (best posting times)                  │
│  ├── Multi-platform publish (TikTok, IG, YouTube)                │
│  ├── Metadata (title, description, hashtags, tags)               │
│  └── Analytics tracking                                          │
│                                                                  │
│  OUTPUT                                                          │
│  ├── Published posts across platforms                            │
│  ├── Analytics dashboard                                         │
│  └── Feedback loop → improve next content                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Implementation

### n8n Workflow (Automation Layer)

n8n ทำหน้าที่เป็น **automation backbone** เชื่อม services ต่างๆ:

```
Trigger (Schedule / Webhook / Manual)
    │
    ▼
[n8n Workflow]
    ├── HTTP Request → Product URL scraping
    ├── LangChain Node → RAG retrieval + Script generation
    ├── HTTP Request → Kling API (video)
    ├── HTTP Request → ElevenLabs API (TTS)
    ├── HTTP Request → Suno (music)
    ├── Code Node → FFmpeg assembly
    ├── HTTP Request → TikTok Content Posting API
    ├── HTTP Request → Instagram Graph API
    └── HTTP Request → YouTube Data API v3
```

**n8n templates ที่เกี่ยวข้อง:**
- Template #4630: Generate videos with AI + ElevenLabs + Shotstack → YouTube
- Template #3066: Multi-Platform Social Media Content Creation with AI
- Template #3135: Automated social media content publishing factory
- Template #4498: Schedule all Instagram content types via Graph API

### FastAPI Backend (Custom Logic)

```python
# src/api/routes/content.py
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/content")

class ContentRequest(BaseModel):
    topic: str
    content_type: str              # "ecommerce" | "creative"
    product_url: str | None = None
    target_platforms: list[str]    # ["tiktok", "ig", "youtube"]
    style: str = "default"        # brand voice preset
    language: str = "th"          # th | en
    duration: int = 60            # target seconds

class ContentResponse(BaseModel):
    job_id: str
    status: str
    estimated_time_seconds: int

@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks,
):
    """Queue content generation job."""
    job_id = create_job(request)
    background_tasks.add_task(run_pipeline, job_id, request)
    return ContentResponse(
        job_id=job_id,
        status="queued",
        estimated_time_seconds=estimate_time(request),
    )

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Check generation status."""
    return get_job_status(job_id)

@router.get("/download/{job_id}")
async def download_content(job_id: str):
    """Download generated content."""
    return get_job_artifacts(job_id)
```

### Celery Task (Background Processing)

```python
# src/workers/tasks/content_tasks.py
from celery import Celery, chain, group

app = Celery("content_pipeline", broker="redis://localhost:6379/0")

@app.task
def stage1_research(job_id: str, params: dict) -> dict:
    """RAG retrieval + product info extraction."""
    context = rag_retriever.search(params["topic"], top_k=10)
    product_info = extract_product_info(params.get("product_url"))
    return {"context": context, "product_info": product_info}

@app.task
def stage2_planning(job_id: str, research: dict) -> dict:
    """Script + emotion + visual + audio planning."""
    script = script_agent.generate(research)
    emotions = emotion_agent.analyze(script)
    visual_prompts = visual_agent.create_prompts(script, emotions)
    audio_plan = audio_agent.plan(script, emotions)
    return {
        "script": script,
        "emotions": emotions,
        "visual_prompts": visual_prompts,
        "audio_plan": audio_plan,
    }

@app.task
def generate_video_clips(job_id: str, visual_prompts: list) -> list:
    """Generate video clips (parallel per scene)."""
    return [video_gen.generate(prompt) for prompt in visual_prompts]

@app.task
def generate_music(job_id: str, audio_plan: dict) -> str:
    """Generate background music."""
    return music_gen.generate(audio_plan["style"], audio_plan["duration"])

@app.task
def generate_voiceover(job_id: str, script: dict, language: str) -> str:
    """Generate TTS voiceover."""
    return tts.generate(script["narration"], language=language)

@app.task
def stage4_assembly(job_id: str, video: list, music: str, voice: str) -> str:
    """Assemble final video."""
    return video_editor.compose(video, music, voice)

# Full pipeline using Celery chord
def run_pipeline(job_id: str, params: dict):
    pipeline = chain(
        stage1_research.s(job_id, params),
        stage2_planning.s(job_id),
        # Parallel generation
        group(
            generate_video_clips.s(job_id),
            generate_music.s(job_id),
            generate_voiceover.s(job_id, params["language"]),
        ),
        stage4_assembly.s(job_id),
    )
    pipeline.apply_async()
```

---

## E-Commerce Content Pipeline

### Product Review Video

```
Product URL
    │
    ▼
[Scrape Product Info]
    ├── Product name, price, specs
    ├── Customer reviews (top positive + negative)
    └── Product images
    │
    ▼
[Generate Script]
    Template: product_review
    Sections:
    1. Hook (3 sec) — "รู้ไหม? สินค้าตัวนี้..."
    2. Problem (5 sec) — pain point ที่สินค้าแก้
    3. Solution (10 sec) — แนะนำสินค้า + features
    4. Demo (15 sec) — สาธิตการใช้งาน
    5. Social proof (10 sec) — รีวิวจากลูกค้า
    6. CTA (5 sec) — "กดลิงก์ด้านล่าง!"
    │
    ▼
[Generate Assets — parallel]
    ├── Video: product shots + demo scenes (Kling)
    ├── Voice: Thai narration (Narakeet/ElevenLabs)
    ├── Music: upbeat background (Suno)
    └── Thumbnail: product + text overlay (Flux)
    │
    ▼
[Assemble]
    ├── 60-sec version (YouTube)
    ├── 30-sec version (TikTok, IG Reels)
    └── 15-sec version (IG Stories)
    │
    ▼
[Publish]
    ├── TikTok (9:16, trending hashtags)
    ├── IG Reels (9:16, product tags)
    └── YouTube Shorts (9:16) or long-form (16:9)
```

### Unboxing / First Impression

```
Script Template:
1. Anticipation hook — "มาดูกันว่าข้างในมีอะไร!"
2. Unboxing sequence — เปิดกล่อง แต่ละชิ้น
3. First impression — ความรู้สึกแรก
4. Key features — จุดเด่น 3 อย่าง
5. Rating + CTA — "ให้ 8/10 กดไลค์ถ้าอยากเห็นรีวิวเต็ม!"
```

---

## Creative / Artist Content Pipeline

### Music Video

```
Song / Music Piece
    │
    ▼
[Analyze Audio]
    ├── BPM, key, mood
    ├── Beat detection
    └── Lyric extraction (if vocal)
    │
    ▼
[Generate Visual Concept]
    ├── Overall aesthetic/style
    ├── Color palette
    └── Scene-by-scene visual descriptions
    │
    ▼
[Generate Video Scenes — parallel]
    ├── Scene 1: intro (Kling/Runway)
    ├── Scene 2: verse 1 ...
    ├── Scene 3: chorus ...
    └── Scene N: outro
    │
    ▼
[Sync & Assemble]
    ├── Match cuts to beats
    ├── Transitions on musical phrases
    └── Color grade for consistency
    │
    ▼
[Publish]
    ├── YouTube (full video, 16:9)
    ├── TikTok (highlight clip, 9:16)
    └── IG Reels (hook + chorus, 9:16)
```

### Art Showcase

```
Art Pieces / Portfolio
    │
    ▼
[Generate Narrative]
    ├── Artist statement
    ├── Process description
    └── Emotional context per piece
    │
    ▼
[Create Presentation]
    ├── Ken Burns effect on art pieces
    ├── Process time-lapse (if available)
    ├── Ambient music matching mood
    └── Voiceover narration
    │
    ▼
[Format for Platforms]
    ├── YouTube (3-5 min showcase, 16:9)
    ├── TikTok (30s highlight, 9:16)
    └── IG carousel (static images + caption)
```

---

## Caching Strategy

ลดค่าใช้จ่ายด้วย caching หลายชั้น:

```
Layer 1: Embedding Cache (Redis)
    → Cache vector embeddings by content hash
    → TTL: 7 days
    → Saves: embedding API calls

Layer 2: Semantic LLM Cache (Vector DB)
    → Similar queries return cached LLM responses
    → Threshold: 0.95 cosine similarity
    → Saves: LLM API calls (biggest cost saver)

Layer 3: Asset Cache (Object Storage)
    → Hash generation request → if identical, return existing
    → Critical for image/video (expensive + slow)
    → Saves: video/image generation costs

Layer 4: HTTP Cache (CDN)
    → Published content served from CDN
    → Cache-Control headers for static assets
```

---

## Publishing Strategy

### Platform-Specific Formats

| Platform | Format | Duration | Aspect | Notes |
|----------|--------|----------|--------|-------|
| TikTok | Video | 15-60s | 9:16 | Trending sounds, hashtags, hooks in 3s |
| IG Reels | Video | 15-90s | 9:16 | Product tags, CTA in caption |
| IG Stories | Video | 15s/slide | 9:16 | Swipe-up links, polls |
| YouTube Shorts | Video | <60s | 9:16 | SEO title, end screen |
| YouTube Long | Video | 3-15 min | 16:9 | Chapters, cards, end screens |
| Facebook | Video | 15-60s | 9:16 or 1:1 | Auto-caption important |

### Optimal Posting Times (Thailand)

```
TikTok:    12:00-13:00 (lunch), 19:00-22:00 (evening)
Instagram: 11:00-13:00, 19:00-21:00
YouTube:   17:00-20:00 (weekdays), 10:00-12:00 (weekends)
```

### Publishing Flow (n8n)

```
Content Ready
    │
    ▼
[Schedule Optimizer]
    ├── Check best posting time per platform
    ├── Avoid overlapping posts
    └── Queue for optimal time
    │
    ▼
[Platform Adapters — parallel]
    ├── TikTok: add hashtags + trending sound
    ├── IG: add product tags + carousel option
    └── YouTube: add SEO metadata + chapters
    │
    ▼
[Publish via APIs]
    ├── TikTok Content Posting API
    │   (Note: audit required for public posts)
    ├── Instagram Graph API
    │   (Rate: 200 req/hour)
    └── YouTube Data API v3
        (Quota: ~6 uploads/day)
    │
    ▼
[Track & Analyze]
    ├── Poll analytics APIs (24h, 48h, 7d)
    ├── Store metrics in BigQuery
    └── Feed back to content optimization
```

---

## Error Handling & Resilience

```python
# Retry strategy for AI service calls
RETRY_CONFIG = {
    "llm_generation": {
        "max_retries": 3,
        "backoff": "exponential",  # 1s, 2s, 4s
        "fallback": "alternative_model",  # Claude → GPT → Gemini
    },
    "video_generation": {
        "max_retries": 2,
        "backoff": "exponential",  # 30s, 60s
        "fallback": "alternative_service",  # Kling → Runway
        "timeout": 300,  # 5 min per clip
    },
    "tts_generation": {
        "max_retries": 3,
        "backoff": "linear",  # 5s, 10s, 15s
        "fallback": "alternative_service",  # ElevenLabs → Fish Audio
    },
    "publishing": {
        "max_retries": 3,
        "backoff": "exponential",
        "dead_letter_queue": True,  # manual retry later
    },
}
```
