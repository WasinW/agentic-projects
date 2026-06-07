# CLAUDE.md — crypto-trading (KB context)

Project-scoped agent context for the personal crypto trading decision-support
engine. Builder/product lens — NOT data-engineering/pipeline, NOT The1/NTT/SCB.

## What to read first
1. `~/Documents/Projects/Project/project_sandbox/crypto-trading/doc/02-project-context.md` — source of truth (mental model + §6 LOCKED contract).
2. `…/doc/03-signal-logic-spec.md` — signal set, weights, confluence, invalidation.
3. [knowledge/adr/INDEX.md](knowledge/adr/INDEX.md) — locked decisions.
4. `…/crypto-trading/.claude/CLAUDE.md` — in-repo working guidance.

## Mental model (don't violate)
- Two indicators: Pine live-signal (TradingView) vs this local analytical engine — different jobs.
- Build-time (Claude Code/agents/skills) vs runtime (the engine, which calls the Anthropic API itself later).
- Engine = deterministic code layer + interpretive LLM layer. v1 = deterministic only.

## Agent routing (reuse, don't create)
- solution-architect → architecture sanity-check (one-time, done).
- software-engineer → lead build (Python). data-analyst → feature/indicator logic.
- investment-consultant → signal/weight/playbook/invalidation spec.
- later: ml-engineer (predictive); frontend-engineer + ui/ux-designer (dashboard).

## Skills
`crypto-ta-math`, `risk-management`, `adr` (all in ~/.claude/skills). Later:
`backtesting-discipline`, `pine-script-v6`.

## Conventions
- All tuning params in `config/engine.yaml` — never hardcode.
- Indicators use Wilder RMA (TradingView parity); drop the unclosed candle.
- Contract changes = version bump + a new ADR.
- Not investment advice; engine systematizes discipline, does not predict.
