# 🚀 Tablet Monitoring System Deployment Guide

Complete step-by-step guide for deploying the JD Engineering Monitoring API on Railway and setting up Android tablets for monitoring.

## 📋 Prerequisites

### Hardware Requirements
- **Android Tablet** (Android 7.0+ recommended)
- **Stable WiFi Connection**
- **Power Source** (USB charger or power bank)
- **Minimum 2GB RAM** and 8GB storage

### Accounts Needed
- **Railway.app account** (free tier available)
- **GitHub account** (for code deployment)
- **PostgreSQL database** (Railway provides this)

---

## 🌐 Part 1: Railway API Deployment

### Step 1: Deploy to Railway

1. **Login to Railway**
   ```bash
   # Visit https://railway.app
   # Sign up/login with GitHub
   ```

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `jd-engineering-monitoring-api` repository
   - Click "Deploy"

3. **Add PostgreSQL Database**
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create `DATABASE_URL` variable

### Step 2: Configure Environment Variables

In Railway dashboard → Settings → Variables, add:

```bash
# Required Variables
API_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
API_TOKEN=your-api-token-for-tablets-min-20-chars
TABLET_API_KEY=backup-token-for-failover

# Optional Variables
LOG_LEVEL=info
RAILWAY_ENVIRONMENT=production
```

**Generate secure tokens:**
```bash
# On your computer:
python3 -c "import secrets; print('API_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('API_TOKEN=' + secrets.token_urlsafe(24))"
```

### Step 3: Verify Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```

2. **Expected Response:**
   ```json
   {
     "status": "healthy",
     "timestamp": "2024-01-15T10:30:00Z",
     "database": "connected",
     "environment": "production"
   }
   ```

3. **Test API Documentation**
   - Visit: `https://your-app-name.up.railway.app/docs`
   - Interactive API documentation should load

4. **Access Dashboard**
   - Visit: `https://your-app-name.up.railway.app/dashboard`
   - The Streamlit monitoring dashboard loads automatically
   - Real-time device monitoring and analytics

---

## 📱 Part 2: Android Tablet Setup

### Step 1: Install Termux

1. **Download Termux**
   - **Recommended:** F-Droid - https://f-droid.org/packages/com.termux/
   - **Alternative:** GitHub Releases - https://github.com/termux/termux-app/releases
   - **NOT Google Play** (outdated version)

2. **Install Termux APK**
   - Enable "Unknown Sources" in Android Settings
   - Install the downloaded APK
   - Open Termux app

### Step 2: Setup Termux Environment

1. **Update Package Lists**
   ```bash
   pkg update && pkg upgrade -y
   ```

2. **Install Required Packages**
   ```bash
   # Core packages
   pkg install python git termux-api -y
   
   # Python packages
   pip install requests
   ```

3. **Grant Termux Permissions**
   - Go to Android Settings → Apps → Termux → Permissions
   - Enable ALL permissions (Location, Storage, etc.)
   - **Critical:** Must enable background execution

### Step 3: Setup Wake Lock and Background Execution

1. **Disable Battery Optimization**
   - Android Settings → Battery → Battery Optimization
   - Find Termux → Select "Don't optimize"

2. **Enable Background App Refresh**
   - Settings → Apps → Termux → Battery
   - Allow background activity
   - Remove from power saving restrictions

3. **Install Termux:Boot (Optional but Recommended)**
   - Download from F-Droid
   - Enables auto-start on device boot

### Step 4: Deploy Monitoring Script

1. **Download the Script**
   ```bash
   # In Termux:
   cd ~
   curl -O https://raw.githubusercontent.com/laikadynamics/jd-engineering-monitoring-api/main/scripts/tablet_client.py
   ```

2. **Update Configuration**
   ```bash
   # Edit the script
   nano tablet_client.py
   
   # Update these lines:
   RAILWAY_API_URL = "https://YOUR-APP-NAME.up.railway.app"
   API_TOKEN = "YOUR-API-TOKEN-FROM-RAILWAY"
   DEVICE_ID = "tablet_electrical_dept_01"  # Unique per tablet
   ```

3. **Make Script Executable**
   ```bash
   chmod +x tablet_client.py
   ```

### Step 5: Test the Connection

1. **Run Initial Test**
   ```bash
   python tablet_client.py
   ```

2. **Expected Output:**
   ```
   🚀 Starting tablet monitoring for tablet_electrical_dept_01
   📡 Sending data to: https://your-app.up.railway.app
   ✅ Data sent successfully at 2024-01-15 10:30:00
   ```

3. **Verify Data in API**
   ```bash
   # On your computer, test the API:
   curl -H "Authorization: Bearer YOUR-API-TOKEN" \
        https://your-app.up.railway.app/devices
   ```

---

