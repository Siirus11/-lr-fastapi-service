#!/usr/bin/env python3
"""
Script to create a sample Logistic Regression model for testing the API
"""

import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import os

def create_sample_model():
    """Create a sample Logistic Regression model for testing"""
    
    # Generate sample training data
    np.random.seed(42)
    n_samples = 1000
    
    # Generate features: age (18-65) and salary (20000-150000)
    age = np.random.uniform(18, 65, n_samples)
    salary = np.random.uniform(20000, 150000, n_samples)
    
    # Create a simple rule for the target (for demonstration)
    # Higher age and salary increase the probability of positive class
    probability = (age - 18) / (65 - 18) * 0.4 + (salary - 20000) / (150000 - 20000) * 0.6
    target = (probability + np.random.normal(0, 0.1, n_samples)) > 0.5
    
    # Combine features
    X = np.column_stack([age, salary])
    y = target.astype(int)
    
    # Create and train the model
    print("Training sample Logistic Regression model...")
    model = LogisticRegression(random_state=42)
    model.fit(X, y)
    
    # Save the model
    model_path = "model.joblib"
    joblib.dump(model, model_path)
    
    print(f"✅ Sample model saved to {model_path}")
    print(f"Model accuracy on training data: {model.score(X, y):.3f}")
    print(f"Model coefficients: {model.coef_[0]}")
    print(f"Model intercept: {model.intercept_[0]}")
    
    # Test a few predictions
    test_cases = [
        (25, 40000),
        (35, 70000),
        (50, 120000)
    ]
    
    print("\nSample predictions:")
    for age, salary in test_cases:
        features = np.array([[age, salary]])
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]
        print(f"Age: {age}, Salary: {salary} → Prediction: {prediction}, Probability: {probability:.3f}")

if __name__ == "__main__":
    create_sample_model()
