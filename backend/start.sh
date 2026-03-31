#!/bin/bash
set -e

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set."
  echo "Ensure the Railway PostgreSQL plugin is linked to this service."
  exit 1
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting Uvicorn server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2
