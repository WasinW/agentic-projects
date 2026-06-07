# Multi-Modal AI — Deep Dive

> Vision, Audio, Video — beyond text-only LLMs
> ปี 2026: Most production LLMs are multi-modal natively

---

## 1. Multi-Modal Landscape

### Modalities

```
Text         ─┐
Image        ─┤
Audio        ─┼─→ LLM/VLM/AAM ─→ Text/Image/Audio out
Video        ─┤
Documents    ─┤  (PDF, slides)
Tables       ─┘  (CSV, charts)
```

### Frontier Models (2026)

| Model | Modalities In | Modalities Out |
|---|---|---|
| **GPT-5** | Text, Image, Audio, Video | Text, Image, Audio |
| **Claude Opus 4.7** | Text, Image, PDF, Video | Text |
| **Gemini 2.5 Pro** | Text, Image, Audio, Video, Code | Text, Image |
| **Gemini Ultra Vision** | All modalities | All |
| **Llama 4 Vision** | Text, Image | Text |
| **Qwen 3 VL** | Text, Image, Video | Text |

### Specialized Models

| Task | Model |
|---|---|
| Image generation | Stable Diffusion 3, FLUX, Imagen |
| Speech-to-text | Whisper v3, AssemblyAI |
| Text-to-speech | ElevenLabs, OpenAI TTS |
| Music | Suno V4, Udio |
| Video gen | Sora, Veo, Kling |

---

## 2. Vision Language Models (VLM)

### Architecture (typical)

```
Image
   ↓
[Vision Encoder] (e.g., CLIP/SigLIP)
   ↓
Image embedding (vectors)
   ↓
[Projection Layer]  (align to LLM space)
   ↓
[LLM] (cross-attends to image)
   ↓
Text output
```

### Use Cases

#### Image Understanding
```python
import anthropic
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }
            },
            {"type": "text", "text": "What's in this image? Describe in detail."}
        ]
    }]
)
```

#### OCR (text in images)
```
"Extract all text from this image"
"What does this receipt say?"
"Read the menu"
```

#### Visual Q&A
```
"How many cats are in this image?"
"What's the brand on the product?"
"Is this person wearing a helmet?"
```

#### Chart/Graph Analysis
```
"What's the trend in this chart?"
"Extract data from this graph as a table"
"Summarize key insights from this dashboard"
```

#### Document Understanding
```
PDFs with text + images + tables
"Summarize this contract"
"Extract invoice details"
```

---

## 3. Document AI

### Beyond Text Extraction

Modern document AI handles:
- **Layout-aware**: tables, columns, headers
- **Multi-page**: cross-references, TOC
- **Mixed media**: images embedded with text
- **Structured extraction**: forms, invoices

### Tools (2026)

#### LlamaParse (LlamaIndex)
```python
from llama_parse import LlamaParse

parser = LlamaParse(
    result_type="markdown",
    parsing_instruction="""
    This is a financial statement. 
    Pay special attention to tables.
    Extract footnotes carefully.
    """,
)
documents = parser.load_data("./financial_report.pdf")
```

#### Unstructured.io
```python
from unstructured.partition.auto import partition

elements = partition(filename="document.pdf")
# Returns list of Title, NarrativeText, Table, etc.
```

#### Docling (IBM)
```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("complex_doc.pdf")
print(result.document.export_to_markdown())
```

#### Azure Document Intelligence
```python
# Best for forms, receipts, invoices
from azure.ai.documentintelligence import DocumentIntelligenceClient

client = DocumentIntelligenceClient(...)
result = client.begin_analyze_document(
    "prebuilt-invoice",
    {"urlSource": "https://..."}
).result()
```

### Production Patterns

#### Pattern 1: Multi-stage extraction
```
1. PDF → Layout analysis (Docling/LlamaParse)
2. Tables → Structured data (Pandas)
3. Text → Embeddings (for RAG)
4. Images → VLM analysis
5. Combine into structured output
```

#### Pattern 2: VLM-only (simpler, modern)
```python
# Send PDF directly to Claude/Gemini
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {"type": "base64", "data": pdf_b64}},
            {"type": "text", "text": "Extract invoice details as JSON"}
        ]
    }]
)
# Claude/Gemini support PDF natively
```

---

## 4. Speech (Audio) AI

### Speech-to-Text (ASR)

#### OpenAI Whisper
```python
import whisper

model = whisper.load_model("large-v3")
result = model.transcribe("audio.mp3", language="th")
print(result["text"])
```

