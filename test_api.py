#!/usr/bin/env python3
"""
Test script for Mortgage Default Prediction API
Uses real mortgage data structure
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data}")
            return True
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print("Testing model info...")
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model info: {data}")
            return True
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False

def test_prediction():
    """Test prediction with real mortgage structure"""
    print("Testing mortgage prediction...")
    
    # Sample mortgage application matching real CSV structure
    mortgage_data = {
        # Core loan details
        "CreditScore": 750,
        "OrigUPB": 250000,
        "OrigInterestRate": 3.75,
        "OrigLoanTerm": 360,
        "DTI": 28,
        "LTV": 80,
        "OCLTV": 80,
        "MIP": 0,
        
        # Property and borrower details
        "Units": 1,
        "NumBorrowers": 2,
        "PropertyState": "CA",
        "PropertyType": "SF",
        "PostalCode": "90210",
        "MSA": "31080",
        
        # Loan characteristics
        "FirstTimeHomebuyer": "N",
        "Occupancy": "O",
        "LoanPurpose": "P",
        "Channel": "R",
        "PPM": "N",
        "ProductType": "FRM",
        
        # Dates
        "FirstPaymentDate": 202301,
        "MaturityDate": 205212,
        
        # Originator/servicer
        "SellerName": "WELLS",
        "ServicerName": "WELLS",
        
        # Performance metrics (optional)
        "MonthsDelinquent": 0,
        "MonthsInRepayment": 12
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(mortgage_data)
        )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction')
            print(f"✅ Prediction: {prediction}")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

def test_high_risk_prediction():
    """Test high-risk mortgage prediction"""
    print("Testing high-risk mortgage...")
    
    # High-risk mortgage application
    high_risk_data = {
        # Core loan details (high risk profile)
        "CreditScore": 580,
        "OrigUPB": 400000,
        "OrigInterestRate": 6.5,
        "OrigLoanTerm": 360,
        "DTI": 48,
        "LTV": 95,
        "OCLTV": 95,
        "MIP": 30,
        
        # Property and borrower details
        "Units": 1,
        "NumBorrowers": 1,
        "PropertyState": "FL",
        "PropertyType": "CO",
        "PostalCode": "33101",
        "MSA": "33100",
        
        # Loan characteristics (higher risk)
        "FirstTimeHomebuyer": "Y",
        "Occupancy": "I",  # Investment property
        "LoanPurpose": "C", # Cash-out refi
        "Channel": "B",
        "PPM": "Y",
        "ProductType": "FRM",
        
        # Dates
        "FirstPaymentDate": 202206,
        "MaturityDate": 205205,
        
        # Originator/servicer
        "SellerName": "OTHER",
        "ServicerName": "OTHER",
        
        # Performance metrics (optional)
        "MonthsDelinquent": 2,
        "MonthsInRepayment": 18
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(high_risk_data)
        )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data.get('prediction')
            print(f"✅ High-risk prediction: {prediction}")
            return True
        else:
            print(f"❌ High-risk prediction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ High-risk prediction error: {e}")
        return False

def test_batch_prediction():
    """Test batch prediction"""
    print("Testing batch prediction...")
    
    # Multiple mortgage applications
    batch_data = [
        {
            "CreditScore": 750, "OrigUPB": 200000, "OrigInterestRate": 3.5,
            "OrigLoanTerm": 360, "DTI": 25, "LTV": 75, "OCLTV": 75, "MIP": 0,
            "Units": 1, "NumBorrowers": 2, "PropertyState": "CA", "PropertyType": "SF",
            "PostalCode": "90210", "MSA": "31080", "FirstTimeHomebuyer": "N",
            "Occupancy": "O", "LoanPurpose": "P", "Channel": "R", "PPM": "N",
            "ProductType": "FRM", "FirstPaymentDate": 202301, "MaturityDate": 205212,
            "SellerName": "WELLS", "ServicerName": "WELLS",
            "MonthsDelinquent": 0, "MonthsInRepayment": 12
        },
        {
            "CreditScore": 620, "OrigUPB": 350000, "OrigInterestRate": 5.0,
            "OrigLoanTerm": 360, "DTI": 42, "LTV": 90, "OCLTV": 90, "MIP": 25,
            "Units": 1, "NumBorrowers": 1, "PropertyState": "TX", "PropertyType": "SF",
            "PostalCode": "77001", "MSA": "26420", "FirstTimeHomebuyer": "Y",
            "Occupancy": "O", "LoanPurpose": "P", "Channel": "B", "PPM": "N",
            "ProductType": "FRM", "FirstPaymentDate": 202212, "MaturityDate": 205211,
            "SellerName": "QUICKEN", "ServicerName": "QUICKEN",
            "MonthsDelinquent": 0, "MonthsInRepayment": 8
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict-batch",
            headers={"Content-Type": "application/json"},
            data=json.dumps(batch_data)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch prediction: {len(data['results'])} results")
            for result in data['results']:
                if 'error' not in result:
                    print(f"   Loan {result['index']}: ${result['loan_amount']:,.0f}, Prediction: {result['prediction']}")
            return True
        else:
            print(f"❌ Batch prediction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch prediction error: {e}")
        return False

def test_validation():
    """Test input validation"""
    print("Testing validation...")
    
    # Invalid credit score (too high)
    invalid_data = {
        "CreditScore": 900,  # Invalid
        "OrigUPB": 250000, "OrigInterestRate": 3.75, "OrigLoanTerm": 360,
        "DTI": 28, "LTV": 80, "OCLTV": 80, "MIP": 0, "Units": 1,
        "NumBorrowers": 2, "PropertyState": "CA", "PropertyType": "SF",
        "PostalCode": "90210", "MSA": "31080", "FirstTimeHomebuyer": "N",
        "Occupancy": "O", "LoanPurpose": "P", "Channel": "R", "PPM": "N",
        "ProductType": "FRM", "FirstPaymentDate": 202301, "MaturityDate": 205212,
        "SellerName": "WELLS", "ServicerName": "WELLS",
        "MonthsDelinquent": 0, "MonthsInRepayment": 6
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        if response.status_code == 422:
            print("✅ Validation working correctly")
            return True
        else:
            print(f"❌ Validation failed: expected 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING MORTGAGE DEFAULT PREDICTION API")
    print("🏠 Using real mortgage data structure")
    print("=" * 50)
    
    # Wait for service
    print("Waiting for service...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Low-Risk Prediction", test_prediction),
        ("High-Risk Prediction", test_high_risk_prediction),
        ("Batch Prediction", test_batch_prediction),
        ("Input Validation", test_validation)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 25)
        if test_func():
            passed += 1
        print()
    
    # Results
    print("=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed!")
        print("\n🏠 Your mortgage API is working with real data structure!")
    else:
        print("⚠️ Some tests failed")
    
    print(f"\n📖 API Docs: {BASE_URL}/docs")
    print(f"🏥 Health Check: {BASE_URL}/health")

if __name__ == "__main__":
    main()