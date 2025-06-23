#!/data/data/com.termux/files/usr/bin/python
"""
JD Engineering Tablet Monitor - BULLETPROOF VERSION
This script is designed to work reliably 24/7 under all conditions.
Priority #1: Reliability and stability.
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
# CONFIGURATION - MODIFY THESE IF NEEDED
# ==========================================
API_URL = "https://jd-engineering-monitoring-api-production.up.railway.app/tablet-metrics"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"
SEND_INTERVAL = 30  # seconds between data sends
MAX_RETRIES = 3     # API call retries
TIMEOUT = 30        # API timeout seconds

class BulletproofTabletMonitor:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.session_id = str(uuid.uuid4())
        self.last_interaction = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        self.total_sends = 0
        self.successful_sends = 0
        
        # Check capabilities
        self.has_termux_api = self._check_termux_api()
        
        print("🚀 BULLETPROOF TABLET MONITOR STARTING")
        print("=" * 50)
        print(f"📱 Device ID: {self.device_id}")
        print(f"🆔 Session: {self.session_id[:8]}...")
        print(f"📡 API: {API_URL}")
        print(f"⏱️  Interval: {SEND_INTERVAL} seconds")
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
                        "battery_level": data.get("percentage", 50),
                        "battery_temperature": data.get("temperature", 25.0),
                        "battery_status": data.get("status", "unknown"),
                        "source": "termux_api"
                    }
            except json.JSONDecodeError:
                pass
            except Exception:
                pass
        
        # Fallback data
        return {
            "battery_level": 50,
            "battery_temperature": 25.0,
            "battery_status": "unknown",
            "source": "fallback"
        }
    
    def get_wifi_info(self):
        """Get WiFi info with fallbacks"""
        wifi_data = {
            "wifi_signal_strength": -50,
            "wifi_ssid": "unknown",
            "connectivity_status": "unknown",
            "source": "fallback"
        }
        
        if self.has_termux_api:
            try:
                output = self._run_command_safe(['termux-wifi-connectioninfo'])
                if output:
                    data = json.loads(output)
                    wifi_data.update({
                        "wifi_signal_strength": data.get("rssi", -50),
                        "wifi_ssid": data.get("ssid", "unknown").replace('"', ''),
                        "source": "termux_api"
                    })
            except:
                pass
        
        # Test connectivity with multiple methods
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
    
    def check_processes(self):
        """Check for MYOB and scanner processes"""
        myob_active = False
        scanner_active = False
        
        try:
            output = self._run_command_safe(['ps', '-A'], timeout=5)
            if output:
                processes = output.lower()
                
                # MYOB detection
                myob_patterns = ['myob', 'accountright', 'com.myob']
                myob_active = any(pattern in processes for pattern in myob_patterns)
                
                # Scanner detection
                scanner_patterns = ['scanner', 'barcode', 'zebra', 'honeywell', 'datalogic']
                scanner_active = any(pattern in processes for pattern in scanner_patterns)
        except:
            pass
        
        return {
            "myob_active": myob_active,
            "scanner_active": scanner_active,
            "source": "ps_command" if output else "fallback"
        }
    
    def detect_activity(self):
        """Detect user activity"""
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
            "source": "accelerometer" if self.has_termux_api else "timer_only"
        }
    
    def collect_all_data(self):
        """Collect all monitoring data safely"""
        try:
            print(f"📊 Collecting data... {datetime.now().strftime('%H:%M:%S')}")
            
            # Get all metrics with error handling
            battery_data = self.get_battery_info()
            wifi_data = self.get_wifi_info()
            process_data = self.check_processes()
            activity_data = self.detect_activity()
            
            # Create session events
            events = []
            if process_data.get("myob_active") and activity_data.get("inactive_seconds", 0) > 300:
                events.append({
                    "event_type": "timeout",
                    "session_id": self.session_id,
                    "duration": activity_data.get("inactive_seconds", 0),
                    "error_message": f"MYOB timeout risk - {activity_data.get('inactive_seconds', 0)}s inactive",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            if process_data.get("scanner_active"):
                events.append({
                    "event_type": "session_start",
                    "session_id": self.session_id,
                    "error_message": "Barcode scanner activity detected",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # Build payload
            payload = {
                "device_id": self.device_id,
                "device_name": f"Android Tablet - {self.device_id}",
                "location": "Electrical Department",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": battery_data,
                "network_metrics": wifi_data,
                "app_metrics": {
                    "screen_state": "active" if activity_data.get("recent_movement") else "dimmed",
                    "app_foreground": "myob" if process_data.get("myob_active") else ("scanner" if process_data.get("scanner_active") else "unknown"),
                    "last_user_interaction": self.last_interaction.isoformat(),
                    **process_data,
                    **activity_data
                },
                "session_events": events,
                "raw_logs": [
                    f"Battery: {battery_data.get('battery_level', 0)}% ({battery_data.get('source', 'unknown')})",
                    f"WiFi: {wifi_data.get('connectivity_status', 'unknown')} ({wifi_data.get('source', 'unknown')})",
                    f"MYOB: {process_data.get('myob_active', False)}",
                    f"Scanner: {process_data.get('scanner_active', False)}",
                    f"Inactive: {activity_data.get('inactive_seconds', 0)}s"
                ]
            }
            
            return payload
            
        except Exception as e:
            print(f"❌ Data collection error: {e}")
            # Return minimal fallback payload
            return {
                "device_id": self.device_id,
                "device_name": f"Android Tablet - {self.device_id}",
                "location": "Electrical Department",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": {"battery_level": 50, "battery_temperature": 25, "battery_status": "unknown"},
                "network_metrics": {"wifi_signal_strength": -50, "wifi_ssid": "unknown", "connectivity_status": "unknown"},
                "app_metrics": {"screen_state": "dimmed", "app_foreground": "unknown"},
                "session_events": [],
                "raw_logs": [f"Error collecting data: {e}"]
            }
    
    def send_data_with_retries(self, payload):
        """Send data with multiple retry attempts"""
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    self.consecutive_failures = 0
                    self.successful_sends += 1
                    
                    # Status summary
                    battery = payload.get('device_metrics', {}).get('battery_level', 0)
                    myob = payload.get('app_metrics', {}).get('myob_active', False)
                    scanner = payload.get('app_metrics', {}).get('scanner_active', False)
                    connectivity = payload.get('network_metrics', {}).get('connectivity_status', 'unknown')
                    
                    print(f"✅ SUCCESS - Battery:{battery}% | WiFi:{connectivity} | MYOB:{myob} | Scanner:{scanner} | Success:{self.successful_sends}/{self.total_sends}")
                    return True
                else:
                    print(f"⚠️  API Error {response.status_code} (attempt {attempt}/{MAX_RETRIES})")
                    
            except requests.exceptions.Timeout:
                print(f"⏱️  Timeout (attempt {attempt}/{MAX_RETRIES})")
            except requests.exceptions.ConnectionError:
                print(f"🌐 Connection error (attempt {attempt}/{MAX_RETRIES})")
            except Exception as e:
                print(f"❌ Send error: {e} (attempt {attempt}/{MAX_RETRIES})")
            
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        self.consecutive_failures += 1
        print(f"❌ FAILED after {MAX_RETRIES} attempts. Consecutive failures: {self.consecutive_failures}")
        return False
    
    def run_monitoring_loop(self):
        """Main monitoring loop - bulletproof"""
        print("🎯 STARTING BULLETPROOF MONITORING LOOP")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        while True:
            try:
                self.total_sends += 1
                
                # Collect and send data
                data = self.collect_all_data()
                success = self.send_data_with_retries(data)
                
                # Adaptive sleep based on success/failure
                if success:
                    sleep_time = SEND_INTERVAL
                else:
                    # Longer sleep on failure to avoid hammering the API
                    sleep_time = min(SEND_INTERVAL * (1 + self.consecutive_failures), 300)
                    print(f"😴 Sleeping {sleep_time}s due to failures...")
                
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print(f"\n⏹️  MONITORING STOPPED BY USER")
                print(f"📊 Final Stats: {self.successful_sends}/{self.total_sends} successful sends")
                break
            except Exception as e:
                print(f"❌ Unexpected error in main loop: {e}")
                print("🔄 Continuing in 60 seconds...")
                time.sleep(60)
        
        print("🛑 BULLETPROOF MONITOR STOPPED")

def main():
    """Main function"""
    print("🚀 JD ENGINEERING BULLETPROOF TABLET MONITOR")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ required")
        sys.exit(1)
    
    # Check requests library
    try:
        import requests
    except ImportError:
        print("❌ requests library not found. Install with: pip install requests")
        sys.exit(1)
    
    print("✅ All requirements satisfied")
    print()
    
    # Start monitoring
    monitor = BulletproofTabletMonitor()
    monitor.run_monitoring_loop()

if __name__ == "__main__":
    main()
