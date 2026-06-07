# UI Designer — Comprehensive Knowledge

> Deep reference for the ui-designer subagent.
> Senior UI / visual-interface designer — the visual craft of interfaces.
> Scope: layout, visual hierarchy, typography, color, spacing, design systems, component design, states.
> General-purpose; not tied to any one project.

---

## 1. Foundations

### What a UI designer does

Owns the **visual surface** of a product — how every screen looks, reads, and feels at the pixel level. Layout, visual hierarchy, type, color, spacing, the design system, and the full set of component states. The deliverable is a **buildable, consistent, accessible visual language** — not a pretty mockup, but a system a frontend engineer can implement faithfully and extend without asking the designer about every edge case. The UI designer is accountable for **clarity + consistency + craft**: does the screen communicate the right thing first, does it look like one product, and does it hold up under real data and edge cases.

Visual design is **communication, not decoration**. Every visual choice — size, weight, color, position, contrast — is a signal that tells the user what matters, what's clickable, what's grouped, what state they're in. Good UI is mostly invisible: the user gets the job done without noticing the design. Bad UI makes them think about the interface instead of the task.

### UI vs UX vs Frontend vs AI Art Director

| | UX Designer | UI Designer | Frontend Engineer | AI Art Director |
|---|---|---|---|---|
| Domain | Research, flows, usability | **Visual surface of the UI** | Build / code | Generative brand art |
| Core question | *Does it work for the user?* | *Does it look right + read clearly?* | *Does it ship + perform?* | *Is it on-brand at scale?* |
| Output | Flows, wireframes, journeys, findings | High-fidelity screens, design system, tokens | Components, code, tokens-in-code | Images, illustration, motion assets |
| Quality bar | task success, learnability | hierarchy, consistency, contrast, polish | correctness, perf, a11y in code | aesthetic, brand coherence |
| Failure mode | confusing flow, wrong feature | inconsistent, low-contrast, decorative noise | broken / janky / inaccessible build | off-brand slop |

These overlap at the seams (a "product designer" often does UX **and** UI), but the **craft** is distinct. UX decides *what screens exist and why*; UI decides *what they look like*; frontend *makes them real*. The art director makes **brand/illustration content** that lives inside the UI — not the UI itself. UI sits in the middle and hands off in both directions (see §8).

### Visual design as a system, not screens

The senior shift: stop designing screens, start designing the **system that generates screens**. A junior pushes pixels on one mockup; a senior defines tokens, components, and rules so the 200th screen is consistent with the 1st **without** the designer touching it. The screen is an output; the system is the asset. This is the single biggest leverage move in modern UI work and the throughline of this whole document.

### The core building blocks

1. **Tokens** — the atomic decisions (color, spacing, type, radius, elevation) as named variables
2. **Type system** — a scale, weights, line-heights, roles (display/body/caption)
3. **Color system** — semantic roles (surface/text/border/accent), not raw hex
4. **Grid + spacing** — an 8pt rhythm, responsive columns
5. **Components** — reusable, with variants + every state
6. **Patterns** — how components compose (forms, tables, nav, dialogs)
7. **Documentation** — usage rules, do/don't, handoff specs

---

## 2. Mental Models / Decision Frameworks

### Visual hierarchy — the first job

Every screen answers "what do I look at first, second, third?" You control rank with a small set of levers, ordered roughly by strength:

| Lever | Effect | Note |
|---|---|---|
| **Size** | Biggest = most important | Strongest, most obvious lever |
| **Weight** | Bold pulls the eye | Cheaper than size; pairs well with it |
| **Color / contrast** | High-contrast = foreground | Use sparingly — one accent, not five |
| **Position** | Top-left read first (LTR), center = focal | Follows reading order + F/Z pattern |
| **Whitespace** | Isolation = importance | Space *around* an element elevates it |

Rule: establish hierarchy with **size + weight + spacing first**, color last. If everything is bold and colorful, nothing is. De-emphasis is as important as emphasis — secondary text should *recede* (lower contrast, smaller), not compete.

### Gestalt principles — how the eye groups

The brain auto-groups visual elements; design *with* that, not against it.

