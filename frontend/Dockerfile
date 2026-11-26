# ── Frontend Dockerfile (multi-stage) ────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration production

# ── Serve with Nginx ─────────────────────────────────────────────────────────
FROM nginx:alpine

COPY --from=build /app/dist/cleanair-companion/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost/ || exit 1

