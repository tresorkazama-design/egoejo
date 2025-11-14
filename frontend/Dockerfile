# Phase 1: Construction (Build)
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json .
COPY package-lock.json .
RUN npm install
COPY . .
RUN npm run build

# Phase 2: Serveur (Serve)
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Vite utilise le port 5173 en dev, mais Nginx utilise 80 en production.
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]