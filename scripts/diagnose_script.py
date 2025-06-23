#!/data/data/com.termux/files/usr/bin/python
"""
Diagnostic script to troubleshoot tablet_client.py issues
"""

import sys
import os
import inspect

def diagnose_script():
    print("🔍 JD Engineering Script Diagnostics")
    print("=" * 50)
    
    # Check if file exists
    script_path = "tablet_client.py"
    if not os.path.exists(script_path):
        print(f"❌ {script_path} not found in current directory")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files: {os.listdir('.')}")
        return False
    
    print(f"✅ {script_path} exists")
    
    # Check file size and basic content
    file_size = os.path.getsize(script_path)
    print(f"📄 File size: {file_size} bytes")
    
    # Read and analyze the file
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        print(f"📝 Total lines: {len(content.splitlines())}")
        
        # Check for class definition
        if "class AdvancedTabletMonitor:" in content:
            print("✅ AdvancedTabletMonitor class found")
        else:
            print("❌ AdvancedTabletMonitor class not found")
            return False
        
        # Check for key methods
        methods_to_check = [
            "__init__",
            "run_termux_command", 
            "get_comprehensive_battery_info",
            "get_advanced_wifi_info",
            "get_running_apps_and_processes",
            "detect_user_interaction",
            "generate_session_events",
            "collect_comprehensive_data",
            "send_data_to_api",
            "run_monitoring_loop",
            "stop"
        ]
        
        missing_methods = []
        for method in methods_to_check:
            if f"def {method}(" in content:
                print(f"✅ Method {method} found")
            else:
                print(f"❌ Method {method} missing")
                missing_methods.append(method)
        
        if missing_methods:
            print(f"\n❌ Missing methods: {missing_methods}")
            return False
        
        # Check for main execution block
        if 'if __name__ == "__main__":' in content:
            print("✅ Main execution block found")
        else:
            print("❌ Main execution block missing")
            return False
        
        # Try to import the module
        print("\n🧪 Testing import...")
        try:
            sys.path.insert(0, '.')
            import tablet_client
            print("✅ Module imports successfully")
            
            # Check if class can be instantiated
            monitor = tablet_client.AdvancedTabletMonitor()
            print("✅ Class instantiates successfully")
            
            # Check if methods exist
            for method in methods_to_check:
                if hasattr(monitor, method):
                    print(f"✅ Method {method} accessible")
                else:
                    print(f"❌ Method {method} not accessible")
                    return False
            
            print("\n🎉 All diagnostics passed! Script should work correctly.")
            return True
            
        except Exception as e:
            print(f"❌ Import/instantiation error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def check_python_environment():
    print("\n🐍 Python Environment Check")
    print("-" * 30)
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check required modules
    required_modules = ['json', 'requests', 'time', 'subprocess', 'os', 'datetime', 'threading', 'uuid']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            print(f"❌ {module} missing")

if __name__ == "__main__":
    check_python_environment()
    success = diagnose_script()
    
    if success:
        print("\n🚀 Ready to run: python tablet_client.py")
    else:
        print("\n🔧 Fix the issues above before running the script") 