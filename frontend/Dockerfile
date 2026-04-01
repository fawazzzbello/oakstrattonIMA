# Stage 1: Build
# Build context: repo root. Root Directory must be blank in Railway.
FROM node:20-alpine AS builder

WORKDIR /app

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

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost:80/health || exit 1

# start.sh substitutes ${BACKEND_URL} in the nginx template using sed,
# then starts nginx. Set BACKEND_URL on the Railway frontend service to
# your backend URL, e.g. https://oakstrattonima-backend.up.railway.app
CMD ["/start.sh"]
