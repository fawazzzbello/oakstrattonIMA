#!/bin/sh
set -e

PORT="${PORT:-80}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "Starting nginx on port ${PORT} with BACKEND_URL=${BACKEND_URL}"

# Substitute ${PORT} and ${BACKEND_URL} in the nginx template
sed \
    -e "s|\${PORT}|${PORT}|g" \
    -e "s|\${BACKEND_URL}|${BACKEND_URL}|g" \
    /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
