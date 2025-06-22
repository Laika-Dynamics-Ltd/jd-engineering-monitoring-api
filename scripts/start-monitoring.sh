#!/data/data/com.termux/files/usr/bin/bash

# Auto-start script for Termux Boot
# Place this in ~/.termux/boot/start-monitoring.sh

echo "🔄 Auto-start monitoring script initiated..."
echo "$(date): Boot script started" >> ~/boot.log

# Wait for network connectivity
echo "⏳ Waiting for network connectivity..."
for i in {1..30}; do
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo "✅ Network is ready"
        break
    fi
    sleep 2
done

# Additional wait to ensure system is stable
echo "⏳ Waiting for system stability..."
sleep 30

# Change to home directory
cd /data/data/com.termux/files/home

# Check if monitoring script exists
if [ ! -f "tablet_client.py" ]; then
    echo "❌ tablet_client.py not found in home directory"
    echo "$(date): tablet_client.py not found" >> ~/boot.log
    exit 1
fi

# Check if control script exists
if [ ! -f "monitor-control.sh" ]; then
    echo "❌ monitor-control.sh not found in home directory"
    echo "$(date): monitor-control.sh not found" >> ~/boot.log
    exit 1
fi

# Make control script executable
chmod +x monitor-control.sh

echo "🚀 Starting tablet monitoring service..."

# Start monitoring using the control script
./monitor-control.sh start

# Keep session alive with wake lock
echo "🔒 Acquiring wake lock..."
termux-wake-lock

# Log successful start
echo "$(date): Monitoring started successfully" >> ~/boot.log
echo "✅ Auto-start complete - monitoring service is running" 