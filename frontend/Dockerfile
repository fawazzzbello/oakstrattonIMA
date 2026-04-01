# Stage 1: Build
# Build context: frontend/ directory (set Root Directory = "frontend" in Railway)
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --silent

COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

RUN apk add --no-cache bash

COPY --from=builder /app/dist /usr/share/nginx/html

# Store nginx template; envsubst will render it at startup
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost:80/health || exit 1

# envsubst replaces ${BACKEND_URL} in nginx template before nginx starts.
# Set BACKEND_URL on the Railway frontend service to your backend URL,
# e.g. https://oakstrattonima-backend.up.railway.app
CMD ["/bin/sh", "-c", "BACKEND_URL=${BACKEND_URL:-http://localhost:8000} envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
