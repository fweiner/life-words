#!/bin/bash

# Start Docker Desktop if not running
if ! docker info &>/dev/null; then
  echo "Starting Docker Desktop..."
  open -a "Docker Desktop"
  while ! docker info &>/dev/null; do
    sleep 2
  done
  echo "Docker is ready."
fi

# Start local Supabase
echo "Starting Supabase..."
cd backend
supabase start

# Start backend
echo "Starting backend..."
uv run uvicorn app.main:app --reload
