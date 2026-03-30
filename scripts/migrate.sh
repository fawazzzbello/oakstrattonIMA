#!/usr/bin/env bash
# ============================================================
# OakstrattonIMA — Database Migration Helper
# Usage:
#   ./scripts/migrate.sh                  # run all pending migrations
#   ./scripts/migrate.sh new "add users"  # create new migration
#   ./scripts/migrate.sh rollback         # downgrade one step
#   ./scripts/migrate.sh status           # show current migration
# ============================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

ACTION="${1:-upgrade}"

case "$ACTION" in
    upgrade|run|"")
        echo "→ Running all pending migrations..."
        alembic upgrade head
        echo "  ✓ Done"
        ;;
    new|create)
        MSG="${2:-migration}"
        echo "→ Creating migration: $MSG"
        alembic revision --autogenerate -m "$MSG"
        echo "  ✓ Created in migrations/versions/"
        ;;
    rollback|down)
        echo "→ Rolling back one migration..."
        alembic downgrade -1
        echo "  ✓ Done"
        ;;
    status|current)
        alembic current
        ;;
    history)
        alembic history --verbose
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo "Usage: migrate.sh [upgrade|new '<msg>'|rollback|status|history]"
        exit 1
        ;;
esac
