#!/data/data/com.termux/files/usr/bin/bash

# JD Engineering Tablet Monitor - One-Click Start
echo "🚀 Starting JD Engineering Tablet Monitor..."

# Install dependencies if needed
python -c "import requests" 2>/dev/null || pip install requests

# Start monitoring
python tablet_client_working.py 