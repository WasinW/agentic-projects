# AI Art Director — Comprehensive Knowledge

> Deep reference for the ai-art-director subagent.
> Senior generative-visual director + prompt engineer for image AND video models.
> Context: high-volume, on-brand, consistent Thai สายมู (mystical/spiritual) AI art + animation.

---

## 1. Foundations

### What an AI Art Director does

Directs **generative visual output** — image and video — at production scale. Not "types prompts into Midjourney." Owns the *look*: defines a style DNA, builds the prompt + reference system that reproduces it across hundreds of posts, curates the slop down to the keepers, and ships an on-brand, consistent visual feed. The director is accountable for **aesthetic coherence + throughput + cost**, the same way a human art director owns a brand's visual language — except the production crew is a stack of diffusion models.

### AI Art Director vs AI Engineer

| | AI Engineer | AI Art Director |
|---|---|---|
| Domain | LLM / RAG / agents | Generative image + video |
| Core skill | System + prompt engineering for text | Visual craft + prompt engineering for pixels |
| Models | Claude, GPT, Gemini (text) | FLUX, Midjourney, Kling, Veo (visual) |
| Output | Generated text, actions | Generated images, animation |
| Quality bar | faithfulness, helpfulness, safety | aesthetic, consistency, on-brand |
| Failure mode | hallucination, schema break | off-brand slop, inconsistent character |

They are complementary, not the same person. The AI engineer **automates the pipeline** (API orchestration, batch jobs, metadata); the art director **decides what good looks like** and how to reproduce it. On Sin's สายมู business they hand off constantly (see §8).

### AI Art Director vs human graphic designer

A human designer composes pixels by hand with full intent. The art director composes **probability distributions** — you steer a model toward intent via prompt, reference, seed, and control signals, then curate. You trade pixel-level control for 100x throughput. The skill is no longer "can you draw it" but "can you describe + constrain + select it reliably." Taste is the moat; the model is a commodity.

### The core loop: generate → curate → refine

```
Direction (style DNA + brief)
   ↓
[Generate — batch, multiple seeds/variations]
   ↓
[Curate — reject slop, keep on-brand keepers]   ← the highest-leverage step
   ↓
[Refine — upscale, inpaint, edit, animate]
   ↓
[Tag + archive — seed, prompt, model, refs]
   ↓
(feed learnings back into the prompt library)
```

Most beginners over-invest in generation and under-invest in **curation**. The model produces 80% garbage at any quality bar; the director's value is the 20% selection and the discipline to throw the rest away. Curation is the job.

### The core building blocks

1. **Style DNA** — the reusable description of "our look" (palette, lighting, mood, medium)
2. **Prompts** — engineered, versioned, parameterized templates
3. **References** — image prompts, style refs, character refs (IP-Adapter, --cref, reference images)
4. **Consistency rig** — LoRA / IP-Adapter / ControlNet / seed control
5. **Models** — image + video, chosen per job
6. **Pipeline** — batch generation, upscaling, image→video
7. **Curation + metadata** — selection workflow, tagging, asset library

---

## 2. Mental Models / Decision Frameworks

### Model selection (image)

| Model | Best at | Weak at | Use for |
|---|---|---|---|
| **FLUX.1 [dev]** | Photorealism, prompt adherence, **self-hostable + LoRA** | Needs GPU/ComfyUI skill | Consistent on-brand pipeline, character LoRA |
| **FLUX.1 [pro] / Kontext** | Photoreal API, **reference-consistent editing** | Closed, per-image cost | Polished hero shots, edit-preserve-identity |
| **Midjourney v7** | **Aesthetics**, editorial, cinematic mood | No API (officially), less literal | Mood boards, beauty shots, style exploration |
| **Ideogram v3** | **Text-in-image** accuracy (Thai/EN overlays) | Less photoreal | Quote cards, typographic mystical posts |
| **Imagen 4** (Vertex) | Product/material rendering, clean isolation | Less stylized | Product shots, amulet/talisman close-ups |
| **Nano Banana Pro** (Gemini 3) | **Multi-ref editing** (up to 14 refs, ~5 people consistent), reasoning | Google ecosystem | Compositing references, consistent characters fast |
| **Seedream 4.x** | Multi-reference, batch outputs | Newer, less tooling | High-volume reference-driven batches |
| **SDXL** | Mature LoRA/ControlNet ecosystem, cheap | Older quality vs FLUX | Legacy LoRAs, low-cost bulk, fine control |

