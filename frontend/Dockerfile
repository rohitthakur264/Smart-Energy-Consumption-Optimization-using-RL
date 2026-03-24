# Smart Energy RL Platform — Frontend Container
# Stage 1: Build the React app
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY index.html .
COPY vite.config.js .
COPY eslint.config.js .
COPY src ./src
COPY public ./public

# Build with production API URL (same origin, proxied by nginx)
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
