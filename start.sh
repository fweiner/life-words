#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCKER_TIMEOUT=30  # seconds to wait for Docker/OrbStack

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

# --- Start Docker (OrbStack preferred, Docker Desktop fallback) ---
USE_REMOTE_SUPABASE=false

start_docker() {
  if docker info &>/dev/null; then
    return 0
  fi

  # Try OrbStack first (starts in ~2 seconds)
  if command -v orb &>/dev/null; then
    echo "Starting OrbStack..."
    orb start 2>/dev/null || true
  elif [ -d "/Applications/OrbStack.app" ]; then
    echo "Starting OrbStack..."
    open -a "OrbStack"
  elif [ -d "/Applications/Docker Desktop.app" ]; then
    echo "Starting Docker Desktop (this may take a while)..."
    open -a "Docker Desktop"
  else
    echo "No Docker runtime found (OrbStack or Docker Desktop)."
    return 1
  fi

  # Wait for Docker to be ready
  local elapsed=0
  while ! docker info &>/dev/null; do
    if [ $elapsed -ge $DOCKER_TIMEOUT ]; then
      echo "Docker did not start within ${DOCKER_TIMEOUT}s."
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  echo "Docker is ready."
  return 0
}

if ! start_docker; then
  echo ""
  echo "============================================="
  echo "  Docker unavailable — using remote Supabase"
  echo "============================================="
  echo ""
  USE_REMOTE_SUPABASE=true
fi

# --- Start Supabase or switch to remote ---
if [ "$USE_REMOTE_SUPABASE" = false ]; then
  echo "Starting local Supabase..."
  cd "$PROJECT_ROOT/backend"
  if ! supabase start 2>&1; then
    echo ""
    echo "Local Supabase failed to start — falling back to remote."
    USE_REMOTE_SUPABASE=true
  fi
fi

if [ "$USE_REMOTE_SUPABASE" = true ]; then
  # Check that .env.remote files exist
  if [ ! -f "$PROJECT_ROOT/backend/.env.remote" ] || [ ! -f "$PROJECT_ROOT/frontend/.env.remote" ]; then
    echo "ERROR: .env.remote files not found. Cannot fall back to remote Supabase."
    echo "Create backend/.env.remote and frontend/.env.remote with production Supabase credentials."
    exit 1
  fi

  # Swap env vars for this session by sourcing remote values
  echo "Loading remote Supabase config..."

  # Backend: override .env.local values with .env.remote
  export SUPABASE_URL=$(grep '^SUPABASE_URL=' "$PROJECT_ROOT/backend/.env.remote" | cut -d= -f2-)
  export SUPABASE_SECRET_KEY=$(grep '^SUPABASE_SECRET_KEY=' "$PROJECT_ROOT/backend/.env.remote" | cut -d= -f2-)

  # Frontend: override via env vars (Next.js reads NEXT_PUBLIC_* from env)
  export NEXT_PUBLIC_SUPABASE_URL=$(grep '^NEXT_PUBLIC_SUPABASE_URL=' "$PROJECT_ROOT/frontend/.env.remote" | cut -d= -f2-)
  export NEXT_PUBLIC_SUPABASE_ANON_KEY=$(grep '^NEXT_PUBLIC_SUPABASE_ANON_KEY=' "$PROJECT_ROOT/frontend/.env.remote" | cut -d= -f2-)

  echo "Using remote Supabase: $NEXT_PUBLIC_SUPABASE_URL"
  echo ""
  echo "NOTE: You are connected to the PRODUCTION database."
  echo "Be careful with write operations."
  echo ""
fi

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
if [ "$USE_REMOTE_SUPABASE" = true ]; then
  echo "Supabase: REMOTE (production)"
else
  echo "Supabase: LOCAL (Docker)"
fi
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait for either process to exit
wait
