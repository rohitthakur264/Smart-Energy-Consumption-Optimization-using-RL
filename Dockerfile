# Multi-stage build: Build frontend + backend
# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./
COPY frontend/index.html ./
COPY frontend/src ./src
COPY frontend/public ./public

# Install dependencies and build
RUN npm install && npm run build

# Stage 2: Python backend
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set pip options for better network handling
ENV PIP_TIMEOUT=60 \
    PIP_RETRIES=3 \
    PIP_RETRY_DELAY=5

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with retry and timeout
RUN pip install --no-cache-dir --timeout=60 --retries=3 -r requirements.txt

# Copy the rest of the application code (backend)
COPY backend ./backend
COPY thermal_physics.py .
COPY preprocess.py .
COPY train_agent_v2.py .
COPY evaluate_agent_v2.py .
COPY enhanced_env.py .
COPY multi_agent_env.py .
COPY energy_data_cleaned.csv .
COPY models ./models

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create uploads directory
RUN mkdir -p uploads

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
