# JD Engineering Tablet Monitor - Setup Guide

## 📱 Quick Setup (5 minutes)

### Step 1: Install Termux
1. Download Termux from F-Droid: https://f-droid.org/packages/com.termux/
2. Install and open Termux

### Step 2: Install Python and Dependencies
```bash
# Update packages
pkg update && pkg upgrade

# Install Python and required tools
pkg install python git curl

# Install Python requests library
pip install requests
```

### Step 3: Install Termux:API (Optional but Recommended)
1. Download Termux:API from F-Droid: https://f-droid.org/packages/com.termux.api/
2. Install the app
3. In Termux, install the API package:
```bash
pkg install termux-api
```

### Step 4: Download the Monitoring Scripts
```bash
# Create a directory for the monitor
mkdir ~/jd-monitor
cd ~/jd-monitor

# Download the working script (copy from your development environment)
# You need to transfer these files to your tablet:
# - tablet_client_working.py
# - start_monitoring_simple.sh
```

### Step 5: Make Scripts Executable
```bash
chmod +x start_monitoring_simple.sh
```

### Step 6: Start Monitoring
```bash
# Simple way - just run the startup script
./start_monitoring_simple.sh

# Or run the Python script directly
python tablet_client_working.py
```

---

## 🔧 What the Monitor Does

### Core Features
- **Battery Monitoring**: Tracks battery level, temperature, and charging status
- **WiFi Monitoring**: Monitors signal strength, connection status, and connectivity
- **MYOB Session Tracking**: Detects MYOB applications and monitors for timeout risks
- **Barcode Scanner Detection**: Identifies when barcode scanning apps are active
- **User Activity Detection**: Uses accelerometer to detect user interaction
- **Session Event Generation**: Creates events for timeouts and scanner activity

### Data Collection
The monitor collects data every 30 seconds and sends it to:
- **API Endpoint**: https://jd-engineering-monitoring-api-production.up.railway.app/tablet-metrics
- **Dashboard**: https://jd-engineering-monitoring-api-production.up.railway.app/dashboard

### Monitored Applications
- **MYOB**: Detects "myob", "accountright", "com.myob" processes
- **Barcode Scanners**: Detects "scanner", "barcode", "zebra", "honeywell", "datalogic" processes

---

## 📊 Output Examples

### Successful Data Collection
```
🚀 Tablet Monitor Started
📱 Device: tablet_electrical_dept
🆔 Session: abc123-def456-ghi789

📊 Collecting data at 14:30:15
✅ Data sent - Battery: 85% | MYOB: True | Scanner: False
```

### MYOB Timeout Detection
```
📊 Collecting data at 14:35:45
⚠️  MYOB timeout risk detected - 320s inactive
✅ Data sent - Battery: 83% | MYOB: True | Scanner: False
```

### Scanner Activity Detection
```
📊 Collecting data at 14:40:20
🔍 Barcode scanner activity detected
✅ Data sent - Battery: 81% | MYOB: False | Scanner: True
```

---

## 🛠️ Troubleshooting

### Common Issues

#### "Python not found"
```bash
pkg install python
```

#### "requests module not found"
```bash
pip install requests
```

#### "termux-battery-status not found"
```bash
# Install Termux:API app from F-Droid first, then:
pkg install termux-api
```

#### "Permission denied" for scripts
```bash
chmod +x start_monitoring_simple.sh
chmod +x tablet_client_working.py
```

#### API Connection Issues
- Check internet connection
- Verify the API URL is accessible
- Check if the API token is correct

### Testing the Setup
```bash
# Test if the script works
python3 test_working_script.py

# Test API connectivity
curl -H "Authorization: Bearer ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681" \
     https://jd-engineering-monitoring-api-production.up.railway.app/health
```

---

## 🔄 Running as a Service

### Option 1: Background Process
```bash
# Start in background
nohup python tablet_client_working.py > monitor.log 2>&1 &

# Check if running
ps aux | grep tablet_client

# Stop the process
pkill -f tablet_client_working.py
```

### Option 2: Termux Boot (Advanced)
1. Install Termux:Boot from F-Droid
2. Create startup script in `~/.termux/boot/`
3. The monitor will start automatically when the device boots

---

## 📈 Monitoring Dashboard

Access the live dashboard at:
https://jd-engineering-monitoring-api-production.up.railway.app/dashboard

### Dashboard Features
- Real-time device status
- Battery level monitoring
- MYOB session tracking
- Scanner activity logs
- Network connectivity status
- Interactive charts and filters

---

## 🔒 Security Notes

- The API token is embedded in the script for simplicity
- Data is sent over HTTPS
- No sensitive personal data is collected
- Only system metrics and app states are monitored

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify internet connectivity
3. Ensure all dependencies are installed
4. Check the monitor.log file for error messages

The system is designed to be robust and will continue running even if some features fail. 