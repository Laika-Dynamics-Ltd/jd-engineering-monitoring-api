#!/bin/bash

# Start script for Railway deployment
# For now, focus on getting API working first

echo "🚀 Starting JD Engineering Monitoring API..."

# Get the PORT from Railway or default to 8000
PORT=${PORT:-8000}

echo "📡 Starting API server on port $PORT..."

# Start FastAPI directly - streamlit can be added later
exec uvicorn main:app --host 0.0.0.0 --port $PORT 