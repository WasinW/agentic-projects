#!/usr/bin/env bash
# Wrapper: run embed_knowledge.py with the _infra venv, then stamp .last_reindex
# Usage:  reindex.sh                 (incremental full walk — idempotent)
#         reindex.sh --reset        (wipe collection + full rebuild)
#         reindex.sh --files A B..  (embed only these files — used by pre-commit hook)
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
python embed_knowledge.py "$@"
touch .last_reindex
