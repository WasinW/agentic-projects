---
name: saymu-oracle
description: Generate a daily oracle / reading post for the lumora project — a card/theme + art prompt + reflective caption in Sin's voice + format, framed as art and reflection (never prediction/medical/financial claims). Use for the "Personalized Oracle/Reading" content pillar.
---

# saymu-oracle

Produce a ready-to-post daily oracle / reading for the **lumora** project (Pillar 2: Oracle/Reading).

## When to use

- "ขอ daily oracle วันนี้" / "การ์ดวันนี้" / fill the oracle pillar (3-5/week).

## Inputs

- **theme/seed** — optional (e.g. "ความรัก", "การงาน", "เริ่มใหม่"); else pick one
- **aesthetic** — optional; else align with the current aesthetic-week
- **personalization** — optional (zodiac/ราศี/birth-day) → tailor the reading + a custom art angle

## Steps

1. **Pick the card/theme** — a single focus (a virtue, direction, color, element, or symbolic image). Keep it open + reflective, not deterministic.
2. **Load voice + guardrails** from project knowledge (`company_filter="project_sandbox"`, query "oracle voice guardrails").
3. **Write the reading caption** in Sin's voice — Thai-led, "fellow explorer", warm, a little playful or poetic. Structure: hook line → the card/theme → a reflective prompt or question for the reader → soft CTA (save/share/comment สิ่งที่คิด). 3-6 lines.
4. **Art prompt** — a 9:16 image of the card/symbol in the chosen aesthetic (hand to `lumora-art-prompt` style: subject/style/lighting/mood + aspect 9:16).
5. **Hashtags** — oracle/มู tags + dimension tags.
6. **Affiliate angle (optional)** — oracle deck, tarot, crystal, หนังสือ — only if natural.

## Guardrails (hard rules)

- **No prediction / fortune-guarantee / medical / financial claims.** Frame as **art, reflection, journaling prompt** — "ไพ่วันนี้ชวนให้คิดว่า..." not "วันนี้คุณจะ...แน่นอน".
- **Fellow explorer, not หมอดู/guru.** Invite reflection; don't dictate fate.
- Respectful, never fear-mongering ("ถ้าไม่ทำจะซวย" — avoid).

## Notes

- Personalization (birth-day → custom art) is a future paid feature (see `04_tech_backend.md`); for now keep it free + light.