- **Proximity** — things close together read as related. The #1 tool for grouping: tighten space within a group, widen it between groups. Most "messy" UIs are a proximity failure.
- **Similarity** — same shape/color/size read as the same kind of thing. Use consistently; break it deliberately to signal difference.
- **Common region** — a shared container (card, border, background) groups strongly, even across distance.
- **Continuity / alignment** — the eye follows lines; aligned elements read as ordered. Misalignment reads as broken.
- **Closure** — the mind completes shapes; lets you imply structure without drawing every line.
- **Figure/ground** — clear separation of foreground from background; elevation + contrast establish it.

### Grid + layout systems

- **Columns** — 12-col is the web default (divisible by 2/3/4/6); use a max content width + responsive gutters. Don't let line length exceed ~60-75 characters for body text.
- **Baseline / vertical rhythm** — align type to a consistent vertical grid so blocks feel ordered.
- **Layout pattern by intent** — single-column (focus/forms), sidebar+content (apps/admin), card grid (browse), split (marketing). Pick from intent, not novelty.
- **Optical alignment** > mathematical — icons, punctuation, and round shapes often need nudging to *look* aligned even when the math says they are.

### Typographic scale

Pick a **modular scale** (a ratio applied consistently) instead of arbitrary sizes:

| Ratio | Feel | Use |
|---|---|---|
| 1.125 (Major Second) | Tight, dense | Data-dense apps, dashboards |
| 1.2 (Minor Third) | Balanced | General product UI — safe default |
| 1.25 (Major Third) | Comfortable | Content / marketing |
| 1.333+ (Perfect Fourth) | Dramatic | Editorial, big display contrast |

Rules: **2 typefaces max** (often one is enough); use weight + size for variety, not new fonts. Line-height ~1.4-1.6 for body, tighter (~1.1-1.25) for headings. Define **roles** (display, h1-h3, body, label, caption) as tokens, not one-off sizes.

### Color theory + contrast

- **Semantic, not raw** — design in roles (`surface`, `text-primary`, `text-muted`, `border`, `accent`, `danger`, `success`), map roles → values. Never scatter raw hex in components.
- **Build ramps** — each hue as a 10-12 step scale (50→950); pick steps for surface/border/text/hover by **role**, so light/dark just remap the same roles.
- **60-30-10** — ~60% dominant/neutral, 30% secondary, 10% accent. UIs are mostly neutral; color is a spotlight.
- **Contrast is non-negotiable** — body text ≥ **4.5:1**, large text/UI components ≥ **3:1** (WCAG 2.2 AA). Never rely on color alone to convey meaning (add icon/label/shape) for color-blind users.

### Spacing + rhythm (the 8pt grid)

Use a **base-8 spacing scale** (4, 8, 12, 16, 24, 32, 48, 64…) for all margins, padding, gaps. Why: aligns to common screen densities, scales cleanly, and removes the "is it 13 or 15px?" bikeshedding. Use a 4pt half-step for tight icon/text gaps. **Consistent spacing is the #1 signal of a designed-vs-amateur UI** — more than color or type. Inconsistent gaps read as broken even when nothing else is wrong.

### Affordance + signifiers

