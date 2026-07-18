# socratic-lab — real Socratic (kevins981/Socratic) in Docker

Runs the actual Socratic KnowledgeOps product in a Linux container, because it
needs Linux kernel ≥ 5.15 and drives the OpenAI **Codex** CLI as its synthesis
brain — neither runs natively on this Intel Mac. Docker Desktop's Linux VM
supplies the kernel.

**For the native, Claude-driven version that plugs into the Qdrant/MCP KB, use
the `/kb-synth` skill instead — no API key, no container.** This lab is for
trying the real thing / deciding whether to adopt it.

## What's here

| File | Purpose |
|---|---|
| `Dockerfile` | node20 + python3.11 + `@openai/codex` + Socratic (cloned at build) |
| `docker-compose.yml` | mounts `data/`, injects the API key, exposes web UI on :3100 |
| `.env.socratic` | Socratic's model config (OpenRouter `z-ai/glm-4.6`) |
| `data/projects/` | curated knowledge bases persist here (host-side) |
| `data/sources/` | drop your own source docs here to synthesize from |

## Status (validated 2026-07-15)

Built and smoke-tested without an API key: image builds, `codex-cli 0.144.4`
present, `socratic-cli create` works, host volume persistence confirmed
(`data/projects/airline_demo/` appears). The `synth` step needs a key (below).

## Run it

```bash
cd ~/Documents/Projects/Agent/_infra/socratic-lab

# 1. Your OpenRouter key (get one at openrouter.ai/keys). Stays in the shell —
#    never baked into the image.
export OPENROUTER_API_KEY=sk-or-...

# 2. Create a project from the built-in demo (no key needed)
docker compose run --rm socratic \
  socratic-cli create --name airline_demo --input_dir examples/repos/tau_airline

# 3. Synthesize — this is where Codex + the model do the work (needs the key)
docker compose run --rm socratic socratic-cli synth --project airline_demo

# 4. Export the curated KB as Agent.md
docker compose run --rm socratic socratic-cli export --project airline_demo
#    -> data/projects/airline_demo/... on the host

# Web UI (inspect / diff / approve) instead of CLI:
docker compose run --rm --service-ports socratic \
  bash -lc 'cd web && npm run dev:project -- --project airline_demo'
#    -> http://localhost:3100
```

### Synthesize your own material
Drop source files into `data/sources/<topic>/`, then
`--input_dir sources/<topic>` in the create step. (Inside the container the host
`data/sources` is mounted at `/opt/Socratic/sources`.)

## Notes / gotchas

- **Model choice** (`.env.socratic`): `z-ai/glm-4.6` and `x-ai/grok-4` are on
  Socratic's "works well" list; `google/gemini-2.5-flash` is cheaper. Small/local
  models are documented as unstable for Socratic's multi-step tool use.
- **Codex sandbox in Docker:** Socratic launches `codex --sandbox workspace-write`.
  If synth errors on sandbox/seccomp inside the container, add
  `security_opt: [seccomp:unconfined]` to the compose service (or try
  `--sandbox danger-full-access` — lab only).
- **Cost:** every synth/digest run makes real API calls. Watch your OpenRouter
  spend; start with the small demo.
- `data/` is host-side and git-ignored — safe to `rm -rf data/projects/<name>`
  to start over.
- Update Socratic: `docker compose build --no-cache`.
