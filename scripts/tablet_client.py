#!/data/data/com.termux/files/usr/bin/python
"""
Updated tablet monitoring script for Railway-deployed API
This replaces the previous monitoring script with Railway endpoint
"""

import json
import requests
import time
import subprocess
import os
from datetime import datetime, timezone

# Railway API Configuration
RAILWAY_API_URL = "https://jd-engineering-monitoring-api-production.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"  # or "tablet_test_001" / "tablet_electrical_dept"

class TabletMonitor:
    def __init__(self):
        self.api_url = f"{RAILWAY_API_URL}/tablet-metrics"
        self.headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.device_id = DEVICE_ID
        
    def get_battery_info(self):
        """Get battery information via Termux API"""
        try:
            result = subprocess.run(['termux-battery-status'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                battery_data = json.loads(result.stdout)
                return {
                    "battery_level": battery_data.get("percentage"),
                    "battery_temperature": battery_data.get("temperature"),
                }
        except Exception as e:
            print(f"Battery info error: {e}")
        return {}
    
    def get_wifi_info(self):
        """Get WiFi information via Termux API"""
        try:
            # WiFi connection info
            result = subprocess.run(['termux-wifi-connectioninfo'], 
                                  capture_output=True, text=True, timeout=10)
            wifi_data = {}
            if result.returncode == 0 and result.stdout.strip():
                try:
                    wifi_info = json.loads(result.stdout)
                    wifi_data = {
                        "wifi_signal_strength": wifi_info.get("rssi"),
                        "wifi_ssid": wifi_info.get("ssid", "").replace('"', ''),
                        "network_type": "WiFi",
                        "ip_address": wifi_info.get("ip")
                    }
                except json.JSONDecodeError as e:
                    print(f"WiFi info JSON parse error: {e} - using defaults")
                    wifi_data = {"network_type": "WiFi"}
            else:
                print("WiFi info command returned empty/invalid data - using defaults")
                wifi_data = {"network_type": "WiFi"}
            
            # Test connectivity
            connectivity_test = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                             capture_output=True, timeout=5)
            wifi_data["connectivity_status"] = "online" if connectivity_test.returncode == 0 else "offline"
            
            return wifi_data
        except Exception as e:
            print(f"WiFi info error: {e}")
            return {"connectivity_status": "unknown"}
    
    def get_app_info(self):
        """Get application and screen state information"""
        try:
            # Check if screen is on by testing torch (harmless test)
            screen_test = subprocess.run(['termux-torch', 'on'], 
                                       capture_output=True, timeout=5)
            if screen_test.returncode == 0:
                subprocess.run(['termux-torch', 'off'], capture_output=True, timeout=5)
                screen_state = "active"
            else:
                screen_state = "locked"
            
            # Get notification count
            notif_result = subprocess.run(['termux-notification-list'], 
                                        capture_output=True, text=True, timeout=5)
            notification_count = 0
            if notif_result.returncode == 0:
                try:
                    notifications = json.loads(notif_result.stdout)
                    notification_count = len(notifications) if isinstance(notifications, list) else 0
                except:
                    notification_count = 0
            
            return {
                "screen_state": screen_state,
                "notification_count": notification_count,
                "screen_timeout_setting": 300  # Default Android timeout
            }
        except Exception as e:
            print(f"App info error: {e}")
            return {"screen_state": "unknown"}
    
    def collect_and_send_data(self):
        """Collect all metrics and send to Railway API"""
        try:
            # Collect all metrics
            device_metrics = self.get_battery_info()
            network_metrics = self.get_wifi_info()
            app_metrics = self.get_app_info()
            
            # Prepare payload
            payload = {
                "device_id": self.device_id,
                "device_name": f"Android Tablet - {self.device_id}",
                "location": "Electrical Department" if "electrical" in self.device_id else "Test Environment",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": device_metrics if device_metrics else None,
                "network_metrics": network_metrics if network_metrics else None,
                "app_metrics": app_metrics if app_metrics else None,
                "session_events": []  # Add session events when detected
            }
            
            # Send to Railway API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Data sent successfully at {datetime.now()}")
                return True
            else:
                print(f"❌ API error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error collecting/sending data: {e}")
            return False
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        print(f"🚀 Starting tablet monitoring for {self.device_id}")
        print(f"📡 Sending data to: {RAILWAY_API_URL}")
        
        while True:
            try:
                success = self.collect_and_send_data()
                if success:
                    # Wait 30 seconds between collections
                    time.sleep(30)
                else:
                    # Wait longer on errors
                    time.sleep(60)
                    
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring loop error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = TabletMonitor()
    monitor.run_monitoring_loop()