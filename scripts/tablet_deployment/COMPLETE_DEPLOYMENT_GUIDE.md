# 🚀 Complete Tablet Manager - One-Command Deployment

## 📱 **SINGLE COMMAND DEPLOYMENT**

### **Copy-Paste This ONE Command on Each Tablet:**

```bash
curl -L -o complete_tablet_manager.sh "https://raw.githubusercontent.com/Laika-Dynamics-Ltd/jd-engineering-monitoring-api/main/scripts/tablet_deployment/complete_tablet_manager.sh" && chmod +x complete_tablet_manager.sh && ./complete_tablet_manager.sh deploy
```

**That's it!** The script will:
- ✅ Ask if it's a test or electrical tablet
- ✅ Install all dependencies automatically
- ✅ Download the correct monitoring script
- ✅ Set up TeamViewer bypass (Android 15)
- ✅ Configure auto-start on boot
- ✅ Start monitoring in background
- ✅ Show you the dashboard URL

---

## 🎛️ **Management Commands**

After deployment, use these commands:

```bash
# Check status
./complete_tablet_manager.sh status

# View live logs
./complete_tablet_manager.sh logs

# Start/stop monitoring
./complete_tablet_manager.sh start
./complete_tablet_manager.sh stop
./complete_tablet_manager.sh restart

# Run TeamViewer bypass again
./complete_tablet_manager.sh bypass

# Interactive menu (all options)
./complete_tablet_manager.sh
```

---

## 🔓 **TeamViewer Android 15 Bypass**

The script automatically handles Android 15 security bypass, but you need to:

1. **When prompted:** Enable TeamViewer in Accessibility Settings
2. **Look for:** "TeamViewer QuickSupport" 
3. **Turn it:** ON
4. **Accept:** Any prompts

**That's the only manual step required!**

---

## ⚡ **Quick Reference**

### **Test Tablet Setup (30 seconds):**
```bash
# 1. Run deployment command above
# 2. Choose "1" for Test Tablet  
# 3. Enable TeamViewer in Accessibility (when prompted)
# 4. Done!
```

### **Electrical Tablet Setup (30 seconds):**
```bash
# 1. Run deployment command above
# 2. Choose "2" for Electrical Department
# 3. Done! (No TeamViewer setup needed)
```

### **Background Monitoring:**
- Runs automatically in background
- Survives tablet reboots
- Auto-restarts if crashes
- Logs everything to `jd_monitoring.log`

---

## 📊 **Dashboard Access**

**View real-time monitoring:**
https://jd-engineering-monitoring-api-production-5d93.up.railway.app/dashboard

Shows:
- 🔋 Battery levels
- 📶 WiFi signals  
- 💻 MYOB activity (electrical)
- 📱 TeamViewer status (test)
- ⏰ Activity timers

---

## 🚨 **Troubleshooting**

### **If Something Goes Wrong:**
```bash
# Emergency recovery
./complete_tablet_manager.sh

# Then choose option 1 (Quick Setup) to redeploy
```

### **Common Issues:**
- **"Command not found"** → Make sure you're in Termux
- **"Permission denied"** → Run `chmod +x complete_tablet_manager.sh`
- **API connection fails** → Check WiFi and try again

---

## ✅ **Success Indicators**

You'll know it's working when you see:
- ✅ "DEPLOYMENT SUCCESSFUL!" message
- ✅ Status shows "Monitoring: RUNNING"
- ✅ Status shows "API: ONLINE"  
- ✅ Dashboard shows your tablet with recent data

---

## 🎯 **For Your 10:30am Meeting**

### **Pre-Meeting (5 minutes total):**
1. Run the one-command deployment on each tablet
2. Choose correct tablet type (test/electrical)
3. Enable TeamViewer accessibility for test tablets
4. Verify status shows "RUNNING" and "ONLINE"

### **During Meeting:**
- **Dashboard:** https://jd-engineering-monitoring-api-production-5d93.up.railway.app/dashboard
- **Show Brad:** Real-time monitoring, TeamViewer bypass working
- **Contact:** Brad at 027 246 7824 (after 10:30am)

**Everything is automated - just run one command per tablet!** 🎉 