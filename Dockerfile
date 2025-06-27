# Use Python 3.11 slim image for Railway compatibility
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and startup script
COPY . .
COPY start.sh .

# Create static directory if it doesn't exist
RUN mkdir -p static

# Make startup script executable
RUN chmod +x start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app \
    && chown -R app:app /app
USER app

# Expose port 8000 (Railway will set PORT environment variable)
EXPOSE 8000

# Health check using environment variable properly
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os, requests; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/health', timeout=5)" || exit 1

# Use startup script to handle PORT variable correctly
CMD ["./start.sh"]