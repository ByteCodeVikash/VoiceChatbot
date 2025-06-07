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
RUN mkdir -p assets/cache

# Set environment
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Start command
CMD ["python", "app.py"]