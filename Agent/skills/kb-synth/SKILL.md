---
name: kb-synth
description: Socratic-style KnowledgeOps for the local Agent-KB — turn raw evidence (knowledge_chat/ session dumps, code, docs) into curated, auditable knowledge units through an interview, then diff → approve → embed into Qdrant. Use to distill a pile of raw notes into a clean knowledge unit instead of dumping it into RAG. Trigger on "synthesize this into a knowledge unit", "curate this chat into KB", "kb-synth", or when knowledge_chat/ has raw material that should become a real knowledge/ file.
---

# kb-synth

Adapts the Socratic (kevins981/Socratic) KnowledgeOps method to Wasin's local
Agent-KB stack. The idea Socratic sells: don't dump documents into an embedding
index — **interview an expert to extract tacit rules, resolve ambiguities, and
surface edge cases**, producing curated plain-text units that are auditable and
approved before they become "what the agent knows".

Here **Claude is the synthesis agent** (Socratic uses OpenAI Codex; on Wasin's
Intel Mac that can't run natively). The pipeline plugs into the existing
Qdrant + MCP infra — no new services.

## Layers (mirror Socratic's execution model)

| Socratic | Here |
|---|---|
| Immutable evidence (`../` source docs, read-only) | `knowledge_chat/*.md` raw dumps, project code, docs |
| Mutable knowledge base (agent edits) | the project's `knowledge/*.md` curated units |
| Synthesis brain (Codex) | Claude, in-session (frontier, free) |
| Inspect / diff / approve | `git diff` on the knowledge unit before embed |
| Downstream consumer | Qdrant index via `_infra/reindex.sh`, searched over MCP |

## Workflow

Run when pointed at raw evidence (a `knowledge_chat/` file, a code area, a topic)
and a target `knowledge/` directory.

1. **Ground.** Read the evidence fully. Never treat it as settled — it is a
   transcript, not curated truth. Identify: the core claims, what is decided vs
   still open, and every place the transcript is ambiguous or unverified.
2. **Draft the unit.** Write ONE cohesive knowledge unit as a candidate file in
   the target `knowledge/` dir, matching that dir's existing convention (look at
   siblings: descriptive-name `.md` + an `00-INDEX.md` entry). One theme per
   file — internally complete, externally decoupled (cross-link other units by
   filename, don't depend on their implicit content). Lead with the decision/
   answer, then the reasoning. Mark anything unverified explicitly.
3. **Interview (the Socratic step).** Before finalizing, ask the user the
   targeted questions the evidence left unresolved — tacit rules a newcomer
   wouldn't know, edge cases, "why X not Y", numbers the transcript hand-waved.
   Keep it to the few questions that actually change the unit. Fold answers in.
4. **Diff → approve.** Show `git diff` (or the new-file content) and get an
   explicit ok. This is the human-in-the-loop gate — nothing enters the KB
   unreviewed.
5. **Embed.** On approval, embed just this file:
   `~/Documents/Projects/Agent/_infra/reindex.sh --files <path/to/unit.md>`
   (requires Qdrant up: `docker compose up -d` in `_infra/`). Update the dir's
   `00-INDEX.md` and embed that too.
6. **Export (optional).** To hand a whole project's curated KB to a downstream
   agent as one file: `python _infra/kb_synth.py export <knowledge_dir>` →
   writes `Agent.md` (Socratic's export format).

## Rules

- Evidence is read-only. Never edit `knowledge_chat/` dumps from here — they are
  the audit trail of where a unit came from.
- One unit = one theme. If the evidence spans three topics, produce three units,
  not one sprawling file.
- Prefer editing an existing unit over adding a near-duplicate. Search first
  (`mcp__agent-knowledge__search_knowledge`) to find the file to extend.
- Unverified stays labeled. If the transcript says "we think" or "TODO verify",
  the unit says so too — curated ≠ fabricated confidence.
- Keep the interview short. The value is the 3-5 questions only the human can
  answer, not re-asking what the evidence already states.

## Not this skill

- Bulk re-indexing everything → `_infra/reindex.sh --reset`.
- Recording a single decision with options/consequences → the `adr` skill.
- Running the real Socratic product (Codex-driven) → `_infra/socratic-lab/`.
