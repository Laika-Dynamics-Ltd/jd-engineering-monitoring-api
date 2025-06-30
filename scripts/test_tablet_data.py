#!/usr/bin/env python3
"""
Test Tablet Data Submission
Simulates exactly what the tablet client sends
"""

import requests
import json
from datetime import datetime, timezone

API_URL = "https://jd-engineering-monitoring-api-production-5d93.up.railway.app/tablet-metrics"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"

# Simulate test tablet data
payload = {
    "device_id": "test_tablet_001",
    "device_name": "Test Tablet - test_tablet_001",
    "location": "Testing Environment",
    "android_version": "Android 15 (Test)",
    "app_version": "test_monitor_1.0",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "device_metrics": {
        "battery_level": 85,
        "battery_temperature": 28.5,
        "battery_status": "not_charging",
        "source": "test_fallback"
    },
    "network_metrics": {
        "wifi_signal_strength": -45,
        "wifi_ssid": "JD_Test_Network",
        "connectivity_status": "online",
        "source": "test_fallback"
    },
    "app_metrics": {
        "screen_state": "active",
        "app_foreground": "teamviewer",
        "last_user_interaction": datetime.now(timezone.utc).isoformat(),
        "teamviewer_active": True,
        "android_settings_active": False,
        "test_environment": True,
        "recent_movement": False,
        "inactive_seconds": 0,
        "test_mode": True,
        "source": "timer_only"
    },
    "session_events": [
        {
            "event_type": "session_start",
            "session_id": "test_session_001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_message": "TeamViewer test session detected"
        }
    ],
    "raw_logs": [
        "TEST MODE: TeamViewer: True",
        "TEST MODE: Settings: False",
        "TEST MODE: Inactive: 0s",
        "TEST MODE: Battery: 85%",
        "TEST MODE: WiFi: -45dBm"
    ]
}

print("📱 Sending test tablet data...")
print(f"🆔 Device ID: {payload['device_id']}")
print(f"📍 Location: {payload['location']}")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

print(f"\n📊 Response Status: {response.status_code}")
print(f"📝 Response: {response.text}")

if response.status_code == 200:
    print("\n✅ SUCCESS! Data sent successfully")
    
    # Now check if device appears in list
    print("\n🔍 Checking devices list...")
    devices_response = requests.get(
        "https://jd-engineering-monitoring-api-production-5d93.up.railway.app/devices",
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    
    if devices_response.status_code == 200:
        devices = devices_response.json()
        print(f"📱 Found {len(devices)} devices:")
        for device in devices:
            print(f"   - {device.get('device_id', 'Unknown')} ({device.get('device_name', 'Unknown')})")
    else:
        print(f"❌ Failed to get devices: {devices_response.status_code}")
        
else:
    print(f"\n❌ FAILED! Status: {response.status_code}")
    print(f"Error: {response.text}") 