FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Create directories
RUN mkdir -p assets/cache templates

# Set environment
ENV PYTHONPATH=/app

# Expose port
EXPOSE $PORT

# FIXED: Use gunicorn instead of uvicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app