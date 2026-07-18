# Frontend Engineer — Comprehensive Knowledge

> Deep reference for the frontend-engineer subagent.
> Turning UI/UX designs into production web front-end (React/Next, TypeScript).
> General-purpose — not tied to one project.

---

## 1. Foundations

### What a frontend engineer does

Owns the layer the user actually touches: markup, styling, interaction, client-side state, data fetching, and the build that ships it. The job is **translating a design + a flow + an API contract into accessible, fast, maintainable UI** — and being accountable for how it behaves on a real device, on a slow network, with a screen reader.

### Three roles, three concerns

| Role | Owns | Output |
|---|---|---|
| **UX designer** | Flows, IA, interaction logic, usability | Wireframes, prototypes, flow specs |
| **UI designer** | Visual language, layout, tokens, components | Figma, design tokens, component specs |
| **Frontend engineer** | Production code of the UI | React/TS components, build, tests |
| **Software engineer** (backend/general) | APIs, data, services, business logic | Endpoints, contracts, BFF |

The frontend engineer is the **bridge**: consumes design from UI/UX, consumes contracts from backend, produces the running product. Distinct from software-engineer (you live in the browser, not the server) and from designers (you ship code, not mockups). When the line blurs — a BFF, a config-driven form renderer — you collaborate, you don't absorb the other role.

### The browser is the platform

You don't control the runtime. The user does. Assume:
- **Variable hardware** — a mid-tier Android is ~6× slower than your MacBook.
- **Variable network** — 3G, flaky wifi, high latency. Test with throttling.
- **Variable input** — mouse, touch, keyboard, screen reader, voice.
- **No install step** — the bundle *is* the cold start. Every KB of JS is parse + compile + execute on the main thread.

### The rendering pipeline (know it cold)

```
HTML → DOM
CSS  → CSSOM
        ↓
     Render tree
        ↓
     Layout (geometry / reflow)
        ↓
     Paint (pixels)
        ↓
     Composite (GPU layers)
```

- **Layout/reflow** is expensive — triggered by reading `offsetHeight`, changing geometry. Batch DOM reads/writes.
- **Paint** — color, shadow, background changes.
- **Composite** — `transform` and `opacity` only. Animate these; they skip layout+paint and run on the GPU/compositor thread.
- The **main thread** runs JS *and* layout/paint. Long tasks (>50ms) block input → bad INP. Yield often.

---

## 2. Mental Models / Decision Frameworks

### Component composition

Build UI from small, single-purpose components. Compose with **children/slots**, not config flags.

```
Bad:   <Card title hasFooter footerText showImage imageUrl variant="x" />
Good:  <Card>
         <Card.Header>…</Card.Header>
         <Card.Body>…</Card.Body>
         <Card.Footer>…</Card.Footer>
       </Card>
```

Rule: if a component has >5 boolean props, it's two components wearing a trench coat. Prefer composition + slots over a prop matrix you can't test.

### State colocation — the most important frontend decision

State lives in **four** different places. Putting it in the wrong one is the root cause of most frontend complexity.

| Kind | Source of truth | Tool | Example |
|---|---|---|---|
| **Server state** | The backend | TanStack Query / RSC | user list, product, orders |
| **URL state** | The address bar | router search params | filters, tab, page, sort |
| **Client/UI state** | The browser session | useState / Zustand / Jotai | modal open, form draft, theme |
| **Form state** | The form, transiently | React Hook Form | field values, validation |

**Default order:** URL → server cache → local component → global store. Promote *up* only when sharing demands it. The #1 mistake is copying server data into `useState` — see anti-patterns.

### Rendering strategies

| Strategy | When renders | Use for | Trade-off |
|---|---|---|---|
| **CSR** | In browser | Highly interactive apps behind auth (dashboards) | Slow first paint, bad SEO, big JS |
| **SSR** | Per request, server | Personalized + needs SEO | Server cost, TTFB |
| **SSG** | At build | Marketing, docs, blogs | Stale until rebuild |
| **ISR** | Build + revalidate | SSG content that changes | Cache complexity |
| **RSC** | Server, streamed, **zero client JS** | Default in Next App Router | New mental model, caching is hard |