**Default for Sin's สายมู pipeline:** FLUX.1 [dev] self-hosted/fal for the consistent core look + LoRA, Midjourney v7 for mood/exploration, Ideogram for Thai text overlays, Kontext/Nano Banana for edits that must preserve identity.

### Prompt anatomy

A strong prompt is composed, not a word-salad. Order roughly by importance:

```
[Subject]      — who/what: "a serene Thai goddess, gold ornaments"
[Style/Medium] — "ethereal digital painting, ukiyo-e influence"
[Composition]  — "centered, rule of thirds, negative space top"
[Lighting]     — "volumetric golden-hour rim light, soft haze"
[Camera]       — "85mm portrait, shallow DOF, low angle"
[Color/Mood]   — "warm gold + deep indigo, mystical, reverent"
[Detail/Quality]— "intricate, high detail, 8k" (model-dependent)
[Params]       — aspect 9:16, seed, --stylize / guidance
```

Keep each axis explicit and consistent across a series — that's what produces a coherent feed. FLUX and Nano Banana respond to natural-language sentences; Midjourney to dense comma phrases; tune per model.

### The consistency problem (the hard one)

The single biggest technical challenge: same character / same style across many posts. Tools ranked by strength + cost:

| Lever | Consistency | Effort | When |
|---|---|---|---|
| **Seed reuse** | Weak | Free | Minor variations of one image |
| **Style reference** (--sref, IP-Adapter style) | Medium (style) | Low | Same *look*, different subjects |
| **Character reference** (--cref, IP-Adapter FaceID, Nano Banana refs) | Medium-high (identity) | Low | Same *character*, few posts |
| **Reference-editing model** (Kontext, Nano Banana) | High (identity, no train) | Low | Preserve subject across edits |
| **Trained LoRA** | **Highest** | High (dataset + train) | A recurring brand character/style at volume |
| **LoRA + IP-Adapter + ControlNet** | Highest + pose control | Highest | Full production rig |

Rule: start with style/character refs (cheap), graduate to a **trained LoRA** only when a character recurs enough to amortize the training cost. For Sin's brand mascot/deity → LoRA is worth it.

### Quality vs Cost vs Control (pick the corner)

```
        CONTROL
         (ComfyUI + FLUX dev + LoRA/ControlNet — full rig, self-host)
        /        \
  QUALITY ------- COST
 (Midjourney v7,  (FLUX schnell, SDXL,
  FLUX pro, Veo)   fal/together cheap APIs)
```

- Need maximum **control + consistency** → ComfyUI + FLUX dev self-hosted.
- Need maximum **aesthetic** with least effort → Midjourney v7 (no pipeline, but no API).
- Need maximum **throughput per baht** → FLUX schnell / SDXL on fal.ai or Together.

You rarely get all three. Sin's high-volume on-brand business lives on the CONTROL edge for the core look (LoRA), borrowing QUALITY (Midjourney) for hero/exploration.

### Aesthetic direction: mood board → style DNA

Before any volume: build a **mood board** (10-30 reference images of the target look) and distill a **style DNA** — a reusable text + reference block:

```
STYLE DNA — "Mystic Gold" (Sin saymu brand)
  Palette:    warm gold, deep indigo, candle amber; muted, never neon
  Lighting:   volumetric, soft haze, golden-hour rim, sacred glow
  Medium:     ethereal digital painting + subtle Thai mural texture
  Mood:       reverent, calm, auspicious — NOT horror, NOT cartoonish
  Camera:     centered/symmetrical, shallow DOF, eye-level or low hero
  Refs:       [board_url] + style-ref image IDs / --sref code / LoRA
```

