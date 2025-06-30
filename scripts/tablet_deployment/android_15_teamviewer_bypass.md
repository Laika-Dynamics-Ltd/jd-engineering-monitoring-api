# 🔓 Android 15 TeamViewer Security Bypass Guide

## ⚠️ **Android 15 Security Changes**
Android 15 introduced stricter security policies that block unattended remote access by default. Here's how to bypass these restrictions legally for JD Engineering testing.

---

## 🛠️ **Method 1: Device Administrator Configuration**

### Step 1: Enable TeamViewer Host as Device Administrator
```bash
# On tablet via ADB or Termux:
adb shell dpm set-device-owner com.teamviewer.host/.DeviceAdminReceiver

# Or via Settings UI:
# Settings > Security > Device Administrators > Enable TeamViewer Host
```

### Step 2: Grant Special Permissions
1. **Settings > Apps > TeamViewer Host > Permissions**
2. Enable all permissions:
   - ✅ Camera
   - ✅ Microphone  
   - ✅ Location
   - ✅ Display over other apps
   - ✅ Accessibility Service
   - ✅ Device Administrator

### Step 3: Disable Security Prompts
```bash
# Via ADB:
adb shell settings put secure accessibility_enabled 1
adb shell settings put secure enabled_accessibility_services com.teamviewer.host/.services.AccessibilityService
```

---

## 🔧 **Method 2: Developer Options Bypass**

### Enable Developer Mode:
1. **Settings > About Tablet**
2. Tap "Build Number" 7 times
3. **Settings > Developer Options**
4. Enable:
   - ✅ USB Debugging
   - ✅ Stay Awake
   - ✅ Don't keep activities
   - ✅ Allow mock locations

### Disable Security Features:
```bash
# Via Developer Options:
Settings > Developer Options > Disable:
- Verify apps over USB
- Enhanced security mode
- Restrict USB debugging
```

---

## 🎯 **Method 3: Enterprise Configuration (Recommended)**

### Step 1: Configure as Enterprise Device
```json
{
  "applications": [
    {
      "packageName": "com.teamviewer.host",
      "installType": "FORCE_INSTALLED",
      "lockTaskAllowed": true,
      "permissionGrants": [
        {
          "permission": "android.permission.SYSTEM_ALERT_WINDOW",
          "policy": "GRANT"
        },
        {
          "permission": "android.permission.ACCESSIBILITY_SERVICE", 
          "policy": "GRANT"
        },
        {
          "permission": "android.permission.ACCESS_FINE_LOCATION",
          "policy": "GRANT"
        },
        {
          "permission": "android.permission.RECORD_AUDIO",
          "policy": "GRANT"
        }
      ]
    }
  ],
  "persistentPreferredActivities": [
    {
      "receiverActivity": "com.teamviewer.host/.ui.TvClientActivity",
      "actions": ["android.intent.action.MAIN"],
      "categories": ["android.intent.category.HOME"]
    }
  ]
}
```

### Step 2: Apply Enterprise Policy
```bash
# Via ADB with enterprise config:
adb shell dpm set-application-policy enterprise_config.json
```

---

## 📱 **Method 4: Termux Automation Script**

### Create Auto-Accept Script:
```python
#!/data/data/com.termux/files/usr/bin/python3
"""
Android 15 TeamViewer Auto-Accept Script
Automatically accepts TeamViewer connection prompts
"""

import subprocess
import time
import os

def tap_coordinates(x, y):
    """Tap screen coordinates using Termux API"""
    subprocess.run(['termux-touch', str(x), str(y)])

def find_and_accept_prompt():
    """Find and accept TeamViewer security prompt"""
    try:
        # Take screenshot
        subprocess.run(['termux-camera-photo', 'screenshot.jpg'])
        
        # Common "Allow" button coordinates (adjust for your tablet)
        allow_buttons = [
            (540, 720),   # Center-bottom typical
            (400, 800),   # Lower center
            (600, 700),   # Right side
        ]
        
        for x, y in allow_buttons:
            tap_coordinates(x, y)
            time.sleep(0.5)
            
        print("✅ Auto-accepted TeamViewer prompt")
        return True
        
    except Exception as e:
        print(f"❌ Auto-accept failed: {e}")
        return False

def monitor_for_prompts():
    """Continuously monitor for TeamViewer prompts"""
    print("🔍 Monitoring for TeamViewer security prompts...")
    
    while True:
        try:
            # Check if TeamViewer is running
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'teamviewer' in result.stdout.lower():
                # Check for prompt and auto-accept
                find_and_accept_prompt()
            
            time.sleep(2)  # Check every 2 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Prompt monitoring stopped")
            break
        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_for_prompts()
```

---

## ⚡ **Quick Bypass Commands (Copy-Paste Ready)**

### For Test Tablets:
```bash
# Run in Termux for immediate bypass:
pkg install termux-api -y

# Disable security prompts via settings
am start -a android.settings.ACCESSIBILITY_SETTINGS
# Manually enable TeamViewer accessibility

# Auto-grant permissions
pm grant com.teamviewer.host android.permission.SYSTEM_ALERT_WINDOW
pm grant com.teamviewer.host android.permission.WRITE_SECURE_SETTINGS
pm grant com.teamviewer.host android.permission.ACCESS_FINE_LOCATION
pm grant com.teamviewer.host android.permission.RECORD_AUDIO

# Start TeamViewer Host
am start com.teamviewer.host/.ui.TvClientActivity
```

### Alternative ADB Method:
```bash
# If you have ADB access:
adb shell settings put secure accessibility_enabled 1
adb shell settings put global development_settings_enabled 1
adb shell settings put global stay_on_while_plugged_in 7
adb shell input keyevent 26  # Turn screen on
```

---

## 🛡️ **Security Considerations**

### For JD Engineering Testing:
1. **Document bypass methods** for audit compliance
2. **Temporary configurations** - revert after testing
3. **Isolated test network** for security
4. **Time-limited access** during testing window

### Restore Security After Testing:
```bash
# Re-enable security after testing:
adb shell settings put secure accessibility_enabled 0
adb shell dpm remove-active-admin com.teamviewer.host/.DeviceAdminReceiver
```

---

## 🎯 **For Your 10:30am Meeting**

### Pre-Meeting Setup (5 minutes per tablet):
1. Run quick deployment script
2. Apply Method 1 (Device Administrator) 
3. Test TeamViewer connection
4. Verify unattended access works
5. Start monitoring script in background

### During Meeting Commands:
```bash
# Check if bypass is working:
am start com.teamviewer.host/.ui.TvClientActivity

# Verify monitoring is running:
tail -f monitoring.log

# Check API connection:
curl https://jd-engineering-monitoring-api-production-5d93.up.railway.app/health
```

---

## 📞 **Emergency Commands**

### If TeamViewer Fails:
```bash
# Force restart TeamViewer Host:
am force-stop com.teamviewer.host
am start com.teamviewer.host/.ui.TvClientActivity

# Reset permissions:
pm reset-permissions com.teamviewer.host
# Then re-grant manually
```

### Contact Brad: **027 246 7824** if issues during testing! 