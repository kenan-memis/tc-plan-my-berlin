#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"

echo "[entrypoint] Starting container on PORT=${PORT}"

# Hard #1 / Option A1:
# Always (re)build the Chroma vectorstore on container start.
# This guarantees production always reflects the current `data/raw/*.md` in the image.
echo "[entrypoint] Ingesting knowledge base into Chroma (may take a few seconds)…"
python -m planmyberlin.rag.ingest
echo "[entrypoint] Ingest completed."

echo "[entrypoint] Launching Streamlit…"
exec streamlit run planmyberlin/ui/app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}"

