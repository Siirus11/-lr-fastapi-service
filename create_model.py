#!/usr/bin/env python3
"""
Create mortgage default prediction model
Trains on REAL LoanExport.csv data (291K+ mortgage records)
"""

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

def load_real_mortgage_data(csv_path="LoanExport.csv"):
    """Load real mortgage data from LoanExport.csv"""
    print(f"🏠 Loading REAL mortgage data from {csv_path}")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Load the actual mortgage data
    print("   Loading CSV file...")
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Clean column names (remove any spaces)
    df.columns = df.columns.str.strip()
    
    print(f"✅ REAL mortgage data loaded:")
    print(f"   Records: {len(df):,}")
    print(f"   Features: {len(df.columns) - 1}")
    
    # Check target variable
    if 'EverDelinquent' in df.columns:
        default_rate = df['EverDelinquent'].mean()
        print(f"   Default rate: {default_rate:.1%}")
        print(f"   Delinquent loans: {df['EverDelinquent'].sum():,}")
        print(f"   Non-delinquent loans: {(df['EverDelinquent'] == 0).sum():,}")
    else:
        raise ValueError("EverDelinquent column not found in CSV")
    
    # Show data sample
    print(f"\n📊 Sample data:")
    print(df.head(2))
    
    return df

def preprocess_data(df):
    """Preprocess mortgage data for training"""
    print("\n🔄 PREPROCESSING REAL MORTGAGE DATA")
    print("-" * 40)
    
    # Drop rows with missing target
    print(f"Before cleaning: {len(df):,} records")
    df = df.dropna(subset=['EverDelinquent'])
    print(f"After removing missing target: {len(df):,} records")
    
    # Separate features and target
    X = df.drop('EverDelinquent', axis=1)
    y = df['EverDelinquent']
    
    # Exclude unique identifiers that shouldn't be used for prediction
    exclude_cols = ['LoanSeqNum']  # Loan sequence number is just an ID
    exclude_cols_present = [col for col in exclude_cols if col in X.columns]
    if exclude_cols_present:
        X = X.drop(columns=exclude_cols_present)
        print(f"Excluded ID columns: {exclude_cols_present}")
    
    # Store preprocessing info
    preprocessing_info = {
        'feature_encoders': {},
        'feature_names': [],
        'categorical_columns': []
    }
    
    # Handle missing values in numeric columns first
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) > 0:
        print(f"Filling missing values in {len(numeric_cols)} numeric columns...")
        X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].median())
    
    # Encode high-cardinality categorical columns (following your Jupyter notebook approach)
    high_cardinality_cols = ['PostalCode', 'MSA', 'SellerName', 'ServicerName']
    
    for col in high_cardinality_cols:
        if col in X.columns:
            print(f"Label encoding: {col} ({X[col].nunique()} unique values)")
            le = LabelEncoder()
            # Handle missing values in categorical columns
            X[col] = X[col].fillna('Unknown')
            X[col] = le.fit_transform(X[col].astype(str))
            preprocessing_info['feature_encoders'][col] = le
    
    # Handle remaining categorical columns
    categorical_cols = ['PropertyState', 'PropertyType', 'FirstTimeHomebuyer', 
                       'Occupancy', 'LoanPurpose', 'Channel', 'PPM', 'ProductType']
    
    # Clean and encode remaining categorical columns
    for col in categorical_cols:
        if col in X.columns:
            # Clean string values (remove trailing spaces)
            X[col] = X[col].astype(str).str.strip()
            # Fill missing values
            X[col] = X[col].fillna('Unknown')
            preprocessing_info['categorical_columns'].append(col)
    
    # One-hot encode the cleaned categorical columns
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # Final cleanup: ensure all columns are numeric
    print(f"Final data type cleaning...")
    for col in X.columns:
        if X[col].dtype == 'object':
            print(f"  Converting {col} from object to numeric")
            # Try to convert to numeric, replace errors with 0
            X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)
    
    # Store final feature names
    preprocessing_info['feature_names'] = list(X.columns)
    
    print(f"  Original features: {len(df.columns) - 1}")
    print(f"  Final features: {len(X.columns)}")
    print(f"  Encoded columns: {len(preprocessing_info['feature_encoders'])}")
    
    return X, y, preprocessing_info