## 🔄 Part 3: Production Setup

### Step 1: Auto-Start Configuration

1. **Create Startup Script**
   ```bash
   # In Termux:
   mkdir -p ~/.termux/boot
   nano ~/.termux/boot/start-monitoring.sh
   ```

2. **Add Content:**
   ```bash
   #!/data/data/com.termux/files/usr/bin/bash
   
   # Wait for network
   sleep 30
   
   # Start monitoring
   cd /data/data/com.termux/files/home
   python tablet_client.py > monitoring.log 2>&1 &
   
   # Keep session alive
   termux-wake-lock
   ```

3. **Make Executable**
   ```bash
   chmod +x ~/.termux/boot/start-monitoring.sh
   ```

### Step 2: Service Management

1. **Create Service Control Script**
   ```bash
   nano monitor-control.sh
   ```

2. **Add Content:**
   ```bash
   #!/data/data/com.termux/files/usr/bin/bash
   
   case "$1" in
     start)
       echo "Starting tablet monitoring..."
       python tablet_client.py > monitoring.log 2>&1 &
       echo $! > monitor.pid
       echo "Started with PID $(cat monitor.pid)"
       ;;
     stop)
       if [ -f monitor.pid ]; then
         PID=$(cat monitor.pid)
         kill $PID 2>/dev/null
         rm monitor.pid
         echo "Monitoring stopped"
       else
         echo "No monitoring process found"
       fi
       ;;
     status)
       if [ -f monitor.pid ]; then
         PID=$(cat monitor.pid)
         if ps -p $PID > /dev/null; then
           echo "Monitoring is running (PID: $PID)"
         else
           echo "Monitoring is not running (stale PID file)"
           rm monitor.pid
         fi
       else
         echo "Monitoring is not running"
       fi
       ;;
     restart)
       $0 stop
       sleep 2
       $0 start
       ;;
     logs)
       tail -f monitoring.log
       ;;
     *)
       echo "Usage: $0 {start|stop|status|restart|logs}"
       exit 1
       ;;
   esac
   ```

3. **Make Executable**
   ```bash
   chmod +x monitor-control.sh
   ```

### Step 3: Device Configuration

1. **Set Device Information**
   ```bash
   # Edit tablet_client.py for each device:
   
   # For electrical department tablets:
   DEVICE_ID = "tablet_electrical_dept_01"  # increment: 01, 02, 03...
   
   # For test tablets:
   DEVICE_ID = "tablet_test_001"
   
   # For specific locations:
   DEVICE_ID = "tablet_workshop_floor_a"
   DEVICE_ID = "tablet_control_room_main"
   ```

2. **Configure Location Settings**
   ```bash
   # In the location field, update to match physical location:
   "location": "Electrical Department - Building A"
   "location": "Workshop Floor - Section B"
   "location": "Control Room - Main Panel"
   ```

---

## 🧪 Part 4: Testing and Validation

### Step 1: Comprehensive Testing

1. **API Endpoint Test**
   ```bash
   # Test from your computer:
   python scripts/test_api.py https://your-app.up.railway.app YOUR-API-TOKEN
   ```

2. **Tablet Connectivity Test**
   ```bash
   # On tablet in Termux:
   curl -H "Authorization: Bearer YOUR-API-TOKEN" \
        https://your-app.up.railway.app/health
   ```

3. **Data Flow Verification**
   ```bash
   # Start monitoring and check logs:
   ./monitor-control.sh start
   ./monitor-control.sh logs
   ```

### Step 2: Performance Monitoring

1. **Check System Resources**
   ```bash
   # On tablet:
   top -n 1 | grep python
   df -h
   free -m
   ```

2. **Monitor Network Usage**
   ```bash
   # Check data usage:
   termux-telephony-deviceinfo
   ```

3. **Battery Impact Assessment**
   ```bash
   # Check battery status:
   termux-battery-status
   ```

---

## 🔧 Part 5: Troubleshooting

### Common Issues and Solutions

#### **1. Connection Refused / Network Errors**
```bash
# Check network connectivity:
ping 8.8.8.8
nslookup your-app.up.railway.app

# Verify Termux permissions:
# Settings → Apps → Termux → Permissions → Enable all
```

#### **2. Authentication Errors**
```bash
# Verify API token:
echo "Your token: YOUR-API-TOKEN"

# Test token manually:
curl -H "Authorization: Bearer YOUR-API-TOKEN" \
     https://your-app.up.railway.app/devices
```

#### **3. Script Stops Running**
```bash
# Check if process is running:
./monitor-control.sh status

# Check logs for errors:
./monitor-control.sh logs

# Restart if needed:
./monitor-control.sh restart
```

