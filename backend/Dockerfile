# Smart Energy RL Platform — Backend Container
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
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

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
