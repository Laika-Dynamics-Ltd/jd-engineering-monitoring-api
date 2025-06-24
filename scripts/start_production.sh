#!/bin/sh
# Production startup script for Railway deployment
# Handles dynamic PORT assignment from Railway

# Railway provides PORT as an environment variable
# Default to 8000 if not set (for local testing)
PORT=${PORT:-8000}

# Log startup information
echo "🚀 Starting J&D McLennan Engineering Production Server"
echo "📍 Port: $PORT"
echo "🔧 Workers: ${GUNICORN_WORKERS:-4}"
echo "🌍 Environment: ${ENVIRONMENT:-production}"

# Start Gunicorn with Uvicorn workers
exec gunicorn main_production:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${GUNICORN_WORKERS:-4} \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --timeout 120 \
    --keep-alive 5 