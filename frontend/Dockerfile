# Stage 1: Build
# Build context: repo root. Root Directory must be blank in Railway.
FROM node:20-alpine AS builder

WORKDIR /app

# VITE_API_URL is baked into the JS bundle at build time by Vite.
# Set it as a Railway Variable on the frontend service:
#   VITE_API_URL=https://oakstrattonima-backend.up.railway.app/api/v1
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY frontend/package*.json ./
RUN npm ci --silent

COPY frontend/ .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/templates/default.conf.template
COPY frontend/start.sh /start.sh
RUN chmod +x /start.sh

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost:${PORT:-80}/health || exit 1

CMD ["/start.sh"]
