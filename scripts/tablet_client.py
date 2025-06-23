#!/data/data/com.termux/files/usr/bin/python
"""
Advanced tablet monitoring script with Termux:API for MYOB session timeout detection
and barcode scanner event monitoring for JD Engineering
"""

import json
import requests
import time
import subprocess
import os
import re
from datetime import datetime, timezone
from threading import Thread, Event
import uuid

# Railway API Configuration
RAILWAY_API_URL = "https://jd-engineering-monitoring-api-production.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"  # or "tablet_test_001" / "tablet_electrical_dept"

class AdvancedTabletMonitor:
    def __init__(self):
        self.api_url = f"{RAILWAY_API_URL}/tablet-metrics"
        self.headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.device_id = DEVICE_ID
        self.session_id = str(uuid.uuid4())
        self.last_user_interaction = datetime.now(timezone.utc)
        self.myob_session_active = False
        self.barcode_scanner_active = False
        self.stop_event = Event()
        
        # MYOB and scanner detection patterns
        self.myob_package_names = [
            "com.myob",
            "au.com.myob",
            "myob",
            "accountright"
        ]
        
        self.scanner_package_names = [
            "com.zebra",
            "barcode",
            "scanner",
            "honeywell",
            "datalogic"
        ]
        
        print(f"🚀 Advanced monitoring initialized for {self.device_id}")
        print(f"📱 Session ID: {self.session_id}")
    
    def run_termux_command(self, command, timeout=10):
        """Safely run Termux API command with error handling"""
        try:
            if isinstance(command, str):
                command = command.split()
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"raw_output": result.stdout.strip()}
            else:
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ Command timeout: {' '.join(command)}")
            return None
        except Exception as e:
            print(f"⚠️ Command error: {e}")
            return None
    
    def get_comprehensive_battery_info(self):
        """Enhanced battery monitoring with health and charging details"""
        battery_data = self.run_termux_command(['termux-battery-status'])
        if battery_data:
            return {
                "battery_level": battery_data.get("percentage"),
                "battery_temperature": battery_data.get("temperature"),
                "battery_health": battery_data.get("health"),
                "battery_plugged": battery_data.get("plugged"),
                "battery_status": battery_data.get("status"),
                "battery_voltage": battery_data.get("voltage")
            }
        return {}
    
    def get_advanced_wifi_info(self):
        """Enhanced WiFi monitoring with detailed connection info"""
        wifi_data = {"network_type": "WiFi", "connectivity_status": "unknown"}
        
        # Get WiFi connection details
        wifi_info = self.run_termux_command(['termux-wifi-connectioninfo'])
        if wifi_info:
            wifi_data.update({
                "wifi_signal_strength": wifi_info.get("rssi"),
                "wifi_ssid": wifi_info.get("ssid", "").replace('"', ''),
                "network_type": "WiFi",
                "ip_address": wifi_info.get("ip"),
                "bssid": wifi_info.get("bssid"),
                "frequency": wifi_info.get("frequency"),
                "link_speed": wifi_info.get("link_speed"),
                "network_id": wifi_info.get("network_id")
            })
        
        # Test connectivity
        try:
            test = subprocess.run(['ping', '-c', '1', '-W', '3', '8.8.8.8'], 
                                capture_output=True, timeout=5)
            wifi_data["connectivity_status"] = "online" if test.returncode == 0 else "offline"
        except:
            wifi_data["connectivity_status"] = "unknown"
        
        return wifi_data
    
    def get_running_apps_and_processes(self):
        """Get detailed information about running applications"""
        try:
            ps_result = subprocess.run(['ps', '-A'], capture_output=True, text=True, timeout=10)
            if ps_result.returncode == 0:
                processes = ps_result.stdout.strip().split('\n')[1:]
                
                myob_processes = []
                scanner_processes = []
                
                for process in processes:
                    process_lower = process.lower()
                    
                    # Check for MYOB processes
                    for myob_pattern in self.myob_package_names:
                        if myob_pattern.lower() in process_lower:
                            myob_processes.append(process.strip())
                            self.myob_session_active = True
                    
                    # Check for barcode scanner processes
                    for scanner_pattern in self.scanner_package_names:
                        if scanner_pattern.lower() in process_lower:
                            scanner_processes.append(process.strip())
                            self.barcode_scanner_active = True
                
                return {
                    "myob_processes": myob_processes,
                    "scanner_processes": scanner_processes,
                    "total_processes": len(processes),
                    "myob_active": len(myob_processes) > 0,
                    "scanner_active": len(scanner_processes) > 0
                }
        except Exception as e:
            print(f"⚠️ Process detection error: {e}")
        
        return {"myob_active": False, "scanner_active": False}
    
    def detect_user_interaction(self):
        """Detect user interaction patterns and session timeouts"""
        interaction_data = {}
        
        # Get sensor data to detect device movement/usage
        sensor_data = self.run_termux_command(['termux-sensor', '-s', 'accelerometer', '-n', '1'])
        if sensor_data and 'values' in sensor_data:
            accel_values = sensor_data['values']
            if len(accel_values) >= 3:
                movement_magnitude = sum(abs(x) for x in accel_values[:3])
                if movement_magnitude > 10:
                    self.last_user_interaction = datetime.now(timezone.utc)
                    interaction_data['recent_movement'] = True
                else:
                    interaction_data['recent_movement'] = False
        
        # Calculate time since last interaction
        time_since_interaction = (datetime.now(timezone.utc) - self.last_user_interaction).total_seconds()
        interaction_data['seconds_since_interaction'] = int(time_since_interaction)
        
        # Detect potential session timeout (5+ minutes of inactivity)
        if time_since_interaction > 300:
            interaction_data['potential_timeout'] = True
            if self.myob_session_active:
                interaction_data['myob_timeout_risk'] = True
        else:
            interaction_data['potential_timeout'] = False
            interaction_data['myob_timeout_risk'] = False
        
        return interaction_data
    
    def generate_session_events(self, interaction_data, app_data):
        """Generate session events based on detected patterns"""
        events = []
        current_time = datetime.now(timezone.utc)
        
        # MYOB session timeout detection
        if (interaction_data.get('myob_timeout_risk', False) and 
            app_data.get('myob_active', False)):
            events.append({
                "event_type": "timeout",
                "session_id": self.session_id,
                "duration": interaction_data.get('seconds_since_interaction', 0),
                "error_message": f"MYOB session timeout risk detected - {interaction_data.get('seconds_since_interaction', 0)}s of inactivity",
                "app_version": "myob_detected",
                "timestamp": current_time.isoformat()
            })
        
        # Scanner event detection
        if app_data.get('scanner_active', False):
            events.append({
                "event_type": "session_start",
                "session_id": self.session_id,
                "error_message": "Barcode scanner activity detected",
                "app_version": "scanner_active",
                "timestamp": current_time.isoformat()
            })
        
        return events
    
    def collect_comprehensive_data(self):
        """Collect all enhanced monitoring data"""
        try:
            print(f"📊 Collecting comprehensive data at {datetime.now()}")
            
            # Collect all metrics
            device_metrics = self.get_comprehensive_battery_info()
            network_metrics = self.get_advanced_wifi_info()
            app_data = self.get_running_apps_and_processes()
            interaction_data = self.detect_user_interaction()
            
            # Combine app and interaction data
            app_metrics = {
                "screen_state": "active" if interaction_data.get('recent_movement') else "idle",
                "app_foreground": "myob" if app_data.get('myob_active') else ("scanner" if app_data.get('scanner_active') else "unknown"),
                "last_user_interaction": self.last_user_interaction.isoformat(),
                "notification_count": 0,
                "screen_timeout_setting": 300,
                **interaction_data,
                **app_data
            }
            
            # Generate session events
            session_events = self.generate_session_events(interaction_data, app_data)
            
            # Prepare comprehensive payload
            payload = {
                "device_id": self.device_id,
                "device_name": f"Android Tablet - {self.device_id}",
                "location": "Electrical Department" if "electrical" in self.device_id else "Test Environment",
                "android_version": "Unknown",
                "app_version": "advanced_monitor_v2.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "device_metrics": device_metrics if device_metrics else None,
                "network_metrics": network_metrics if network_metrics else None,
                "app_metrics": app_metrics if app_metrics else None,
                "session_events": session_events,
                "raw_logs": [
                    f"MYOB Active: {app_data.get('myob_active', False)}",
                    f"Scanner Active: {app_data.get('scanner_active', False)}",
                    f"Timeout Risk: {interaction_data.get('myob_timeout_risk', False)}"
                ]
            }
            
            return payload
            
        except Exception as e:
            print(f"❌ Error collecting comprehensive data: {e}")
            return None
    
    def send_data_to_api(self, payload):
        """Send collected data to Railway API"""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Data sent - MYOB: {payload.get('app_metrics', {}).get('myob_active', False)}, Scanner: {payload.get('app_metrics', {}).get('scanner_active', False)}")
                return True
            else:
                print(f"❌ API error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending data: {e}")
            return False
    
    def run_monitoring_loop(self):
        """Main enhanced monitoring loop"""
        print(f"🚀 Starting advanced tablet monitoring for {self.device_id}")
        print(f"📡 Monitoring MYOB sessions and barcode scanner events")
        print(f"🎯 API endpoint: {RAILWAY_API_URL}")
        
        while not self.stop_event.is_set():
            try:
                payload = self.collect_comprehensive_data()
                
                if payload:
                    success = self.send_data_to_api(payload)
                    if success:
                        time.sleep(30)  # 30 seconds between collections
                    else:
                        time.sleep(60)  # Wait longer on API errors
                else:
                    time.sleep(45)  # Wait on data collection errors
                    
            except KeyboardInterrupt:
                print("\n⏹️ Advanced monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring loop error: {e}")
                time.sleep(60)
    
    def stop(self):
        """Stop the monitoring loop"""
        self.stop_event.set()

if __name__ == "__main__":
    monitor = AdvancedTabletMonitor()
    try:
        monitor.run_monitoring_loop()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down advanced monitoring...")
        monitor.stop()
