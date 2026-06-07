---
name: user-story-gen
description: Turn a feature or requirement into well-formed, INVEST user stories with Given/When/Then acceptance criteria, edge cases, MoSCoW prioritization, and noted non-functional requirements + dependencies — a ready-for-grooming story set. Use when a feature/need has to be broken into stories the team can estimate and build.
---

# user-story-gen

Converts a feature or raw requirement into a groomable set of user stories: each story INVEST-shaped, each with testable Given/When/Then acceptance criteria, edge cases surfaced, priority set via MoSCoW, and NFRs + dependencies flagged. Output is ready for backlog refinement.

## When to use

- A feature/requirement needs decomposing into stories the team can estimate and pull into a sprint.
- A vague ask ("we need reporting") has to become concrete, testable backlog items.
- Someone asks "write the user stories / acceptance criteria for X."

## Inputs (ASK for any that are missing BEFORE writing stories)

- **The feature / need** — what's being built and the problem it solves.
- **User role(s)** — the personas/actors involved (end user, admin, system, partner).
- **Business goal** — the outcome/value the feature is meant to deliver (the "so that").
- **Constraints** — known platform, compliance, or integration boundaries (optional but useful).

## Steps

1. **Load BA + SA knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="user story INVEST acceptance criteria given when then MoSCoW non-functional requirements backlog", role_filter="business-analyst", top_k=5)`
   and `mcp__agent-knowledge__search_knowledge(query="requirements decomposition edge cases dependencies system behavior acceptance", role_filter="system-analyst", top_k=5)`.
   Fallback if MCP is down: read those roles' `knowledge.md`.
2. **Confirm inputs** — if feature, roles, or goal are unclear, ASK first; don't invent the value.
3. **Write stories** — `As a [role], I want [goal], so that [value]`. Make each **INVEST** (Independent, Negotiable, Valuable, Estimable, Small, Testable); split anything too big into a thin vertical slice.
4. **Acceptance criteria** — for each story, **Given / When / Then** scenarios that are testable; cover the happy path explicitly.
5. **Edge cases** — empty/invalid input, permission denied, concurrency, failure/timeout, boundary values — as their own AC or stories.
6. **Prioritize** — tag each story **Must / Should / Could / Won't (MoSCoW)**; identify the thin MVP slice.
7. **NFRs + dependencies** — note performance, security/PDPA, accessibility, scalability requirements, and upstream/downstream dependencies and sequencing.
8. **Output** a clean, ready-for-grooming set.

## Guardrails / Notes

- Every story carries the **"so that" value** — if you can't state it, the story may not be worth building; flag it.
- AC must be **testable** — avoid "works well"; write observable Given/When/Then.
- Don't bury NFRs inside prose — call them out so they're estimated, not forgotten.
- Split vertically (a usable slice), not horizontally (UI-only / backend-only) — keep each story shippable.
- Be explicit about assumptions; a story built on a guessed goal is rework waiting to happen.
