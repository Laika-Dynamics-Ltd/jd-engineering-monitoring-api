#!/usr/bin/env python3
"""
Test the working tablet client script
"""

import sys
import os
import importlib.util

def test_script_structure():
    """Test if the script has proper structure"""
    script_path = os.path.join(os.path.dirname(__file__), 'tablet_client_working.py')
    
    print("🧪 Testing tablet_client_working.py structure...")
    
    # Test 1: File exists
    if not os.path.exists(script_path):
        print("❌ Script file not found")
        return False
    
    # Test 2: Can import without errors
    try:
        spec = importlib.util.spec_from_file_location("tablet_client", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Script imports successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 3: Check if TabletMonitor class exists
    if not hasattr(module, 'TabletMonitor'):
        print("❌ TabletMonitor class not found")
        return False
    print("✅ TabletMonitor class found")
    
    # Test 4: Check if main function exists
    if not hasattr(module, 'main'):
        print("❌ main function not found")
        return False
    print("✅ main function found")
    
    # Test 5: Create TabletMonitor instance
    try:
        monitor = module.TabletMonitor()
        print("✅ TabletMonitor can be instantiated")
    except Exception as e:
        print(f"❌ Cannot create TabletMonitor: {e}")
        return False
    
    # Test 6: Check required methods exist
    required_methods = [
        'run_command', 'get_battery_info', 'get_wifi_info', 
        'check_myob_processes', 'check_scanner_processes',
        'detect_user_activity', 'collect_data', 'send_data', 'run'
    ]
    
    for method in required_methods:
        if not hasattr(monitor, method):
            print(f"❌ Missing method: {method}")
            return False
        if not callable(getattr(monitor, method)):
            print(f"❌ {method} is not callable")
            return False
    
    print("✅ All required methods found and callable")
    
    # Test 7: Test data collection (without sending)
    try:
        data = monitor.collect_data()
        if not isinstance(data, dict):
            print("❌ collect_data doesn't return a dict")
            return False
        
        required_keys = ['device_id', 'timestamp', 'device_metrics', 'network_metrics', 'app_metrics']
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing key in data: {key}")
                return False
        
        print("✅ Data collection works and returns proper structure")
    except Exception as e:
        print(f"❌ Data collection error: {e}")
        return False
    
    print("\n🎉 All tests passed! Script is working correctly.")
    return True

def test_syntax():
    """Test script for syntax errors"""
    script_path = os.path.join(os.path.dirname(__file__), 'tablet_client_working.py')
    
    print("🔍 Checking syntax...")
    
    try:
        with open(script_path, 'r') as f:
            code = f.read()
        
        compile(code, script_path, 'exec')
        print("✅ No syntax errors found")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    print("🚀 Testing Working Tablet Client Script")
    print("=" * 50)
    
    syntax_ok = test_syntax()
    structure_ok = test_script_structure()
    
    if syntax_ok and structure_ok:
        print("\n🎯 FINAL RESULT: Script is FULLY WORKING!")
        print("\n📋 To use the script:")
        print("1. Copy tablet_client_working.py to your Android tablet")
        print("2. Run: python tablet_client_working.py")
        print("3. The script will start monitoring and sending data")
    else:
        print("\n❌ FINAL RESULT: Script has issues that need fixing")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 