- **Affordance** = what an element *can* do; **signifier** = the visual cue that *tells* the user it can. A button affords clicking; its raised/filled/colored look is the signifier.
- Make interactive things **look** interactive (consistent button/link styling) and non-interactive things not. The cardinal sin is fake affordance (text styled like a button that isn't) or hidden affordance (clickable things with no signifier — "mystery meat").
- **Consistency is itself a signifier** — once "blue underlined = link" is learned, every blue underline must be a link.

### Consistency vs novelty

Default to **consistency** — reuse patterns the user (and the rest of the product) already knows; novelty has a learning-cost the user pays. Spend novelty budget only where it earns its keep (a signature moment, a differentiating interaction), never on core controls. "Creative" date pickers, custom scrollbars, and reinvented dropdowns are almost always a net loss. **Boring where it counts, delightful where it's safe.**

---

## 3. Standard Practices

### Design systems — tokens, components, variants

The backbone of professional UI. Three layers:

```
Tokens         — primitive (color.blue.500) + semantic (color.action.bg)
   ↓
Components     — Button, Input, Card… built from semantic tokens
   ↓
Patterns       — Form, Table, Dialog, Page templates from components
```

- **Token tiers** — primitive (raw scale values) → semantic/alias (role-based, e.g. `text.muted`) → component-level (optional, e.g. `button.primary.bg`). Components consume **semantic** tokens so a theme swap (light/dark, brand A/B) is a token remap, not a component rewrite.
- **Variants** — one component, many configurations (type, size, state) via component properties. Don't make 12 separate "Button" components; make one with variant props.
- **Naming** — consistent, predictable, role-based. `color.text.primary` not `darkGray2`. The token name should survive a redesign.

### Component states — design every one

The #1 thing juniors skip. Every interactive component needs the full set:

| State | Don't forget |
|---|---|
| **Default / rest** | The baseline |
| **Hover** | Desktop affordance cue |
| **Focus** | Visible focus ring — **keyboard a11y, mandatory** |
| **Active / pressed** | Tactile feedback |
| **Disabled** | Lower contrast but still legible; explain *why* if possible |
| **Loading** | Spinner/skeleton; prevent double-submit |
| **Selected / checked** | For toggles, tabs, list items |
| **Error / invalid** | Color + icon + message, not color alone |

And for **screens/containers**, design the full lifecycle:

| State | Why it matters |
|---|---|
| **Empty** | First-run + zero-data; guide the next action, don't show a blank void |
| **Loading** | Skeletons > spinners for perceived speed |
| **Error** | What broke + how to recover |
| **Partial / few items** | Looks different from "full"; design it |
| **Ideal / full** | The happy path everyone designs |
| **Overflow / too much** | Long names, huge numbers, 500 rows — truncation, wrapping, pagination |

A design isn't done until empty, loading, and error are designed. Demoing only the happy path is the most common review failure.

### Responsive layout

- **Mobile-first** for content/consumer; **desktop-first** is fine for data-dense internal tools (their primary use is desktop).
- Design at real breakpoints (e.g. 360 / 768 / 1024 / 1440), but think **fluid** — define behavior between breakpoints, not just at them.
- **Reflow, don't shrink** — columns stack, nav collapses, tables become cards/scroll; never just scale everything down.
- Respect **touch targets** ≥ 44×44px on touch; denser is OK on pointer devices.

### Design handoff (specs / redlines)

- In 2025-2026, handoff is mostly **Figma Dev Mode** + tokens/variables — engineers inspect spacing, type, color as **named tokens/code**, not eyeballed pixels. Code Connect maps a component to its real code snippet.
- Annotate intent the inspector can't show: **why** this spacing, what's responsive, interaction/motion, edge cases, which states exist.
- Hand off **tokens**, not screenshots of colors. If design tokens and code tokens share a source, handoff is a non-event — the engineer reads the same names you used.

### Design QA

After build, the designer reviews the implementation against the design: spacing, type, color, states, responsive behavior, focus rings, motion. Maintain a checklist; file pixel/state bugs like any other. **The design isn't shipped until it's QA'd in the real product** — Figma lies (real fonts, real data, real browsers differ).

### Dark mode

Don't invert. Design it as a **second set of token values** mapped to the same semantic roles:
- Dark surfaces are rarely pure black — use very dark gray (#0E0E11-ish) to reduce halation and allow elevation.
- **Elevation by lightness** in dark mode (lighter = higher), not just shadow (shadows barely read on dark).
- Desaturate + adjust accent colors — bright saturated colors vibrate on dark backgrounds.
- Re-check contrast in **both** themes; a ramp that passes in light can fail in dark.

### Brand → UI translation

Translate brand (logo, brand palette, voice) into a **functional UI system**: brand colors rarely map 1:1 to UI roles (a vivid brand red may be too loud for every button — reserve it as accent, build neutral ramps around it). Derive a usable palette, type pairing, radius/elevation personality, and motion feel **from** the brand without letting brand assets dictate unusable UI. Brand sets the personality; usability sets the constraints.

---

## 4. Tools Landscape (2026)

> Fast-moving. Confirmed mid-2026; re-verify before standardizing a team on anything.

### Design + prototyping
- **Figma** — the default. **Variables** (modes for theme/density/brand), **Dev Mode** (inspect as tokens/code, Code Connect), components + variants, auto-layout. The center of gravity for product UI. *Expression/conditional variables* rolling out late-2025/2026 for dynamic, context-driven theming.
- **Figma First Draft / Figma Make** — AI prompt-to-UI. First Draft = fast wireframe/first-pass generator (now folding into Figma's **agent**, the new entry point as of mid-2026); Figma Make generates interactive prototypes from natural language. Treat as a **junior roughing in a layout** — a starting point you refine, not a finisher.
- **Penpot** — open-source, self-hostable, design-tokens-native; strong choice when you want tokens + open standards without Figma lock-in.
- **Framer** — design + publish real sites; good for marketing/landing with interaction.
- **Sketch** — still around (Mac), largely superseded by Figma for teams.

### Design-system tooling
- **Figma Variables** — native tokens for color/number/string/boolean with modes; the first stop before reaching for a plugin.
- **Tokens Studio** (Figma plugin) — advanced token management: math, aliasing, themes, and export to the **W3C DTCG** format. The serious choice for multi-brand/multi-theme token systems.
- **W3C DTCG Design Tokens spec** — reached its **first stable version (2025.10)** in Oct 2025; a vendor-neutral JSON format now supported across Figma, Penpot, Sketch, Framer, Supernova, zeroheight, etc. Design tokens to this spec for portability.
- **Style Dictionary** — transforms DTCG tokens → CSS vars / iOS / Android / JS. The standard token build pipeline (design → code).
- **Storybook** — the component-library workbench on the **code** side; renders every component + state, the living source of truth engineers and designers QA against.
- **Supernova / zeroheight / Knapsack** — design-system documentation + token-sync platforms (design ↔ code ↔ docs).

### AI design assists
- **Figma agent / First Draft / Make** — in-tool generation (above).
- **UX Pilot, Builder.io (Visual Copilot), v0 (Vercel)** — prompt/figma → UI or → code. v0 and Builder lean **design-to-code**; useful for quick functional prototypes and bootstrapping internal tools, weak on bespoke craft + brand nuance.
- Reality check (2026): AI gets you a **fast first draft / wireframe**; the system, hierarchy, states, and polish are still the designer's job. It compresses the boring 60%, not the craft 40%.

### Handoff / inspection
- **Figma Dev Mode + Code Connect** — the default handoff; inspect as tokens, get real code snippets linked to the codebase.
- **Storybook** — engineers verify the built component against design.
- **Token pipeline** (Tokens Studio → DTCG → Style Dictionary → code) — the gold-standard "design tokens *are* code tokens" setup; makes redlining largely obsolete.

### Accessibility checking
- **Stark / Able / Contrast** (Figma plugins) — in-canvas contrast + color-blind checks.
- **WebAIM Contrast Checker**, **Polypane**, browser a11y devtools — verify in the real build.

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| **Inconsistent spacing** | Ad-hoc 13/17/21px gaps read as broken | One 8pt scale, applied everywhere via tokens |
| **Too many fonts / weights** | Visual noise, no hierarchy, slow load | ≤2 typefaces; vary size + weight, not family |
| **Too many colors / accents** | Nothing stands out, looks amateur | Neutral-dominant, one accent; 60-30-10 |
| **Low contrast** | Illegible, fails WCAG, excludes users | ≥4.5:1 body, ≥3:1 large/UI; check both themes |
| **Decoration over clarity** | Gradients/shadows/animation that hide the message | Earn every visual; clarity first, delight second |
| **No empty / error / loading states** | Breaks on real data, blank voids, mystery failures | Design the full lifecycle, not just happy path |
| **Pixel-pushing without a system** | Per-screen tweaks, drift, unmaintainable | Tokens + components; fix it once, everywhere |
| **Mystery-meat navigation** | Icon-only / hidden affordances, users guess | Label interactive things; visible signifiers |
| **Fake / inconsistent affordance** | Non-buttons look clickable (or vice versa) | One consistent button/link language |
| **Color-only meaning** | Excludes color-blind users (status by hue alone) | Color **+** icon/label/shape |
| **No visible focus state** | Keyboard users lost, fails a11y | Always design + keep a focus ring |
| **Center-aligning everything / body text** | Ragged left edge kills scannability | Left-align body; reserve center for short/hero |
| **Truncation ignored** | Long names/numbers/i18n explode the layout | Design overflow: truncate, wrap, max-width |
| **Designing only at one breakpoint** | Mid-sizes break in the real browser | Define fluid behavior between breakpoints |

---

## 6. Advanced / Expert Topics

### Scalable design systems — multi-brand theming via tokens

The payoff of the token discipline. With a **3-tier token model** (primitive → semantic → component), a multi-brand or white-label product themes by swapping **one layer**:

```
Primitive   brand-a.blue.500=#2563EB   brand-b.green.500=#16A34A
   ↓ (alias)
Semantic    color.action.bg  → brand's accent.500    (same role name)
   ↓
Component   Button reads color.action.bg              (untouched per brand)
```

- Components **never** reference primitives — only semantic roles. A new brand = a new value map for the semantic layer, zero component edits.
- **Modes** (Figma variables) handle the axes: theme (light/dark), brand (A/B/C), density (compact/comfortable) as independent mode dimensions on the same components.
- This is what lets a 5-brand portfolio ship from one system. Get the **semantic layer naming** right early — it's the expensive thing to change later.

### Accessibility in visual design

Visual a11y is the UI designer's direct responsibility (not "the engineer's problem"):
- **Contrast** — ≥4.5:1 body, ≥3:1 large text + UI components/icons/borders (WCAG 2.2 AA). AAA (7:1) for critical/long-form. APCA (Lc-based, WCAG 3.0) is more perceptually accurate but **not yet the legal standard** — design to 2.2 ratios, watch APCA.
- **Don't encode meaning in color alone** — pair status with icon/text/pattern.
- **Visible focus** — a clear, high-contrast focus ring on every interactive element; never remove it without replacing it.
- **Target size** — ≥24×24 (WCAG 2.2 SC 2.5.8 AA), ≥44×44 recommended for touch.
- **Text** — respect user font-size/zoom (use relative units in the spec'd system); don't lock tiny fixed sizes.
- **Motion** — honor `prefers-reduced-motion`; never gate meaning behind animation.

### Motion + micro-interactions

Motion is **functional**, not garnish:
- **Purpose** — feedback (button press), continuity (shared-element transition), orientation (where a panel came from), status (loading/progress).
- **Timing** — fast (~100-200ms) for direct feedback, ~200-300ms for transitions; slower feels laggy. Ease-out for entering, ease-in for exiting.
- **Restraint** — micro-interactions reward + reassure; gratuitous animation annoys on the 50th view. If it doesn't communicate, cut it. Always provide a reduced-motion path.

### Data-dense UI (dashboards, tables)

Where most "pretty UI" instincts are *wrong* — density + scannability beat whitespace + flourish:
- **Tables** — right-align numbers, left-align text, consistent decimals, tabular/monospaced figures so digits align. Zebra/row-hover sparingly; strong column alignment does more than borders.
- **Density modes** — offer compact for power users; a 1.125 type scale + tighter (4pt) spacing.
- **Hierarchy under density** — use weight + subtle color, not size (no room); muted secondary data, strong primary.
- **Charts** — minimal chrome (kill gridline/axis clutter), label directly over legends where possible, accessible categorical palettes, never color-only encoding.
- **Progressive disclosure** — summary first, detail on demand (expand/drawer); don't show everything at once.

### Internal-tool / developer-tool UI (config-heavy admin)

A distinct discipline — **clarity and speed over polish**:
- The user is an expert doing repetitive work; optimize for **throughput + scannability**, not first-impression delight. Density > whitespace; keyboard > mouse.
- **Forms + config** dominate: clear labels (not just placeholders), sensible grouping, inline validation, obvious required/optional, defaults that work, and **don't hide destructive/irreversible actions**.
- Make **state + system feedback** explicit — what's running, what failed, what changed, what's saved. Engineers tolerate ugly; they do not tolerate ambiguity about system state.
- Reuse a boring, consistent component kit; **don't reinvent controls**. Novelty here is pure cost. A clear table + a reliable form beats any visual flourish.
- This is where over-design actively *hurts*: big hero spacing, animation, and decorative color slow down the power user. Tighten up.

### Design-to-code with tokens

The senior end-state: **design tokens and code tokens are the same source.**
```
Figma Variables / Tokens Studio
   ↓ export (W3C DTCG JSON)
Style Dictionary  →  CSS vars / Tailwind / iOS / Android
   ↓
Components (Storybook) consume the same named tokens
   ↓
Figma Dev Mode + Code Connect ties design component ↔ code component
```
When this loop is closed, "handoff" mostly disappears — the engineer reads the exact names the designer used, themes/dark-mode are a token swap on both sides, and visual drift between design and product collapses. Driving a team toward this pipeline is the highest-leverage thing a senior UI designer does.

---

## 7. References

### Foundational
- **Refactoring UI** (Wathan & Schoger) — https://www.refactoringui.com/ — the single best practical book on UI craft (hierarchy, spacing, color, depth).
- **Laws of UX** (Gestalt, Hick, Fitts, Jakob…) — https://lawsofux.com/
- **Material Design 3** — https://m3.material.io/ — Google's system; tokens, components, motion, theming reference.
- **Shopify Polaris** — https://polaris.shopify.com/ — admin/commerce patterns, exemplary content + component docs.
- **IBM Carbon** — https://carbondesignsystem.com/ — data-dense / enterprise patterns, tokens, grids.
- **Atlassian / Primer (GitHub) / Base (Uber)** — https://atlassian.design/ , https://primer.style/ — more system references, dev-tool flavored.

### Tokens + handoff
- **W3C Design Tokens spec (DTCG)** — https://www.w3.org/community/design-tokens/ (stable 2025.10) — https://tr.designtokens.org/format/
- **Tokens Studio** — https://tokens.studio/ , docs https://docs.tokens.studio/
- **Style Dictionary** — https://styledictionary.com/
- **Figma Variables / Dev Mode** — https://help.figma.com/hc/en-us/articles/15339657135383 , https://www.figma.com/dev-mode/
- **Storybook** — https://storybook.js.org/

### Accessibility
- **WCAG 2.2** — https://www.w3.org/TR/WCAG22/ (contrast SC 1.4.3 / 1.4.11, focus, target size)
- **WebAIM Contrast Checker** — https://webaim.org/resources/contrastchecker/ ; Contrast & color — https://webaim.org/articles/contrast/
- **APCA (WCAG 3 contrast)** — https://git.apcacontrast.com/ (watch, not yet legal standard)
- **Stark** — https://www.getstark.co/ (Figma a11y plugin)

### Type + color
- **Type Scale** — https://typescale.com/ ; **Modularscale** — https://www.modularscale.com/
- **Practical Typography** (Butterick) — https://practicaltypography.com/
- **Coolors / Leonardo (Adobe)** — https://coolors.co/ , https://leonardocolor.io/ (accessible color ramps)
- **Realtime Colors** — https://www.realtimecolors.com/ (preview palettes on real UI)

### Communities / inspiration
- **Mobbin** (real-product UI patterns), **Dribbble**/**Behance** (inspiration — vet for realism), **Designsystems.com**, **Design Systems Collective**, **r/UI_Design**, **Component Gallery** (https://component.gallery/).

---

## 8. Working With Other Roles

| Role | Handoff |
|---|---|
| **UX Designer** | Receives **flows + wireframes + research** (what screens exist, the task, the constraints). UI designer raises them to high fidelity — hierarchy, type, color, states. Push back early if a flow can't be made visually clear; loop UX in on findability + content order. |
| **Frontend Engineer** | The core handoff: **visuals → code via tokens**. Deliver components + every state + a token system through Figma Dev Mode / Code Connect / DTCG export, not screenshots. Co-own the token pipeline (Style Dictionary, Storybook) so design tokens *are* code tokens. Do **design QA** on the built result. |
| **AI Art Director** | Receives **illustration, brand imagery, icons, hero/empty-state art, motion assets** to drop into the UI. UI designer specs the slot (size, ratio, safe area, palette to match the system); art director produces on-brand content. They keep the *UI* and the *art inside it* coherent. |
| **Product / Business** | Translates product goals + brand into a visual system; negotiates scope (what states/breakpoints/themes ship), defends consistency + a11y against one-off "make it pop" requests, and explains the cost of novelty vs the leverage of the system. |

---

*UI design in 2026 = clarity first, a token-driven system second, polish third. The screen is an output; the design system — tokens, components, states, accessibility — is the asset. Visual craft is communication, and consistency is the loudest signal that something was designed.*