**Sizes**: tiny, base, small, medium, large (multilingual)

#### Cloud APIs
```python
# OpenAI API
audio_file = open("audio.mp3", "rb")
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="th",
    response_format="verbose_json",  # includes timestamps
    timestamp_granularities=["word"]
)

# AssemblyAI (better accuracy on long audio)
import assemblyai as aai
aai.settings.api_key = "..."
transcript = aai.Transcriber().transcribe("audio.mp3")

# Speaker diarization
transcript = aai.Transcriber().transcribe(
    "meeting.mp3",
    config=aai.TranscriptionConfig(speaker_labels=True)
)
```

#### Real-time Streaming
```python
# Whisper streaming, AssemblyAI Universal-Streaming
# Latency: ~500ms - 2s
# Use case: live captions, voice agents
```

### Text-to-Speech (TTS)

#### ElevenLabs (best quality)
```python
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="...")
audio = client.text_to_speech.convert(
    voice_id="...",
    text="Hello world",
    model_id="eleven_multilingual_v2"
)
```

#### OpenAI TTS
```python
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="alloy",  # or echo, fable, onyx, nova, shimmer
    input="Hello world"
)
response.write_to_file("output.mp3")
```

#### Voice Cloning
- ElevenLabs: clone any voice from 1 minute of audio
- Cartesia, Resemble: similar
- **Ethical**: only with consent, watermarking required

### Speech-to-Speech (S2S)

```
Voice in → Voice out (no text intermediate)
- Lower latency (~250ms vs ~2s)
- Better prosody preservation
- Models: GPT-4o realtime, Gemini 2 Flash voice
```

```python
# OpenAI Realtime API
async with client.beta.realtime.connect(model="gpt-4o-realtime") as conn:
    await conn.session.update(session={
        "modalities": ["audio", "text"],
        "voice": "alloy",
        "instructions": "You are a helpful assistant"
    })
    
    # Stream audio in
    await conn.input_audio_buffer.append(audio_chunk)
    await conn.input_audio_buffer.commit()
    
    # Stream audio out
    async for event in conn:
        if event.type == "response.audio.delta":
            play(event.delta)
```

---

## 5. Image Generation

### Models (2026)

| Model | Strength |
|---|---|
| **DALL-E 3** | OpenAI native, integrated |
| **Stable Diffusion 3** | Open source, customizable |
| **FLUX** | Best open quality |
| **Midjourney v7** | Best aesthetic |
| **Imagen 3** | Google, accurate text |
| **Stable Diffusion XL Turbo** | Fastest |

### Architectures

#### Diffusion Models
```
Random noise
    ↓ iterative denoising
    ↓ guided by text prompt
    ↓
Final image
```

#### Latent Diffusion (SDXL, FLUX)
- Operate in latent space (not pixel)
- Faster, less memory

### Implementation

```python
# Stable Diffusion via Diffusers
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium",
    torch_dtype=torch.bfloat16,
).to("cuda")

image = pipe(
    prompt="A futuristic cityscape at sunset",
    num_inference_steps=28,
    guidance_scale=7.0,
).images[0]
image.save("output.png")
```

### Control Methods

#### ControlNet
Condition on:
- Pose (skeleton)
- Edge map (canny)
- Depth map
- Segmentation
- Reference image

#### IP-Adapter
Use reference image as style guide

#### LoRA for Diffusion
Fine-tune for specific style/character

```python
pipe.load_lora_weights("./my_style_lora.safetensors")
image = pipe("character in my style").images[0]
```

### Use Cases

```
- Marketing imagery generation
- Product visualization
- Concept art
- Social media content
- Synthetic training data
- Personalization
```

---

## 6. Video Generation (frontier 2026)

### Models

| Model | Provider | Notes |
|---|---|---|
| **Sora** | OpenAI | High quality, 60s clips |
| **Veo 2** | Google | Photorealistic |
| **Kling** | Chinese, available globally | Decent quality |
| **Runway Gen-3** | Runway | Creator tool focus |
| **Pika** | Pika Labs | Easy UI |
| **Hunyuan** | Tencent | Open source |

### Capabilities (2026)

✅ 5-60 second clips
✅ Text-to-video
✅ Image-to-video (animate stills)
✅ Video-to-video (style transfer)
✅ Decent physics + temporal consistency
⚠️ Long-form storytelling still limited
⚠️ Text in video unreliable

