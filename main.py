#!/usr/bin/env python3
"""
Mortgage Default Prediction FastAPI Service
Clean API matching real LoanExport.csv structure
"""

import os
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variables
model = None
preprocessing_info = None

def load_model_and_info():
    """Load model and preprocessing info"""
    global model, preprocessing_info
    
    try:
        model_path = os.getenv("MODEL_PATH", "model.pkl")
        info_path = os.getenv("INFO_PATH", "preprocessing_info.pkl")
        
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        
        logger.info(f"Loading preprocessing info from {info_path}")
        preprocessing_info = joblib.load(info_path)
        
        logger.info("Model and preprocessing info loaded successfully")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler"""
    success = load_model_and_info()
    if not success:
        logger.warning("Model not loaded - service will return errors")
    else:
        logger.info("Mortgage prediction service ready")
    
    yield
    logger.info("Service shutting down")

# Initialize FastAPI
app = FastAPI(
    title="Mortgage Default Prediction API",
    description="API for mortgage default prediction using real loan data structure",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model matching your real CSV structure
class MortgageInput(BaseModel):
    """Mortgage application input matching LoanExport.csv structure"""
    
    # Core loan details
    CreditScore: int = Field(..., ge=300, le=850, description="Credit score")
    OrigUPB: float = Field(..., gt=0, description="Original loan amount")
    OrigInterestRate: float = Field(..., gt=0, le=20, description="Interest rate %")
    OrigLoanTerm: int = Field(..., ge=60, le=480, description="Loan term in months")
    DTI: int = Field(..., ge=0, le=100, description="Debt-to-income ratio %")
    LTV: int = Field(..., ge=1, le=150, description="Loan-to-value ratio %")
    OCLTV: int = Field(..., ge=1, le=150, description="Combined LTV %")
    MIP: int = Field(..., ge=0, le=100, description="Mortgage insurance premium %")
    
    # Property and borrower details
    Units: int = Field(1, ge=1, le=4, description="Number of units")
    NumBorrowers: int = Field(..., ge=1, le=8, description="Number of borrowers")
    PropertyState: str = Field(..., min_length=2, max_length=2, description="State code")
    PropertyType: str = Field(..., description="Property type (SF/PU/CO/MH)")
    PostalCode: str = Field(..., min_length=5, max_length=5, description="ZIP code")
    MSA: str = Field(..., description="Metropolitan area code")
    
    # Loan characteristics
    FirstTimeHomebuyer: str = Field(..., description="First-time buyer (Y/N/X)")
    Occupancy: str = Field(..., description="Occupancy type (O/S/I)")
    LoanPurpose: str = Field(..., description="Loan purpose (P/C/N/U)")
    Channel: str = Field(..., description="Origination channel (R/B/C/T)")
    PPM: str = Field(..., description="Prepayment penalty (Y/N/X)")
    ProductType: str = Field(..., description="Product type (FRM)")
    
    # Dates (YYYYMM format)
    FirstPaymentDate: int = Field(..., ge=199001, le=209912, description="First payment date")
    MaturityDate: int = Field(..., ge=199001, le=209912, description="Maturity date")
    
    # Originator/servicer (simplified)
    SellerName: str = Field(..., description="Loan seller/originator")
    ServicerName: str = Field(..., description="Loan servicer")
    
    # Performance metrics (optional - for historical data)
    MonthsDelinquent: Optional[int] = Field(0, ge=0, description="Months delinquent (optional)")
    MonthsInRepayment: Optional[int] = Field(0, ge=0, description="Months in repayment (optional)")

# Response model
class PredictionResponse(BaseModel):
    """Prediction response"""
    prediction: int = Field(..., description="Prediction (0=No Default, 1=Default)")

def preprocess_mortgage_data(data: MortgageInput) -> np.ndarray:
    """Preprocess mortgage data for prediction"""
    if preprocessing_info is None:
        raise ValueError("Preprocessing info not loaded")
    
    # Convert to DataFrame for easier processing
    data_dict = data.model_dump()
    df = pd.DataFrame([data_dict])
    
    # Apply the same preprocessing as training
    feature_encoders = preprocessing_info.get('feature_encoders', {})
    
    # Encode categorical features
    for col, encoder in feature_encoders.items():
        if col in df.columns:
            try:
                df[col] = encoder.transform(df[col].astype(str))
            except ValueError:
                # Handle unknown categories with default value
                df[col] = 0
    
    # Apply one-hot encoding for remaining categoricals
    categorical_cols = ['PropertyType', 'FirstTimeHomebuyer', 'Occupancy', 
                       'LoanPurpose', 'Channel', 'PPM', 'ProductType']
    
    for col in categorical_cols:
        if col in df.columns:
            df = pd.get_dummies(df, columns=[col], drop_first=True)
    
    # Ensure all expected features are present
    expected_features = preprocessing_info.get('feature_names', [])
    for feature in expected_features:
        if feature not in df.columns:
            df[feature] = 0
    
    # Select only expected features in correct order
    df = df[expected_features]
    
    return df.values



# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mortgage Default Prediction API",
        "description": "API matching real mortgage data structure",
        "features": 27,
        "endpoints": {
            "predict": "/predict",
            "batch": "/predict-batch",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessing_loaded": preprocessing_info is not None
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for healthchecks"""
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: MortgageInput):
    """Predict mortgage default"""
    if model is None or preprocessing_info is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model or preprocessing info not loaded"
        )
    
    try:
        # Preprocess input
        features = preprocess_mortgage_data(data)
        
        # Make prediction
        prediction = int(model.predict(features)[0])
        
        logger.info(f"Prediction: {prediction}")
        
        return PredictionResponse(
            prediction=prediction
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/predict-batch")
async def predict_batch(applications: List[MortgageInput]):
    """Batch predictions"""
    if model is None or preprocessing_info is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model or preprocessing info not loaded"
        )
    
    if len(applications) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 applications per batch"
        )
    
    results = []
    for i, app in enumerate(applications):
        try:
            features = preprocess_mortgage_data(app)
            prediction = int(model.predict(features)[0])
            
            results.append({
                "index": i,
                "loan_amount": app.OrigUPB,
                "prediction": prediction
            })
        except Exception as e:
            results.append({
                "index": i,
                "error": str(e)
            })
    
    return {"results": results}

@app.get("/model-info")
async def model_info():
    """Get model information"""
    if model is None or preprocessing_info is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return {
        "model_type": type(model).__name__,
        "features": len(preprocessing_info.get('feature_names', [])),
        "data_structure": "Real mortgage data (LoanExport.csv format)",
        "preprocessing": {
            "categorical_encoders": len(preprocessing_info.get('feature_encoders', {})),
            "feature_count": len(preprocessing_info.get('feature_names', []))
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
