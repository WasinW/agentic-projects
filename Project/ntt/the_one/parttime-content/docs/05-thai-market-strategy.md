# 05 - Thai Market Strategy

## Platform Landscape (Thailand 2025-2026)

### Platform Ranking

| Rank | Platform | Strength | Key Metric |
|------|----------|----------|------------|
| 1 | **TikTok** | #1 user preference, discovery, live commerce | 21% platform preference |
| 2 | **YouTube** | #1 screen time, long-form + Shorts | Most viewing hours |
| 3 | **Facebook** | Older demographics, groups, marketplace | Still massive reach |
| 4 | **Instagram** | Lifestyle, fashion, beauty | Strong for visual content |
| 5 | **LINE** | Messaging (#1 in TH), CRM, broadcast | Unique to TH/JP/TW |
| 6 | **Shopee** | #1 e-commerce marketplace | 80%+ combined with Lazada |
| 7 | **TikTok Shop** | Fastest growing commerce | 12.07B baht first-year revenue |

### Key Insights

- **TikTok Shop (21%)** แซง **Lazada (16%)** ในด้าน platform preference แล้ว
- **Live-selling** เป็น dominant format ในไทย — ต้องมี strategy รองรับ
- **Double-digit sales events** (11.11, 12.12) ใหญ่มากในไทย
- **Vertical video first** — ทุก platform prioritize 9:16
- **UGC-style content** ทำงานดีกว่า polished ads

---

## Thai Language TTS Options

### Comparison

| Provider | Thai Voices | Quality | Price | Best For |
|----------|------------|---------|-------|----------|
| **Narakeet** | **93 voices** | Good, natural | Pay per minute | **Largest Thai selection** |
| **Google Cloud TTS** | Multiple (Chirp 3 HD) | Good | Pay per char | GCP teams, enterprise |
| **ElevenLabs** | Limited | Best overall quality | $5-330/mo | Premium quality (limited TH) |
| **Murf** | Multiple variants | Good ("Speech Gen 2") | Subscription | Cultural depth, tonal |
| **LOVO** | Thai accents | Good | Subscription | 500+ voices, 100+ languages |
| **AI Studios** | Bangkok + regional | Good | Subscription | Regional dialect variations |
| **Fliki** | Emotion support | Good | Subscription | Emotional Thai speech |

### Recommendation

```
Primary (Thai content):     Narakeet — 93 Thai voices, best selection
Backup (quality-first):     ElevenLabs — best overall but limited Thai
Enterprise/GCP:             Google Cloud TTS Chirp 3 HD — SLA, pay-per-use
Budget:                     Google Cloud TTS standard — cheapest
```

### Testing Strategy

ก่อนเลือก provider ให้ test ด้วย script เดียวกัน:

```
Test script (Thai):
"สวัสดีค่ะ วันนี้เราจะมาลองรีวิวสินค้าตัวนี้กัน
ซึ่งต้องบอกเลยว่า ประทับใจมากค่ะ!
ถ้าใครสนใจ กดลิงก์ด้านล่างได้เลยนะคะ"

Test criteria:
1. ความเป็นธรรมชาติ (naturalness)
2. สำเนียง/โทนเสียง (accent/tone)
3. อารมณ์ (emotion — excitement vs calm)
4. ความเร็วในการ generate
5. ราคาต่อนาที
```

---

## Thai Content Trends

### Top Content Categories (E-Commerce)

| Category | Platform | Format |
|----------|----------|--------|
| **Beauty / Skincare** | TikTok, IG | Review, before/after, tutorial |
| **Fashion** | TikTok, IG | Outfit of the day, haul, try-on |
| **Lifestyle** | TikTok, YouTube | Day-in-my-life, room tour |
| **Travel Accessories** | TikTok | Packing tips, travel essentials |
| **Fandom / Collectibles** | TikTok | Unboxing, collection showcase |
| **Food / Supplements** | TikTok, Facebook | Taste test, health tips |
| **Tech / Gadgets** | YouTube, TikTok | Review, comparison, tutorial |

### Content Format Trends

```
1. Hook-first content (3 วินาทีแรกต้อง hook)
   → "รู้ไหม?", "อย่าซื้อก่อนดูคลิปนี้!", "ตกใจมาก!"

2. Storytelling format
   → เล่าเรื่อง problem → solution → result

3. UGC-style (User Generated Content)
   → ดูเป็นธรรมชาติ ไม่ production มากเกินไป

4. Behind-the-scenes
   → โชว์ process, ความจริงใจ

5. Split-screen comparison
   → เปรียบเทียบ before/after, สินค้า A vs B

6. Text overlay + fast cuts
   → ข้อความบนจอ + ตัดภาพเร็ว

7. ASMR / Satisfying
   → เสียง unboxing, texture, process
```

### Trending Hook Patterns (Thai)

```python
HOOK_TEMPLATES_TH = [
    # Curiosity
    "รู้ไหม? {product} ตัวนี้ {surprising_fact}",
    "อย่าซื้อ {category} ก่อนดูคลิปนี้!",

    # Problem-solution
    "ใครมีปัญหา {problem} ต้องลอง!",
    "{problem} แก้ได้ด้วย {product}",

    # Social proof
    "ขายดีจนต้องมาลอง!",
    "TikTok viral {product} ดีจริงมั้ย?",

    # Urgency
    "เหลืออีกแค่ {time}! ลดราคา {discount}%",
    "Flash sale! {product} ราคานี้ไม่ได้มีบ่อย",

    # Emotional
    "ตกใจมาก! {product} ทำให้ {result}",
    "ดีใจที่ได้ลอง {product} เพราะ...",
]
```

---

## E-Commerce Strategy (Thai Market)

### Platform Priority

```
Phase 1 (Start):
  1. TikTok + TikTok Shop — organic reach ดีที่สุด
  2. Instagram Reels — visual content, fashion/beauty

Phase 2 (Scale):
  3. YouTube Shorts + Long-form — SEO value, evergreen content
  4. Shopee / Lazada — marketplace integration

Phase 3 (Expand):
  5. Facebook — broader demographics
  6. LINE — CRM, repeat customers
```

### TikTok Shop Strategy

```
Content Mix:
  40% — Product showcases (short, punchy reviews)
  25% — Tutorial/How-to (สอนใช้งาน)
  20% — Live selling (ขายสด)
  15% — Trend-riding (ใช้ trending sounds/formats)

Posting Frequency:
  Minimum: 1 video/day
  Recommended: 2-3 videos/day
  Live: 2-3 times/week (30-60 min each)

Key Tactics:
  • ใช้ trending sounds + hashtags
  • Hook ใน 3 วินาทีแรก
  • CTA ชัดเจน ("กดตะกร้าสีเหลือง!")
  • ตอบ comments ด้วยวิดีโอ
  • Collab กับ creators อื่น
```

### Double-Digit Sales Events

```
Prepare content pipeline for:
  1.1   → New Year sale
  2.2   → Valentine's
  3.3   → March sale
  ...
  11.11 → Singles' Day (BIGGEST)
  12.12 → Year-end sale

Timeline:
  -14 days:  Tease content (countdown, sneak peek)
  -7 days:   Product highlight videos
  -3 days:   Comparison/best deals content
  D-day:     Live selling + flash deal videos
  +1-3 days: Last chance + review content
```

---

## Live Selling Integration

Live selling เป็น dominant format ในไทย — ต้องมี strategy:

### AI-Assisted Live Selling

```
Pre-Live:
  • AI generate script outline for products to showcase
  • Prepare product info cards (prices, features, stock)
  • Generate talking points per product

During Live:
  • AI real-time comment analysis (sentiment, questions)
  • Auto-generate responses to common questions
  • Dynamic pricing/discount suggestions based on engagement

Post-Live:
  • AI clip extraction (best moments → short-form content)
  • Opus Clip for auto-repurposing
  • Analytics summary + improvement suggestions
```

---

## Localization Considerations

### Language Mix

```
Pure Thai:           Skincare, beauty, food, daily life
Thai + English mix:  Tech, fashion, lifestyle (common in urban TH)
English subtitle:    If targeting international audience
```

### Cultural Notes

```
DO:
  ✓ ใช้ภาษาเป็นกันเอง ("ค่ะ/ครับ" + casual tone)
  ✓ แสดงความจริงใจ (honest reviews ดีกว่า overselling)
  ✓ ใช้ humor ที่เข้ากับวัฒนธรรมไทย
  ✓ Reference Thai celebrities/trends เมื่อเหมาะสม
  ✓ ใช้สี/เทมเพลตที่สดใส eye-catching

DON'T:
  ✗ Hard sell มากเกินไป
  ✗ Content ที่ดูเป็น robot/ไม่เป็นธรรมชาติ
  ✗ ละเลยการตอบ comments/DMs
  ✗ Copy content จากต่างประเทศมาตรงๆ โดยไม่ localize
```

---

## Analytics & Optimization

### Key Metrics to Track

```
Content Performance:
  • View count (ยอดวิว)
  • Watch time / retention (ดูจนจบกี่ %)
  • Engagement rate (like + comment + share / views)
  • Save rate (บันทึก — signal ที่ดีมาก)
  • Click-through rate (กดลิงก์)

Commerce Metrics:
  • Product page visits from content
  • Add to cart rate
  • Conversion rate
  • Revenue per content piece
  • ROAS (Return on Ad Spend, if paid)

Growth Metrics:
  • Follower growth rate
  • Profile visits
  • Content reach (unique viewers)
```

### Feedback Loop

```
Publish Content
    │
    ▼
Collect Metrics (24h, 48h, 7d)
    │
    ▼
Analyze:
  • Which hooks worked? (retention in first 3s)
  • Which emotions resonated? (engagement by segment)
  • Which products converted? (click-through + purchase)
  • Which formats performed? (review vs tutorial vs unboxing)
    │
    ▼
Update Knowledge Base:
  • Successful hook patterns → RAG
  • High-performing scripts → templates
  • Trending styles → visual prompts
  • Best posting times → scheduler
    │
    ▼
Generate Better Content (next cycle)
```
