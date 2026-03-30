#!/usr/bin/env bash
# ============================================================
# OakstrattonIMA — Start all services for local development
# Usage: ./scripts/dev.sh
# ============================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting OakstrattonIMA development environment..."

# Run migrations
echo "→ Running database migrations..."
cd "$ROOT_DIR/backend"
source venv/bin/activate
alembic upgrade head
echo "  ✓ Migrations applied"

# Start backend in background
echo "→ Starting FastAPI backend on :8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Celery worker in background
echo "→ Starting Celery worker..."
celery -A app.tasks.worker worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Start frontend
echo "→ Starting Vite frontend on :5173..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=============================="
echo " All services running:"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend: http://localhost:5173"
echo ""
echo " Press Ctrl+C to stop all services"
echo "=============================="

# Cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $CELERY_PID $FRONTEND_PID 2>/dev/null || true
    echo "Done."
}
trap cleanup EXIT INT TERM

wait
