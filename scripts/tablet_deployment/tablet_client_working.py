#!/data/data/com.termux/files/usr/bin/python
"""
JD Engineering Tablet Monitoring - WORKING VERSION
Monitors MYOB sessions, barcode scanners, and system metrics
"""

import json
import requests
import time
import subprocess
import os
from datetime import datetime, timezone
import uuid

# Configuration
API_URL = "https://jd-engineering-monitoring-api-production.up.railway.app/tablet-metrics"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"

class TabletMonitor:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.session_id = str(uuid.uuid4())
        self.last_interaction = datetime.now(timezone.utc)
        
        print(f"🚀 Tablet Monitor Started")
        print(f"📱 Device: {self.device_id}")
        print(f"🆔 Session: {self.session_id}")
    
    def run_command(self, cmd):
        """Run a command safely"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_battery_info(self):
        """Get battery information"""
        try:
            output = self.run_command(['termux-battery-status'])
            if output:
                data = json.loads(output)
                return {
                    "battery_level": data.get("percentage", 0),
                    "battery_temperature": data.get("temperature", 0),
                    "battery_status": data.get("status", "unknown")
                }
        except:
            pass
        return {"battery_level": 50, "battery_temperature": 25, "battery_status": "unknown"}
    
    def get_wifi_info(self):
        """Get WiFi information"""
        try:
            output = self.run_command(['termux-wifi-connectioninfo'])
            if output:
                data = json.loads(output)
                wifi_data = {
                    "wifi_signal_strength": data.get("rssi", -50),
                    "wifi_ssid": data.get("ssid", "").replace('"', ''),
                    "connectivity_status": "unknown"
                }
                
                # Test connectivity
                ping_result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                           capture_output=True, timeout=5)
                wifi_data["connectivity_status"] = "online" if ping_result.returncode == 0 else "offline"
                return wifi_data
        except:
            pass
        return {"wifi_signal_strength": -50, "wifi_ssid": "unknown", "connectivity_status": "unknown"}
    
    def check_myob_processes(self):
        """Check if MYOB is running"""
        try:
            output = self.run_command(['ps', '-A'])
            if output:
                processes = output.lower()
                myob_patterns = ['myob', 'accountright', 'com.myob']
                myob_active = any(pattern in processes for pattern in myob_patterns)
                return {"myob_active": myob_active, "myob_processes": len([p for p in myob_patterns if p in processes])}
        except:
            pass
        return {"myob_active": False, "myob_processes": 0}
    
    def check_scanner_processes(self):
        """Check if barcode scanner is active"""
        try:
            output = self.run_command(['ps', '-A'])
            if output:
                processes = output.lower()
                scanner_patterns = ['scanner', 'barcode', 'zebra', 'honeywell', 'datalogic']
                scanner_active = any(pattern in processes for pattern in scanner_patterns)
                return {"scanner_active": scanner_active, "scanner_processes": len([p for p in scanner_patterns if p in processes])}
        except:
            pass
        return {"scanner_active": False, "scanner_processes": 0}
    
    def detect_user_activity(self):
        """Detect user activity using accelerometer"""
        try:
            output = self.run_command(['termux-sensor', '-s', 'accelerometer', '-n', '1'])
            if output:
                data = json.loads(output)
                if 'values' in data and len(data['values']) >= 3:
                    movement = sum(abs(x) for x in data['values'][:3])
                    if movement > 10:  # Device is moving
                        self.last_interaction = datetime.now(timezone.utc)
                        return {"recent_movement": True, "movement_magnitude": movement}
        except:
            pass
        
        # Calculate inactivity time
        inactive_seconds = int((datetime.now(timezone.utc) - self.last_interaction).total_seconds())
        return {"recent_movement": False, "inactive_seconds": inactive_seconds}
    
    def generate_session_events(self, myob_data, scanner_data, activity_data):
        """Generate session events"""
        events = []
        
        # MYOB timeout detection
        if myob_data.get("myob_active") and activity_data.get("inactive_seconds", 0) > 300:
            events.append({
                "event_type": "timeout",
                "session_id": self.session_id,
                "duration": activity_data.get("inactive_seconds", 0),
                "error_message": f"MYOB timeout risk - {activity_data.get('inactive_seconds', 0)}s inactive",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Scanner activity detection
        if scanner_data.get("scanner_active"):
            events.append({
                "event_type": "session_start",
                "session_id": self.session_id,
                "error_message": "Barcode scanner activity detected",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return events
    
    def collect_data(self):
        """Collect all monitoring data"""
        print(f"📊 Collecting data at {datetime.now().strftime('%H:%M:%S')}")
        
        # Get all metrics
        battery_data = self.get_battery_info()
        wifi_data = self.get_wifi_info()
        myob_data = self.check_myob_processes()
        scanner_data = self.check_scanner_processes()
        activity_data = self.detect_user_activity()
        
        # Generate events
        events = self.generate_session_events(myob_data, scanner_data, activity_data)
        
        # Create payload
        payload = {
            "device_id": self.device_id,
            "device_name": f"Android Tablet - {self.device_id}",
            "location": "Electrical Department",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_metrics": battery_data,
            "network_metrics": wifi_data,
            "app_metrics": {
                "screen_state": "active" if activity_data.get("recent_movement") else "idle",
                "app_foreground": "myob" if myob_data.get("myob_active") else ("scanner" if scanner_data.get("scanner_active") else "unknown"),
                "last_user_interaction": self.last_interaction.isoformat(),
                **myob_data,
                **scanner_data,
                **activity_data
            },
            "session_events": events,
            "raw_logs": [
                f"MYOB: {myob_data.get('myob_active', False)}",
                f"Scanner: {scanner_data.get('scanner_active', False)}",
                f"Inactive: {activity_data.get('inactive_seconds', 0)}s"
            ]
        }
        
        return payload
    
    def send_data(self, payload):
        """Send data to API"""
        try:
            headers = {
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                myob_status = payload.get('app_metrics', {}).get('myob_active', False)
                scanner_status = payload.get('app_metrics', {}).get('scanner_active', False)
                battery = payload.get('device_metrics', {}).get('battery_level', 0)
                print(f"✅ Data sent - Battery: {battery}% | MYOB: {myob_status} | Scanner: {scanner_status}")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Send error: {e}")
            return False
    
    def run(self):
        """Main monitoring loop"""
        print(f"🎯 Starting monitoring loop...")
        print(f"📡 API: {API_URL}")
        print(f"⏱️  Interval: 30 seconds")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Collect and send data
                data = self.collect_data()
                success = self.send_data(data)
                
                # Wait based on success
                if success:
                    time.sleep(30)  # 30 seconds on success
                else:
                    time.sleep(60)  # 60 seconds on error
                    
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Loop error: {e}")
                time.sleep(60)
        
        print("🛑 Monitoring stopped")

def main():
    """Main function"""
    print("🚀 JD Engineering Tablet Monitor v1.0")
    print("=" * 50)
    
    monitor = TabletMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 