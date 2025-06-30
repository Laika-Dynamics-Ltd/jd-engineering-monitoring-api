#!/data/data/com.termux/files/usr/bin/python
"""
Quick connection test for JD Engineering Tablet Monitor
Tests API connectivity before starting full monitoring
"""

import requests
import json
from datetime import datetime, timezone

# Configuration
API_URL = "https://jd-engineering-monitoring-api-production-5d93.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DEVICE_ID = "tablet_electrical_dept"

def test_connection():
    """Test API connectivity"""
    print("🧪 TESTING API CONNECTION")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Health check PASSED")
        else:
            print(f"   ❌ Health check FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check ERROR: {e}")
        return False
    
    # Test 2: Tablet metrics endpoint
    print("2️⃣ Testing tablet metrics endpoint...")
    test_data = {
        "device_id": f"{DEVICE_ID}_test",
        "device_name": "Connection Test",
        "location": "Testing",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_level": 100,
        "connectivity_status": "online",
        "wifi_signal_strength": -30,
        "myob_active": False,
        "scanner_active": False
    }
    
    try:
        response = requests.post(f"{API_URL}/tablet-metrics", 
                               headers=headers, 
                               json=test_data, 
                               timeout=10)
        if response.status_code == 200:
            print("   ✅ Tablet metrics PASSED")
            result = response.json()
            print(f"   📝 Response: {result.get('message', 'Success')}")
        else:
            print(f"   ❌ Tablet metrics FAILED: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Tablet metrics ERROR: {e}")
        return False
    
    # Test 3: Dashboard access
    print("3️⃣ Testing dashboard access...")
    try:
        response = requests.get(f"{API_URL}/dashboard", timeout=10)
        if response.status_code == 200:
            print("   ✅ Dashboard ACCESSIBLE")
        else:
            print(f"   ⚠️ Dashboard status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Dashboard error: {e}")
    
    print()
    print("🎉 CONNECTION TEST COMPLETE!")
    print("✅ Ready to start full monitoring")
    return True

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1) 