### Use Cases

- Marketing videos
- Product demos
- Concept previs
- Social media
- Training data
- Avatars (talking head)

---

## 7. Music Generation

### Models

| Model | Provider |
|---|---|
| **Suno V4** | Best quality, full songs |
| **Udio** | Similar quality |
| **Stable Audio** | Open source |
| **MusicGen** | Meta open source |

### Use Case

```
"Upbeat jazz with saxophone, 90 seconds"
"Sad piano ballad in C minor"
"Epic orchestral for trailer"
```

---

## 8. Multi-Modal Embeddings

### Why

Search across modalities:
- Find images similar to text
- Find audio matching mood
- Cross-modal retrieval

### CLIP (foundational)
```python
from transformers import CLIPModel, CLIPProcessor

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Text embedding
text_inputs = processor(text=["a dog playing"], return_tensors="pt")
text_features = model.get_text_features(**text_inputs)

# Image embedding
image_inputs = processor(images=image, return_tensors="pt")
image_features = model.get_image_features(**image_inputs)

# Cross-modal similarity
similarity = (text_features @ image_features.T).softmax(dim=-1)
```

### Modern (2026)

- **SigLIP-2**: better than CLIP
- **DINOv2**: self-supervised, better images
- **ImageBind**: 6 modalities aligned (text, image, audio, depth, thermal, IMU)

### Use in RAG

```
1. Index images using CLIP embeddings
2. User text query → CLIP text embedding
3. Search vector DB → find similar images
4. Return + describe with VLM
```

---

## 9. Multi-Modal RAG

### Architecture

```
Index time:
  PDF → extract text + images
  Text → text embeddings
  Images → CLIP embeddings + caption (VLM)
  Store in vector DB with type metadata

Query time:
  User query (text)
  → text embedding
  → search across both modalities
  → retrieve mix of text + images
  → send to VLM for answer
```

### Implementation Sketch

```python
# Index
for page in pdf:
    text = extract_text(page)
    images = extract_images(page)
    
    # Index text
    vector_db.add(
        embedding=text_embed(text),
        metadata={"type": "text", "page": page.num},
        content=text
    )
    
    # Index each image
    for img in images:
        caption = vlm.describe(img)  # generate caption
        vector_db.add(
            embedding=clip_embed(img),
            metadata={"type": "image", "page": page.num},
            content=caption,
            blob=img
        )

# Query
def query(user_q):
    # Search both
    results = vector_db.search(text_embed(user_q), top_k=10)
    
    # Build multi-modal context
    context = []
    for r in results:
        if r.metadata["type"] == "text":
            context.append({"type": "text", "text": r.content})
        else:
            context.append({"type": "image", "source": r.blob})
    
    # Ask VLM
    return vlm.complete(context + [{"type": "text", "text": user_q}])
```

### Use Cases

- Technical documentation (text + diagrams)
- Medical imaging + reports
- E-commerce (text + product photos)
- Architecture (text + blueprints)

---

## 10. Production Architecture for Multi-Modal

### Latency Considerations

```
Text-only LLM:        500ms - 2s
Vision (image):       1s - 5s
Audio (transcribe):   real-time + transcribe time
Video analysis:       10s - minutes
Image generation:     5s - 30s
Video generation:     30s - 5 min
```

### Cost Considerations

```
Text:           ~$3 / 1M tokens (Sonnet)
Image input:    ~$3 / 1M tokens (~1.5K tokens per image)
Image gen:      $0.04 - $0.30 per image
Video input:    expensive (per-frame tokens)
Audio in/out:   ~$6 / minute (TTS), ~$0.006/min (STT)
```

### Caching for Cost

```python
# Anthropic prompt caching for image-heavy systems
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {...},
                    "cache_control": {"type": "ephemeral"}  # ← cache
                },
                {"type": "text", "text": user_question}
            ]
        }
    ]
)
# 90% off cached image tokens
```

### Streaming for UX

```python
# Stream long responses
with client.messages.stream(
    model="claude-sonnet-4-6",
    messages=[...],
) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
```

---

## 11. Common Use Case Architectures

### Use Case 1: Visual Search Engine

```
User uploads image
    ↓
CLIP embedding
    ↓
Vector search (Pinecone)
    ↓
Top-K similar images
    ↓
VLM ranks relevance
    ↓
Display results
```

### Use Case 2: Voice Assistant

