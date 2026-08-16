# 06 — Library Framework: Architecture & Solution Design

> **DRAFT FOR REVIEW — 2026-08-07.** Written so Sin can check whether we understand the framework the same way.
> Every section is marked: **[KB]** = stated in the canonical docs · **[INF]** = Claude's inference, needs confirming · **[GAP]** = something the docs don't answer.
> Canonical source: `lumora/knowledge/01_creative_library.md` (v3) + `content-taxonomy` SKILL.md.

---

## 1. What the framework is, in one sentence

**[INF]** Library Framework is a **tagged-experiment system for content**: it turns every post into a labelled point in a discrete design space, so that performance data becomes attributable to a *reason* rather than to luck.

**[KB]** The stated problem it solves: *systematic diverse content at scale without homogenization.*

**[INF]** The two halves of that problem are in tension, and the framework resolves them by splitting levels:
- **Diversity** comes from the post-level combinatorial space (C × T × M)
- **Non-homogenization** — i.e. still feeling like one creator — comes from the account level being pinned

Without the split, wide visual range destroys identity. With it, range is safe.

---

## 2. The two levels, as a constraint system

**[KB]** Account-level is fixed per channel; post-level varies per post.

**[INF]** Architecturally these are not "two sets of tags" — they are **constraint** and **variable**:

```
ACCOUNT-LEVEL  =  the CONSTRAINT SET
   Voice / Archetype  ┐
   Audience Persona   ├── defines which combos are LEGAL for this channel
   Niche scope        ┘   and which C-pillars are even in play (pick 2-4 of C1-C10)

POST-LEVEL     =  the DECISION SPACE
   C × T × M          ─── the arms you choose between, post by post
   (+ JTBD, HHH)          optional analytic dimensions
```

