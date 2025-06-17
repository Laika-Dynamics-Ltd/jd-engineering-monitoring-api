#!/usr/bin/env python3
"""
Test script for Railway-deployed Tablet Monitoring API
Usage: python test_api.py <railway_url> <api_token>
"""

import requests
import json
import sys
from datetime import datetime, timezone

def test_api(base_url, api_token):
    """Test all API endpoints"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🧪 Testing API at: {base_url}")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Submit test tablet data
    print("\n2. Testing tablet data submission...")
    test_data = {
        "device_id": "test_tablet_001",
        "device_name": "Test Tablet - Railway Deploy",
        "location": "Test Environment",
        "android_version": "13.0",
        "device_metrics": {
            "battery_level": 85,
            "battery_temperature": 32.5,
            "memory_available": 2147483648,
            "memory_total": 4294967296,
            "cpu_usage": 45.2
        },
        "network_metrics": {
            "wifi_signal_strength": -45,
            "wifi_ssid": "TestNetwork",
            "connectivity_status": "online",
            "network_type": "WiFi",
            "dns_response_time": 12.5
        },
        "app_metrics": {
            "screen_state": "active",
            "app_foreground": "com.company.loginapp",
            "app_memory_usage": 134217728,
            "screen_timeout_setting": 300,
            "notification_count": 2
        },
        "session_events": [
            {
                "event_type": "login",
                "session_id": "test_session_001",
                "duration": 0,
                "user_id": "test_user"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/tablet-metrics",
            headers=headers,
            json=test_data,
            timeout=15
        )
        print(f"✅ Data submission: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Data submission failed: {e}")
        return False
    
    # Test 3: Get devices list
    print("\n3. Testing devices list...")
    try:
        response = requests.get(f"{base_url}/devices", headers=headers, timeout=10)
        devices = response.json()
        print(f"✅ Devices list: {response.status_code} - Found {len(devices)} devices")
        for device in devices[:3]:  # Show first 3
            print(f"   📱 {device['device_id']} - {device.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Devices list failed: {e}")
    
    # Test 4: Get device metrics
    print("\n4. Testing device metrics...")
    try:
        response = requests.get(
            f"{base_url}/devices/test_tablet_001/metrics?hours=1",
            headers=headers,
            timeout=10
        )
        metrics = response.json()
        print(f"✅ Device metrics: {response.status_code}")
        print(f"   📊 Device records: {len(metrics.get('device_metrics', []))}")
        print(f"   📡 Network records: {len(metrics.get('network_metrics', []))}")
        print(f"   📱 App records: {len(metrics.get('app_metrics', []))}")
    except Exception as e:
        print(f"❌ Device metrics failed: {e}")
    
    # Test 5: Session analytics
    print("\n5. Testing session analytics...")
    try:
        response = requests.get(
            f"{base_url}/analytics/session-issues?hours=24",
            headers=headers,
            timeout=10
        )
        analytics = response.json()
        print(f"✅ Session analytics: {response.status_code}")
        print(f"   📈 Session analysis records: {len(analytics.get('session_analysis', []))}")
    except Exception as e:
        print(f"❌ Session analytics failed: {e}")
    
    print("\n🎉 API testing completed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_api.py <railway_url> <api_token>")
        print("Example: python test_api.py https://your-app.railway.app your-api-token")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    api_token = sys.argv[2]
    
    test_api(base_url, api_token)