#!/usr/bin/env python3
"""
Comprehensive Railway API Test Script
Tests API health, database connectivity, and tablet metrics submission
"""

import requests
import json
import time
from datetime import datetime, timezone

# Configuration
API_BASE_URL = "https://jd-engineering-monitoring-api-production-5d93.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"

def test_api_health():
    """Test API health endpoint"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data.get('status')}")
            print(f"   🗄️ Database: {data.get('database')}")
            print(f"   🌍 Environment: {data.get('environment')}")
            return True
        else:
            print(f"   ❌ Health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_api_docs():
    """Test API documentation availability"""
    print("\n📚 Testing API Documentation...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Docs Available: {'✅ Yes' if response.status_code == 200 else '❌ No'}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Docs test error: {e}")
        return False

def test_tablet_metrics_endpoint():
    """Test tablet metrics submission"""
    print("\n📱 Testing Tablet Metrics Submission...")
    
    # Create test payload
    test_payload = {
        "device_id": "test_tablet_api_check",
        "device_name": "Test Tablet - API Verification",
        "location": "Testing Environment",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_metrics": {
            "battery_level": 85,
            "battery_temperature": 28.5,
            "memory_available": 2000000000,
            "cpu_usage": 45.2
        },
        "network_metrics": {
            "wifi_signal_strength": -45,
            "connectivity_status": "online",
            "dns_response_time": 15.2
        },
        "app_metrics": {
            "screen_state": "active",
            "myob_active": True,
            "scanner_active": False,
            "last_user_interaction": datetime.now(timezone.utc).isoformat()
        },
        "session_events": [
            {
                "event_type": "session_start",
                "session_id": "test_session_123",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_message": "API connectivity test"
            }
        ],
        "raw_logs": ["Test log entry 1", "Test log entry 2"]
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tablet-metrics",
            headers=headers,
            json=test_payload,
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Tablet metrics submission successful!")
            return True
        else:
            print(f"   ❌ Tablet metrics submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Tablet metrics test error: {e}")
        return False

def test_device_listing():
    """Test device listing endpoint"""
    print("\n📋 Testing Device Listing...")
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/devices", headers=headers, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            devices = response.json()
            print(f"   ✅ Found {len(devices)} devices")
            return True
        else:
            print(f"   ❌ Device listing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Device listing error: {e}")
        return False

def test_database_endpoints():
    """Test database-related endpoints"""
    print("\n🗄️ Testing Database Endpoints...")
    
    # Test simple database query endpoint
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/test-devices", headers=headers, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Database test successful")
            print(f"   Database Type: {data.get('database_type', 'unknown')}")
            print(f"   Device Count: {data.get('device_count', 0)}")
            return True
        else:
            print(f"   ❌ Database test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Database test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 RAILWAY API COMPREHENSIVE TEST")
    print("=" * 50)
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"🔑 Using API Token: {API_TOKEN[:10]}...")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_api_health),
        ("API Documentation", test_api_docs),
        ("Database Test", test_database_endpoints),
        ("Tablet Metrics", test_tablet_metrics_endpoint),
        ("Device Listing", test_device_listing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
    
    print(f"\n🏆 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your API is working correctly!")
        print("\n📱 Ready for tablet deployment:")
        print(f"   - Update tablet scripts with: {API_BASE_URL}")
        print(f"   - Use API token: {API_TOKEN}")
        print("   - Run tablet monitoring script")
    else:
        print("⚠️  Some tests failed. Check Railway logs and database connection.")
        print("\n🔍 Troubleshooting steps:")
        print("   1. Check Railway deployment status")
        print("   2. Verify DATABASE_URL environment variable")
        print("   3. Check application logs in Railway dashboard")
        print("   4. Ensure PostgreSQL service is running")

if __name__ == "__main__":
    main() 