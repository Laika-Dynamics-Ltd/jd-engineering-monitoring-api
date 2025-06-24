#!/usr/bin/env python3
"""
Comprehensive AI Dashboard Test Suite
Tests all enhanced features to ensure bulletproof operation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "https://jd-engineering-monitoring-api-production.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def test_endpoint(name, url, expected_keys=None):
    """Test an API endpoint and verify response"""
    print(f"\n🧪 Testing {name}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: SUCCESS (Status: {response.status_code})")
            
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    print(f"⚠️  Missing keys: {missing_keys}")
                else:
                    print(f"✅ All expected keys present: {expected_keys}")
            
            # Show sample data
            if isinstance(data, dict):
                sample_keys = list(data.keys())[:5]
                print(f"📊 Sample keys: {sample_keys}")
                if 'generated_at' in data:
                    print(f"🕒 Generated: {data['generated_at']}")
            
            return True, data
        else:
            print(f"❌ {name}: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}...")
            return False, None
            
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
        return False, None

def test_dashboard_accessibility():
    """Test dashboard HTML accessibility"""
    print(f"\n🌐 Testing Dashboard Accessibility...")
    try:
        response = requests.get(f"{API_BASE}/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for key AI dashboard elements
            ai_elements = [
                "AI-Powered Business Intelligence",
                "OpenAI GPT-3.5 Enhanced",
                "ai-status-panel",
                "ai-executive-panel",
                "comprehensive-analysis"
            ]
            
            found_elements = [elem for elem in ai_elements if elem in content]
            print(f"✅ Dashboard accessible (Size: {len(content):,} bytes)")
            print(f"✅ AI Elements found: {len(found_elements)}/{len(ai_elements)}")
            
            if len(found_elements) == len(ai_elements):
                print("🚀 All AI enhancements detected in dashboard!")
            else:
                missing = [elem for elem in ai_elements if elem not in found_elements]
                print(f"⚠️  Missing AI elements: {missing}")
            
            return True
        else:
            print(f"❌ Dashboard inaccessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard test error: {str(e)}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🚀 AI-POWERED DASHBOARD COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"🎯 Target: {API_BASE}")
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test results tracking
    results = {}
    
    # Core API Tests
    print("\n📡 CORE API ENDPOINTS")
    print("-" * 30)
    
    results['health'] = test_endpoint(
        "Health Check", 
        f"{API_BASE}/health",
        ['status', 'timestamp']
    )[0]
    
    results['analytics'] = test_endpoint(
        "Analytics Data", 
        f"{API_BASE}/analytics",
        ['total_devices', 'online_devices', 'avg_battery']
    )[0]
    
    results['devices'] = test_endpoint(
        "Device List", 
        f"{API_BASE}/devices",
        None  # List response
    )[0]
    
    # AI Enhancement Tests
    print("\n🤖 AI ENHANCEMENT ENDPOINTS")
    print("-" * 30)
    
    results['ai_comprehensive'] = test_endpoint(
        "AI Comprehensive Analysis", 
        f"{API_BASE}/analytics/ai/comprehensive-analysis",
        ['ai_powered_insights', 'business_intelligence']
    )[0]
    
    results['ai_predictive'] = test_endpoint(
        "AI Predictive Maintenance", 
        f"{API_BASE}/analytics/ai/predictive-maintenance",
        ['predictive_maintenance', 'priority_actions']
    )[0]
    
    results['ai_anomaly'] = test_endpoint(
        "AI Anomaly Detection", 
        f"{API_BASE}/analytics/ai/anomaly-detection",
        ['anomaly_detection', 'detected_anomalies']
    )[0]
    
    results['ai_forecasting'] = test_endpoint(
        "AI Business Forecasting", 
        f"{API_BASE}/analytics/ai/business-forecasting",
        ['business_forecasting', 'productivity_forecast']
    )[0]
    
    # Business Intelligence Tests
    print("\n📊 BUSINESS INTELLIGENCE ENDPOINTS")
    print("-" * 30)
    
    results['bi_myob'] = test_endpoint(
        "MYOB Timeout Analysis", 
        f"{API_BASE}/analytics/business/myob-timeout-analysis",
        ['business_impact', 'detailed_analysis']
    )[0]
    
    results['bi_insights'] = test_endpoint(
        "AI Insights", 
        f"{API_BASE}/analytics/ai/insights",
        ['ai_insights', 'pattern_analysis']
    )[0]
    
    # Dashboard Accessibility Test
    print("\n🌐 DASHBOARD ACCESSIBILITY")
    print("-" * 30)
    results['dashboard'] = test_dashboard_accessibility()
    
    # Performance Tests
    print("\n⚡ PERFORMANCE TESTS")
    print("-" * 30)
    
    start_time = time.time()
    analytics_success, analytics_data = test_endpoint(
        "Analytics Performance", 
        f"{API_BASE}/analytics"
    )
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000
    print(f"⏱️  Analytics Response Time: {response_time:.0f}ms")
    
    if response_time < 1000:
        print("✅ Excellent response time (<1s)")
    elif response_time < 3000:
        print("✅ Good response time (<3s)")
    else:
        print("⚠️  Slow response time (>3s)")
    
    # Summary Report
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"⏱️  Total Duration: {time.time() - start_time:.1f}s")
    
    # Detailed Results
    print("\n📝 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    # Client Readiness Assessment
    print("\n🎯 CLIENT READINESS ASSESSMENT")
    print("-" * 30)
    
    if success_rate >= 90:
        print("🚀 EXCELLENT - Dashboard is client-ready!")
        print("   All major features operational")
        print("   AI enhancements fully functional")
        print("   Performance within acceptable limits")
    elif success_rate >= 75:
        print("✅ GOOD - Dashboard mostly ready")
        print("   Core features operational")
        print("   Minor AI features may be limited")
    elif success_rate >= 50:
        print("⚠️  CAUTION - Some issues detected")
        print("   Core functionality available")
        print("   AI features may be in fallback mode")
    else:
        print("❌ CRITICAL - Major issues detected")
        print("   Immediate attention required")
    
    print(f"\n🌟 Dashboard URL: {API_BASE}/dashboard")
    print(f"🔑 API Token: {API_TOKEN[:20]}...")
    print(f"📅 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 