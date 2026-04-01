# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Build context is the repo root; copy from frontend/ subdirectory
COPY frontend/package*.json ./
RUN npm ci --silent

COPY frontend/ .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

RUN apk add --no-cache bash

COPY --from=builder /app/dist /usr/share/nginx/html

# Store nginx template; envsubst will render it at startup
COPY frontend/nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost:80/health || exit 1

# envsubst replaces ${BACKEND_URL} in nginx template before nginx starts.
# Default: http://localhost:8000 (safe fallback; set BACKEND_URL on Railway
# to your backend service URL, e.g. https://backend.up.railway.app)
CMD ["/bin/sh", "-c", "BACKEND_URL=${BACKEND_URL:-http://localhost:8000} envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
