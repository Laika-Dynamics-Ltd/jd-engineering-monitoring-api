# Use Python 3.11 slim image for Railway
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including nginx and supervisor
RUN apt-get update && apt-get install -y \
    gcc \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy configs
RUN cp supervisord.conf /etc/supervisor/conf.d/supervisord.conf && \
    cp nginx.conf /etc/nginx/nginx.conf

# Create necessary directories and fix permissions
RUN mkdir -p /var/log/supervisor /var/log/nginx /tmp /var/cache/nginx /var/run && \
    chmod -R 777 /tmp /var/log /var/cache/nginx /var/run

# Make start script executable
RUN chmod +x start.sh

# Create non-root user for security (but nginx needs to run as root)
RUN useradd --create-home --shell /bin/bash app

# Expose Railway's port
EXPOSE 8080

# Health check for API
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Use start script to configure and launch services
CMD ["./start.sh"]