#!/usr/bin/env python3
"""
Test script to verify Railway auto-deployment is working
Run this to test that deployments trigger automatically on git push
"""

import requests
import json
from datetime import datetime

def test_auto_deployment():
    """Test that the Railway deployment is working and responding"""
    try:
        url = "https://jd-engineering-monitoring-api-production.up.railway.app/health"
        
        print("🔄 Testing Railway auto-deployment...")
        print(f"📍 URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Deployment successful!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🗄️ Database: {data.get('database')}")
            print(f"🌍 Environment: {data.get('environment')}")
            print(f"⏰ Timestamp: {data.get('timestamp')}")
            print(f"🆔 Auto-deploy test: {datetime.now().isoformat()}")
            return True
        else:
            print(f"❌ Deployment failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing deployment: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_auto_deployment()
    exit(0 if success else 1) # Auto-deploy verification test: Sat Jun 28 08:21:32 NZST 2025
Auto-deploy test from corrected repository: Sat Jun 28 08:32:20 NZST 2025
Railway auto-deploy test Sat Jun 28 08:36:39 NZST 2025
