# UX Designer — Comprehensive Knowledge

> Deep reference for the ux-designer subagent: a senior UX / product designer + researcher, with a strong bias toward **DevEx / internal-platform UX** — designing the tools that engineers (e.g. DEs) use, so they work easily.

---

## 1. Foundations

### What a UX Designer does

Reduces the **friction between user intent and outcome**. A user shows up with a goal; the UX designer's job is to make the path from "I want X" to "X happened" as short, clear, and forgiving as possible.

- Understand users + their goals (research)
- Structure information so people can find + act (IA)
- Design flows + interactions that match how users think
- Validate with real users before + after build
- Catch friction, error, and dead-ends early

UX is not a screen. It's the whole experience of getting something done — discovery, decision, action, recovery, repeat.

### How it differs

- **UI Designer** — *visual* craft: layout, type, color, components, motion, design-system tokens. Makes it look right + on-brand. UX decides *what the flow is*; UI decides *how it looks*.
- **System Analyst** — *requirements + process*: elicits what the system must do, maps as-is/to-be, writes specs + acceptance criteria. SA owns "what to build"; UX owns "how it should feel to use."
- **Product Manager** — *what to build + why* (market, value, prioritization). PM owns the bet; UX owns the usability of the bet.
- **UX Designer** — *how the user reaches their goal* with least friction. Sits between PM intent, SA requirements, and UI craft.

In small teams one person wears several hats. Don't fight the title — fight the friction.

### Core deliverables

- Research findings + insights (not raw notes)
- Personas / user segments + Jobs-to-be-Done
- Journey maps + service blueprints
- User flows + task analysis
- Information architecture (sitemaps, nav models)
- Wireframes + interactive prototypes
- Usability test reports + heuristic evaluations
- Interaction specs (states, errors, empty, loading)

---

## 2. Mental Models / Decision Frameworks

### User-centered design (UCD)

Design *with* the user in the loop, not for an imagined one. Loop: **understand → define → ideate → prototype → test → repeat**. Every decision traces back to a real user need, not a stakeholder whim or the designer's taste.

### Jobs-to-be-Done (JTBD)

People don't want features; they "hire" a product to make progress in a situation. Frame work as: *When [situation], I want to [motivation], so I can [outcome]*. JTBD beats demographic personas for product decisions because it captures **why**, not **who**. (AI now helps cluster interview data into jobs at scale — but human judgment still picks the job that matters.)

### Mental model vs system model

- **Mental model** — how the user *thinks* the thing works.
- **System model** — how it *actually* works internally.
- **Interface** — the bridge.

Friction = the gap between the two. Good UX shapes the interface around the user's mental model and *hides* the system model. Bad UX leaks the system model (DB tables, internal job names, infra concepts) into the UI and forces the user to learn the implementation.

### Information architecture

Structure content + functionality so people can **find** and **understand** it.
- Group by the user's mental model, not your org chart
- Label in the user's language, not internal jargon
- Shallow + broad usually beats deep + narrow for findability
- One clear primary action per screen

### Progressive disclosure

Show only what's needed now; reveal complexity on demand. Defaults for the 80%, advanced options tucked behind "Advanced." Reduces cognitive load without removing power.

### Cognitive load

