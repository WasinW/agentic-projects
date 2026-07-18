#!/bin/bash
# KB doctor — one-line health report for the agent system (SessionStart hook).
# --fix: run incremental reindex over the whole tree (idempotent, needs Docker/Qdrant up).
A="$HOME/Documents/Projects/Agent"
ISSUES=()

# 1) Qdrant reachable? (RAG is optional — agents work without it)
if ! curl -s -m 2 http://localhost:6333/healthz >/dev/null 2>&1; then
  ISSUES+=("qdrant down (RAG off — optional)")
fi

# 2) ~/.claude/{skills,agents} must contain symlinks only
n=$(find "$HOME/.claude/skills" -mindepth 1 -maxdepth 1 ! -type l 2>/dev/null | wc -l | tr -d ' ')
[ "$n" != "0" ] && ISSUES+=("$n non-symlink in ~/.claude/skills")
m=$(find "$HOME/.claude/agents" -mindepth 2 -maxdepth 2 -name '*.md' ! -type l 2>/dev/null | wc -l | tr -d ' ')
[ "$m" != "0" ] && ISSUES+=("$m non-symlink agent files")

# 3) broken symlinks
b=0
for l in $(find "$HOME/.claude/skills" "$HOME/.claude/agents" -type l 2>/dev/null); do
  [ -e "$l" ] || b=$((b+1))
done
[ "$b" != "0" ] && ISSUES+=("$b broken symlinks")

# 4) uncommitted changes piling up in Agent/
u=$(git -C "$A" status --porcelain -- . 2>/dev/null | wc -l | tr -d ' ')
[ "$u" -gt 20 ] && ISSUES+=("$u uncommitted files in Agent/")

# 5) RAG staleness: .md newer than last reindex (excluding machine-excluded dirs)
marker="$A/_infra/.last_reindex"
count_eligible() {
  find "$A" -name '*.md' \
    -not -path '*/_*' -not -path '*/.git/*' -not -path '*/archive/*' \
    -not -path '*/knowledge_base_legacy/*' -not -path '*/memory/*' -not -path '*/bak_mem/*' \
    "$@" 2>/dev/null | wc -l | tr -d ' '
}
total=$(count_eligible)
if [ -f "$marker" ]; then
  stale=$(count_eligible -newer "$marker")
  [ "$stale" != "0" ] && ISSUES+=("$stale .md newer than last reindex")
else
  ISSUES+=("no reindex marker — run reindex.sh")
fi

if [ "$1" = "--fix" ]; then
  exec "$A/_infra/reindex.sh"
fi

if [ ${#ISSUES[@]} -eq 0 ]; then
  echo "KB OK (~$total files eligible, index fresh, symlinks clean)"
else
  joined=$(printf '%s; ' "${ISSUES[@]}")
  printf 'KB DRIFT: %s— fix: Agent/_infra/doctor.sh --fix\n' "$joined"
fi
exit 0
