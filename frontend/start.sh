#!/bin/sh
set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "Starting nginx with BACKEND_URL=${BACKEND_URL}"

# Substitute ${BACKEND_URL} in the nginx template
sed "s|\${BACKEND_URL}|${BACKEND_URL}|g" \
    /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
