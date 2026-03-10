# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set pip options for better network handling
ENV PIP_TIMEOUT=60 \
    PIP_RETRIES=3 \
    PIP_RETRY_DELAY=5

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies with retry and timeout
RUN pip install --no-cache-dir --timeout=60 --retries=3 -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose the port the app runs on
# Hugging Face Spaces uses 7860 by default
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
