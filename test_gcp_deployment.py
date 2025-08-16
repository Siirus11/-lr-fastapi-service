#!/usr/bin/env python3
"""
Test script for GCP Cloud Run deployment
"""

import requests
import json
import time
import sys
from typing import Dict, Any

def test_gcp_deployment(service_url: str) -> bool:
    """Test the GCP deployed API"""
    
    print(f"🚀 Testing GCP deployment at: {service_url}")
    print("=" * 60)
    
    # Remove trailing slash if present
    service_url = service_url.rstrip('/')
    
    tests = [
        ("Root endpoint", f"{service_url}/", "GET"),
        ("Health check", f"{service_url}/ping", "GET"),
        ("Model info", f"{service_url}/model-info", "GET"),
        ("Prediction", f"{service_url}/predict", "POST"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, url, method in tests:
        print(f"\n📋 Testing {test_name}...")
        print("-" * 40)
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                payload = {
                    "age": 30,
                    "salary": 60000,
                    "education_level": 2
                }
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=10
                )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test_name} passed!")
                print(f"   Response: {data}")
                passed += 1
            else:
                print(f"❌ {test_name} failed!")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test_name} error: {e}")
        except Exception as e:
            print(f"❌ {test_name} unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your GCP deployment is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def main():
    """Main function"""
    
    # Check if service URL is provided
    if len(sys.argv) != 2:
        print("Usage: python test_gcp_deployment.py <service_url>")
        print("Example: python test_gcp_deployment.py https://lr-fastapi-service-abc123-uc.a.run.app")
        sys.exit(1)
    
    service_url = sys.argv[1]
    
    # Test the deployment
    success = test_gcp_deployment(service_url)
    
    if success:
        print(f"\n🌐 Your API is live at: {service_url}")
        print(f"📖 API Documentation: {service_url}/docs")
        print(f"🏥 Health Check: {service_url}/ping")
        print("\n🎯 Try making a prediction:")
        print(f"curl -X POST '{service_url}/predict' \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"age\": 30, \"salary\": 60000, \"education_level\": 2}'")
    else:
        print("\n❌ Deployment test failed. Please check your deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
