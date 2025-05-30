FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV USER_SERVICE_PORT=8001
ENV RESTAURANT_SERVICE_PORT=8002
ENV DELIVERY_SERVICE_PORT=8003
ENV GRAPHQL_GATEWAY_PORT=8000

# Copy the startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose all service ports
EXPOSE 8000 8001 8002 8003

# Use the startup script as entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"] 