# 📱 Manual Tablet Deployment Guide

## Files to Copy to Tablet

You only need these 2 files on your tablet:

1. **`tablet_client_working.py`** - The main monitoring script
2. **`start_monitoring_simple.sh`** - Easy startup script

## Quick Deployment Steps

### Step 1: Copy Files to Tablet
Transfer these files to your Android tablet using any method:
- USB cable + file manager
- Email attachments
- Cloud storage (Google Drive, Dropbox)
- ADB push
- Bluetooth file transfer

### Step 2: Place Files in Termux
```bash
# In Termux on the tablet:
cd ~
mkdir jd-monitor
cd jd-monitor

# Move your copied files here
# (files should be in ~/jd-monitor/)
```

### Step 3: Make Executable
```bash
chmod +x start_monitoring_simple.sh
chmod +x tablet_client_working.py
```

### Step 4: Install Dependencies (One Time Only)
```bash
# Update Termux
pkg update

# Install Python and requests
pkg install python
pip install requests

# Optional: Install Termux:API for better monitoring
pkg install termux-api
```

### Step 5: Start Monitoring
```bash
# Easy way - run the startup script
./start_monitoring_simple.sh

# Or directly run the Python script
python tablet_client_working.py
```

## What You'll See When It Works

```
🚀 JD Engineering Tablet Monitor
==================================
📦 Checking required packages...
✅ All packages available
✅ Script found: tablet_client_working.py
✅ Termux:API available

🎯 Starting tablet monitoring...
Press Ctrl+C to stop monitoring

🚀 Tablet Monitor Started
📱 Device: tablet_electrical_dept
🆔 Session: abc123-def456-ghi789

📊 Collecting data at 14:30:15
✅ Data sent - Battery: 85% | MYOB: False | Scanner: False
```

## Troubleshooting

### "Permission denied"
```bash
chmod +x *.sh *.py
```

### "Python not found"
```bash
pkg install python
```

### "requests not found"
```bash
pip install requests
```

### API Connection Issues
- Check WiFi connection
- Verify tablet can access internet
- The script will retry automatically

## Running in Background

To keep monitoring running when you close Termux:
```bash
nohup python tablet_client_working.py > monitor.log 2>&1 &
```

To stop background monitoring:
```bash
pkill -f tablet_client_working.py
```

## File Locations

- **Script files**: `~/jd-monitor/`
- **Log file**: `~/jd-monitor/monitor.log`
- **Termux home**: `/data/data/com.termux/files/home/` 