Every prompt inherits from the DNA. This is what makes a feed look designed instead of random. Version it; it evolves.

---

## 3. Standard Practices

### Prompt engineering patterns

- **Template + slots** — fixed DNA block + variable subject/scene. Keeps the look constant.
- **Front-load the important** — subject + style first; models weight early tokens.
- **One concept per axis** — don't fight yourself ("realistic anime oil-painting photo").
- **Weighting** — `(word:1.3)` in SD/FLUX-ComfyUI; `::` and `--no` in Midjourney.
- **Natural language for modern models** — FLUX, Nano Banana, Imagen reason over sentences; SDXL/MJ prefer tag-dense phrasing.
- **Iterate one variable at a time** — change lighting OR camera OR subject, not all at once, to learn what the lever does.

### Negative prompts

SD/FLUX-ComfyUI: explicit negative field. Midjourney: `--no`. Common removals: `extra fingers, deformed hands, watermark, text, oversaturated, lowres, jpeg artifacts, cartoon` (when going photoreal). For สายมู work also negative-prompt away the unwanted: `horror, creepy, demonic, gore` — keep it auspicious, not scary.

### Style references + image prompting

- **Midjourney:** `--sref <url/code>` (style), `--cref <url>` (character), `--sw` style weight.
- **FLUX/SD (ComfyUI):** IP-Adapter (style + composition), IP-Adapter FaceID (identity).
- **Nano Banana / Seedream:** drop in up to many reference images directly; strong zero-train consistency.
- **Kontext:** feed an image + edit instruction; preserves identity across rounds.

### Seeds

Fix the seed to lock composition and vary one thing; randomize the seed to explore. Always **log the seed** of every keeper — it's how you reproduce or remix later. Seed alone won't give cross-image character consistency (that needs refs/LoRA), but it stabilizes single-image iteration.

### Aspect ratios for short-form

| Ratio | Use |
|---|---|
| **9:16** | TikTok / Reels / Shorts / Stories — Sin's primary |
| 1:1 | Feed grid, carousels |
| 4:5 | IG portrait (max feed real estate) |
| 16:9 | YouTube, banners, video |

Generate native to target ratio — don't crop a 1:1 into 9:16 and lose the subject. Set `--ar 9:16` / aspect param up front.

### Upscaling

- **Topaz Gigapixel** — faithful, no invented detail; safe for final print/clean upscales.
- **Magnific** — *generative* upscale, invents detail/texture; great for art, can hallucinate (watch faces, Thai script — it will corrupt text). Use creative slider low for portraits.
- **ComfyUI upscale** (ultimate SD upscale, tiled) — free, controllable, in-pipeline.

Rule: generate at model-native res, upscale once at the end. Don't upscale before inpainting.

### LoRA / IP-Adapter / ControlNet for consistency

- **LoRA** — fine-tune a small adapter on 15-30 images of your character/style; the durable solution for a recurring brand identity.
- **IP-Adapter** — inject a reference image's style or face at inference, no training. FaceID variant for identity.
- **ControlNet** — constrain composition: pose (OpenPose), edges (Canny), depth, for FLUX use XLabs Canny/Depth/HED. Lock layout while changing everything else.

Production rig = **LoRA (identity) + IP-Adapter FaceID (face lock) + ControlNet (pose)**.

### Batch generation + curation workflow

```
1. Lock prompt template (DNA + scene slot)
2. Batch N seeds/variations (e.g. 20-50 per concept)
3. Contact-sheet review — fast reject pass (keep ~10-20%)
4. Second pass on keepers — refine/inpaint/upscale
5. Tag + archive every keeper with metadata
6. Ship to content-strategist's calendar
```

Curate ruthlessly. A 10-20% keep rate is healthy. Posting unselected output is the #1 way to look like slop.

### Metadata tagging

