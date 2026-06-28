---
name: agent-policy-engine
description: Design a declarative policy engine for autonomous agents (Regent AI) — permissions (which agent may call which tool), resource caps (spend, rate), action constraints (no external email, no irreversible ops without approval), HITL approval thresholds, and a runtime enforcer that validates every request BEFORE execution. Use when defining what an agent is allowed to do and how that's enforced at runtime. Distinct from LLM output guardrails (those are covered in ai-engineer). Trigger on "agent permissions", "policy engine", "spend cap", "approval threshold", "what can the agent do", "runtime enforcement".
---

# agent-policy-engine

Regent-specific design reference for the **autonomy/permission** layer — what an agent
*may do*, enforced before it acts. Background: `regent-ai/knowledge/01-agent-governance-landscape.md`.
Note: LLM input/output guardrails (PII, injection, topics) are a *different* layer, already
covered in ai-engineer/governance-consultant — this is **tool/action-level** governance, the gap.

## When to use
Defining or reviewing an agent's permission model + runtime enforcement.

## The three-part stack (2026 convergent pattern)
1. **Policy engine** — central declarative repo of plans, permissions, contextual rules.
2. **Runtime enforcer** — validates *every* request/tool-call against policy *before* execution (~200-300ms budget). Block or transform.
3. **Audit** — logs every action + the policy that permitted it (see `audit-trail-design`).

## Policy primitives (declarative)
- **Permissions**: which agent / role may call which tool, with what scopes.
- **Resource caps**: spend limit (e.g. ≤ $100), rate limits, token/time budgets.
- **Action constraints**: deny-list (no external-domain email, no DB drop), allow-list for sensitive ops.
- **Approval thresholds (HITL)**: actions above a declared risk → require human approval. Define the thresholds explicitly (irreversible, > $X, external recipients, prod writes).
- **Handoff governance**: trust-gated agent→agent handoffs (esp. cross-vendor via A2A) with accountability — ties to OWASP Agentic Top 10.

## Design rules
- **Default-deny** for sensitive tools; explicit grants only.
- **Least privilege per task**, not per agent lifetime — scope auth to the current task.
- Policy is **data, not code** — declarative + versioned so it's auditable and reviewable.
- Enforce at the **tool-call boundary**, where the OpenAI Agents SDK and friends are weak.

## Checklist
- [ ] Permission matrix (agent × tool × scope)
- [ ] Resource caps (spend/rate/budget)
- [ ] Action allow/deny lists
- [ ] HITL approval thresholds defined + wired to checkpoints
- [ ] Handoff trust gates
- [ ] Default-deny + least-privilege-per-task
- [ ] Policies versioned + audit-linked

## Consult
governance-consultant (regulation → controls), security-engineer (enforcement, zero-trust, OWASP Agentic), ai-architect (where it sits vs NeurX runtime).
