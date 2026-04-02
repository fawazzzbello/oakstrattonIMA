#!/bin/sh
set -e

PORT="${PORT:-80}"
BACKEND_URL="${BACKEND_URL:-}"

if [ -z "$BACKEND_URL" ]; then
    echo "ERROR: BACKEND_URL is not set. Set it to your backend Railway URL, e.g.:"
    echo "  https://oakstrattonima-backend.up.railway.app"
    exit 1
fi

# Strip trailing slash
BACKEND_URL="${BACKEND_URL%/}"

echo "Starting nginx on port ${PORT}"
echo "Proxying /api/ -> ${BACKEND_URL}/api/"

sed -e "s|\${PORT}|${PORT}|g" \
    -e "s|\${BACKEND_URL}|${BACKEND_URL}|g" \
    /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