**2026 default (Next App Router):** Server Components by default; add `"use client"` only at the leaves that need interactivity/state/effects/browser APIs. Push the client boundary *down* the tree. Next 16's Cache Components (PPR + `use cache`) blends static shell + streamed dynamic.

### Data fetching patterns & the network waterfall

The enemy is the **request waterfall** — request B can't start until A finishes because B needs A's data, or because the component that fires B doesn't render until A's component does.

- **Server-side (RSC):** fetch in the server component; parallelize independent fetches with `Promise.all`. No client round-trip.
- **Client-side:** TanStack Query — cache, dedupe, background refetch, stale-while-revalidate. Prefetch on hover/intent.
- **Kill waterfalls:** hoist fetches, use route loaders (TanStack Router / Next), parallel routes, and `<Suspense>` to stream independent chunks instead of blocking on the slowest.

### Accessibility-first (not a11y-later)

Build it in from the first commit — retrofitting is 10× the cost. Cheap habits that prevent most issues:
- Semantic HTML first (`<button>`, `<nav>`, `<main>`, `<label>`) — ARIA is a patch, not a default.
- Every interactive element is keyboard-reachable and has a visible focus ring.
- Images have `alt`; icon-only buttons have `aria-label`.
- Color is never the *only* signal; contrast ≥ 4.5:1 for text.

### Performance budget

Set numbers before you build, fail CI when exceeded:
- **JS bundle:** budget per route (e.g. < 170KB gzipped initial).
- **Core Web Vitals (p75 of real users):** LCP < 2.5s, **INP < 200ms**, CLS < 0.1.
- **Lighthouse / bundle-size checks in CI** — a budget no one enforces is a wish.

### Progressive enhancement

Core content + actions should work with HTML + minimal JS; richer interaction layers on top. Server-render the meaningful markup, hydrate to enhance. Especially relevant with RSC/forms — a form that posts works before JS loads.

---

## 3. Standard Practices

### React / Next patterns

- **Server Components by default**, `"use client"` at interactive leaves only.
- **Composition over config**; lift state only as far as the lowest common parent.
- **Keys** on lists must be stable IDs, never array index (breaks reconciliation + state).
- **Derive, don't sync** — compute from props/state during render instead of mirroring into `useState` + `useEffect`.
- **Server Actions / route handlers** for mutations; revalidate the cache after.
- Custom hooks to extract reusable logic — name `useX`, return a stable shape.

### TypeScript discipline

- `strict: true`. No `any` in props/public APIs — use `unknown` + narrow.
- Type **props explicitly**; discriminated unions for variant components.
- Type the **API boundary** — generate types from OpenAPI/GraphQL or validate with **Zod** and infer (`z.infer`). Runtime validation at the network edge, types everywhere inside.
- Prefer `type` for unions/props, `interface` for extendable object contracts. Avoid enums; use union literals.

### Design-system implementation (tokens → components)

```
Design tokens (JSON / CSS vars)   ← from UI designer
   ↓  (color, space, radius, type, shadow, motion)
Primitives / headless behavior    ← Radix / React Aria
   ↓
Styled components (Tailwind / CSS) ← shadcn/ui pattern: you own the code
   ↓
App components + patterns
```

- Tokens as **CSS custom properties** → theming + dark mode + multi-brand for free.
- **shadcn/ui model:** copy components into your repo, own + modify them — not a black-box dependency.
- **Headless (Radix/React Aria)** gives you accessible behavior (focus, ARIA, keyboard); you bring the styling.
- Document in **Storybook** — every component + its states.

### Forms + validation

- **React Hook Form** (uncontrolled, minimal re-renders) + **Zod** schema (`zodResolver`).
- Validate on **blur/submit**, not every keystroke; show errors after first interaction.
- One schema = client validation + (reused) server validation + inferred TS types.
- Always: labels tied to inputs, `aria-invalid` + `aria-describedby` for errors, disabled+pending submit state.

### Error / loading / empty states — the "other 90%"

Every async surface needs **four** states; juniors ship only the happy one:
- **Loading** — skeletons (reserve layout to avoid CLS), not spinners-everywhere.
- **Empty** — guidance + a call to action, not a blank screen.
- **Error** — recoverable message + retry; **Error Boundaries** for render-time crashes.
- **Success** — the actual content.

