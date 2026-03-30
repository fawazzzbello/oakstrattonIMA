#!/usr/bin/env bash
# ============================================================
# OakstrattonIMA — Local Development Setup Script
# Run once after cloning the repo.
# ============================================================
set -euo pipefail

echo "=============================="
echo " OakstrattonIMA Setup"
echo "=============================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---- Backend ----
echo ""
echo "→ Setting up Python backend..."
cd "$ROOT_DIR/backend"

if [ ! -f ".env" ]; then
    cp ../.env.example .env
    echo "  ✓ Created backend .env from .env.example"
    echo "  ! Edit .env and fill in your credentials before running"
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✓ Python dependencies installed"

# ---- Frontend ----
echo ""
echo "→ Setting up Node frontend..."
cd "$ROOT_DIR/frontend"

if [ ! -f ".env" ]; then
    echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
    echo "  ✓ Created frontend .env"
fi

npm install --silent
echo "  ✓ Node dependencies installed"

echo ""
echo "=============================="
echo " Setup complete!"
echo ""
echo " Next steps:"
echo "   1. Edit .env with your credentials"
echo "   2. Start Postgres & Redis (or use Docker Compose)"
echo "   3. Run: ./scripts/dev.sh"
echo "=============================="
