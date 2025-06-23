#!/data/data/com.termux/files/usr/bin/python
"""
Termux:API Test Script for JD Engineering Tablet Monitoring
Tests all required Termux:API functions before deploying full monitoring
"""

import json
import subprocess
import time
from datetime import datetime

def test_termux_command(command, description):
    """Test a Termux API command and return results"""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {' '.join(command) if isinstance(command, list) else command}")
    
    try:
        if isinstance(command, str):
            command = command.split()
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    print(f"✅ SUCCESS: {json.dumps(data, indent=2)}")
                    return True, data
                except json.JSONDecodeError:
                    print(f"✅ SUCCESS (raw): {result.stdout.strip()}")
                    return True, {"raw_output": result.stdout.strip()}
            else:
                print("✅ SUCCESS: Command executed (no output)")
                return True, None
        else:
            print(f"❌ FAILED: Return code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print("❌ FAILED: Command timeout")
        return False, None
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None

def main():
    print("🚀 JD Engineering Termux:API Test Suite")
    print("=" * 50)
    
    tests = [
        # Battery monitoring
        (['termux-battery-status'], "Battery Status"),
        
        # WiFi and networking
        (['termux-wifi-connectioninfo'], "WiFi Connection Info"),
        (['termux-wifi-scaninfo'], "WiFi Scan Info"),
        
        # Sensors for user interaction detection
        (['termux-sensor', '-s', 'accelerometer', '-n', '1'], "Accelerometer Sensor"),
        (['termux-sensor', '-l'], "List Available Sensors"),
        
        # Notifications and system events
        (['termux-notification-list'], "Notification List"),
        
        # System info
        (['termux-telephony-deviceinfo'], "Device Info"),
        
        # Camera for barcode scanning capability
        (['termux-camera-info'], "Camera Info"),
        
        # Audio for scanner beep detection
        (['termux-microphone-record', '-h'], "Microphone Help (for audio monitoring)"),
        
        # Clipboard for app interaction monitoring
        (['termux-clipboard-get'], "Clipboard Content"),
        
        # Toast notifications for testing
        (['termux-toast', 'Termux API Test'], "Toast Notification"),
        
        # Volume control
        (['termux-volume'], "Volume Status"),
        
        # Torch test (screen state detection)
        (['termux-torch', 'on'], "Torch On"),
        (['termux-torch', 'off'], "Torch Off"),
    ]
    
    results = []
    
    for command, description in tests:
        success, data = test_termux_command(command, description)
        results.append((description, success, data))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for description, success, data in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All Termux:API functions working! Ready for advanced monitoring.")
    else:
        print(f"\n⚠️ {failed} functions failed. Check Termux:API installation.")
        print("Run: pkg install termux-api")
        print("And install Termux:API app from F-Droid or Google Play")
    
    # Test process monitoring
    print("\n🔍 Testing Process Monitoring...")
    try:
        ps_result = subprocess.run(['ps', '-A'], capture_output=True, text=True, timeout=10)
        if ps_result.returncode == 0:
            processes = ps_result.stdout.strip().split('\n')
            print(f"✅ Process monitoring working: {len(processes)} processes found")
            
            # Look for common Android processes
            android_processes = [p for p in processes if any(x in p.lower() for x in ['android', 'system', 'com.'])]
            print(f"Android processes detected: {len(android_processes)}")
            
        else:
            print("❌ Process monitoring failed")
    except Exception as e:
        print(f"❌ Process monitoring error: {e}")
    
    # Test network connectivity
    print("\n🌐 Testing Network Connectivity...")
    try:
        ping_result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                   capture_output=True, timeout=5)
        if ping_result.returncode == 0:
            print("✅ Network connectivity working")
        else:
            print("❌ Network connectivity failed")
    except Exception as e:
        print(f"❌ Network test error: {e}")

if __name__ == "__main__":
    main() 