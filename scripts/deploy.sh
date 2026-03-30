#!/usr/bin/env bash
# ============================================================
# OakstrattonIMA — Railway Deployment Helper
# Requires Railway CLI: npm install -g @railway/cli
# ============================================================
set -euo pipefail

echo "Deploying OakstrattonIMA to Railway..."

# Ensure we're on the right branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "→ Branch: $BRANCH"

# Build frontend first
echo ""
echo "→ Building frontend..."
cd frontend
npm ci --silent
npm run build
echo "  ✓ Frontend built"
cd ..

# Commit dist if needed (for static deploy strategy)
# git add frontend/dist -f && git commit -m "chore: build frontend for deploy"

# Railway deploy
echo ""
echo "→ Deploying to Railway..."
railway up --detach

echo ""
echo "=============================="
echo " Deployment triggered!"
echo " Monitor at: https://railway.app/dashboard"
echo "=============================="