Tag every keeper: `model + version, full prompt, negative prompt, seed, refs/LoRA used, aspect, upscaler, brand campaign, license`. This makes the library searchable, reproducible, and remixable — and feeds the de-engineer's asset pipeline (§8). Embed in PNG metadata (ComfyUI does automatically) + a sidecar record.

---

## 4. Tools Landscape (2026)

> Fast-moving. Versions confirmed mid-2026; re-verify before committing budget.

### Image models
- **FLUX.1 [dev]** (Black Forest Labs) — open-weight, self-hostable, **best for LoRA + control**; photoreal, strong prompt adherence.
- **FLUX.1 [pro] / FLUX.1 Kontext [pro]** — API; Kontext = reference-consistent **editing** (preserve identity across rounds), ~$0.04/image.
- **FLUX.2** — newer BFL generation; verify availability/pricing.
- **Midjourney v7** (v8 emerging) — **aesthetic king**, editorial/cinematic; no official API.
- **Ideogram v3** — **best text-in-image** (typographic + quote cards).
- **Google Imagen 4** (Vertex AI) — product/material realism, clean isolation.
- **Nano Banana Pro** (Gemini 3 Pro image) — multimodal reasoning, up to ~14 reference images, ~5 consistent people, strong editing.
- **Seedream 4.x** — multi-reference, batch generation.
- **SDXL** — mature, cheapest, deepest LoRA/ControlNet ecosystem; quality below FLUX.
- **GPT Image / Recraft v3** — alternatives; Recraft strong on brand/vector/design.

### Video models
- **Google Veo 3.1** — leads on prompt adherence, **native audio**, 4K; cinematic realism.
- **Kling 3.0** — excellent human motion, **start/end frame**, motion brush, motion-transfer from reference video; up to ~120s; cheap (~$0.07/sec).
- **Runway Gen-4 / Gen-4.5** — **most mature creative control**: motion brush, camera moves, reference-driven character consistency; pro filmmaking workflow.
- **Luma Ray3 / Dream Machine** — fast, accessible image→video.
- **MiniMax Hailuo 02** — strong free/cheap tier for exploration.
- **Sora** — ⚠️ **discontinued** (web/app ended Apr 2026, API end Sep 2026). Do not build on it.

### Workflow / orchestration
- **ComfyUI** — node-based, the power-user standard; full control, LoRA/ControlNet/IP-Adapter, embeds metadata in PNGs. The backbone of a self-hosted consistent pipeline.
- **fal.ai** — fast serverless API for FLUX/SDXL/Kling/Veo/Seedream/Nano Banana, near-zero cold start; FLUX schnell ~$0.025, pro ~$0.05/image.
- **Replicate** — broad model catalog, simple API; pricier per image (~$0.03-0.05).
- **Together AI** — cheap FLUX schnell (~$0.003/image).
- **RunPod** — serverless/dedicated GPU (e.g. 3090 ~$0.22/hr community); run ComfyUI + FLUX yourself; one-click templates.
- **Modal** — serverless GPU for custom Python pipelines.

### Upscalers
- **Topaz Gigapixel** — faithful upscale (no invented detail), desktop ~$99-199.
- **Magnific** — generative/creative upscale, $39-299/mo; great for art, corrupts text/faces if pushed.
- **ComfyUI tiled upscale** — free, in-pipeline.

