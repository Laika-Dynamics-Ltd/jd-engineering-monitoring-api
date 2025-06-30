#!/data/data/com.termux/files/usr/bin/bash

# Auto-Start Setup for Tablet Monitoring
# This script sets up the tablet to automatically start monitoring after boot

echo "🚀 Setting up Auto-Start for Tablet Monitoring"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "tablet_client_bulletproof.py" ]; then
    echo "❌ Error: tablet_client_bulletproof.py not found in current directory"
    echo "💡 Please run this script from the directory containing the monitoring script"
    exit 1
fi

# Check if monitor-control.sh exists
if [ ! -f "monitor-control.sh" ]; then
    echo "❌ Error: monitor-control.sh not found"
    echo "💡 Please ensure monitor-control.sh is in the same directory"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x tablet_client_bulletproof.py
chmod +x monitor-control.sh

# Create Termux boot directory if it doesn't exist
BOOT_DIR="$HOME/.termux/boot"
if [ ! -d "$BOOT_DIR" ]; then
    echo "📁 Creating Termux boot directory..."
    mkdir -p "$BOOT_DIR"
fi

# Create auto-start script for Termux
AUTO_START_SCRIPT="$BOOT_DIR/start-monitoring"
echo "📝 Creating auto-start script: $AUTO_START_SCRIPT"

cat > "$AUTO_START_SCRIPT" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# Auto-start tablet monitoring after boot
# This script runs automatically when Termux starts

# Wait for system to be ready
sleep 10

# Change to monitoring directory
cd ~/monitoring

# Start monitoring if not already running
if [ -f "monitor-control.sh" ]; then
    ./monitor-control.sh start
    echo "✅ Auto-started tablet monitoring at $(date)"
else
    echo "❌ monitor-control.sh not found in ~/monitoring"
fi
EOF

# Make auto-start script executable
chmod +x "$AUTO_START_SCRIPT"

# Set up directory structure
MONITORING_DIR="$HOME/monitoring"
echo "📁 Setting up monitoring directory: $MONITORING_DIR"

if [ ! -d "$MONITORING_DIR" ]; then
    mkdir -p "$MONITORING_DIR"
fi

# Copy scripts to monitoring directory
echo "📋 Copying scripts to monitoring directory..."
cp tablet_client_bulletproof.py "$MONITORING_DIR/"
cp monitor-control.sh "$MONITORING_DIR/"

# Update monitor-control.sh to use bulletproof script
sed -i 's/tablet_client\.py/tablet_client_bulletproof.py/g' "$MONITORING_DIR/monitor-control.sh"

echo ""
echo "✅ Auto-start setup complete!"
echo "==============================================="
echo "📁 Monitoring directory: $MONITORING_DIR"
echo "🚀 Auto-start script: $AUTO_START_SCRIPT"
echo ""
echo "📱 Manual Controls:"
echo "  Start:   ~/monitoring/monitor-control.sh start"
echo "  Stop:    ~/monitoring/monitor-control.sh stop"
echo "  Status:  ~/monitoring/monitor-control.sh status"
echo "  Logs:    ~/monitoring/monitor-control.sh logs"
echo ""
echo "🔄 To start monitoring now:"
echo "  cd ~/monitoring && ./monitor-control.sh start"
echo ""
echo "🔋 To test auto-start:"
echo "  1. Restart Termux app"
echo "  2. Wait ~15 seconds"
echo "  3. Check: cd ~/monitoring && ./monitor-control.sh status"
echo ""
echo "💡 The monitoring will now start automatically every time the tablet boots!" 