# Railway Production Deployment Checklist
## J&D McLennan Engineering - Real Device Monitoring Only

**IMPORTANT**: This deployment uses **REAL DEVICE DATA ONLY** - no mock or sample data.

---

## 🔐 Step 1: Set Environment Variables in Railway

Copy these secure keys to Railway Dashboard → Variables:

```bash
# Security Keys (Generated for you - use these exact values)
SECRET_KEY=kX7QNLI8adcQIjchFntRXf1ixr-7rSUmcPJJxT4FxEk
API_TOKEN=4EuB1ysj6iOIxVEglcLIOrtJQcUEPHmTi6gYQGLcplk
JWT_SECRET=FkY1C4nipN4hY0s0GSG4_jhoEw9xf3Pz88JQ3G9aRNk

# Application Settings
ENVIRONMENT=production
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
GUNICORN_WORKERS=4
CACHE_TTL=300
API_RATE_LIMIT=100
METRICS_ENABLED=true
LOG_LEVEL=info
DEBUG=false
```

---

## 🚀 Step 2: Deploy to Railway

```bash
# Deploy the application
railway up

# Monitor deployment
railway logs --follow
```

---

## 🗄️ Step 3: Initialize Database (NO MOCK DATA)

```bash
# Connect to PostgreSQL
railway connect Postgres

# Run initialization (creates empty tables for real devices)
\i scripts/railway_init_db.sql

# Verify empty tables
SELECT COUNT(*) FROM device_registry;  -- Should be 0
SELECT COUNT(*) FROM device_metrics;   -- Should be 0

# Exit
\q
```

---

## 📱 Step 4: Connect Real Tablets

### On Each Android Tablet:

1. **Install Termux**:
   ```bash
   pkg update && pkg upgrade
   pkg install python termux-api
   pip install requests
   ```

2. **Update Monitoring Script**:
   Edit `tablet_client_working.py`:
   ```python
   API_URL = "https://your-app.railway.app/tablet-metrics"
   API_TOKEN = "4EuB1ysj6iOIxVEglcLIOrtJQcUEPHmTi6gYQGLcplk"
   DEVICE_ID = "tablet_electrical_dept"  # Unique per tablet
   ```

3. **Run Monitoring**:
   ```bash
   python tablet_client_working.py
   ```

---

## ✅ Step 5: Verify Real Device Connection

### Check Dashboard:
```
https://your-app.railway.app/dashboard
```
- Initially shows: "No Tablets Connected"
- After tablets connect: Shows real device cards

### Check API:
```bash
# List real devices (empty until tablets connect)
curl -H "Authorization: Bearer 4EuB1ysj6iOIxVEglcLIOrtJQcUEPHmTi6gYQGLcplk" \
  https://your-app.railway.app/devices

# Monitor logs for real device data
railway logs --follow
# Look for: "📱 Received data from real device: tablet_electrical_dept"
```

### Check Database:
```bash
railway connect Postgres

-- Check real devices
SELECT * FROM device_registry;

-- Check latest metrics
SELECT * FROM device_metrics ORDER BY timestamp DESC LIMIT 5;
```

---

## 🎯 Success Criteria

✅ **Dashboard shows "No Tablets Connected"** when no real devices  
✅ **Real device IDs appear** when tablets connect (e.g., `tablet_electrical_dept`)  
✅ **Battery levels update** in real-time from actual tablets  
✅ **MYOB/Scanner status** reflects actual app usage  
✅ **No mock devices** (tablet-001, tablet-002, etc.) appear  
✅ **Railway logs show** real device data arriving  
✅ **Database contains** only real device records  

---

## 🚨 Troubleshooting

### Dashboard Still Shows Mock Data?
1. Clear browser cache
2. Verify you deployed the updated code
3. Check Railway logs for errors
4. Ensure database was initialized with new script (no sample data)

### Tablets Not Connecting?
1. Verify API_TOKEN matches Railway environment
2. Check tablet network connectivity
3. Ensure API_URL is correct Railway URL
4. Monitor Railway logs for connection attempts

### Database Issues?
```sql
-- Reset database if needed
DELETE FROM device_metrics;
DELETE FROM network_metrics;
DELETE FROM app_metrics;
DELETE FROM session_events;
DELETE FROM device_registry;
```

---

## 📊 What Real Data Looks Like

### Device Registry Entry:
```sql
device_id: 'tablet_electrical_dept'
device_name: 'Android Tablet - tablet_electrical_dept'
location: 'Electrical Department'
android_version: '11.0'
app_version: '2.1.0'
is_active: true
last_seen: [current timestamp]
```

### Real-time Metrics:
- Battery levels that actually change
- WiFi signal strength variations
- MYOB timeout events when detected
- Scanner activity when barcode apps used

---

## 🔒 Security Reminders

- **Keep API_TOKEN secure** - Don't commit to git
- **Rotate keys regularly** - Update in Railway variables
- **Monitor access logs** - Check for unauthorized attempts
- **Use HTTPS only** - Railway provides automatic SSL

---

## 📝 Final Notes

**This deployment is configured for REAL DEVICE DATA ONLY:**
- No mock data in database initialization
- No fallback devices in API responses
- Dashboard shows actual state when empty
- All metrics come from real connected tablets

**To see data in the dashboard, you MUST:**
1. Deploy monitoring script to real Android tablets
2. Configure each tablet with unique DEVICE_ID
3. Ensure tablets are running and connected
4. Use the correct API_TOKEN for authentication

---

**Deployment Complete! 🎉**

Your J&D McLennan Engineering Dashboard is now live on Railway, ready to monitor real tablets only. No mock data will be displayed - only actual device information from connected tablets. 