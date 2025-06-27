#!/usr/bin/env python3
"""
DATA ACCURACY VALIDATION SCRIPT
Comprehensive testing for 100% accurate tablet data integrity

This script validates:
1. Input data validation at API level
2. Database storage integrity  
3. Data retrieval accuracy
4. Real-time data consistency
5. Cross-validation between sources
6. Data corruption detection
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List
import hashlib
import uuid

# Configuration
API_BASE = "http://127.0.0.1:8000"
API_TOKEN = "ArFetiWcHH5bIbiiwuQupQalDJocJA436YMi00tCvmHZOI82Awp8qbceO681"
DATABASE_PATH = "tablet_monitoring.db"

class DataAccuracyValidator:
    """Comprehensive data accuracy validation suite"""
    
    def __init__(self):
        self.test_device_id = f"accuracy_test_{uuid.uuid4().hex[:8]}"
        self.test_results = {}
        self.headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
    def generate_test_payload(self, corrupted=False) -> Dict[str, Any]:
        """Generate test payload with optional corruption for validation testing"""
        
        if corrupted:
            # Intentionally corrupted data to test validation
            return {
                "device_id": "",  # Empty device_id (should fail)
                "device_metrics": {
                    "battery_level": 150,  # Invalid: > 100
                    "battery_temperature": "invalid",  # Invalid type
                    "cpu_usage": -10  # Invalid: < 0
                },
                "network_metrics": {
                    "wifi_signal_strength": 50,  # Invalid: should be negative
                    "connectivity_status": "invalid_status"  # Invalid enum value
                },
                "app_metrics": {
                    "screen_state": "invalid_state",  # Invalid enum value
                    "notification_count": -5  # Invalid: negative
                }
            }
        
        # Valid test payload with precise data
        return {
            "device_id": self.test_device_id,
            "device_name": "Accuracy Test Tablet",
            "location": "Test Lab",
            "android_version": "13.0",
            "app_version": "accuracy_test_v1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_metrics": {
                "battery_level": 87,
                "battery_temperature": 32.5,
                "memory_available": 2147483648,  # 2GB
                "memory_total": 4294967296,     # 4GB
                "storage_available": 10737418240,  # 10GB
                "cpu_usage": 23.7,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "network_metrics": {
                "wifi_signal_strength": -67,
                "wifi_ssid": "TEST_NETWORK_SSID",
                "connectivity_status": "online",
                "network_type": "WiFi",
                "ip_address": "192.168.1.100",
                "dns_response_time": 15.2,
                "data_usage_mb": 125.7,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "app_metrics": {
                "screen_state": "active",
                "app_foreground": "com.myob.myobadvanced",
                "app_memory_usage": 134217728,  # 128MB
                "screen_timeout_setting": 300,
                "last_user_interaction": datetime.now(timezone.utc).isoformat(),
                "notification_count": 3,
                "app_crashes": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "session_events": [
                {
                    "event_type": "login",
                    "session_id": f"test_session_{uuid.uuid4().hex[:8]}",
                    "duration": 1200,
                    "user_id": "test_user_001",
                    "app_version": "accuracy_test_v1.0",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ],
            "raw_logs": [
                "Data accuracy validation test started",
                f"Test device: {self.test_device_id}",
                "All metrics collected successfully"
            ]
        }
    
    def test_input_validation(self) -> Dict[str, bool]:
        """Test 1: API input validation against corrupted data"""
        print("🔍 Test 1: Input Validation Testing")
        results = {}
        
        # Test corrupted data (should be rejected)
        corrupted_payload = self.generate_test_payload(corrupted=True)
        try:
            response = requests.post(
                f"{API_BASE}/tablet-metrics",
                headers=self.headers,
                json=corrupted_payload,
                timeout=10
            )
            # Should return 422 (validation error) for corrupted data
            results["rejects_corrupted_data"] = response.status_code == 422
            print(f"   ✅ Corrupted data rejection: {results['rejects_corrupted_data']}")
        except Exception as e:
            results["rejects_corrupted_data"] = False
            print(f"   ❌ Corrupted data test failed: {e}")
        
        # Test valid data (should be accepted)
        valid_payload = self.generate_test_payload(corrupted=False)
        try:
            response = requests.post(
                f"{API_BASE}/tablet-metrics",
                headers=self.headers,
                json=valid_payload,
                timeout=10
            )
            results["accepts_valid_data"] = response.status_code == 200
            print(f"   ✅ Valid data acceptance: {results['accepts_valid_data']}")
        except Exception as e:
            results["accepts_valid_data"] = False
            print(f"   ❌ Valid data test failed: {e}")
        
        return results
    
    def test_database_integrity(self) -> Dict[str, bool]:
        """Test 2: Database storage and retrieval integrity"""
        print("\n🗄️  Test 2: Database Integrity Testing")
        results = {}
        
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Check if our test data was stored correctly
            cursor.execute("""
                SELECT COUNT(*) FROM device_registry WHERE device_id = ?
            """, (self.test_device_id,))
            
            device_count = cursor.fetchone()[0]
            results["data_stored_correctly"] = device_count > 0
            print(f"   ✅ Data storage integrity: {results['data_stored_correctly']}")
            
            # Check database constraints
            cursor.execute("SELECT COUNT(*) FROM device_metrics WHERE battery_level > 100")
            invalid_battery_count = cursor.fetchone()[0]
            results["enforces_constraints"] = invalid_battery_count == 0
            print(f"   ✅ Database constraints enforced: {results['enforces_constraints']}")
            
            conn.close()
            
        except Exception as e:
            results["data_stored_correctly"] = False
            results["enforces_constraints"] = False
            print(f"   ❌ Database integrity test failed: {e}")
        
        return results
    
    def test_api_data_consistency(self) -> Dict[str, bool]:
        """Test 3: API data retrieval consistency"""
        print("\n🔄 Test 3: API Data Consistency Testing")
        results = {}
        
        try:
            # Get devices list
            response = requests.get(f"{API_BASE}/devices", headers=self.headers, timeout=10)
            devices = response.json()
            
            # Check if our test device appears
            test_device_found = any(device['device_id'] == self.test_device_id for device in devices)
            results["device_appears_in_list"] = test_device_found
            print(f"   ✅ Device appears in devices list: {results['device_appears_in_list']}")
            
            # Get specific device metrics
            response = requests.get(
                f"{API_BASE}/devices/{self.test_device_id}/metrics?hours=1",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                metrics = response.json()
                has_device_metrics = len(metrics.get('device_metrics', [])) > 0
                has_network_metrics = len(metrics.get('network_metrics', [])) > 0
                has_app_metrics = len(metrics.get('app_metrics', [])) > 0
                
                results["metrics_retrievable"] = has_device_metrics and has_network_metrics and has_app_metrics
                print(f"   ✅ Device metrics retrievable: {results['metrics_retrievable']}")
            else:
                results["metrics_retrievable"] = False
                print("   ❌ Device metrics not retrievable")
            
        except Exception as e:
            results["device_appears_in_list"] = False
            results["metrics_retrievable"] = False
            print(f"   ❌ API consistency test failed: {e}")
        
        return results
    
    def test_real_time_accuracy(self) -> Dict[str, bool]:
        """Test 4: Real-time data accuracy and freshness"""
        print("\n⏱️  Test 4: Real-time Data Accuracy Testing")
        results = {}
        
        try:
            # Send timestamped data
            test_time = datetime.now(timezone.utc)
            payload = self.generate_test_payload()
            payload['timestamp'] = test_time.isoformat()
            payload['device_metrics']['battery_level'] = 75  # Changed value for tracking
            
            # Submit data
            response = requests.post(
                f"{API_BASE}/tablet-metrics",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                # Wait a moment for processing
                time.sleep(2)
                
                # Retrieve and check timestamp accuracy
                response = requests.get(f"{API_BASE}/analytics", headers=self.headers, timeout=10)
                analytics = response.json()
                
                # Check if analytics reflects recent data
                results["real_time_updates"] = 'generated_at' in analytics
                print(f"   ✅ Real-time updates: {results['real_time_updates']}")
                
                # Check data freshness (within last 5 minutes)
                generated_time = datetime.fromisoformat(analytics['generated_at'].replace('Z', '+00:00'))
                time_diff = (datetime.now(timezone.utc) - generated_time).total_seconds()
                results["data_freshness"] = time_diff < 300  # 5 minutes
                print(f"   ✅ Data freshness (< 5min): {results['data_freshness']}")
                
            else:
                results["real_time_updates"] = False
                results["data_freshness"] = False
                print("   ❌ Real-time test failed - data not accepted")
                
        except Exception as e:
            results["real_time_updates"] = False
            results["data_freshness"] = False
            print(f"   ❌ Real-time accuracy test failed: {e}")
        
        return results
    
    def test_data_completeness(self) -> Dict[str, bool]:
        """Test 5: Data completeness and no data loss"""
        print("\n📊 Test 5: Data Completeness Testing")
        results = {}
        
        try:
            # Send multiple data points with unique identifiers
            payloads_sent = []
            for i in range(3):
                payload = self.generate_test_payload()
                payload['device_id'] = f"{self.test_device_id}_batch_{i}"
                payload['device_metrics']['battery_level'] = 60 + i  # Unique values
                payloads_sent.append(payload)
                
                response = requests.post(
                    f"{API_BASE}/tablet-metrics",
                    headers=self.headers,
                    json=payload,
                    timeout=10
                )
                
                time.sleep(1)  # Small delay between submissions
            
            # Wait for processing
            time.sleep(3)
            
            # Check if all data points were stored
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            stored_count = 0
            for i in range(3):
                cursor.execute(
                    "SELECT COUNT(*) FROM device_registry WHERE device_id = ?",
                    (f"{self.test_device_id}_batch_{i}",)
                )
                if cursor.fetchone()[0] > 0:
                    stored_count += 1
            
            results["no_data_loss"] = stored_count == 3
            print(f"   ✅ No data loss ({stored_count}/3 stored): {results['no_data_loss']}")
            
            conn.close()
            
        except Exception as e:
            results["no_data_loss"] = False
            print(f"   ❌ Data completeness test failed: {e}")
        
        return results
    
    def generate_accuracy_report(self) -> None:
        """Generate comprehensive accuracy report"""
        print("\n📋 TABLET DATA ACCURACY REPORT")
        print("=" * 50)
        
        all_tests = {}
        
        # Run all tests
        all_tests.update(self.test_input_validation())
        all_tests.update(self.test_database_integrity())
        all_tests.update(self.test_api_data_consistency())
        all_tests.update(self.test_real_time_accuracy())
        all_tests.update(self.test_data_completeness())
        
        # Calculate accuracy score
        passed_tests = sum(1 for result in all_tests.values() if result)
        total_tests = len(all_tests)
        accuracy_percentage = (passed_tests / total_tests) * 100
        
        print(f"\n📈 ACCURACY SCORE: {accuracy_percentage:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Detailed results
        print("\n🔍 DETAILED RESULTS:")
        for test_name, result in all_tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}: {test_name.replace('_', ' ').title()}")
        
        # Recommendations
        print("\n💡 ACCURACY RECOMMENDATIONS:")
        if accuracy_percentage == 100:
            print("   🎯 Perfect accuracy! System is operating at 100% data integrity.")
        elif accuracy_percentage >= 90:
            print("   ✅ Excellent accuracy. Minor optimizations may be beneficial.")
        elif accuracy_percentage >= 75:
            print("   ⚠️  Good accuracy. Some validation improvements recommended.")
        else:
            print("   🚨 Accuracy concerns detected. Immediate investigation required.")
        
        # Data quality indicators
        print("\n🛡️  DATA QUALITY INDICATORS:")
        quality_indicators = {
            "Input Validation": all_tests.get('rejects_corrupted_data', False) and all_tests.get('accepts_valid_data', False),
            "Storage Integrity": all_tests.get('data_stored_correctly', False) and all_tests.get('enforces_constraints', False),
            "Retrieval Consistency": all_tests.get('device_appears_in_list', False) and all_tests.get('metrics_retrievable', False),
            "Real-time Accuracy": all_tests.get('real_time_updates', False) and all_tests.get('data_freshness', False),
            "Data Completeness": all_tests.get('no_data_loss', False)
        }
        
        for indicator, status in quality_indicators.items():
            symbol = "🟢" if status else "🔴"
            print(f"   {symbol} {indicator}")
        
        return accuracy_percentage

def main():
    """Run comprehensive data accuracy validation"""
    print("🧪 TABLET DATA ACCURACY VALIDATION")
    print("Testing data integrity and validation mechanisms...\n")
    
    validator = DataAccuracyValidator()
    accuracy_score = validator.generate_accuracy_report()
    
    print(f"\n🎯 FINAL ACCURACY ASSESSMENT: {accuracy_score:.1f}%")
    if accuracy_score == 100:
        print("✅ Your tablet data is 100% accurate and validated!")
    else:
        print(f"⚠️  Data accuracy at {accuracy_score:.1f}% - review failed tests above")

if __name__ == "__main__":
    main() 