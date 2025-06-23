#!/usr/bin/env python3
"""
Test script to verify data persistence in the JD Engineering monitoring system.
"""

import requests
import json
import time
from datetime import datetime, timezone

# Configuration
API_BASE = "https://jd-engineering-monitoring-api-production.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"

def test_data_submission():
    """Test submitting comprehensive data to the API"""
    print("🧪 Testing data submission...")
    
    test_payload = {
        "device_id": "test_tablet_persistence",
        "device_name": "Test Tablet - Persistence Check",
        "location": "Test Lab",
        "android_version": "11.0",
        "app_version": "1.0.0-test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_metrics": {
            "battery_level": 75,
            "battery_temperature": 28.5,
            "memory_available": 2147483648,
            "memory_total": 4294967296,
            "storage_available": 10737418240,
            "cpu_usage": 45.2,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "network_metrics": {
            "wifi_signal_strength": -45,
            "wifi_ssid": "JD_Engineering_WiFi",
            "connectivity_status": "online",
            "network_type": "WiFi",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "app_metrics": {
            "screen_state": "active",
            "app_foreground": "myob",
            "last_user_interaction": datetime.now(timezone.utc).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/tablet-metrics",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            },
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data submitted successfully!")
            return True
        else:
            print(f"❌ Submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Submission error: {e}")
        return False

def test_chart_data():
    """Test chart data endpoints"""
    print("📊 Testing chart data endpoints...")
    
    endpoints = [
        "/analytics/charts/battery",
        "/analytics/charts/wifi", 
        "/analytics/charts/myob",
        "/analytics/charts/scanner"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{API_BASE}{endpoint}?hours=24",
                headers={"Authorization": f"Bearer {API_TOKEN}"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                devices_count = len(data.get('devices', {}))
                print(f"✅ {endpoint}: {devices_count} devices with data")
            else:
                print(f"❌ {endpoint}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    """Run persistence tests"""
    print("🚀 JD ENGINEERING DATA PERSISTENCE TEST")
    print("=" * 50)
    
    # Test data submission
    success = test_data_submission()
    
    if success:
        print("\n⏳ Waiting for data processing...")
        time.sleep(5)
        
        # Test chart data retrieval
        test_chart_data()
        
        print("\n🎉 Data persistence tests completed!")
    else:
        print("\n⚠️ Data persistence test failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
