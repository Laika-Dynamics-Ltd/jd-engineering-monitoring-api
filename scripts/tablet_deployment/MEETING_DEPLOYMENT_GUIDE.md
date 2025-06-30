# 🚀 10:30am Meeting Deployment Guide

## ⏰ **5 Minutes Per Tablet Setup**

### **Step 1: Download Quick Deploy Script**
```bash
# On each tablet in Termux, copy-paste this ONE command:
curl -L -o quick_deploy.sh "https://raw.githubusercontent.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api/main/scripts/tablet_deployment/quick_deploy.sh" && chmod +x quick_deploy.sh && bash quick_deploy.sh
```

### **Step 2: Run the Script**
- Script will ask: "Test tablet (1) or Electrical (2)?"
- Choose appropriate option
- Script automatically:
  - ✅ Installs dependencies
  - ✅ Downloads correct monitoring script
  - ✅ Tests API connection
  - ✅ Starts monitoring in background
  - ✅ Shows useful commands

---

## 🔓 **Android 15 TeamViewer Bypass (2 minutes)**

### **Quick Method - Copy-Paste in Termux:**
```bash
# Grant TeamViewer permissions:
pm grant com.teamviewer.quicksupport.android android.permission.SYSTEM_ALERT_WINDOW
pm grant com.teamviewer.quicksupport.android android.permission.WRITE_SECURE_SETTINGS

# Start TeamViewer:
am start com.teamviewer.quicksupport.android/.MainActivity

# Open accessibility settings (manual step):
am start -a android.settings.ACCESSIBILITY_SETTINGS
```

### **Manual Step (30 seconds):**
1. In Accessibility Settings that just opened
2. Find "TeamViewer QuickSupport" 
3. Turn it **ON**
4. Accept any prompts

---

## 📱 **Complete Tablet Setup Commands**

### **Test Tablet Commands:**
```bash
# Single command setup:
curl -L https://raw.githubusercontent.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api/main/scripts/tablet_deployment/quick_deploy.sh | bash

# TeamViewer bypass:
pm grant com.teamviewer.quicksupport.android android.permission.SYSTEM_ALERT_WINDOW
am start -a android.settings.ACCESSIBILITY_SETTINGS
# Manually enable TeamViewer in accessibility
```

### **Electrical Tablet Commands:**
```bash
# Single command setup:
curl -L https://raw.githubusercontent.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api/main/scripts/tablet_deployment/quick_deploy.sh | bash

# Same TeamViewer bypass if needed:
pm grant com.teamviewer.quicksupport.android android.permission.SYSTEM_ALERT_WINDOW
am start -a android.settings.ACCESSIBILITY_SETTINGS
```

---

## 🎯 **Background Management Commands**

### **Check Status:**
```bash
# View monitoring logs:
tail -f monitoring.log

# Check if monitoring is running:
ps aux | grep python

# Check API connection:
curl https://jd-engineering-monitoring-api-production-5d93.up.railway.app/health
```

### **Control Commands:**
```bash
# Stop monitoring:
pkill -f tablet_client.py

# Restart monitoring:
bash quick_deploy.sh

# Keep alive (if needed):
nohup python test_tablet_client.py > monitoring.log 2>&1 &
```

---

## 📊 **Meeting Dashboard**

**Open this during the meeting:**
https://jd-engineering-monitoring-api-production-5d93.up.railway.app/dashboard

Shows real-time:
- 🔋 Battery levels
- 📶 WiFi signal strength  
- 💻 MYOB activity (electrical tablet)
- 📱 TeamViewer status (test tablets)
- ⏰ Activity timers

---

## 🚨 **Emergency Troubleshooting**

### **If Monitoring Stops:**
```bash
# Quick restart:
pkill -f python && nohup python test_tablet_client.py > monitoring.log 2>&1 &
```

### **If TeamViewer Won't Connect:**
```bash
# Force restart TeamViewer:
am force-stop com.teamviewer.quicksupport.android
am start com.teamviewer.quicksupport.android/.MainActivity
```

### **If API Connection Fails:**
```bash
# Test connection:
curl https://jd-engineering-monitoring-api-production-5d93.up.railway.app/health

# Check WiFi:
ping 8.8.8.8
```

---

## ✅ **Pre-Meeting Checklist (2 minutes before 10:30am)**

### **Test Tablets:**
- [ ] Quick deploy script ran successfully
- [ ] TeamViewer accessibility enabled
- [ ] Monitoring running in background (`tail -f monitoring.log` shows activity)
- [ ] TeamViewer connecting without prompts

### **Electrical Tablet:**
- [ ] Quick deploy script ran successfully  
- [ ] Monitoring running in background
- [ ] MYOB detection working (if MYOB is running)

### **Dashboard:**
- [ ] Open https://jd-engineering-monitoring-api-production-5d93.up.railway.app/dashboard
- [ ] Verify tablets showing up with recent data
- [ ] All tablets showing "online" status

---

## 📞 **Meeting Contact**

**Brad: 027 246 7824** (after 10:30am as planned)

**Show Brad:**
1. **Dashboard** - real-time tablet monitoring
2. **TeamViewer** - unattended access working
3. **API Logs** - data flowing successfully
4. **Background monitoring** - scripts running automatically

**Ready to demonstrate Android 15 security bypass and real-time monitoring!** 🎉 