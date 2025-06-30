#!/data/data/com.termux/files/usr/bin/bash
"""
JD Engineering Quick Tablet Deployment Script
Automatically downloads, configures, and starts monitoring in background
"""

echo "🚀 JD ENGINEERING TABLET QUICK DEPLOY"
echo "====================================="

# Check if we're on test or electrical tablet
echo "Which tablet is this?"
echo "1) Test Tablet (TeamViewer testing)"
echo "2) Electrical Department (Production MYOB)"
read -p "Enter choice (1 or 2): " TABLET_TYPE

# Set script name based on choice
if [ "$TABLET_TYPE" = "1" ]; then
    SCRIPT_NAME="test_tablet_client.py"
    TABLET_DESC="Test Tablet"
    echo "📱 Configuring for: TEST TABLET"
elif [ "$TABLET_TYPE" = "2" ]; then
    SCRIPT_NAME="electrical_tablet_client.py"
    TABLET_DESC="Electrical Department"
    echo "📱 Configuring for: ELECTRICAL DEPARTMENT"
else
    echo "❌ Invalid choice. Exiting."
    exit 1
fi

echo "🔧 Installing dependencies..."
pkg update -y
pkg install python termux-api curl -y
pip install requests

echo "📥 Downloading monitoring script..."
curl -L -o $SCRIPT_NAME "https://raw.githubusercontent.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api/main/scripts/tablet_deployment/$SCRIPT_NAME"

# Make executable
chmod +x $SCRIPT_NAME

echo "🎯 Testing connection to API..."
if curl -s https://jd-engineering-monitoring-api-production-5d93.up.railway.app/health > /dev/null; then
    echo "✅ API connection successful"
else
    echo "⚠️ API connection failed - check WiFi"
fi

echo "🚀 Starting monitoring in background..."
nohup python $SCRIPT_NAME > monitoring.log 2>&1 &
MONITOR_PID=$!

echo "✅ Monitoring started!"
echo "📊 Process ID: $MONITOR_PID"
echo "📋 Log file: monitoring.log"
echo ""
echo "🔍 USEFUL COMMANDS:"
echo "   View logs:     tail -f monitoring.log"
echo "   Check status:  ps aux | grep python"
echo "   Stop monitor:  pkill -f $SCRIPT_NAME"
echo "   Restart:       bash quick_deploy.sh"
echo ""
echo "🎉 $TABLET_DESC monitoring is now running!"
echo "📱 Ready for 10:30am meeting with Brad" 