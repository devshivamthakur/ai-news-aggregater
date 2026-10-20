# ---- build ----
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- serve ----
# Static assets served by nginx. `nginx.conf` is rendered through envsubst so
# the API upstream can be changed at runtime via BACKEND_URL.
FROM nginx:1.27-alpine AS runner
WORKDIR /usr/share/nginx/html

ENV BACKEND_URL=http://localhost:8000

COPY --from=builder /app/dist ./dist
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