### Testing

| Layer | Tool | Tests what |
|---|---|---|
| Unit / component | **Vitest + Testing Library** | behavior via the DOM, "user-visible" |
| Visual / docs | **Storybook** (+ play, a11y addon) | states, interactions, a11y |
| E2E | **Playwright** | critical user journeys, real browser |

- Test behavior, not implementation. Query by **role/label/text**, never by class or test-id-everything. `getByRole` doubles as an a11y check.
- E2E only for critical happy paths (login, checkout) — they're slow + flaky.

### Code-splitting

- Route-level splitting is automatic in Next/TanStack Router. Add `React.lazy` / `dynamic()` for heavy below-the-fold or modal-only chunks (charts, editors, maps).
- Don't over-split — too many tiny chunks = request overhead. Split at meaningful boundaries.

### Responsive + mobile-first

- Design from the small breakpoint up; add complexity at larger widths.
- Modern CSS: **container queries** (component responds to its container, not viewport), `clamp()` for fluid type/space, CSS Grid for layout, logical properties for i18n.
- Test touch targets ≥ 44px; real-device test, not just devtools.

### i18n

- Externalize all strings (`next-intl` / `react-i18next`); never concatenate translated fragments.
- Handle plurals (ICU MessageFormat), date/number formatting (`Intl`), RTL (logical CSS properties + `dir`).
- Don't hardcode layout widths — translated strings expand ~30%.

---

## 4. Tools Landscape (2026)

### Framework + runtime
- **React 19** — stable in both Next routers; Actions, `use()`, `useOptimistic`, `useFormStatus`, ref-as-prop, the React Compiler reducing manual memoization.
- **Next.js 16** — App Router default; RSC + streaming; **Cache Components** (PPR + `use cache`), stable `after()`. Production-ready in 2026 but adds real architectural complexity — caching/debugging RSC is the hard part.
- **TanStack Start** — full-stack React on TanStack Router; a more-control alternative to Next when you want explicit routing/data loading without the RSC caching model.

### Routing + data
- **TanStack Router** — type-safe routes, search-param schemas, built-in loaders/caching. Best-in-class TS routing.
- **TanStack Query** — server-state caching, dedupe, background refetch, mutations. The default for client data fetching.

### Styling + components
- **Tailwind CSS** — utility-first; the de-facto styling layer.
- **shadcn/ui** — copy-in components on Radix + Tailwind; you own the code.
- **Radix UI / React Aria** — headless, accessible primitives.

### State
- **Zustand** — minimal global store, no boilerplate. Default for app/UI state.
- **Jotai** — atomic/composable state; `jotai-tanstack-query` bridges server state.
- Redux Toolkit only for large, complex, time-travel-debugging needs — increasingly niche.

### Build + tooling
- **Vite 8** — dev server + build (production via **Rolldown**, Rust). Default for non-Next apps.
- **Turbopack** — Rust bundler powering Next dev (and stabilizing for prod builds).
- **Bun** — runtime + package manager + test runner; in 2026 commonly **Bun for installs/scripts + Vite for the app**, not a full replacement.
- **Storybook** (Vite builder) — component workshop, docs, a11y/interaction testing.

