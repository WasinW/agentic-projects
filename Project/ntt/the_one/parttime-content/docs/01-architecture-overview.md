# 01 - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RAG Agentic Content Pipeline                      │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │ Knowledge     │    │ LangGraph    │    │ Content Generation   │   │
│  │ Base (RAG)    │───▶│ Orchestrator │───▶│ Services             │   │
│  │               │    │              │    │                      │   │
│  │ • Brand       │    │ • Script     │    │ • Text (LLM)         │   │
│  │   guidelines  │    │   Agent      │    │ • Image (Flux/SD)    │   │
│  │ • Script      │    │ • Emotion    │    │ • Video (Kling/      │   │
│  │   templates   │    │   Agent      │    │   Runway/Sora)       │   │
│  │ • Tone refs   │    │ • Visual     │    │ • Music (Suno)       │   │
│  │ • Scenarios   │    │   Agent      │    │ • TTS (ElevenLabs/   │   │
│  │ • Music moods │    │ • Audio      │    │   Fish Audio)        │   │
│  │               │    │   Agent      │    │                      │   │
│  └──────────────┘    │ • Assembly   │    └──────────────────────┘   │
│                       │   Agent      │                               │
│                       └──────┬───────┘                               │
│                              │                                       │
│                       ┌──────▼───────┐    ┌──────────────────────┐   │
│                       │ Post-Process │    │ Publishing           │   │
│                       │              │───▶│                      │   │
│                       │ • FFmpeg     │    │ • TikTok API         │   │
│                       │ • Remotion   │    │ • Instagram API      │   │
│                       │ • Opus Clip  │    │ • YouTube API        │   │
│                       │   (repurpose)│    │ • Shopee/Lazada      │   │
│                       └──────────────┘    └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Pipeline Flow

```
User Input (topic/product URL/creative brief)
    │
    ▼
[1. RAG Retrieval] ──── Vector DB query for relevant context
    │                    (brand voice, templates, tone references)
    │
    ▼
[2. Script Agent] ───── Generate speaking script + scene descriptions
    │                    LLM: Claude Sonnet 4 / GPT-5.2
    │
    ▼
[3. Emotion Agent] ──── Analyze script segments → emotional prompts
    │                    Tag each segment: excitement, trust, urgency, etc.
    │
    ▼
[4. Visual Agent] ───── Generate image/video prompts per scene
    │                    Include camera angles, lighting, mood
    │
    ├────────────────── Parallel Generation ──────────────────┐
    │                                                          │
    ▼                                                          ▼
[5a. Video Gen] ─── Kling/Runway/Sora        [5b. Audio Gen] ─── Suno/MusicGen
    │               per scene clip                │                 background music
    │                                              │
    │               [5c. TTS/Voice] ───────────────┘
    │               ElevenLabs/Fish Audio
    │               voiceover from script
    │
    ▼
[6. Assembly Agent] ── Combine video + audio + voiceover + captions
    │                   FFmpeg/Remotion/Shotstack
    │
    ▼
[7. Quality Check] ── Human-in-the-loop review (optional)
    │
    ▼
[8. Repurpose] ────── Opus Clip: long → short-form clips
    │                  Format adaptation: 9:16, 16:9, 1:1
    │
    ▼
[9. Publish] ──────── n8n orchestration → platform APIs
                       Schedule optimal posting times
```

## Agent Design (LangGraph)

### Agent Roles

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Script Agent** | สร้างบทพูด/บท narration | topic + RAG context | structured script (scenes, dialogues, CTA) |
| **Emotion Agent** | วิเคราะห์อารมณ์แต่ละ segment | script | emotional tags + intensity per segment |
| **Visual Agent** | สร้าง prompt สำหรับ image/video | script + emotion tags | image prompts, video scene descriptions |
| **Audio Agent** | เลือก/สร้างเสียงประกอบ | script + emotion tags | music style, SFX cues, voice tone direction |
| **Assembly Agent** | รวม assets ทั้งหมด | video clips + audio + voice | final rendered content |
| **Publishing Agent** | จัดการ publish + scheduling | final content + metadata | published posts + analytics tracking |

