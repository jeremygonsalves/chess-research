# Base Dockerfile - can be used for all services
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Stockfish (if available in apt)
RUN apt-get update && apt-get install -y stockfish || echo "Stockfish not in apt, install manually"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Default command (override in docker-compose)
CMD ["python", "-m", "app.api.main"]

