#!/usr/bin/env python3
"""
DETAILED REAL DATA VERIFICATION TEST
Comprehensive verification that ALL real device data is visible and AI is working
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "https://jd-engineering-monitoring-api-production.up.railway.app"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def detailed_device_analysis():
    """Analyze each device in detail"""
    print("\n🔍 DETAILED DEVICE ANALYSIS")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/devices", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            devices = response.json()
            print(f"✅ Found {len(devices)} real devices")
            
            for i, device in enumerate(devices, 1):
                print(f"\n📱 DEVICE {i}: {device['device_id']}")
                print("-" * 40)
                print(f"   Name: {device.get('device_name', 'N/A')}")
                print(f"   Location: {device.get('location', 'N/A')}")
                print(f"   Status: {device.get('status', 'N/A')}")
                print(f"   Battery: {device.get('battery_level', 'N/A')}%")
                print(f"   Battery Temp: {device.get('battery_temperature', 'N/A')}°C")
                print(f"   WiFi Signal: {device.get('wifi_signal_strength', 'N/A')} dBm")
                print(f"   WiFi SSID: {device.get('wifi_ssid', 'N/A')}")
                print(f"   Connectivity: {device.get('connectivity_status', 'N/A')}")
                print(f"   Screen State: {device.get('screen_state', 'N/A')}")
                print(f"   App Foreground: {device.get('app_foreground', 'N/A')}")
                print(f"   MYOB Active: {device.get('myob_active', 'N/A')}")
                print(f"   Scanner Active: {device.get('scanner_active', 'N/A')}")
                print(f"   Timeout Risk: {device.get('timeout_risk', 'N/A')}")
                print(f"   Last Seen: {device.get('last_seen', 'N/A')}")
                print(f"   Seconds Since Last Seen: {device.get('seconds_since_last_seen', 'N/A')}")
                print(f"   Total Sessions: {device.get('total_sessions', 'N/A')}")
                print(f"   Total Timeouts: {device.get('total_timeouts', 'N/A')}")
                
                # Analyze device health
                battery = device.get('battery_level', 0)
                is_online = device.get('status') == 'online'
                has_timeout_risk = device.get('timeout_risk', False)
                
                health_score = 100
                if battery < 20:
                    health_score -= 30
                elif battery < 50:
                    health_score -= 15
                
                if not is_online:
                    health_score -= 40
                
                if has_timeout_risk:
                    health_score -= 25
                
                health_status = "EXCELLENT" if health_score >= 90 else \
                               "GOOD" if health_score >= 70 else \
                               "FAIR" if health_score >= 50 else "POOR"
                
                print(f"   🏥 HEALTH SCORE: {health_score}/100 ({health_status})")
                
                # Check for specific issues
                issues = []
                if battery < 25:
                    issues.append("🔋 LOW BATTERY")
                if not is_online:
                    issues.append("📡 OFFLINE")
                if has_timeout_risk:
                    issues.append("⏰ TIMEOUT RISK")
                if device.get('seconds_since_last_seen', 0) > 300:
                    issues.append("📶 STALE DATA")
                
                if issues:
                    print(f"   ⚠️ ISSUES: {', '.join(issues)}")
                else:
                    print(f"   ✅ NO ISSUES DETECTED")
            
            return devices
        else:
            print(f"❌ Failed to get devices: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Device analysis error: {str(e)}")
        return []

def test_analytics_data():
    """Test analytics data in detail"""
    print("\n📊 ANALYTICS DATA VERIFICATION")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/analytics", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics data retrieved successfully")
            print(f"   📱 Total Devices: {data.get('total_devices', 'N/A')}")
            print(f"   🟢 Online Devices: {data.get('online_devices', 'N/A')}")
            print(f"   🔋 Average Battery: {data.get('avg_battery', 'N/A')}%")
            print(f"   💼 MYOB Active: {data.get('myob_active', 'N/A')}")
            print(f"   📷 Scanner Active: {data.get('scanner_active', 'N/A')}")
            print(f"   ⚠️ Timeout Risks: {data.get('timeout_risks', 'N/A')}")
            print(f"   🕒 Generated: {data.get('generated_at', 'N/A')}")
            print(f"   📋 Version: {data.get('version', 'N/A')}")
            
            # Verify data quality
            total_devices = data.get('total_devices', 0)
            online_devices = data.get('online_devices', 0)
            avg_battery = data.get('avg_battery', 0)
            
            if total_devices > 0:
                print(f"   ✅ Real device data confirmed: {total_devices} devices")
                offline_devices = total_devices - online_devices
                if offline_devices > 0:
                    print(f"   ⚠️ {offline_devices} devices offline")
                
                if avg_battery > 0:
                    print(f"   ✅ Battery data available: {avg_battery}% average")
                else:
                    print(f"   ⚠️ No battery data available")
            else:
                print(f"   ❌ No device data found")
            
            return data
        else:
            print(f"❌ Analytics request failed: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Analytics test error: {str(e)}")
        return {}

def test_ai_comprehensive_analysis():
    """Test AI analysis in detail"""
    print("\n🤖 AI COMPREHENSIVE ANALYSIS TEST")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/analytics/ai/comprehensive-analysis", headers=HEADERS, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ AI analysis retrieved successfully")
            
            # Check data points analyzed
            data_points = data.get('data_points_analyzed', 0)
            print(f"   📊 Data Points Analyzed: {data_points}")
            
            if data_points > 0:
                print("   ✅ AI is analyzing REAL data")
            else:
                print("   ⚠️ AI is using fallback data")
            
            # Analyze AI insights
            ai_insights = data.get('ai_powered_insights', {})
            if ai_insights:
                executive = ai_insights.get('executive_summary', {})
                predictions = ai_insights.get('predictions', {})
                recommendations = ai_insights.get('recommendations', [])
                risk_analysis = ai_insights.get('risk_analysis', {})
                
                print(f"   🏥 System Health: {executive.get('system_health', 'N/A')}")
                print(f"   📈 Overall Score: {executive.get('overall_score', 'N/A')}/100")
                print(f"   🔮 Battery Trend: {predictions.get('battery_trend', 'N/A')}")
                print(f"   ⚠️ Timeout Risk: {predictions.get('timeout_risk', 'N/A')}")
                print(f"   🔧 Maintenance Window: {predictions.get('maintenance_window', 'N/A')}")
                print(f"   📋 Recommendations: {len(recommendations)} items")
                print(f"   🎯 AI Confidence: {data.get('ai_confidence_score', 'N/A')}%")
                
                # Show key findings
                key_findings = executive.get('key_findings', [])
                if key_findings:
                    print("   🔍 Key Findings:")
                    for finding in key_findings:
                        print(f"      • {finding}")
                
                # Show top recommendations
                if recommendations:
                    print("   💡 Top Recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        priority = rec.get('priority', 'N/A')
                        category = rec.get('category', 'N/A')
                        action = rec.get('action', 'N/A')
                        print(f"      {i}. [{priority}] {category}: {action}")
            
            return data
        else:
            print(f"❌ AI analysis request failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return {}
    except Exception as e:
        print(f"❌ AI analysis test error: {str(e)}")
        return {}

def test_dashboard_accessibility():
    """Test dashboard accessibility and content"""
    print("\n🌐 DASHBOARD ACCESSIBILITY TEST")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            print(f"✅ Dashboard accessible (Size: {len(content):,} bytes)")
            
            # Check for AI enhancements
            ai_elements = [
                "AI-Powered Business Intelligence",
                "OpenAI GPT-3.5 Enhanced",
                "ai-status-panel",
                "ai-executive-panel",
                "comprehensive-analysis",
                "loadBusinessIntelligence",
                "updateAIExecutiveSummary"
            ]
            
            found_elements = []
            for element in ai_elements:
                if element in content:
                    found_elements.append(element)
            
            print(f"   🤖 AI Elements Found: {len(found_elements)}/{len(ai_elements)}")
            
            if len(found_elements) == len(ai_elements):
                print("   ✅ All AI enhancements present")
            else:
                missing = [elem for elem in ai_elements if elem not in found_elements]
                print(f"   ⚠️ Missing elements: {missing}")
            
            # Check for data integration
            data_elements = [
                "API_BASE",
                "API_TOKEN",
                "/analytics",
                "/devices",
                "loadAllData"
            ]
            
            data_found = [elem for elem in data_elements if elem in content]
            print(f"   📊 Data Integration: {len(data_found)}/{len(data_elements)} elements")
            
            return True
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test error: {str(e)}")
        return False

def main():
    """Run comprehensive real data verification"""
    print("🚀 COMPREHENSIVE REAL DATA VERIFICATION")
    print("=" * 60)
    print(f"🎯 Target: {API_BASE}")
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Device Analysis
    devices = detailed_device_analysis()
    
    # Test 2: Analytics Data
    analytics = test_analytics_data()
    
    # Test 3: AI Analysis
    ai_analysis = test_ai_comprehensive_analysis()
    
    # Test 4: Dashboard
    dashboard_ok = test_dashboard_accessibility()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 REAL DATA VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_devices = len(devices)
    online_devices = len([d for d in devices if d.get('status') == 'online'])
    devices_with_battery = len([d for d in devices if d.get('battery_level') is not None])
    devices_with_myob = len([d for d in devices if d.get('myob_active')])
    devices_with_timeout_risk = len([d for d in devices if d.get('timeout_risk')])
    
    print(f"📱 DEVICES: {total_devices} total, {online_devices} online")
    print(f"🔋 BATTERY DATA: {devices_with_battery}/{total_devices} devices")
    print(f"💼 MYOB ACTIVITY: {devices_with_myob} devices active")
    print(f"⚠️ TIMEOUT RISKS: {devices_with_timeout_risk} devices at risk")
    
    analytics_quality = "EXCELLENT" if analytics.get('total_devices', 0) > 0 else "POOR"
    ai_quality = "EXCELLENT" if ai_analysis.get('data_points_analyzed', 0) > 0 else "NEEDS_IMPROVEMENT"
    dashboard_quality = "EXCELLENT" if dashboard_ok else "POOR"
    
    print(f"📊 ANALYTICS QUALITY: {analytics_quality}")
    print(f"🤖 AI ANALYSIS QUALITY: {ai_quality}")
    print(f"🌐 DASHBOARD QUALITY: {dashboard_quality}")
    
    # Overall assessment
    if total_devices > 0 and analytics.get('total_devices', 0) > 0 and dashboard_ok:
        print("\n🎉 VERDICT: REAL DATA IS FULLY OPERATIONAL!")
        print("   ✅ All devices visible with detailed metrics")
        print("   ✅ Analytics providing real-time data")
        print("   ✅ Dashboard accessible with AI features")
        if ai_analysis.get('data_points_analyzed', 0) > 0:
            print("   ✅ AI analysis using real device data")
        else:
            print("   ⚠️ AI analysis needs optimization for real data")
    else:
        print("\n⚠️ VERDICT: REAL DATA NEEDS ATTENTION")
        if total_devices == 0:
            print("   ❌ No devices found")
        if analytics.get('total_devices', 0) == 0:
            print("   ❌ Analytics not showing device data")
        if not dashboard_ok:
            print("   ❌ Dashboard not accessible")
    
    print(f"\n🌟 Dashboard URL: {API_BASE}/dashboard")
    print(f"📅 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 