#!/bin/sh
set -e

PORT="${PORT:-80}"

echo "Starting nginx on port ${PORT}"

sed "s|\${PORT}|${PORT}|g" \
    /etc/nginx/templates/default.conf.template \
    > /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
