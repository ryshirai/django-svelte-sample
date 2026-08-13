#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Waiting for PostgreSQL..."
for attempt in $(seq 1 30); do
  if pg_isready -h localhost -p 5432 -U postgres -d app >/dev/null 2>&1; then
    break
  fi
  if [[ "${attempt}" -eq 30 ]]; then
    echo "PostgreSQL did not become ready in time." >&2
    exit 1
  fi
  sleep 1
done

echo "Installing backend dependencies..."
cd "${ROOT}/backend"
uv sync

echo "Applying Django migrations..."
uv run python manage.py migrate --noinput

echo "Installing frontend dependencies..."
cd "${ROOT}/frontend"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi

echo "Installing Playwright Chromium for frontend tests..."
npx playwright install --with-deps chromium

echo
echo "Dev environment is ready."
echo "  Django:    cd backend && uv run python manage.py runserver 0.0.0.0:8000"
echo "  SvelteKit: cd frontend && npm run dev"