#### **4. Termux API Errors**
```bash
# Reinstall Termux API:
pkg uninstall termux-api
pkg install termux-api

# Check permissions in Android settings
```

#### **5. Battery Optimization Issues**
```bash
# Disable power saving for Termux:
# Settings → Device Care → Battery → App Power Management
# Add Termux to "Apps that won't be put to sleep"
```

### Debugging Commands

```bash
# View system info:
uname -a
termux-info

# Check running processes:
ps aux | grep python

# Network diagnostics:
termux-wifi-connectioninfo
termux-telephony-cellinfo

# Storage check:
df -h $HOME
```

---

## 📊 Part 6: Monitoring and Maintenance

### Daily Checks

1. **Verify Data Flow**
   ```bash
   # Check last data submission:
   curl -H "Authorization: Bearer YOUR-API-TOKEN" \
        "https://your-app.up.railway.app/devices" | jq '.[] | {device_id, last_seen, status}'
   ```

2. **System Health**
   ```bash
   # On each tablet:
   ./monitor-control.sh status
   tail -20 monitoring.log
   ```

### Weekly Maintenance

1. **Update System**
   ```bash
   pkg update && pkg upgrade -y
   pip install --upgrade requests
   ```

2. **Clean Logs**
   ```bash
   # Rotate logs to prevent disk full:
   mv monitoring.log monitoring.log.old
   touch monitoring.log
   ```

3. **Restart Services**
   ```bash
   ./monitor-control.sh restart
   ```

### Monthly Tasks

1. **Database Cleanup** (Run on Railway console)
   ```sql
   -- Remove old data (older than 30 days)
   DELETE FROM device_metrics WHERE timestamp < NOW() - INTERVAL '30 days';
   DELETE FROM network_metrics WHERE timestamp < NOW() - INTERVAL '30 days';
   DELETE FROM app_metrics WHERE timestamp < NOW() - INTERVAL '30 days';
   ```

2. **Performance Review**
   - Check Railway dashboard for API performance
   - Review tablet battery usage patterns
   - Analyze connectivity issues

---

## 📱 Part 7: Multi-Tablet Deployment

### Scaling to Multiple Devices

1. **Device Naming Convention**
   ```
   tablet_electrical_dept_01    # First electrical dept tablet
   tablet_electrical_dept_02    # Second electrical dept tablet
   tablet_workshop_floor_a      # Workshop floor section A
   tablet_control_room_main     # Main control room
   ```

2. **Configuration Management**
   ```bash
   # Create config file template:
   nano tablet-config-template.py
   
   # Variables to customize per tablet:
   DEVICE_ID = "REPLACE_DEVICE_ID"
   LOCATION = "REPLACE_LOCATION"
   ```

3. **Deployment Script**
   ```bash
   # Create deployment helper:
   nano deploy-tablet.sh
   
   #!/bin/bash
   DEVICE_ID=$1
   LOCATION=$2
   
   if [ -z "$DEVICE_ID" ]; then
     echo "Usage: $0 <device_id> <location>"
     exit 1
   fi
   
   # Download and configure
   curl -O https://raw.githubusercontent.com/laikadynamics/jd-engineering-monitoring-api/main/scripts/tablet_client.py
   sed -i "s/tablet_electrical_dept/$DEVICE_ID/g" tablet_client.py
   sed -i "s/Electrical Department/$LOCATION/g" tablet_client.py
   
   echo "Tablet $DEVICE_ID configured for $LOCATION"
   ```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Railway app deployed and healthy
- [ ] Environment variables configured
- [ ] Database connected
- [ ] API token generated
- [ ] Test script executed successfully

### Tablet Setup
- [ ] Termux installed from F-Droid
- [ ] Packages updated and installed
- [ ] Permissions granted to Termux
- [ ] Battery optimization disabled
- [ ] Monitoring script downloaded and configured
- [ ] Initial connection test successful

### Production Setup
- [ ] Auto-start script configured
- [ ] Service control script installed
- [ ] Device ID and location configured
- [ ] Monitoring logs created
- [ ] Wake lock enabled

### Validation
- [ ] Data appearing in API endpoints
- [ ] Tablet staying connected
- [ ] Battery impact acceptable
- [ ] Network connectivity stable
- [ ] Error handling working

---

## 🆘 Support and Contacts

### Emergency Procedures
1. **API Down**: Check Railway dashboard and logs
2. **Tablet Offline**: Restart monitoring service
3. **Data Not Flowing**: Verify network and tokens
4. **High Battery Drain**: Check running processes

### Documentation References
- **Termux Wiki**: https://wiki.termux.com/
- **Railway Docs**: https://docs.railway.app/
- **API Documentation**: `https://your-app.up.railway.app/docs`

---

**✨ Deployment Complete!** Your tablet monitoring system is now operational and ready for production use. 