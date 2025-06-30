# 📱 JD Engineering Tablet Setup Instructions

## 🧪 Test Tablet Setup

### For Test Tablets (TeamViewer Security Testing)

1. **Copy the test script to tablet:**
   ```bash
   # Copy test_tablet_client.py to the tablet
   scp scripts/tablet_deployment/test_tablet_client.py tablet:/data/data/com.termux/files/home/
   ```

2. **On the tablet (Termux):**
   ```bash
   # Install required packages
   pkg update && pkg upgrade
   pkg install python termux-api

   # Install Python dependencies
   pip install requests

   # Make script executable
   chmod +x test_tablet_client.py

   # Run the test monitor
   python test_tablet_client.py
   ```

3. **For multiple test tablets:**
   - Edit `DEVICE_ID` in the script:
     - Test Tablet 1: `"test_tablet_001"`
     - Test Tablet 2: `"test_tablet_002"`
     - Test Tablet 3: `"test_tablet_003"`

4. **Test Features:**
   - ✅ TeamViewer detection
   - ✅ Android Settings monitoring
   - ✅ Faster reporting (15 seconds)
   - ✅ Enhanced error handling
   - ✅ Test session event logging

---

## ⚡ Electrical Department Tablet Setup

### For Production Electrical Department Tablet

1. **Copy the electrical script to tablet:**
   ```bash
   # Copy electrical_tablet_client.py to the tablet
   scp scripts/tablet_deployment/electrical_tablet_client.py tablet:/data/data/com.termux/files/home/
   ```

2. **On the tablet (Termux):**
   ```bash
   # Install required packages
   pkg update && pkg upgrade
   pkg install python termux-api

   # Install Python dependencies
   pip install requests

   # Make script executable
   chmod +x electrical_tablet_client.py

   # Run the electrical monitor
   python electrical_tablet_client.py
   ```

3. **Production Features:**
   - ✅ MYOB AccountRight monitoring
   - ✅ Barcode scanner detection
   - ✅ Critical timeout alerts (5+ minutes)
   - ✅ Extended inactivity warnings (10+ minutes)
   - ✅ Production-grade error handling
   - ✅ 30-second reporting interval

---

## 🚀 Quick Start Commands

### Test Tablet (Quick Copy-Paste)
```bash
# On test tablet in Termux:
pkg install python termux-api -y
pip install requests
curl -O https://raw.githubusercontent.com/your-repo/jd-engineering-monitoring-api/main/scripts/tablet_deployment/test_tablet_client.py
python test_tablet_client.py
```

### Electrical Tablet (Quick Copy-Paste)
```bash
# On electrical tablet in Termux:
pkg install python termux-api -y
pip install requests
curl -O https://raw.githubusercontent.com/your-repo/jd-engineering-monitoring-api/main/scripts/tablet_deployment/electrical_tablet_client.py
python electrical_tablet_client.py
```

---

## 🔧 Configuration

### API Configuration (Already Set)
- **API URL:** `https://jd-engineering-monitoring-api-production-5d93.up.railway.app/tablet-metrics`
- **API Token:** `ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681`

### Device IDs
- **Test Tablets:** `test_tablet_001`, `test_tablet_002`, etc.
- **Electrical Tablet:** `tablet_electrical_dept`

---

## 📊 Monitoring Dashboard

Access the monitoring dashboard at:
**https://jd-engineering-monitoring-api-production-5d93.up.railway.app/dashboard**

### Key Metrics Monitored:
- 🔋 Battery level and temperature
- 📶 WiFi signal strength and connectivity
- 💻 MYOB AccountRight activity
- 📱 Barcode scanner usage
- ⏰ Session timeouts and inactivity
- 🏃 User activity and movement

---

## 🛠️ Troubleshooting

### Common Issues:

1. **"Command not found: python"**
   ```bash
   pkg install python -y
   ```

2. **"ModuleNotFoundError: requests"**
   ```bash
   pip install requests
   ```

3. **"Permission denied"**
   ```bash
   chmod +x tablet_client.py
   ```

4. **API connection errors:**
   - Check WiFi connectivity
   - Verify API URL is correct
   - Check if API token is valid

### Testing Connection:
```bash
# Quick API health check
curl https://jd-engineering-monitoring-api-production-5d93.up.railway.app/health
```

---

## ⚠️ Important Notes

### For Test Tablets:
- Reports every **15 seconds** for faster testing
- Monitors TeamViewer and Android Settings
- Use device IDs: `test_tablet_001`, `test_tablet_002`, etc.

### For Electrical Department:
- Reports every **30 seconds** for production stability
- Monitors MYOB and barcode scanners
- Critical alerts for 5+ minute timeouts
- Use device ID: `tablet_electrical_dept`

### Ready for 10:30am Meeting:
- ✅ API is fully operational
- ✅ Database connected
- ✅ Both scripts ready to deploy
- ✅ Real-time monitoring active 