import subprocess
import time
import os
import sys
import signal
import atexit

# Global process references
streamlit_process = None

def cleanup():
    """Clean up subprocess on exit"""
    global streamlit_process
    if streamlit_process:
        streamlit_process.terminate()
        streamlit_process.wait()

# Register cleanup
atexit.register(cleanup)

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start Streamlit in background
print("🎨 Starting Streamlit dashboard...")
streamlit_process = subprocess.Popen([
    sys.executable, "-m", "streamlit", "run", 
    "streamlit_app.py",
    "--server.port", "8501",
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--browser.gatherUsageStats", "false"
], env={**os.environ, "API_TOKEN": os.getenv("API_TOKEN", "")})

# Give Streamlit time to start
time.sleep(5)

# Import and run FastAPI
print("📡 Starting FastAPI...")
import uvicorn
from main import app

# Run FastAPI
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port) 