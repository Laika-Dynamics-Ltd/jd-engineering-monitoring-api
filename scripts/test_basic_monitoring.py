#!/data/data/com.termux/files/usr/bin/python
"""
Basic test script to verify tablet monitoring functionality
Run this first to ensure everything is working before using the advanced monitor
"""

import json
import requests
import time
import subprocess
from datetime import datetime, timezone

# Configuration
RAILWAY_API_URL = "https://jd-engineering-monitoring-api-production.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"

def test_api_connection():
    """Test connection to the API"""
    print("🔗 Testing API connection...")
    try:
        response = requests.get(f"{RAILWAY_API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_termux_battery():
    """Test basic Termux battery function"""
    print("🔋 Testing Termux battery status...")
    try:
        result = subprocess.run(['termux-battery-status'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            battery_data = json.loads(result.stdout)
            print(f"✅ Battery: {battery_data.get('percentage', 'Unknown')}%")
            return True
        else:
            print("❌ Battery status failed")
            return False
    except Exception as e:
        print(f"❌ Battery test error: {e}")
        return False

def send_test_data():
    """Send a simple test payload to the API"""
    print("📤 Sending test data...")
    
    payload = {
        "device_id": DEVICE_ID,
        "device_name": f"Test Tablet - {DEVICE_ID}",
        "location": "Test Environment",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_metrics": {"battery_level": 85, "battery_temperature": 25.0},
        "network_metrics": {"connectivity_status": "online", "wifi_ssid": "test_network"},
        "app_metrics": {"screen_state": "active", "app_foreground": "test"},
        "session_events": [],
        "raw_logs": ["Basic monitoring test"]
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{RAILWAY_API_URL}/tablet-metrics",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Test data sent successfully")
            return True
        else:
            print(f"❌ Data send failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Send test error: {e}")
        return False

def main():
    print("🚀 JD Engineering Basic Monitoring Test")
    print("=" * 50)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Termux Battery", test_termux_battery),
        ("Send Test Data", send_test_data)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            failed += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All basic tests passed! Ready to run advanced monitoring.")
        print("Run: python tablet_client.py")
    else:
        print(f"\n⚠️ {failed} tests failed. Fix issues before running advanced monitoring.")
        
        if failed == 1 and passed >= 2:
            print("Basic functionality works - you can try the advanced monitor.")

if __name__ == "__main__":
    main() 