**[INF]** This means account-level changes are **expensive** (they invalidate the accumulated performance history, because the constraint set moved) while post-level changes are **free** (that's the whole point). That asymmetry is why the KB says lock the account level and vary the post level — and it is also why changing archetype mid-sprint would reset learning, not just confuse the brand.

---

## 3. Design-time vs run-time — two distinct sub-systems

**[INF]** The framework contains two functions that are usually discussed together but behave completely differently:

| | **Design-time** (rare, deliberate) | **Run-time** (every post) |
|---|---|---|
| Question | How many channels? What is this channel? | What do I post next? |
| Inputs | S (subject breadth), A (audience segments), aesthetic DNA | trends, account config, recent post history, performance |
| Machinery | Channel Count Formula `1 ≤ N ≤ S×A` + V1/V2/V3 gates | scorer + validator |
| Output | N channels, each with Voice/Persona/Niche + 2-4 pillars | one validated `(C, T, M)` + JTBD + HHH |
| Frequency | at channel birth; revisit quarterly | daily / batch weekly |
| Skill | `content-taxonomy` (channel-count mode) | `lumora-combo-recommend` → `content-taxonomy` (validate mode) → `lumora-content-batch` |

**[KB]** The formula's floor is `1`, not `MIN(S,A)` — corrected 2026-07-18. The gates decide, not the arithmetic. Default N = 1; over-splitting is the solo-creator failure mode.

**[INF]** Worth naming explicitly: the Channel Count Formula is a **justification device, not a calculator.** Its job is to force each proposed split to survive V1 (overlap → merge), V2 (size → fold), V3 (distinctness → merge). The bounds only frame the space.

---

## 4. Run-time architecture

```
┌─ DESIGN-TIME (set once per channel) ───────────────────────────────┐
│                                                                    │
│   S × A  ──▶ [ V1 overlap ] ──▶ [ V2 size ] ──▶ [ V3 distinct ]     │
│                                                       │            │
│                                                       ▼            │
│                                            N channels, each with:  │
│                                            Voice/Archetype         │
│                                            Audience Persona        │
│                                            Niche scope             │
│                                            active pillars (2-4)    │
│                                            active themes           │
│                                            sustainable media set   │
└───────────────────────────────────┬────────────────────────────────┘
                                    │ account config
                                    ▼
┌─ RUN-TIME (every post) ────────────────────────────────────────────┐
│                                                                    │
│  ① CANDIDATE SPACE                                                 │
│     active_C × active_T × sustainable_M  ──▶ candidate combos      │
│                                    │                               │
│  ② SCORE                           ▼                               │
│     score = 0.30·trend + 0.25·fit + 0.20·lift                      │
│           + 0.10·recency + 0.10·season − fatigue                   │
│     ├─ trend   ← lumora-trend-scan (external signal)               │
│     ├─ fit     ← account config (does it match voice/persona)      │
│     ├─ lift    ← post_log history (has this combo performed)       │
│     ├─ season  ← calendar (วันพระ, ตรุษจีน, festivals)              │
│     └─ fatigue ← recent post history (have I over-used this)       │
│                                    │                               │
│  ③ VALIDATE  (content-taxonomy, 5 gates, in order)                 │
│     1 Legality      — is (C,T,M) allowed for this channel          │
│     2 Brand fit     — matches Voice / Persona / Niche              │
│     3 Diversity     — not a near-duplicate of recent (C,T)/(C,M)   │
│     4 Funnel balance— Hero 5% / Hub 35% / Hygiene 60%              │
│     5 JTBD coverage — are the channel's core jobs each served      │
│                                    │                               │
│  ④ HUMAN APPROVE                   ▼        ← Sin, per combo       │
│                                    │           (revise allowed)    │
│  ⑤ EXPAND  (lumora-content-batch)  ▼                               │
│     combo → concept → hook → caption (voice) → image prompt        │
│           → hashtags → affiliate angle                             │
│     (lumora-art-prompt for the image spec)                         │
│                                    │                               │
│  ⑥ HUMAN APPROVE asset             ▼        ← Sin, second gate     │
│                                    │                               │
│  ⑦ PUBLISH — manual only           ▼                               │
│                                    │                               │
│  ⑧ MEASURE ──▶ post_log row: (C,T,M) + hook_type + funnel          │
│                              + views_24h/7d, saves, follows, gmv   │
│                                    │                               │
│  ⑨ LEARN ──▶ v_post_scores ──▶ weekly rollup ──┐                   │
│              save_rate, follow_rate,           │                   │
│              tail_multiple (7d/24h)            │                   │
└────────────────────────────────────────────────┼───────────────────┘
                                                 │
                     feeds `lift` and `fatigue` ─┘  back into ②
```

---

## 5. What this actually is, formally

**[INF] — this is the interpretation most worth confirming or rejecting.**

The run-time loop is a **multi-armed bandit over a discrete combo space, with human-in-the-loop gating**:

| Bandit concept | Framework element |
|---|---|
| Arms | legal `(C, T, M)` combos for the channel |
| Arm space bounds | account-level constraint set |
| Reward | `save_rate`, `follow_rate`, `tail_multiple`, `gmv` |
| Exploitation | the `lift` term — repeat what performed |
| Exploration | the `fatigue` penalty — forced rotation off over-used arms |
| Contextual signal | `trend` + `season` — the same arm is worth more at some times |
| Prior | `fit` — how well the arm suits this channel before any data |
| Safety layer | the 5 validation gates + two human approvals |

**Why this framing matters practically:**
- It explains why the framework *needs* a log to work at all. With no history, `lift` and `fatigue` are both undefined, so the scorer degenerates to `trend + fit + season` — a reasonable cold-start prior, but not learning. **This is exactly what ADR-0001 means by "the scorer is data-starved by construction."**
- It explains why over-splitting channels is fatal beyond just effort: **splitting divides the sample count per arm.** One channel with 30 posts learns; three channels with 10 posts each learn nothing. That is a stronger argument than "effort ×N" and I think it's the real reason `N=1` is right.
- It sets a rough threshold for when the loop starts producing signal: **[INF]** with 3 pillars × ~4 active themes × ~4 sustainable media ≈ 48 combos, a 30-post sprint samples well under one post per arm. Learning at the combo level is not statistically available yet. **What *is* available at 30 posts is learning at the axis level** — pillar performance, hook_type performance, theme block performance — which is exactly what the weekly rollup queries group by. That looks deliberate.

---

## 6. Where the framework lives, physically, today

**[KB]** Under ADR-0001 there is no code. The framework is realised as:

| Component | Realised as |
|---|---|
| Axis definitions | Markdown in `01_creative_library.md` |
| Account config | Not yet a file — lives in the account-decisions package **[GAP]** |
| Candidate generation + scoring | `lumora-combo-recommend` skill (prompt, not code) |
| Validation | `content-taxonomy` skill (prompt) |
| Expansion | `lumora-content-batch` (+ oracle mode) and `lumora-art-prompt` |
| External signal | `lumora-trend-scan` |
| Approval | Sin, in conversation |
| Log | `lumora_sprint.db` / spreadsheet |
| Learning | the 10-minute weekly ritual, run by hand |

**[INF]** The skill layer is the framework's *implementation*, and the parked backend was going to be a re-implementation of the same logic in code. That is why ADR-0001 could say the backend is "partly redundant" — `lumora-combo-recommend` is a better scorer than the `hash(ext) % len(PILLARS)` in the codebase.

---

## 7. Open gaps I can see

**[GAP] 1 — Account config has no home.** Voice/Archetype, Persona, Niche, active pillars, active themes, sustainable media are needed as *inputs* by two skills, but live in prose across `00-account-decisions.md` and the KB. A single `account.yaml` per channel would make the constraint set explicit and let the skills read one source. This is the smallest artifact with the highest leverage, and it doesn't violate ADR-0001 — it's config, not an adapter.

**[GAP] 2 — Fatigue has no defined window.** The validator says "beyond a set cadence" and the scorer has a `fatigue` term, but no number is written down. Without it, "is this combo over-used" is a judgment call each time and is not reproducible.

**[GAP] 3 — Theme is open-ended but `lift` needs stable labels.** If themes are added freely, the arm space grows and history fragments. **[INF]** Suggested resolution: keep theme *open* for creative purposes but require every new theme to declare a parent cluster, so learning aggregates at cluster level even as leaves multiply.

**[GAP] 4 — The framework claims catalog-agnosticism but has only ever run on one catalog.** That claim is currently a design intention, not an observed property. Worth stating as such until catalog #2 exists.

**[GAP] 5 — `content-taxonomy` SKILL.md still carries two drifts** the canonical corrected: the frontmatter `description` advertises `MIN(S,A)≤N≤S×A`, and HHH appears as Hero/Hub/**Help** instead of **Hygiene**. The description matters more than it looks — it's what an agent reads when deciding whether to invoke the skill.

---

## 8. What I am least sure about

1. Whether the bandit framing in §5 matches how Sin thinks about it, or is Claude over-formalising.
2. Whether `fit` is meant as a static prior from the account config, or something that also learns.
3. Whether the framework is meant to own the **calendar** (sequencing and batching by aesthetic week) or only the per-post choice. The KB mentions "batch by aesthetic, one block per week" as a hard rule, which is a *sequencing constraint over combos* — that arguably belongs inside the framework, but currently reads as a separate content-and-channels rule.
4. Whether Library Framework is meant to cover only content, or eventually any "diverse output at scale" problem — the CLAUDE.md line "solves a *general* problem, not just Lumora's" hints at the latter.