def train_model(X, y):
    """Train mortgage default prediction model"""
    print("\nTraining model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    
    # Evaluate
    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))
    
    print(f"  Training accuracy: {train_acc:.3f}")
    print(f"  Test accuracy: {test_acc:.3f}")
    
    if train_acc - test_acc > 0.05:
        print("  ⚠️ Possible overfitting")
    else:
        print("  ✅ Model generalizes well")
    
    return model

def save_model_and_info(model, preprocessing_info):
    """Save model and preprocessing information"""
    print("\nSaving model and preprocessing info...")
    
    # Save model
    model_path = "model.pkl"
    joblib.dump(model, model_path)
    print(f"  Model saved: {model_path}")
    
    # Save preprocessing info
    info_path = "preprocessing_info.pkl"
    joblib.dump(preprocessing_info, info_path)
    print(f"  Preprocessing info saved: {info_path}")
    
    return model_path, info_path

def test_predictions(model, preprocessing_info, sample_df):
    """Test model with sample predictions"""
    print("\nTesting sample predictions:")
    
    # Create test cases from sample data
    test_cases = sample_df.head(3)
    
    for i, (_, row) in enumerate(test_cases.iterrows()):
        try:
            # Convert to the format expected by the API preprocessing
            test_data = row.drop('EverDelinquent').to_dict()
            
            # Simulate the preprocessing (simplified)
            features = pd.DataFrame([test_data])
            
            # Apply encoders
            for col, encoder in preprocessing_info['feature_encoders'].items():
                if col in features.columns:
                    features[col] = encoder.transform(features[col].astype(str))
            
            # One-hot encode
            cat_cols = [col for col in preprocessing_info['categorical_columns'] if col in features.columns]
            features = pd.get_dummies(features, columns=cat_cols, drop_first=True)
            
            # Ensure all features are present
            for feature in preprocessing_info['feature_names']:
                if feature not in features.columns:
                    features[feature] = 0
            
            features = features[preprocessing_info['feature_names']]
            
            # Make prediction
            prediction = model.predict(features.values)[0]
            probability = model.predict_proba(features.values)[0][1]
            
            risk = "Low" if probability <= 0.3 else "Medium" if probability <= 0.7 else "High"
            
            print(f"  Test {i+1}: Credit={row['CreditScore']}, LTV={row['LTV']}")
            print(f"          → Prediction={prediction}, Probability={probability:.3f}, Risk={risk}")
            
        except Exception as e:
            print(f"  Test {i+1}: Error - {str(e)}")

def main():
    """Main function"""
    print("🏠 CREATING MORTGAGE DEFAULT PREDICTION MODEL")
    print("=" * 60)
    
    try:
        # Load REAL mortgage data from your CSV
        df = load_real_mortgage_data("LoanExport.csv")
        
        # Preprocess data
        X, y, preprocessing_info = preprocess_data(df)
        
        # Train model
        model = train_model(X, y)
        
        # Save model and preprocessing info
        model_path, info_path = save_model_and_info(model, preprocessing_info)
        
        # Test predictions
        test_predictions(model, preprocessing_info, df)
        
        print(f"\n" + "=" * 60)
        print(f"✅ REAL MORTGAGE MODEL CREATION COMPLETED!")
        print(f"📁 Files created:")
        print(f"   - {model_path}")
        print(f"   - {info_path}")
        print(f"🏠 TRAINED ON YOUR ACTUAL DATA:")
        print(f"   - Dataset: {len(df):,} real mortgage loans")
        print(f"   - Features: {len(preprocessing_info['feature_names'])}")
        print(f"   - Default rate: {df['EverDelinquent'].mean():.1%}")
        print(f"🚀 Ready for FastAPI service with REAL model!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()