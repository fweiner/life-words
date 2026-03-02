#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# --- Port cleanup ---
cleanup_port() {
  local port=$1
  local pids
  pids=$(lsof -ti :"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "Killing stale process(es) on port $port: $pids"
    kill -9 $pids 2>/dev/null || true
    sleep 1
  fi
}

cleanup_port 8000
cleanup_port 3000

# --- Validate .env.local files ---
if [ ! -f "$PROJECT_ROOT/backend/.env.local" ]; then
  echo "ERROR: backend/.env.local not found. Copy backend/.env.example and fill in values."
  exit 1
fi
if [ ! -f "$PROJECT_ROOT/frontend/.env.local" ]; then
  echo "ERROR: frontend/.env.local not found. Copy frontend/.env.example and fill in values."
  exit 1
fi

# --- Start Docker Desktop if not running ---
if ! docker info &>/dev/null; then
  echo "Starting Docker Desktop..."
  open -a "Docker Desktop"
  while ! docker info &>/dev/null; do
    sleep 2
  done
  echo "Docker is ready."
fi

# --- Start local Supabase ---
echo "Starting Supabase..."
cd "$PROJECT_ROOT/backend"
supabase start

# --- Trap Ctrl+C to kill both background processes ---
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo ""
  echo "Shutting down..."
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "Done."
  exit 0
}

trap cleanup INT TERM

# --- Start backend ---
echo "Starting backend on port 8000..."
cd "$PROJECT_ROOT/backend"
uv run uvicorn app.main:app --reload 2>&1 | sed 's/^/[backend] /' &
BACKEND_PID=$!

# --- Start frontend ---
echo "Starting frontend on port 3000..."
cd "$PROJECT_ROOT/frontend"
npm run dev 2>&1 | sed 's/^/[frontend] /' &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait for either process to exit
wait
