#!/data/data/com.termux/files/usr/bin/bash
# JD Engineering Tablet Monitoring Restart Script

echo "🔄 Restarting JD Engineering Tablet Monitoring"
echo "=" * 50

# Kill any existing monitoring processes
echo "🛑 Stopping existing monitoring processes..."
pkill -f tablet_client.py
pkill -f python.*tablet_client
sleep 2

# Verify Python and script exist
echo "🔍 Checking environment..."
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Run: pkg install python"
    exit 1
fi

if [ ! -f "tablet_client.py" ]; then
    echo "❌ tablet_client.py not found in current directory"
    echo "Current directory: $(pwd)"
    echo "Files: $(ls -la)"
    exit 1
fi

# Test script syntax
echo "🧪 Testing script syntax..."
python -m py_compile tablet_client.py
if [ $? -ne 0 ]; then
    echo "❌ Script has syntax errors"
    exit 1
fi

echo "✅ Script syntax is valid"

# Test basic functionality
echo "🔋 Testing basic functionality..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from tablet_client import AdvancedTabletMonitor
    monitor = AdvancedTabletMonitor()
    print('✅ Script imports successfully')
    print('✅ Class initializes successfully')
    if hasattr(monitor, 'run_monitoring_loop'):
        print('✅ run_monitoring_loop method exists')
    else:
        print('❌ run_monitoring_loop method missing')
        sys.exit(1)
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi

echo "✅ Basic functionality test passed"

# Start monitoring
echo "🚀 Starting advanced monitoring..."
echo "Press Ctrl+C to stop monitoring"
echo ""

python tablet_client.py 