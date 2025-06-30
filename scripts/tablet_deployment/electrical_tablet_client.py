#!/data/data/com.termux/files/usr/bin/python
"""
JD Engineering Electrical Department Tablet Monitor
Production monitoring for MYOB sessions and barcode scanners
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
# ELECTRICAL DEPARTMENT CONFIGURATION
# ==========================================
API_URL = "https://jd-engineering-monitoring-api-production-5d93.up.railway.app/tablet-metrics"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"
LOCATION = "Electrical Department"
SEND_INTERVAL = 30  # Production interval (30 seconds)
MAX_RETRIES = 3     # Standard retries
TIMEOUT = 30        # Standard timeout

class ElectricalTabletMonitor:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.session_id = str(uuid.uuid4())
        self.last_interaction = datetime.now(timezone.utc)
        self.consecutive_failures = 0
        self.total_sends = 0
        self.successful_sends = 0
        self.production_mode = True
        
        # Check capabilities
        self.has_termux_api = self._check_termux_api()
        
        print("⚡ ELECTRICAL DEPARTMENT TABLET MONITOR STARTING")
        print("=" * 50)
        print(f"📱 Device ID: {self.device_id}")
        print(f"📍 Location: {LOCATION}")
        print(f"🆔 Session: {self.session_id[:8]}...")
        print(f"📡 API: {API_URL}")
        print(f"⏱️  Interval: {SEND_INTERVAL} seconds (PRODUCTION)")
        print(f"🔧 Termux:API: {'✅ Available' if self.has_termux_api else '❌ Not available (basic mode)'}")
        print(f"🏭 Monitoring: MYOB AccountRight, Barcode Scanners")
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
                        "battery_health": data.get("health", "unknown"),
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
            "battery_health": "unknown",
            "source": "fallback"
        }
    
    def get_wifi_info(self):
        """Get WiFi info with fallbacks"""
        wifi_data = {
            "wifi_signal_strength": -50,
            "wifi_ssid": "JD_Electrical",
            "connectivity_status": "unknown",
            "network_type": "wifi",
            "source": "fallback"
        }
        
        if self.has_termux_api:
            try:
                output = self._run_command_safe(['termux-wifi-connectioninfo'])
                if output:
                    data = json.loads(output)
                    wifi_data.update({
                        "wifi_signal_strength": data.get("rssi", -50),
                        "wifi_ssid": data.get("ssid", "JD_Electrical").replace('"', ''),
                        "network_type": "wifi",
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
    
    def check_myob_processes(self):
        """Check for MYOB AccountRight processes"""
        myob_active = False
        myob_process_count = 0
        
        try:
            output = self._run_command_safe(['ps', '-A'], timeout=5)
            if output:
                processes = output.lower()
                
                # MYOB detection patterns
                myob_patterns = [
                    'myob', 'accountright', 'com.myob',
                    'myob.accountright', 'ar.android'
                ]
                
                for pattern in myob_patterns:
                    if pattern in processes:
                        myob_active = True
                        myob_process_count += processes.count(pattern)
        except:
            pass
        
        return {
            "myob_active": myob_active,
            "myob_process_count": myob_process_count,
            "source": "ps_command" if output else "fallback"
        }
    
    def check_scanner_processes(self):
        """Check for barcode scanner processes"""
        scanner_active = False
        scanner_process_count = 0
        
        try:
            output = self._run_command_safe(['ps', '-A'], timeout=5)
            if output:
                processes = output.lower()
                
                # Scanner detection patterns
                scanner_patterns = [
                    'scanner', 'barcode', 'zebra', 'honeywell', 
                    'datalogic', 'scan', 'qr', 'camera'
                ]
                
                for pattern in scanner_patterns:
                    if pattern in processes:
                        scanner_active = True
                        scanner_process_count += processes.count(pattern)
        except:
            pass
        
        return {
            "scanner_active": scanner_active,
            "scanner_process_count": scanner_process_count,
            "source": "ps_command" if output else "fallback"
        }
    
    def detect_user_activity(self):
        """Detect user activity for production monitoring"""
        movement_detected = False
        
        if self.has_termux_api:
            try:
                output = self._run_command_safe(['termux-sensor', '-s', 'accelerometer', '-n', '1'], timeout=5)
                if output:
                    data = json.loads(output)
                    if 'values' in data and len(data['values']) >= 3:
                        movement = sum(abs(x) for x in data['values'][:3])
                        if movement > 10:  # Device is moving
                            movement_detected = True
                            self.last_interaction = datetime.now(timezone.utc)
            except:
                pass
        
        inactive_seconds = int((datetime.now(timezone.utc) - self.last_interaction).total_seconds())
        
        return {
            "recent_movement": movement_detected,
            "inactive_seconds": inactive_seconds,
            "production_mode": True,
            "source": "accelerometer" if self.has_termux_api else "timer_only"
        }
    
    def generate_session_events(self, myob_data, scanner_data, activity_data):
        """Generate session events for production monitoring"""
        events = []
        
        # MYOB timeout detection (critical for electrical department)
        if myob_data.get("myob_active") and activity_data.get("inactive_seconds", 0) > 300:  # 5 minutes
            events.append({
                "event_type": "timeout",
                "session_id": self.session_id,
                "duration": activity_data.get("inactive_seconds", 0),
                "error_message": f"MYOB timeout risk - {activity_data.get('inactive_seconds', 0)}s inactive in electrical dept",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # MYOB session start detection
        if myob_data.get("myob_active") and myob_data.get("myob_process_count", 0) > 0:
            events.append({
                "event_type": "session_start",
                "session_id": self.session_id,
                "error_message": f"MYOB AccountRight active - {myob_data.get('myob_process_count', 0)} processes",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Scanner activity detection (important for inventory)
        if scanner_data.get("scanner_active"):
            events.append({
                "event_type": "session_start",
                "session_id": self.session_id,
                "error_message": f"Barcode scanner activity - {scanner_data.get('scanner_process_count', 0)} processes",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Extended inactivity warning (critical for production)
        if activity_data.get("inactive_seconds", 0) > 600:  # 10 minutes
            events.append({
                "event_type": "error",
                "session_id": self.session_id,
                "duration": activity_data.get("inactive_seconds", 0),
                "error_message": f"Extended inactivity - electrical dept tablet idle for {activity_data.get('inactive_seconds', 0)}s",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return events
    
    def collect_all_data(self):
        """Collect all monitoring data for electrical department"""
        try:
            print(f"⚡ Collecting electrical dept data... {datetime.now().strftime('%H:%M:%S')}")
            
            # Get all metrics
            battery_data = self.get_battery_info()
            wifi_data = self.get_wifi_info()
            myob_data = self.check_myob_processes()
            scanner_data = self.check_scanner_processes()
            activity_data = self.detect_user_activity()
            
            # Generate events
            events = self.generate_session_events(myob_data, scanner_data, activity_data)
            
            # Create comprehensive payload
            payload = {
                "device_id": self.device_id,
                "device_name": "Android Tablet - Electrical Department",
                "location": LOCATION,
                "android_version": "Production Android",
                "app_version": "electrical_monitor_1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": battery_data,
                "network_metrics": wifi_data,
                "app_metrics": {
                    "screen_state": "active" if activity_data.get("recent_movement") else "idle",
                    "app_foreground": (
                        "myob" if myob_data.get("myob_active") else
                        ("scanner" if scanner_data.get("scanner_active") else "unknown")
                    ),
                    "last_user_interaction": self.last_interaction.isoformat(),
                    "notification_count": 0,
                    **myob_data,
                    **scanner_data,
                    **activity_data
                },
                "session_events": events,
                "raw_logs": [
                    f"ELECTRICAL: MYOB Active: {myob_data.get('myob_active', False)}",
                    f"ELECTRICAL: MYOB Processes: {myob_data.get('myob_process_count', 0)}",
                    f"ELECTRICAL: Scanner Active: {scanner_data.get('scanner_active', False)}",
                    f"ELECTRICAL: Scanner Processes: {scanner_data.get('scanner_process_count', 0)}",
                    f"ELECTRICAL: Inactive: {activity_data.get('inactive_seconds', 0)}s",
                    f"ELECTRICAL: Battery: {battery_data.get('battery_level', 0)}%",
                    f"ELECTRICAL: Signal: {wifi_data.get('wifi_signal_strength', 0)}dBm"
                ]
            }
            
            return payload
            
        except Exception as e:
            print(f"❌ Data collection error: {e}")
            # Return minimal valid payload on error
            return {
                "device_id": self.device_id,
                "device_name": "Android Tablet - Electrical Department",
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
                    myob = payload.get('app_metrics', {}).get('myob_active', False)
                    scanner = payload.get('app_metrics', {}).get('scanner_active', False)
                    inactive = payload.get('app_metrics', {}).get('inactive_seconds', 0)
                    
                    print(f"✅ ELECTRICAL DATA SENT - Battery: {battery}% | MYOB: {myob} | Scanner: {scanner} | Idle: {inactive}s")
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
        """Main monitoring loop for electrical department"""
        print("🚀 Starting electrical department monitoring...")
        
        while True:
            try:
                # Collect and send data
                data = self.collect_all_data()
                self.total_sends += 1
                success = self.send_data_with_retries(data)
                
                # Display stats
                success_rate = (self.successful_sends / self.total_sends * 100) if self.total_sends > 0 else 0
                print(f"📊 ELECTRICAL Stats: {self.successful_sends}/{self.total_sends} sent ({success_rate:.1f}%) | Failures: {self.consecutive_failures}")
                
                # Critical warning for production environment
                if self.consecutive_failures >= 3:
                    print("🚨 CRITICAL: Multiple failures in electrical department monitoring!")
                    print("🚨 Check network connectivity and API status immediately!")
                
                # Wait for next interval
                time.sleep(SEND_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n🛑 Electrical department monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitoring loop error: {e}")
                time.sleep(10)  # Wait before retrying

def main():
    """Main function"""
    try:
        print("⚡ JD ENGINEERING ELECTRICAL DEPARTMENT MONITOR")
        print(f"Production monitoring for MYOB AccountRight & Barcode Scanners")
        print(f"Critical timeout detection for electrical department workflows")
        print(f"Use Ctrl+C to stop monitoring\n")
        
        monitor = ElectricalTabletMonitor()
        monitor.run_monitoring_loop()
        
    except Exception as e:
        print(f"❌ Fatal error in electrical department monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 