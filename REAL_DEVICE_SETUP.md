# Real Device Setup Guide
## J&D McLennan Engineering - Production Tablet Monitoring

This guide ensures you're using **REAL DEVICE DATA ONLY** - no mock or sample data.

---

## 🚫 Changes Made to Remove Mock Data

### 1. **Database Initialization** (`scripts/railway_init_db.sql`)
- ✅ Removed all sample data inserts
- ✅ Database now starts empty, waiting for real devices
- ✅ Expected device: `tablet_electrical_dept`

### 2. **Production Dashboard** (`static/dashboard_production.html`)
- ✅ Removed fallback mock devices
- ✅ Shows "No Tablets Connected" when no real devices
- ✅ Displays expected device IDs for reference

### 3. **Production API** (`main_production.py`)
- ✅ Removed mock data fallback from `/devices` endpoint
- ✅ Added `/tablet-metrics` endpoint for real device data
- ✅ Returns empty array when no real devices connected

---

## 📱 Setting Up Real Tablet Monitoring

### Step 1: Deploy to Railway (if not already done)
```bash
# Deploy the updated production code
railway up

# Initialize database without mock data
railway connect Postgres
\i scripts/railway_init_db.sql
```

### Step 2: Get Your API Details
```bash
# Get your Railway URL
railway domain
# Example: https://jd-engineering-monitoring-api-production.up.railway.app

# Get your API token from environment
railway variables get API_TOKEN
```

### Step 3: Deploy Monitoring Script to Tablets

Copy the monitoring script to each Android tablet:

1. **Install Termux on the tablet**:
   - Download from F-Droid (recommended) or Play Store
   - Open Termux and run:
   ```bash
   pkg update && pkg upgrade
   pkg install python
   pkg install termux-api
   pip install requests
   ```

2. **Copy the monitoring script**:
   ```bash
   # Copy scripts/tablet_client_working.py to the tablet
   # Update the API_URL to your Railway URL:
   API_URL = "https://your-railway-app.railway.app/tablet-metrics"
   API_TOKEN = "your-api-token-here"
   DEVICE_ID = "tablet_electrical_dept"  # Unique for each tablet
   ```

3. **Run the monitoring script**:
   ```bash
   python tablet_client_working.py
   ```

### Step 4: Verify Real Data Flow

1. **Check the dashboard**:
   ```
   https://your-railway-app.railway.app/dashboard
   ```
   - Should show "No Tablets Connected" initially
   - Will display real devices as they connect

2. **Check API endpoints**:
   ```bash
   # List connected devices (should be empty initially)
   curl -H "Authorization: Bearer your-api-token" \
     https://your-railway-app.railway.app/devices

   # Check health status
   curl https://your-railway-app.railway.app/health
   ```

3. **Monitor logs**:
   ```bash
   railway logs --follow
   # Look for: "📱 Received data from real device: tablet_electrical_dept"
   ```

---

## 🔍 Real Device Data Structure

When a real tablet connects, it sends:

```json
{
  "device_id": "tablet_electrical_dept",
  "device_name": "Android Tablet - tablet_electrical_dept",
  "location": "Electrical Department",
  "device_metrics": {
    "battery_level": 85,
    "battery_temperature": 25.3,
    "memory_available": 2048000000,
    "memory_total": 4096000000,
    "storage_available": 8192000000,
    "cpu_usage": 12.5
  },
  "network_metrics": {
    "wifi_signal_strength": -45,
    "wifi_ssid": "JD_McLennan_Warehouse",
    "connectivity_status": "online",
    "network_type": "wifi"
  },
  "app_metrics": {
    "screen_state": "active",
    "app_foreground": "myob",
    "myob_active": true,
    "scanner_active": false,
    "inactive_seconds": 120
  },
  "session_events": [
    {
      "event_type": "timeout",
      "session_id": "uuid-here",
      "duration": 300,
      "error_message": "MYOB timeout risk - 300s inactive"
    }
  ]
}
```

---

## 📊 Dashboard Features with Real Data

### When Tablets Are Connected:
- **Device Cards**: Show real battery levels, locations, last seen times
- **KPI Metrics**: Calculate actual averages from connected devices
- **Business Intelligence**: Based on real timeout events and usage patterns
- **Real-time Updates**: WebSocket broadcasts when new data arrives

### When No Tablets Connected:
- **Clear Message**: "No Tablets Connected"
- **Instructions**: Shows expected device IDs
- **Empty Metrics**: KPIs show "-" or "0"
- **No Mock Data**: No fake devices or simulated metrics

---

## 🚨 Troubleshooting Real Device Connection

### Tablet Not Appearing in Dashboard?

1. **Check tablet connectivity**:
   ```bash
   # On tablet in Termux:
   ping -c 1 8.8.8.8
   curl https://your-railway-app.railway.app/health
   ```

2. **Verify API token**:
   ```bash
   # Test from tablet:
   curl -H "Authorization: Bearer your-api-token" \
     https://your-railway-app.railway.app/devices
   ```

3. **Check monitoring script**:
   - Ensure `API_URL` points to your Railway app
   - Verify `API_TOKEN` matches Railway environment
   - Confirm `DEVICE_ID` is unique per tablet

4. **Monitor Railway logs**:
   ```bash
   railway logs --follow
   # Should see tablet data arriving
   ```

### Database Issues?

```bash
# Connect to Railway PostgreSQL
railway connect Postgres

# Check if devices are registered
SELECT * FROM device_registry;

# Check recent metrics
SELECT * FROM device_metrics ORDER BY timestamp DESC LIMIT 10;

# Verify device is active
UPDATE device_registry SET is_active = TRUE WHERE device_id = 'tablet_electrical_dept';
```

---

## ✅ Success Indicators

You'll know real device monitoring is working when:

1. **Dashboard shows real devices** with actual device IDs (not tablet-001, etc.)
2. **Battery levels vary** and update in real-time
3. **Locations match** your actual tablet deployments
4. **MYOB/Scanner status** reflects actual app usage
5. **Railway logs show** "Received data from real device"
6. **Database contains** real device records with timestamps

---

## 🔐 Security Notes

- **API Tokens**: Keep secure, rotate regularly
- **Device IDs**: Use meaningful, unique identifiers
- **Network**: Ensure tablets connect over secure WiFi
- **Access Control**: Limit dashboard access as needed

---

**Remember**: The system now ONLY shows real data. If you see "No Tablets Connected", you need to:
1. Deploy the monitoring script to actual tablets
2. Ensure tablets are running and connected
3. Verify API endpoints and tokens are correct

No mock data will be displayed - only real device information! 