### Quality
- **ESLint** (flat config) + **Prettier** / **Biome** (fast all-in-one alt).
- **TypeScript** strict, **Zod** for runtime boundaries.
- **Lighthouse CI** + bundle-size budgets in the pipeline.

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| **Server data in `useState`** | Stale, manual sync, refetch chaos | TanStack Query / RSC owns server state |
| **`useEffect` for everything** | Fetch-in-effect waterfalls, double-fetch, sync bugs | Derive in render; fetch in loaders/RSC/Query |
| **Prop drilling 5+ levels** | Brittle, noisy | Composition, context, or a store at the right level |
| **Giant 500-line components** | Untestable, unreadable | Split by responsibility; extract hooks |
| **Array index as key** | Wrong reconciliation, lost state | Stable unique ID |
| **No a11y** (div-as-button, no labels) | Excludes users, legal risk | Semantic HTML, roles, focus, labels |
| **Layout shift (CLS)** | Janky, mis-clicks | Reserve space: dimensions, skeletons, `aspect-ratio` |
| **Unmemoized heavy renders** | Jank, bad INP | React Compiler / memo + virtualization for big lists |
| **`any`-typed props** | Type safety theater | Explicit prop types, Zod at boundaries |
| **Fetch waterfalls** | Slow, sequential | Parallelize, hoist, route loaders, Suspense streaming |
| **Only the happy path** | Blank/broken on load/error/empty | Handle all four async states |
| **Inline styles / magic px** | No theming, inconsistent | Design tokens / CSS vars / Tailwind scale |
| **Animating `top`/`width`/`height`** | Reflow jank | Animate `transform`/`opacity` (compositor) |
| **Hydration mismatch** (Date.now, `window` in render) | Errors, flicker | Stable SSR output; gate browser APIs in effects |

---

## 6. Advanced / Expert Topics

### RSC + streaming

- **Server Components** render on the server, ship **zero JS** for themselves, and can `await` data directly. They serialize a tree (not HTML) the client merges.
- **The boundary discipline:** `"use client"` is a one-way door — everything imported below becomes client. Keep it at leaves; pass server-fetched data *down* as props, pass interactivity *up* via client wrappers.
- **Streaming + Suspense:** send the shell immediately, stream slow segments as they resolve. Improves perceived LCP and lets independent data render independently.
- **Hard parts:** caching semantics (request memoization vs data cache vs full-route cache vs Cache Components), serialization limits (no functions/classes across the boundary), and debugging "why is this dynamic?".

### Core Web Vitals optimization

- **LCP < 2.5s** — find the LCP element (usually hero image/heading). Preload it, serve modern formats (AVIF/WebP) with explicit dimensions, `fetchpriority="high"`, cut render-blocking CSS/JS, fast TTFB (SSG/edge/cache).
- **INP < 200ms** (the metric most sites fail in 2026) — interaction responsiveness. Break up long tasks, `yield` to the main thread, debounce expensive handlers, move heavy work to a Web Worker, ship less JS, avoid synchronous layout reads in handlers.
- **CLS < 0.1** — reserve space for images/ads/embeds (`width`/`height` or `aspect-ratio`), never inject content above existing content, use `font-display: optional/swap` + size-adjust to avoid layout-shifting font swaps.
- Measure **real users** (web-vitals lib → analytics), not just lab Lighthouse. Google scores p75 of field data.

### Accessibility depth

- **ARIA rule #1:** don't use ARIA if native HTML works. A `<button>` beats `<div role="button" tabindex aria-pressed>`.
- **Focus management:** on route change move focus to the heading; in modals trap focus, return it to the trigger on close, close on Esc. `inert` for background.
- **Live regions:** `aria-live="polite"` for async status (saved, error) so screen readers announce.
- **Screen readers:** test with VoiceOver (macOS/iOS) and NVDA (Windows). The DOM order = reading order — don't reorder with CSS.
- **Keyboard:** every action reachable + operable by keyboard; visible focus indicators; logical tab order; roving tabindex for composite widgets.
- Target **WCAG 2.2 AA**.

### Design-system architecture

- **Headless behavior + tokens + styling** as separate layers. Behavior from Radix/React Aria, tokens as CSS variables, styling per brand.
- **Theming / multi-brand:** semantic tokens (`--color-surface`, `--color-text-primary`) mapped to primitive tokens per brand/theme. Swap the variable set, not the components. Dark mode = one more token map.
- **Token pipeline:** Figma → Style Dictionary / Tokens Studio → CSS vars + TS types, so design and code share one source.
- Version + changelog the system; treat it as a product with its own consumers.

### Micro-frontends — when / when-not

- **When:** multiple autonomous teams, independent deploy cadence, a large org where one app/team can't scale. Module Federation, route-level splits.
- **When NOT (usually):** one team, one product. The cost — duplicated deps, version skew, shared-state pain, cross-app a11y/perf inconsistency — outweighs the benefit. Most "we need micro-frontends" is really "we need better module boundaries." Reach for a monorepo + clear package boundaries first.

