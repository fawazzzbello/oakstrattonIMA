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

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
