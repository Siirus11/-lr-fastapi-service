#!/usr/bin/env python3
"""
Test script for the Logistic Regression FastAPI service
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check() -> bool:
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/ping")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint() -> bool:
    """Test the root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_model_info() -> bool:
    """Test the model info endpoint"""
    print("Testing model info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info: {data}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Model info error: {e}")
        return False

def test_prediction(age: float, salary: float) -> bool:
    """Test the prediction endpoint"""
    print(f"Testing prediction endpoint with age={age}, salary={salary}...")
    
    payload = {
        "age": age,
        "salary": salary
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful: {data}")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction error: {e}")
        return False

def test_invalid_input() -> bool:
    """Test input validation"""
    print("Testing input validation...")
    
    # Test negative age
    payload = {"age": -5, "salary": 50000}
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response.status_code == 422:
            print("✅ Negative age validation working")
        else:
            print(f"❌ Negative age validation failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Validation test error: {e}")
        return False
    
    # Test negative salary
    payload = {"age": 30, "salary": -1000}
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response.status_code == 422:
            print("✅ Negative salary validation working")
            return True
        else:
            print(f"❌ Negative salary validation failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Validation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print("=" * 50)
    
    # Wait a moment for the service to be ready
    time.sleep(2)
    
    tests = [
        ("Root endpoint", test_root_endpoint),
        ("Health check", test_health_check),
        ("Model info", test_model_info),
        ("Valid prediction", lambda: test_prediction(30, 60000)),
        ("Another prediction", lambda: test_prediction(45, 80000)),
        ("Input validation", test_invalid_input),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n📖 API Documentation available at:")
    print(f"   {BASE_URL}/docs")
    print(f"   {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