### Aggregators
- Platforms (FLUX Context-style) bundle 25+ models (FLUX, Midjourney, Seedream, Veo, Kling) under one account — convenient for exploration, less control than ComfyUI.

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| **Prompt spaghetti** | Contradictory word-salad, unpredictable | Composed prompt: one concept per axis, DNA template |
| **No seed control** | Can't reproduce or iterate keepers | Log seed of every keeper; fix to iterate |
| **Inconsistent style across feed** | Looks random, off-brand | Style DNA + sref/LoRA on every post |
| **Over-reliance on one model** | Miss each model's strength | Right model per job (MJ aesthetic, FLUX consistency, Ideogram text) |
| **Slop without curation** | Posting unselected output | Ruthless curate, ~10-20% keep rate |
| **Upscale before edit** | Locks in artifacts, wastes compute | Inpaint/fix first, upscale once at end |
| **Magnific on text/faces** | Invents/corrupts Thai script + features | Topaz or low creative slider for those |
| **Ignoring rights/licensing** | Legal + platform risk | Track model license + commercial terms per asset |
| **Cropping to reframe** | Loses subject, bad composition | Generate native to 9:16 / target ratio |
| **No metadata** | Library unsearchable, irreproducible | Tag model/prompt/seed/refs/license on every keeper |
| **Training a LoRA too early** | Wasted effort for one-off | Use refs first; LoRA only for recurring identity |
| **Disrespectful sacred imagery** | Cultural harm, audience backlash | Reverent direction, negative-prompt horror, review (§6) |

---

## 6. Advanced / Expert Topics

### Character / style consistency (the deep version)

**Reference-first ladder.** Style ref → character ref (--cref / IP-Adapter FaceID / Nano Banana multi-ref) → **trained LoRA** when a character recurs at volume.

**Training a character LoRA (FLUX/SDXL in ComfyUI or fal):**
- Dataset: 15-30 images, varied pose/lighting/background, consistent identity, clean captions.
- Train low-rank (rank 8-32), watch for overfit (same pose every time = too long/high rank).
- Tag with a rare trigger token (`s1n_goddess`) so it doesn't bleed into normal words.
- Combine at inference with IP-Adapter FaceID (face lock) + ControlNet OpenPose (pose) for full control.

**Style LoRA** — same process on a *look* not a person; locks "Mystic Gold" across any subject. This is the highest-leverage asset for an on-brand high-volume feed.

### Image → video pipeline

The reliable production path: **generate a strong still → animate it**, rather than text-to-video raw (more control, consistent identity from the still).

```
Still (FLUX/MJ, on-brand, 9:16)
   ↓
[Image→Video — Kling / Runway / Veo]
   ├─ Kling start+end frame: define first & last → smooth interpolation
   ├─ Runway motion brush: mask + draw motion path per region
   ├─ Camera control: dolly, orbit, push-in (Runway/Kling)
   └─ Veo: prompt adherence + native audio, 4K
   ↓
[Stitch / extend, add sound, color match]
   ↓
9:16 short-form clip
```

### Motion control

- **Motion brush** (Runway/Kling) — paint a region, draw its path; everything else stays still. Best for "drape moves, candle flickers, subject still."
- **Start/end frame** (Kling) — two stills, model interpolates; great for controlled reveals/transitions.
- **Camera moves** — explicit dolly/orbit/push for cinematic feel; keep slow for mystical/reverent mood.
- **Motion transfer** (Kling) — extract motion from a ref video, apply to your subject.

### Composition control (ControlNet)

OpenPose (pose), Canny (edges/layout), Depth (3D arrangement), HED (soft edges). FLUX: XLabs Canny/Depth/HED. Use to lock a composition (e.g. a fixed altar layout) while swapping subject/style — invaluable for series with a consistent frame.

### Self-hosting vs API economics

```
API (fal/Replicate):  ~$0.025-0.05/image, zero ops, instant scale
Self-host (RunPod):   ~$0.22-2/GPU-hr; break-even depends on volume + idle

Rule of thumb:
  - Low/spiky volume, no LoRA → API (fal/Together cheapest).
  - High steady volume + custom LoRAs + full control → self-host ComfyUI on RunPod.
  - Hybrid (common): self-host the LoRA core look, burst hero shots to MJ/Kontext API.
```

Sin's high-volume on-brand case → self-hosted ComfyUI + FLUX dev + brand LoRA is the cost + control winner once volume is steady; keep fal for overflow + Midjourney for exploration.

### Building a reusable prompt library

