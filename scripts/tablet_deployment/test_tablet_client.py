#!/data/data/com.termux/files/usr/bin/python
"""
JD Engineering Test Tablet Monitor
Specialized for testing TeamViewer security bypass scenarios
"""

import json
import requests
import time
import subprocess
import os
import sys
from datetime import datetime, timezone
import uuid

# ==========================================
# TEST TABLET CONFIGURATION
# ==========================================
API_URL = "https://jd-engineering-monitoring-api-production-5d93.up.railway.app/tablet-metrics"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "test_tablet_001"  # Change this for each test tablet (test_tablet_002, etc.)
LOCATION = "Testing Environment"
SEND_INTERVAL = 15  # More frequent for testing (15 seconds)
MAX_RETRIES = 5     # More retries for testing
TIMEOUT = 20        # Shorter timeout for testing

class TestTabletMonitor:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.session_id = str(uuid.uuid4())
        self.last_interaction = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        self.total_sends = 0
        self.successful_sends = 0
        self.test_mode = True
        
        # Check capabilities
        self.has_termux_api = self._check_termux_api()
        
        print("🧪 TEST TABLET MONITOR STARTING")
        print("=" * 50)
        print(f"📱 Device ID: {self.device_id}")
        print(f"📍 Location: {LOCATION}")
        print(f"🆔 Session: {self.session_id[:8]}...")
        print(f"📡 API: {API_URL}")
        print(f"⏱️  Interval: {SEND_INTERVAL} seconds (TEST MODE)")
        print(f"🔧 Termux:API: {'✅ Available' if self.has_termux_api else '❌ Not available (basic mode)'}")
        print("=" * 50)
    
    def _check_termux_api(self):
        """Check if Termux:API is available"""
        try:
            result = subprocess.run(['termux-battery-status'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _run_command_safe(self, cmd, timeout=10):
        """Run command with comprehensive error handling"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"⚠️  Command timeout: {' '.join(cmd)}")
        except FileNotFoundError:
            pass  # Command not found, silent fail
        except Exception as e:
            print(f"⚠️  Command error: {e}")
        return None
    
    def get_battery_info(self):
        """Get battery info with fallbacks"""
        if self.has_termux_api:
            try:
                output = self._run_command_safe(['termux-battery-status'])
                if output:
                    data = json.loads(output)
                    return {
                        "battery_level": data.get("percentage", 85),
                        "battery_temperature": data.get("temperature", 28.0),
                        "battery_status": data.get("status", "unknown"),
                        "source": "termux_api"
                    }
            except json.JSONDecodeError:
                pass
            except Exception:
                pass
        
        # Test data for validation
        return {
            "battery_level": 85,
            "battery_temperature": 28.5,
            "battery_status": "not_charging",
            "source": "test_fallback"
        }
    
    def get_wifi_info(self):
        """Get WiFi info with fallbacks"""
        wifi_data = {
            "wifi_signal_strength": -45,
            "wifi_ssid": "JD_Test_Network",
            "connectivity_status": "unknown",
            "source": "test_fallback"
        }
        
        if self.has_termux_api:
            try:
                output = self._run_command_safe(['termux-wifi-connectioninfo'])
                if output:
                    data = json.loads(output)
                    wifi_data.update({
                        "wifi_signal_strength": data.get("rssi", -45),
                        "wifi_ssid": data.get("ssid", "JD_Test_Network").replace('"', ''),
                        "source": "termux_api"
                    })
            except:
                pass
        
        # Test connectivity
        connectivity = "offline"
        try:
            # Quick ping test
            result = subprocess.run(['ping', '-c', '1', '-W', '3', '8.8.8.8'], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                connectivity = "online"
        except:
            try:
                # Fallback: try to connect to our API
                response = requests.get(API_URL.replace('/tablet-metrics', '/health'), 
                                      timeout=5)
                if response.status_code == 200:
                    connectivity = "online"
            except:
                pass
        
        wifi_data["connectivity_status"] = connectivity
        return wifi_data
    
    def check_test_processes(self):
        """Check for test-related processes"""
        teamviewer_active = False
        android_settings_active = False
        
        try:
            output = self._run_command_safe(['ps', '-A'], timeout=5)
            if output:
                processes = output.lower()
                
                # TeamViewer detection
                teamviewer_patterns = ['teamviewer', 'quicksupport']
                teamviewer_active = any(pattern in processes for pattern in teamviewer_patterns)
                
                # Android Settings detection
                settings_patterns = ['settings', 'com.android.settings']
                android_settings_active = any(pattern in processes for pattern in settings_patterns)
        except:
            pass
        
        return {
            "teamviewer_active": teamviewer_active,
            "android_settings_active": android_settings_active,
            "test_environment": True,
            "source": "ps_command" if output else "fallback"
        }
    
    def detect_activity(self):
        """Detect user activity for testing"""
        movement_detected = False
        
        if self.has_termux_api:
            try:
                output = self._run_command_safe(['termux-sensor', '-s', 'accelerometer', '-n', '1'], timeout=5)
                if output:
                    data = json.loads(output)
                    if 'values' in data and len(data['values']) >= 3:
                        movement = sum(abs(x) for x in data['values'][:3])
                        if movement > 10:
                            movement_detected = True
                            self.last_interaction = datetime.now(timezone.utc)
            except:
                pass
        
        inactive_seconds = int((datetime.now(timezone.utc) - self.last_interaction).total_seconds())
        
        return {
            "recent_movement": movement_detected,
            "inactive_seconds": inactive_seconds,
            "test_mode": True,
            "source": "accelerometer" if self.has_termux_api else "timer_only"
        }
    
    def collect_all_data(self):
        """Collect all monitoring data for testing"""
        try:
            print(f"🧪 Collecting test data... {datetime.now().strftime('%H:%M:%S')}")
            
            # Get all metrics with error handling
            battery_data = self.get_battery_info()
            wifi_data = self.get_wifi_info()
            process_data = self.check_test_processes()
            activity_data = self.detect_activity()
            
            # Generate test session events
            events = []
            if process_data.get("teamviewer_active"):
                events.append({
                    "event_type": "session_start",
                    "session_id": self.session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_message": "TeamViewer test session detected"
                })
            
            if activity_data.get("inactive_seconds", 0) > 60:  # 1 minute for testing
                events.append({
                    "event_type": "timeout",
                    "session_id": self.session_id,
                    "duration": activity_data.get("inactive_seconds", 0),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_message": f"Test timeout - {activity_data.get('inactive_seconds', 0)}s inactive"
                })
            
            # Create comprehensive payload
            payload = {
                "device_id": self.device_id,
                "device_name": f"Test Tablet - {self.device_id}",
                "location": LOCATION,
                "android_version": "Android 15 (Test)",
                "app_version": "test_monitor_1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": battery_data,
                "network_metrics": wifi_data,
                "app_metrics": {
                    "screen_state": "active" if activity_data.get("recent_movement") else "idle",
                    "app_foreground": "teamviewer" if process_data.get("teamviewer_active") else ("settings" if process_data.get("android_settings_active") else "unknown"),
                    "last_user_interaction": self.last_interaction.isoformat(),
                    **process_data,
                    **activity_data
                },
                "session_events": events,
                "raw_logs": [
                    f"TEST MODE: TeamViewer: {process_data.get('teamviewer_active', False)}",
                    f"TEST MODE: Settings: {process_data.get('android_settings_active', False)}",
                    f"TEST MODE: Inactive: {activity_data.get('inactive_seconds', 0)}s",
                    f"TEST MODE: Battery: {battery_data.get('battery_level', 0)}%",
                    f"TEST MODE: WiFi: {wifi_data.get('wifi_signal_strength', 0)}dBm"
                ]
            }
            
            return payload
            
        except Exception as e:
            print(f"❌ Data collection error: {e}")
            # Return minimal valid payload on error
            return {
                "device_id": self.device_id,
                "device_name": f"Test Tablet - {self.device_id}",
                "location": LOCATION,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": {"battery_level": 50, "battery_temperature": 25.0},
                "network_metrics": {"connectivity_status": "unknown"},
                "app_metrics": {"screen_state": "unknown"},
                "session_events": [],
                "raw_logs": [f"ERROR: {str(e)}"]
            }
    
    def send_data_with_retries(self, payload):
        """Send data with retry logic"""
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    self.successful_sends += 1
                    self.consecutive_failures = 0
                    
                    # Extract key metrics for display
                    battery = payload.get('device_metrics', {}).get('battery_level', 0)
                    teamviewer = payload.get('app_metrics', {}).get('teamviewer_active', False)
                    connectivity = payload.get('network_metrics', {}).get('connectivity_status', 'unknown')
                    
                    print(f"✅ TEST DATA SENT - Battery: {battery}% | TeamViewer: {teamviewer} | Network: {connectivity}")
                    return True
                    
                else:
                    print(f"⚠️  Attempt {attempt}/{MAX_RETRIES} failed: HTTP {response.status_code}")
                    if attempt == MAX_RETRIES:
                        self.consecutive_failures += 1
                        
            except requests.exceptions.Timeout:
                print(f"⚠️  Attempt {attempt}/{MAX_RETRIES} timed out")
            except requests.exceptions.ConnectionError:
                print(f"⚠️  Attempt {attempt}/{MAX_RETRIES} connection failed")
            except Exception as e:
                print(f"⚠️  Attempt {attempt}/{MAX_RETRIES} error: {e}")
            
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        self.consecutive_failures += 1
        return False
    
    def run_monitoring_loop(self):
        """Main monitoring loop for testing"""
        print("🚀 Starting test monitoring loop...")
        
        while True:
            try:
                # Collect and send data
                data = self.collect_all_data()
                self.total_sends += 1
                success = self.send_data_with_retries(data)
                
                # Display stats
                success_rate = (self.successful_sends / self.total_sends * 100) if self.total_sends > 0 else 0
                print(f"📊 Stats: {self.successful_sends}/{self.total_sends} sent ({success_rate:.1f}%) | Failures: {self.consecutive_failures}")
                
                # Warning if too many consecutive failures
                if self.consecutive_failures >= 5:
                    print("⚠️  WARNING: Multiple consecutive failures - check network/API")
                
                # Wait for next interval
                time.sleep(SEND_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n🛑 Test monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring loop error: {e}")
                time.sleep(10)  # Wait before retrying

def main():
    """Main function"""
    try:
        print("🧪 JD ENGINEERING TEST TABLET MONITOR")
        print(f"Ready for TeamViewer security bypass testing")
        print(f"Use Ctrl+C to stop monitoring\n")
        
        monitor = TestTabletMonitor()
        monitor.run_monitoring_loop()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 