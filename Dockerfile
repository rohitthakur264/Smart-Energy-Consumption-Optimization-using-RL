# ==========================================
# Stage 1: Build the React/Vite Frontend
# ==========================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package.json and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the rest of the frontend source code and build
COPY frontend/ ./
# Set the API URL to be relative so it uses the same origin as the hosted frontend
ENV VITE_API_URL=/api
RUN npm run build

# ==========================================
# Stage 2: Build the FastAPI Backend
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for ML libraries and OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
# (frontend and other unused folders are excluded via .dockerignore)
COPY . .

# Copy the built frontend static files from Stage 1 into the location FastAPI expects
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using sh to evaluate environment variables
# This allows cloud providers (like Hugging Face or Render) to dynamically assign a port
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