```
User speaks
    ↓
[Whisper STT] → text
    ↓
[LLM] → response text
    ↓
[ElevenLabs TTS] → audio
    ↓
Play to user
```

Latency budget: ~2-3 seconds total

Or skip text: GPT-4o realtime API for ~250ms

### Use Case 3: Document Processing Pipeline

```
PDF uploaded
    ↓
[LlamaParse / Docling] → structured markdown
    ↓
Text → embeddings (RAG)
Tables → DataFrame
Images → VLM analysis
    ↓
Structured output (JSON)
    ↓
Validate against schema
    ↓
Save to database
```

### Use Case 4: Product Image Generation

```
Product description
    ↓
[Stable Diffusion + ControlNet] (with brand style LoRA)
    ↓
Generated images
    ↓
[VLM quality check] (matches description?)
    ↓
Approve or regenerate
```

---

## 12. Pitfalls

### Pitfall 1: VLM Hallucinations on Images
```
"How many cats?" → "3 cats"
Reality: 0 cats in image

Fix: Lower temperature, ask for confidence, verify with second LLM
```

### Pitfall 2: Token Cost Surprise
```
1 image = 1500-3000 tokens
100 images = 300K tokens = $0.90 input cost

Fix: Resize images, cache, use cheaper model
```

### Pitfall 3: PDF Layout Issues
```
Tables in PDF → garbage text extraction

Fix: Use layout-aware tool (Docling, LlamaParse)
Or: Send PDF directly to VLM (Claude, Gemini)
```

### Pitfall 4: Speech Recognition Accuracy
```
Bad audio: noise, accents, jargon
   → Whisper poor accuracy

Fix:
- Pre-process audio (denoise)
- Use larger model
- Domain-specific fine-tune
- AssemblyAI for hard accents
```

### Pitfall 5: Video Analysis Cost Explosion
```
Send full video to VLM = expensive
Each frame = image tokens

Fix:
- Sample frames (1 per second)
- Pre-filter relevant segments
- Use specialized video models
```

### Pitfall 6: Generated Content Quality Variance
```
Image gen sometimes great, sometimes bad
Hard to make reliable production use

Fix:
- Generate N images, pick best (LLM judge)
- Use ControlNet for predictable structure
- Human review before publish
```

---

## 13. Cheat Sheet

### Q: "VLM ทำอะไรได้บ้าง?"
> "อ่านภาพ ตอบคำถาม OCR แยกตาราง วิเคราะห์ chart/graph
> ปี 2026 production: Claude Opus, Gemini 2.5 Pro, GPT-5
> Use case: doc processing, visual QA, accessibility"

### Q: "ทำ document AI ใช้ tool ไหน?"
> "PDF + tables: LlamaParse / Docling (best layout)
> Forms / receipts: Azure Document Intelligence
> Simple: send to VLM directly (Claude, Gemini)
> Production: combine — extract structure, send to VLM for understanding"

### Q: "Whisper vs Cloud APIs?"
> "Whisper: free, self-host, slight quality gap
> AssemblyAI: best accuracy, speaker diarization
> OpenAI API: easy, slightly worse than self-hosted Whisper Large
> Real-time: GPT-4o realtime / streaming APIs"

### Q: "Image gen ใช้ตัวไหน?"
> "Production: FLUX (open) / Midjourney (best aesthetic) / DALL-E (integrated)
> Custom style: SDXL + LoRA
> Realistic + text: Imagen 3
> Cost-conscious: SDXL Turbo (10x faster)"

### Q: "Multi-modal embeddings ทำอะไร?"
> "Search ข้าม modalities — text query หา image, audio query หา music
> CLIP / SigLIP-2 / ImageBind
> Use case: visual search, content moderation, multi-modal RAG"

---

## Sources

- [OpenAI Multi-Modal Models](https://platform.openai.com/docs/models)
- [Anthropic Vision Documentation](https://docs.anthropic.com/claude/docs/vision)
- [Google Gemini Multi-Modal](https://ai.google.dev/gemini-api/docs/vision)
- [LlamaParse Documentation](https://docs.cloud.llamaindex.ai/llamaparse)
- [Whisper GitHub](https://github.com/openai/whisper)
- [Stable Diffusion 3](https://stability.ai/news/stable-diffusion-3)
- [CLIP Paper](https://arxiv.org/abs/2103.00020)
- [SigLIP-2](https://arxiv.org/abs/2502.14786)
- [ImageBind](https://imagebind.metademolab.com/)