Every choice, label, and field costs mental effort. Budget it.
- Fewer decisions per step
- Sensible defaults > empty fields
- Recognition > recall (show options, don't make them remember)
- Chunk long flows into steps with clear progress

This maps directly to the **DevEx** cognitive-load dimension in §6 — same principle, engineer as the user.

### Error prevention > error messages

The best error message is the one that never fires. Rank your defenses:
1. **Prevent** — constrain input, disable invalid actions, smart defaults
2. **Confirm** — guard destructive/irreversible actions
3. **Recover** — undo, drafts, autosave
4. **Explain** — clear, specific, actionable error message (last resort)

A great error message tells the user *what happened, why, and how to fix it* — in plain language, not a stack trace.

### The Double Diamond

| Phase | Mode | Activity |
|---|---|---|
| **Discover** | Diverge | Research broadly, gather problems |
| **Define** | Converge | Frame the *right* problem |
| **Develop** | Diverge | Ideate many solutions |
| **Deliver** | Converge | Prototype, test, ship one |

Two diamonds = problem space then solution space. Most teams skip diamond 1 and solve the wrong problem beautifully.

### North-star + task success

Tie design to one outcome metric (the North-star) plus per-task success measures:
- **Task success rate** — % who complete the task
- **Time-on-task** — how long it takes
- **Error rate** — slips + mistakes per task
- **SUS / SEQ** — perceived ease (System Usability Scale / Single Ease Question)

If you can't measure the task, you can't tell if the redesign helped.

---

## 3. Standard Practices

### UX research methods

| Method | When | Gives you |
|---|---|---|
| **User interviews** | Early, understand needs | Why, motivations, context (qual) |
| **Contextual inquiry / shadowing** | Understand real workflow | Actual behavior, workarounds |
| **Usability testing** | Validate a design | Where people get stuck (qual) |
| **Surveys** | Many users, structured | Scale, prioritization (quant) |
| **Card sorting** | IA + navigation | How users group concepts |
| **A/B testing** | Live, two variants | Which performs better (quant) |
| **Analytics review** | Existing product | Where users drop off (quant) |

Rule of thumb: **5 users** surface ~85% of usability problems in a qualitative test. You don't need 50.

**Moderated vs unmoderated** — moderated = depth, follow-up questions, fewer users; unmoderated (Maze, Lyssna) = scale, speed, cheaper, no probing.

### Personas + journey maps

- **Personas / segments** — archetypal users with goals, context, pain. Keep them grounded in research; a fictional persona is worse than none.
- **Journey map** — the user's experience over time across touchpoints: phases, actions, thoughts, emotions, pain points, opportunities. Surfaces *where* the experience breaks.

### User flows + task analysis

- **Task analysis** — break a goal into the steps a user must take. Count the steps; each one is a chance to drop off.
- **User flow** — the diagram of paths through the system (happy path + branches + error paths). Design the flow *before* the screens.

### Wireframing

Low fidelity first. Boxes + labels, no color, no polish. The point is to settle structure + flow cheaply, before anyone falls in love with a pretty mockup. Fidelity rises only as confidence rises.

### Information architecture practices

- **Card sorting** (open/closed) — derive groupings from users
- **Tree testing** — validate findability of a nav structure
- **Sitemap** — the map of the structure
- Navigation patterns: global nav, breadcrumbs, faceted filtering, search-first

### Interaction patterns

Reuse established patterns; users have learned them already. Reinvent only when the standard genuinely fails the task. Always design the **full set of states**: default, hover/focus, active, loading, empty, error, success, disabled. Missing states are the #1 source of "looks done but feels broken."

### Usability heuristics — Nielsen's 10

1. Visibility of system status
2. Match between system + real world (user's language)
3. User control + freedom (undo, exits)
4. Consistency + standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility + efficiency (shortcuts for experts)
8. Aesthetic + minimalist design
9. Help users recognize, diagnose, recover from errors
10. Help + documentation

Still the workhorse rubric in 2025 — Nielsen's point is they describe *how humans use technology*, and humans don't change. Use them for quick **heuristic evaluation** before/without a full test.

### Accessibility / inclusive design

Not optional, not a late checklist. Target **WCAG 2.2 AA**.
- Perceivable, Operable, Understandable, Robust (POUR)
- Color contrast ≥ 4.5:1 for body text
- Full keyboard operability; visible focus
- Semantic structure + labels for screen readers
- Don't rely on color alone to convey meaning
- Respect reduced-motion + zoom

Inclusive design (edge cases, temporary/situational impairments) makes the product better for *everyone*, not just users with disabilities. Many Nielsen heuristics map cleanly onto WCAG criteria.

---

## 4. Tools Landscape (2026)

### Design + prototyping
- **Figma** — the default; design, prototype, dev-mode handoff, plugins, AI assists (FigJam for workshops)
- **Penpot** — open-source alternative
- **Framer** — high-fidelity, production-grade interactive prototypes

### Research + usability testing
- **Maze** — unmoderated testing, validates prototypes fast; native Figma integration
- **UserTesting** — all-in-one moderated/unmoderated, recruited panel; market leader
- **Lyssna** (ex-UsabilityHub) — quick unmoderated tests, preference + 5-second tests, card sorting
- **Dovetail** — research repository + analysis; the standard for storing + tagging insights, AI-assisted synthesis
- **UserInterviews** — participant recruiting

### Product + behavioral analytics
- **PostHog** — open-source product analytics: funnels, session replay, cohorts, flags, A/B — strong for internal tools
- **Hotjar** — heatmaps, session recordings, on-page surveys
- **Amplitude / Mixpanel** — funnel + retention analytics at scale
- **Maze / Lyssna** double as quant for prototypes

### Flow / diagram / IA
- **FigJam, Miro, Mural** — journey maps, workshops, card sorting
- **Whimsical / Lucidchart / draw.io** — user flows, sitemaps
- **Optimal Workshop** — card sorting + tree testing

### AI UX assists (2025-2026)
- AI for **research synthesis** (clustering interviews → themes/jobs): Dovetail, Marvin, reloadux-style JTBD mapping
- AI **first-draft wireframes/copy** from prompts inside Figma
- AI **moderated-interview** + transcript analysis tools
- Caveat (Nielsen, 2025): AI tools still apply usability heuristics *poorly*; improving slowly. AI gives scale; humans still give judgment. Treat AI output as a draft to critique, never a verdict.

---

## 5. Anti-Patterns

| Anti-pattern | Why it hurts | Better |
|---|---|---|
| **Designing for yourself** | You are not the user; you know too much | Research real users |
| **No research ("we know users")** | Builds on assumptions | At least 5 interviews / usability sessions |
| **Feature soup** | Every request bolted on; nothing coherent | One clear job per surface; say no |
| **Hidden critical actions** | Users can't find the thing they came for | Primary action visible + obvious |
| **Inconsistent patterns** | Re-learning cost every screen | Pattern library + consistency |
| **Ignoring error/empty/loading states** | "Looks done," feels broken in reality | Design all states up front |
| **Dark patterns** | Coerced consent, hidden opt-outs, fake urgency | Honest, user-respecting design |
| **Polishing before validating** | Beautiful solution to the wrong problem | Lo-fi + test before pixel polish |
| **Jargon / system-model labels** | Leaks implementation onto the user | Speak the user's language |
| **Deep nav, everything 5 clicks away** | Findability collapses | Shallow + broad; search |
| **No defaults, empty forms** | Max cognitive load on every field | Smart defaults; progressive disclosure |
| **One-and-done (ship, never measure)** | Never learn if it worked | Instrument task success + iterate |

---

## 6. Advanced / Expert Topics — DevEx / Platform UX (the core differentiator)

> This is *why this role exists* on a data/ML org. The user is an **engineer**; the product is an **internal platform**; the goal is to make building, shipping, and handing off work low-friction. UX principles apply fully — the persona just happens to write code.

### The painpoint this solves

Data platforms commonly rot into **N independent pipelines**, each started from scratch, each with its own conventions, no common/standard base. Symptoms:
- Every new pipeline re-solves boilerplate (scheduling, IO, config, retries, lineage)
- No standardization → every pipeline is a special snowflake
- Onboarding is slow; the only way to learn "how we do X" is to ask whoever did it last ("rumour-driven development," Spotify's term)
- **Handoff is brutal** — when someone leaves, their pipelines become unmaintainable folklore

The UX-designer's job here: design an internal platform UX where a data engineer **declares dependencies + business logic and nothing else** — the platform handles the boilerplate. Engineers focus only on the hard, domain-specific part. This is **Developer Experience (DevEx) / Platform UX**, and it is a design problem as much as an engineering one.

### Config-driven main service, not N pipelines — from a UX lens

Reframe: instead of "write a pipeline," the experience should be "**declare** a pipeline." The interface is the config surface. Design questions:
- What's the smallest set of things the user *must* specify (their dependencies + transform logic)?
- What should be **defaulted / inherited / convention** (everything else)?
- How does a user override a default *without* leaving the paved path?

The config schema **is** the UX. A bad config schema is a bad UI — confusing keys, no validation, silent failures, leaked internals. Treat config design like form design.

### Config-as-UI — the spectrum

| Surface | Best for | Tradeoff |
|---|---|---|
| **YAML/JSON config** | Engineers, version-controlled, diffable | Needs great schema + validation + docs |
| **DSL** | Repeated domain patterns, expressiveness | Learning curve; you own a language now |
| **Visual builder / form** | Lower-skill users, discoverability | Less flexible; escape hatch needed |
| **Scaffolding CLI / template** | Start-from-golden-path | One-time; drifts after generation |
| **Annotations in code** | Keep logic + config co-located | Couples to language |

Opinion: for DE platforms, **declarative config + schema validation + a scaffolding CLI** is usually the sweet spot. Add a visual layer only once the config model is proven. Always provide an **escape hatch** so the 5% advanced case doesn't force a fork off the platform.

### Golden paths + paved roads (UX framing)

A **golden path** is the opinionated, well-lit, supported route for a common task (e.g. "stand up a new batch pipeline"). Make the paved route *so good people choose it on their own* — guidance not enforcement. From a UX lens this is just **the happy path, productized**: one obvious way, sane defaults, docs + templates inline, friction removed.

- Centralize the hard decisions *once* so each DE doesn't re-decide every time
- Templates/scaffolds encode the standard; using them *is* easier than not
- Pave the most-traveled roads first (measure which tasks recur)

### Time-to-first-success (the headline metric)

The single most important DevEx number: **how long from "new engineer / new task" to "first working result"** (first green pipeline, first deployed model). In 2026, 30-minute onboarding to first success is the bar, not aspiration. Drive it down ruthlessly:
- Working example that runs out of the box
- Scaffolding that produces a runnable artifact, not a blank repo
- Local/dry-run mode so feedback is instant, not "wait for the nightly run"

### The three DevEx dimensions (Storey/Noda/Forsgren — the DevEx framework)

The successor to SPACE distills DevEx into three felt dimensions — design directly against them:

| Dimension | Meaning | UX levers |
|---|---|---|
| **Feedback loops** | Speed + quality of response to an action | Fast local runs, dry-run, clear validation errors, fast CI |
| **Cognitive load** | Mental effort to do the task | Good defaults, hide internals, golden paths, great docs at point-of-use |
| **Flow state** | Ability to stay in focused flow | Minimize interruptions, handoffs, ticket-and-wait, context switches |

A friction is a DevEx bug. Every "you have to ask someone," "wait for the platform team," or "read this 40-page wiki" is a flow-state and feedback-loop violation.

### Self-service vs guard-rails

The balance that defines a good platform:
- **Self-service** — the DE creates/deploys/manages without filing a ticket or waiting on ops
- **Guard-rails** — policy, security, cost, standards baked into the path (policy-as-code), so the easy way is also the *safe* way

Design goal: **"guardrails, not gatekeepers."** Developers target *environments + outcomes*, not infra details; complexity is managed centrally; the platform presents simple choices. Governance becomes an invisible safeguard, not an approval queue. The wrong thing should be hard to do; the right thing should be the default.

### Designing for the "user is an engineer" persona

Engineers are users with specific traits — design for them:
- Value **speed, control, and transparency** over hand-holding
- Trust the tool only if they can see what it does (no magic black boxes that fail silently)
- Prefer **text + diffable + composable** over locked-in GUIs
- Hate repetition + boilerplate viscerally
- Will route *around* a bad platform (shadow tooling) the moment it's slower than DIY — your real competitor is "they build their own"
- Read errors, not tooltips — so make **error messages excellent**: what failed, why, exact fix

### Onboarding + handoff design

The antidote to "knowledge leaves with the person":
- **Onboarding** — a new DE should reach first-success in <1 day via golden path + runnable examples, *without* tapping a senior on the shoulder
- **Handoff** — because pipelines are config-driven + standardized, any DE can read + own any pipeline. Standardization *is* the handoff strategy. Self-documenting config + conventions beat tribal knowledge.
- Design the **"day-2" experience**, not just creation: debugging, modifying, deprecating, observing a pipeline someone else wrote

### Service blueprints (for internal platforms)

Extend the journey map: map the **frontstage** (what the DE sees/does) against the **backstage** (platform services, automation, the platform team) and supporting systems. Surfaces where a self-service experience secretly depends on a human or a ticket — those are the handoffs to automate away.

### Measuring DevEx

- **Friction logs** — engineer narrates a task, every annoyance timestamped. Cheap, brutal, high-signal.
- **Time-to-X** — time-to-first-PR, time-to-first-deploy, time-to-first-pipeline, time-to-recovery
- **DevEx surveys** — periodic perception survey across the three dimensions
- **Funnel/analytics on the platform itself** — where do users drop off in the scaffold flow? (treat your IDP like a product with PostHog-style analytics)
- Pair perceptual (survey) + behavioral (telemetry) — neither alone is enough

### Adjacent expert topics

- **Design ops** — design system, pattern library, research repository, governance so quality scales past one designer
- **Experimentation / A-B** — hypothesis → variant → measure; guard against peeking + underpowered tests; even internal tools benefit from measured changes
- **Accessibility depth** — WCAG 2.2 AA as floor, ARIA authoring practices, screen-reader + keyboard-only testing as routine, not audit-time

---

## 7. References

### Books
- **Don't Make Me Think** — Steve Krug (usability, the canonical starter)
- **The Design of Everyday Things** — Don Norman (affordances, mental models, signifiers)
- **The Elements of User Experience** — Jesse James Garrett (the layered model)
- **Team Topologies** — Skelton & Pais (team cognitive load, platform-as-a-product)
- **Sprint** — Jake Knapp (design sprint method)

### DevEx / Platform research
- **DevEx: What Actually Drives Productivity** — Storey, Noda, Forsgren, et al. — https://queue.acm.org/detail.cfm?id=3595878
- **DevEx metrics framework** (from the SPACE authors) — https://www.infoq.com/articles/devex-metrics-framework/
- **Golden paths** — https://jellyfish.co/library/platform-engineering/golden-paths/ · https://www.port.io/blog/developer-experience
- **Self-service with guardrails** (Microsoft Platform Engineering) — https://learn.microsoft.com/en-us/platform-engineering/about/self-service
- **DevEx in 2026** — https://dev.to/austinwdigital/developer-experience-devex-in-2026-the-real-competitive-advantage-2996

### UX standards + orgs
- **Nielsen Norman Group (NN/g)** — https://www.nngroup.com (heuristics, research methods, the reference)
- **WCAG 2.2** — https://www.w3.org/TR/WCAG22/
- **Nielsen on AI + usability (2025)** — https://dovetail.com/blog/past-present-future-of-usability-with-jakob-nielsen/

### Tools
- UX research tools roundup — https://cleverx.com/blog/best-user-research-tools-2026-12-platforms-ranked-and-reviewed
- UX analytics tools — https://www.usehubble.io/blog/ux-analytics-tools

---

## 8. Working With Other Roles

| Role | Handoff / overlap |
|---|---|
| **UI Designer** | UX hands off **flows + wireframes + states**; UI turns them into visual design + components. "Here's the structure + interaction — make it look right + on-brand." |
| **Frontend Engineer** | UX/UI hands off prototypes + specs; FE builds. UX stays in the loop for state edge-cases, responsiveness, real-data behavior. |
| **System Analyst** | SA provides **requirements + process + acceptance criteria**; UX turns "what the system must do" into "how it should feel to do it." Strong overlap on task flows. |
| **Platform Architect** | **Strongest overlap for internal platforms.** Architect owns platform-as-a-product + golden-path *capability*; UX owns the golden-path *experience* — config surface, onboarding, self-service ergonomics. Co-design the paved road. |
| **Data Architect** | Designs the data/platform structure; UX makes the architect's concepts legible + usable to DEs. The architect's model leaks into the UX if not deliberately abstracted. |
| **DE / ML Engineer** | **The platform's users.** Research subjects + validators. Their friction logs + workflows drive the platform UX backlog. Design *with* them, not for an imagined DE. |
| **Product Manager** | PM sets the bet + priorities; UX ensures the bet is usable. Negotiate scope vs friction. |

---

*UX's value is reducing the friction between user intent and outcome. On a data platform, the user is often an engineer, the outcome is a working pipeline, and the best UX is the one where they declare what they want — and never touch the boilerplate.*
