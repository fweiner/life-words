#!/usr/bin/env bash
set -euo pipefail

PORT=8000

echo "Checking port $PORT..."
PID=$(lsof -ti :"$PORT" 2>/dev/null || true)
if [ -n "$PID" ]; then
  echo "Killing process(es) on port $PORT: $PID"
  kill -9 $PID 2>/dev/null || true
  sleep 1
fi

echo "Starting FastAPI dev server on port $PORT..."
cd "$(dirname "$0")/../backend"
uv run uvicorn app.main:app --reload
