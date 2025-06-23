# JD Engineering Tablet Advanced Monitoring Setup Guide

## 📱 Prerequisites

### 1. Install Termux
- Download **Termux** from F-Droid (recommended) or Google Play Store
- Open Termux and run initial setup

### 2. Install Termux:API
- Download **Termux:API** app from F-Droid or Google Play Store
- This provides access to Android system functions

### 3. Update Termux packages
```bash
pkg update && pkg upgrade
```

## 🔧 Installation Steps

### Step 1: Install Required Packages
```bash
# Install Python and required tools
pkg install python git curl

# Install Termux:API package
pkg install termux-api

# Install Python packages
pip install requests
```

### Step 2: Download Monitoring Scripts
```bash
# Create monitoring directory
mkdir -p ~/jd-monitoring
cd ~/jd-monitoring

# Download the advanced monitoring script
curl -o tablet_client.py https://raw.githubusercontent.com/laikadynamics/jd-engineering-monitoring-api/main/scripts/tablet_client.py

# Download the test script
curl -o test_termux_api.py https://raw.githubusercontent.com/laikadynamics/jd-engineering-monitoring-api/main/scripts/test_termux_api.py

# Make scripts executable
chmod +x tablet_client.py test_termux_api.py
```

### Step 3: Test Termux:API Functions
```bash
# Run the comprehensive test suite
python test_termux_api.py
```

**Expected Results:**
- ✅ Battery Status: Should show battery percentage, temperature, charging status
- ✅ WiFi Connection Info: Should show network details, signal strength
- ✅ Accelerometer Sensor: Should detect device movement
- ✅ Process monitoring: Should list running Android processes

If any tests fail, ensure:
1. Termux:API app is installed
2. Required permissions are granted
3. Run `pkg install termux-api` again

### Step 4: Configure Device Settings

#### Grant Required Permissions
Go to Android Settings → Apps → Termux:API → Permissions and enable:
- 📍 **Location** (for WiFi scanning)
- 📷 **Camera** (for barcode scanner detection)
- 🎤 **Microphone** (for audio monitoring)
- 📱 **Phone** (for device info)
- 🔔 **Notifications** (for system events)
- 💾 **Storage** (for file access)

#### Device Configuration
1. **Keep Screen On**: Settings → Developer Options → Stay Awake (ON)
2. **Disable Sleep**: Settings → Display → Sleep → Never
3. **Background Apps**: Settings → Battery → Optimize battery usage → Termux (Don't optimize)

## 🚀 Running the Advanced Monitor

### Start Monitoring
```bash
cd ~/jd-monitoring
python tablet_client.py
```

### Expected Output:
```
🚀 Advanced monitoring initialized for tablet_electrical_dept
📱 Session ID: abc123-def456-ghi789
🚀 Starting advanced tablet monitoring for tablet_electrical_dept
📡 Monitoring MYOB sessions and barcode scanner events
🎯 API endpoint: https://jd-engineering-monitoring-api-production.up.railway.app
📊 Collecting comprehensive data at 2025-06-23 10:30:00
✅ Data sent - MYOB: False, Scanner: False
```

## 📊 What the Advanced Monitor Detects

### 🏢 MYOB Session Monitoring
- **Process Detection**: Scans for MYOB-related processes
- **Session Timeout Risk**: Detects 5+ minutes of user inactivity while MYOB is active
- **Session Events**: Logs login, logout, timeout events

### 📷 Barcode Scanner Events
- **Scanner Apps**: Detects Zebra, Honeywell, DataLogic scanner processes
- **Scanner Activity**: Monitors when barcode scanning is active
- **Hardware Integration**: Tracks physical scanner device connections

### 📱 System Monitoring
- **Battery**: Level, temperature, charging status, health
- **Network**: WiFi signal, connectivity, speed, network changes
- **Performance**: Memory usage, CPU load, storage space
- **User Interaction**: Movement detection via accelerometer
- **Notifications**: System alerts, app errors, network issues

### 🔍 Advanced Features
- **Real-time Process Monitoring**: Continuously scans for MYOB and scanner processes
- **Interaction Detection**: Uses accelerometer to detect user activity
- **Session Timeout Prediction**: Warns before MYOB sessions timeout
- **Network Connectivity Testing**: Multi-endpoint connectivity verification
- **Comprehensive Logging**: Detailed logs for troubleshooting

## 🛠️ Troubleshooting

### Common Issues

#### "Command not found: termux-*"
```bash
# Reinstall termux-api
pkg install termux-api
# Restart Termux completely
```

#### "Permission denied" errors
- Go to Android Settings → Apps → Termux:API → Permissions
- Enable all requested permissions
- Restart both Termux and Termux:API apps

#### "Network connectivity failed"
- Check WiFi connection
- Verify API endpoint is reachable
- Test with: `ping 8.8.8.8`

#### "Process detection not working"
- Ensure MYOB or scanner apps are actually running
- Check process names with: `ps -A | grep -i myob`
- Verify package name patterns in script

### Debug Mode
To run with detailed debugging:
```bash
# Add debug prints
python -u tablet_client.py 2>&1 | tee monitoring.log
```

### Restart Monitoring Service
```bash
# Kill existing monitoring
pkill -f tablet_client.py

# Start fresh
python tablet_client.py
```

## 📈 Dashboard Integration

The advanced monitoring sends data to:
- **API Endpoint**: https://jd-engineering-monitoring-api-production.up.railway.app
- **Dashboard**: https://jd-engineering-monitoring-api-production.up.railway.app/dashboard

Data includes:
- Real-time MYOB session status
- Barcode scanner activity alerts
- Session timeout warnings
- Comprehensive system metrics

## 🔄 Auto-Start Setup (Optional)

To automatically start monitoring on device boot:

### Create Startup Script
```bash
cat > ~/jd-monitoring/start_monitoring.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/jd-monitoring
python tablet_client.py
EOF

chmod +x ~/jd-monitoring/start_monitoring.sh
```

### Using Termux:Boot (if available)
1. Install Termux:Boot from F-Droid
2. Create `~/.termux/boot/start-monitoring`
3. Add: `~/jd-monitoring/start_monitoring.sh`

## 📞 Support

For issues or questions:
1. Check the monitoring logs
2. Run the test script to verify Termux:API
3. Verify network connectivity to the API
4. Check the dashboard for received data

**API Status**: https://jd-engineering-monitoring-api-production.up.railway.app/health 