### LangGraph State Machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ContentState(TypedDict):
    # Input
    topic: str
    content_type: str          # "ecommerce" | "creative"
    product_url: str | None
    target_platform: list[str] # ["tiktok", "ig", "youtube"]

    # RAG
    context: list[str]         # retrieved documents
    brand_voice: dict          # tone, style guidelines

    # Generation
    script: dict               # structured script with scenes
    emotions: list[dict]       # emotion tags per segment
    visual_prompts: list[str]  # image/video generation prompts
    audio_plan: dict           # music style, SFX, voice direction

    # Assets
    video_clips: list[str]     # paths to generated clips
    audio_tracks: list[str]    # background music files
    voiceover: str             # TTS audio file

    # Output
    final_video: str           # assembled video path
    short_clips: list[str]     # repurposed short-form clips
    publish_status: dict       # per-platform status

workflow = StateGraph(ContentState)

# Add nodes
workflow.add_node("retrieve_context", rag_retrieval)
workflow.add_node("generate_script", script_agent)
workflow.add_node("analyze_emotions", emotion_agent)
workflow.add_node("create_visual_prompts", visual_agent)
workflow.add_node("plan_audio", audio_agent)
workflow.add_node("generate_video", video_generation)
workflow.add_node("generate_audio", audio_generation)
workflow.add_node("generate_voiceover", tts_generation)
workflow.add_node("assemble", assembly_agent)
workflow.add_node("review", human_review)      # optional
workflow.add_node("repurpose", repurpose_clips)
workflow.add_node("publish", publishing_agent)

# Define flow
workflow.set_entry_point("retrieve_context")
workflow.add_edge("retrieve_context", "generate_script")
workflow.add_edge("generate_script", "analyze_emotions")
workflow.add_edge("analyze_emotions", "create_visual_prompts")
workflow.add_edge("analyze_emotions", "plan_audio")

# Parallel generation after prompts are ready
workflow.add_edge("create_visual_prompts", "generate_video")
workflow.add_edge("plan_audio", "generate_audio")
workflow.add_edge("plan_audio", "generate_voiceover")

# Assembly waits for all generation
workflow.add_edge("generate_video", "assemble")
workflow.add_edge("generate_audio", "assemble")
workflow.add_edge("generate_voiceover", "assemble")

# Post-assembly
workflow.add_conditional_edges("assemble", needs_review, {
    "review": "review",
    "skip": "repurpose",
})
workflow.add_edge("review", "repurpose")
workflow.add_edge("repurpose", "publish")
workflow.add_edge("publish", END)

pipeline = workflow.compile()
```

## Content Types

### 1. E-Commerce Content (ขายของออนไลน์)

```
Product URL / Product Info
    │
    ▼
Script Types:
  • Product review (ข้อดี ข้อเสีย การใช้งาน)
  • Unboxing (เปิดกล่อง first impression)
  • Tutorial/How-to (สอนใช้งาน)
  • Comparison (เปรียบเทียบกับคู่แข่ง)
  • Social proof (รีวิวจากลูกค้า)
  • Flash sale / Promotion (ด่วน! ลดราคา)
```

### 2. Creative / Artist Content

```
Creative Brief / Concept
    │
    ▼
Content Types:
  • Music video (AI-generated visuals synced to music)
  • Short film / Story (narrative with scenes)
  • Art showcase (AI art + narration)
  • Behind-the-scenes (creative process)
  • Educational (สอนเทคนิค art/music)
  • Mood / Aesthetic (ambient content)
```

## Knowledge Base Structure (RAG)

```
knowledge_base/
├── brand/
│   ├── voice_guidelines.md      # tone, style, vocabulary
│   ├── visual_identity.md       # colors, fonts, image style
│   └── target_audience.md       # demographics, preferences
│
├── scripts/
│   ├── ecommerce/
│   │   ├── product_review.md    # template + examples
│   │   ├── unboxing.md
│   │   ├── tutorial.md
│   │   └── promotion.md
│   └── creative/
│       ├── music_video.md
│       ├── short_film.md
│       └── art_showcase.md
│
├── emotions/
│   ├── tone_mapping.md          # emotion → visual/audio cues
│   ├── hook_patterns.md         # attention-grabbing openers
│   └── cta_patterns.md          # effective call-to-actions
│
├── trends/
│   ├── tiktok_trends.md         # current trending formats
│   ├── music_moods.md           # popular music styles
│   └── visual_styles.md         # trending visual aesthetics
│
└── products/                    # product-specific knowledge
    ├── product_catalog.json     # ข้อมูลสินค้า
    └── reviews_summary.md       # สรุปรีวิว
```
