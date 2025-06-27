#!/bin/bash

# Railway startup script for JD Engineering Monitoring API
# Handles dynamic PORT environment variable from Railway

# Get port from environment variable, default to 8000 if not set
PORT=${PORT:-8000}

echo "🚀 Starting JD Engineering Monitoring API on port $PORT"
echo "📊 Environment: ${RAILWAY_ENVIRONMENT:-development}"
echo "🗄️ Database: ${DATABASE_URL:+Connected}"

# Start uvicorn with proper port
exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --log-level info 