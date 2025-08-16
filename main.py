import os
import logging
from typing import Dict, Any, Optional
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from contextlib import asynccontextmanager
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variable
model = None

def load_model(model_path: str) -> Optional[object]:
    """Load the trained model from file"""
    try:
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except FileNotFoundError:
        logger.error(f"Model file not found: {model_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI"""
    # Startup
    global model
    model_path = os.getenv("MODEL_PATH", "model.joblib")
    model = load_model(model_path)
    if model is None:
        logger.warning("Model not loaded. Service will return errors for prediction requests.")
    yield
    # Shutdown
    logger.info("Shutting down FastAPI service")

# Initialize FastAPI app
app = FastAPI(
    title="Logistic Regression API",
    description="Production-ready FastAPI service for Logistic Regression predictions",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for input validation
class PredictionInput(BaseModel):
    """Input model for prediction requests"""
    age: float = Field(..., ge=0, le=120, description="Age of the person")
    salary: float = Field(..., ge=0, description="Annual salary")
    education_level: int = Field(..., ge=0, le=10, description="Education level (0-10)")
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError('Age must be between 0 and 120')
        return v
    
    @field_validator('salary')
    @classmethod
    def validate_salary(cls, v):
        if v < 0:
            raise ValueError('Salary must be positive')
        return v
    
    @field_validator('education_level')
    @classmethod
    def validate_education_level(cls, v):
        if v < 0 or v > 10:
            raise ValueError('Education level must be between 0 and 10')
        return v

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: int
    probability: float
    features: Dict[str, float]

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    model_loaded: bool
    model_path: str

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "Logistic Regression API is running"}

@app.get("/ping", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    model_path = os.getenv("MODEL_PATH", "model.joblib")
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_path=model_path
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: PredictionInput):
    """Make predictions using the loaded model"""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please check the MODEL_PATH environment variable."
        )
    
    try:
        # Convert input to numpy array with all three features
        features = np.array([[input_data.age, input_data.salary, input_data.education_level]])
        
        # Make prediction
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])  # Probability of positive class
        
        logger.info(f"Prediction made: {prediction}, Probability: {probability:.4f}")
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            features={
                "age": input_data.age, 
                "salary": input_data.salary,
                "education_level": input_data.education_level
            }
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/model-info")
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        model_info = {
            "model_type": type(model).__name__,
            "classes": model.classes_.tolist() if hasattr(model, 'classes_') else None,
            "n_features": model.n_features_in_ if hasattr(model, 'n_features_in_') else None,
            "model_path": os.getenv("MODEL_PATH", "model.joblib")
        }
        return model_info
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model information"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
