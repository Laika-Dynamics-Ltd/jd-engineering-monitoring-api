#!/bin/bash

# Start script for Railway deployment
# Runs both FastAPI and Streamlit services

echo "🚀 Starting JD Engineering Monitoring Services..."

# Start FastAPI in the background on port 8000
echo "📡 Starting API server on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait a moment for API to start
sleep 5

# Check if API is running
if ps -p $API_PID > /dev/null; then
    echo "✅ API server started successfully (PID: $API_PID)"
else
    echo "❌ Failed to start API server"
    exit 1
fi

# Start Streamlit on Railway's PORT (or 8501 for local)
PORT=${PORT:-8501}
echo "🎨 Starting Streamlit UI on port $PORT..."

# Configure Streamlit
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Pass API token to Streamlit
export API_TOKEN=$API_TOKEN

# Run Streamlit (this blocks and keeps the container running)
streamlit run streamlit_app.py 