Treat prompts as versioned assets (like the ai-engineer treats text prompts):
- **DNA blocks** (per brand look) + **scene modules** (subject/setting) + **modifier snippets** (lighting/camera/mood).
- Store with example outputs + seeds + model + what-works notes.
- Parameterize for batch (template + slot CSV → 50 posts).
- This is the direct input to the `saymu-content-batch` workflow — each combo becomes a filled template.

### Sacred / cultural imagery sensitivity (สายมู)

Non-negotiable for this business. Generative models will happily produce disrespectful or inaccurate sacred imagery.

- **Reverent by default** — direction = auspicious, calm, dignified; negative-prompt `horror, demonic, gore, mockery`.
- **Accuracy of symbols** — Buddhist/Hindu/Thai folk iconography has meaning; wrong mudra, deity attributes, or mashed-up symbols read as ignorant or offensive. Verify against references; when unsure, abstract rather than fake specifics.
- **Don't fabricate real sacred objects/temples** as if authentic — frame as artistic interpretation.
- **Avoid AI artifacts on holy figures** — extra fingers/melted faces on a deity is both slop and disrespectful; curate hard, inpaint, or discard.
- **Audience trust** — สายมู audiences are devout; respect is the brand. Loop in governance-consultant on anything near real religious institutions, monks, or royal/protected imagery (Thai law is strict here).

---

## 7. References

### Model docs
- **FLUX (Black Forest Labs)** — https://blackforestlabs.ai/ ; FLUX/Kontext API: https://fal.ai/flux
- **Midjourney** — https://docs.midjourney.com/
- **Ideogram** — https://ideogram.ai/
- **Google Imagen / Veo (Vertex AI)** — https://cloud.google.com/vertex-ai
- **Nano Banana (Gemini image)** — https://ai.google.dev/
- **Runway** — https://runwayml.com/ ; **Kling** — https://klingai.com/ ; **Luma** — https://lumalabs.ai/

### Prompt + workflow guides
- **ComfyUI** — https://www.comfyui.org/ (node graphs, LoRA/ControlNet/IP-Adapter)
- **fal.ai model + pricing** — https://fal.ai/pricing
- **RunPod ComfyUI+FLUX guides** — https://www.runpod.io/blog/run-flux-image-generator-on-runpod
- **Kling prompting/camera** — https://www.ambienceai.com/tutorials/kling-prompting-guide
- **Comparisons (re-verify, fast-moving)** — https://melies.co/compare/ai-image-models , https://www.aimagicx.com/blog/ai-video-generation-showdown-2026

### Communities
- **r/StableDiffusion**, **r/comfyui**, **r/midjourney** (Reddit)
- **Civitai** — LoRA/model sharing (vet licenses + content)
- **Banodoco** (Discord) — open-source AI video/animation
- **Black Forest Labs / fal.ai Discords** — FLUX tooling

### Upscalers
- **Topaz** — https://www.topazlabs.com/ ; **Magnific** — https://magnific.ai/

---

## 8. Working With Other Roles

| Role | Handoff |
|---|---|
| **Content Strategist** | Receives the brief: *what* to make + *when* (calendar, hooks, captions). Art director turns each `saymu-content-batch` combo into prompts + assets; strategist sequences them into the feed. |
| **AI Engineer** | Builds the **automation**: batch API orchestration (fal/Replicate), ComfyUI-as-service, queueing, retries, programmatic prompt-template fill. Art director defines the visual spec; engineer makes it run at volume. |
| **DE Engineer** | Owns the **asset metadata pipeline**: ingest tagged keepers (prompt/seed/model/refs/license), index for search/reuse, track lineage. Art director emits the metadata schema; DE persists + serves it. |
| **Governance Consultant** | **Content rights + safety**: model commercial licenses, Civitai/LoRA provenance, platform ToS, and the sacred/cultural + Thai legal sensitivities (§6). Review gate for anything near religious institutions, royalty, or real persons. |

---

*AI art direction in 2026 = taste + prompt craft + a consistency rig + ruthless curation. The model is a commodity; the style DNA, the LoRA, and the selection eye are the moat.*
