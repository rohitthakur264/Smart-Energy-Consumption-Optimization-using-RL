# Smart Energy RL Platform — Unified Single-Container Build
# Use this for single-container deployments (Render, Railway, Fly.io, HuggingFace Spaces)
# For multi-container deployment, use docker-compose.yml instead.

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/index.html ./
COPY frontend/vite.config.js ./
COPY frontend/eslint.config.js ./
COPY frontend/src ./src
COPY frontend/public ./public

RUN npm run build

# Stage 2: Python backend + serve built frontend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set pip options
ENV PIP_TIMEOUT=120 \
    PIP_RETRIES=3

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend ./backend
COPY thermal_physics.py .
COPY preprocess.py .
COPY train_agent_v2.py .
COPY evaluate_agent_v2.py .
COPY enhanced_env.py .
COPY multi_agent_env.py .
COPY app.py .

# Copy data and models
COPY energy_data_cleaned.csv .
COPY synthetic_energy_data.csv .
COPY models ./models

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