### Offline / PWA

- Service worker for caching/offline; **Workbox** for strategy (cache-first for assets, network-first for data).
- Web App Manifest for installability; background sync for deferred mutations; IndexedDB for offline data.
- Worth it for field/mobile/flaky-network use cases; skip for simple sites.

### Config-driven / internal-tool UIs (platform + admin tools)

Highly relevant for platform/admin/data-tooling work — render UI **from schema** instead of hand-coding each screen.

- **Schema-driven forms:** a JSON Schema / Zod schema drives field rendering, validation, and layout (RJSF-style or a custom renderer). One renderer, N forms — admin panels, settings, pipeline configs.
- **Config-driven dashboards/tables:** column defs, filters, and actions described as data; a generic table/dashboard component renders them (TanStack Table is the workhorse).
- **Why it matters:** internal tools are high-volume, low-bespoke. A schema renderer turns "build 40 CRUD screens" into "define 40 schemas." Backend/platform owns the schema; frontend owns the renderer + escape hatches.
- **The trap:** over-generalizing. Keep an escape hatch (custom field/widget overrides) for the 10% that don't fit the schema — don't bend the whole renderer to model one weird screen.

### Edge rendering

- Run SSR/handlers at the edge (**Cloudflare Workers/Pages**, Vercel Edge) — close to users, low TTFB, great for personalization + geolocation + auth gating.
- Constraints: a lighter runtime (no full Node APIs), CPU/time limits, cold-start nuances. Keep edge handlers lean; push heavy compute to origin/queues.
- Pair with SSG/ISR: static shell from cache, dynamic bits at the edge.

---

## 7. References

### Official docs
- **React** — https://react.dev (esp. "You Might Not Need an Effect", "Thinking in React")
- **Next.js** — https://nextjs.org/docs/app (App Router, RSC, caching)
- **TanStack** — https://tanstack.com/query, https://tanstack.com/router
- **MDN Web Docs** — https://developer.mozilla.org (the canonical web platform reference)

### Performance
- **web.dev — Core Web Vitals** — https://web.dev/articles/vitals
- **CWV thresholds** — https://web.dev/articles/defining-core-web-vitals-thresholds (LCP 2.5s / INP 200ms / CLS 0.1, p75)
- **Optimize INP** — https://web.dev/articles/optimize-inp

### Accessibility
- **WCAG 2.2** — https://www.w3.org/TR/WCAG22/
- **ARIA Authoring Practices (APG)** — https://www.w3.org/WAI/ARIA/apg/
- **MDN Accessibility** — https://developer.mozilla.org/en-US/docs/Web/Accessibility

### Learning / opinion
- **Kent C. Dodds** — https://kentcdodds.com (Testing Library philosophy, state colocation, Epic React)
- **Josh Comeau** — https://www.joshwcomeau.com (CSS, animation, React internals — deep + visual)
- **patterns.dev** — https://www.patterns.dev (rendering + React patterns)

---

## 8. Working With Other Roles

| Role | Handoff / collaboration |
|---|---|
| **UI Designer** | Receive design tokens, components, visual specs → implement design system. Push back on a11y/perf-hostile designs (contrast, tiny targets, heavy assets). |
| **UX Designer** | Receive flows, IA, interaction logic → implement loading/error/empty states they may not have specced. Flag flows that fight the platform. |
| **Software Engineer (backend)** | Agree on **API contracts** (OpenAPI/GraphQL/types), pagination, error shapes, auth. Co-design a **BFF** when the UI needs aggregation/shaping the public API doesn't give. |
| **DevOps** | Build pipeline, env config, CDN/cache headers, preview deploys, Lighthouse/bundle budgets in CI, edge config. |
| **Platform Architect** | For internal-tool platforms: agree on the **schema contract** (who owns config), the renderer's extension points, and shared design-system distribution across apps. |
| **QA** | Provide stable `role`/`label` selectors, Playwright journeys, Storybook states to test against. |
| **Product / PM** | Translate requirements into states + edge cases; surface perf/a11y trade-offs early. |

---

*Frontend engineering = the user's device is the runtime you don't control. Ship accessible, fast, resilient UI — and own every state, not just the happy one.*
