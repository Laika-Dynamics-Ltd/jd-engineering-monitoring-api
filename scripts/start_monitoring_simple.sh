#!/data/data/com.termux/files/usr/bin/bash

# JD Engineering Tablet Monitor - Simple Startup Script
# This script starts the working tablet monitoring client

echo "🚀 JD Engineering Tablet Monitor"
echo "=================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python in Termux:"
    echo "   pkg install python"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking required packages..."

python -c "import requests" 2>/dev/null || {
    echo "❌ requests module not found. Installing..."
    pip install requests
}

python -c "import uuid" 2>/dev/null || {
    echo "❌ uuid module not found (should be built-in)"
    exit 1
}

echo "✅ All packages available"

# Check if the working script exists
SCRIPT_PATH="tablet_client_working.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ $SCRIPT_PATH not found in current directory"
    echo "Please ensure the script is in the same folder as this startup script"
    exit 1
fi

echo "✅ Script found: $SCRIPT_PATH"

# Check if Termux:API is available
if ! command -v termux-battery-status &> /dev/null; then
    echo "⚠️  Termux:API not found. Some features may not work."
    echo "   Install from: https://f-droid.org/packages/com.termux.api/"
    echo "   Then run: pkg install termux-api"
    echo ""
    echo "Continuing without Termux:API (basic monitoring only)..."
else
    echo "✅ Termux:API available"
fi

echo ""
echo "🎯 Starting tablet monitoring..."
echo "Press Ctrl+C to stop monitoring"
echo ""

# Start the monitoring script
python "$SCRIPT_PATH" 