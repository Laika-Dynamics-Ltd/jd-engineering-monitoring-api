#!/bin/bash

# Start script for Railway deployment
# Runs both FastAPI and Streamlit services

echo "🚀 Starting JD Engineering Monitoring Services..."

# On Railway, we need to run everything on the single PORT provided
PORT=${PORT:-8000}

# Check if we're on Railway
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "🚂 Running on Railway - Single port mode on $PORT"
    
    # Configure Streamlit for internal port
    export STREAMLIT_SERVER_PORT=8501
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    export API_TOKEN=$API_TOKEN
    
    # Start Streamlit in background on internal port
    echo "🎨 Starting Streamlit UI on internal port 8501..."
    streamlit run streamlit_app.py &
    STREAMLIT_PID=$!
    
    # Wait for Streamlit to start
    sleep 5
    
    # Start FastAPI on Railway's PORT with proxy capabilities
    echo "📡 Starting API server on port $PORT with dashboard proxy..."
    export STREAMLIT_INTERNAL_URL="http://localhost:8501"
    exec uvicorn main:app --host 0.0.0.0 --port $PORT
else
    # Local development - run services on separate ports
    echo "💻 Running locally - Multi-port mode"
    
    # Start FastAPI on port 8000
    echo "📡 Starting API server on port 8000..."
    uvicorn main:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    
    # Configure and start Streamlit on port 8501
    export STREAMLIT_SERVER_PORT=8501
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    export API_TOKEN=$API_TOKEN
    
    echo "🎨 Starting Streamlit UI on port 8501..."
    exec streamlit run streamlit_app.py
fi 