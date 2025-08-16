#!/bin/bash

# GCP Deployment Script for Logistic Regression FastAPI Service
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"  # Replace with your actual project ID
REGION="us-central1"
SERVICE_NAME="lr-fastapi-service"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Starting GCP deployment..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run 'gcloud auth login' first."
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Build and push the Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "📤 Pushing image to Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --set-env-vars MODEL_PATH=model.joblib

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📖 API Documentation: $SERVICE_URL/docs"
echo "🏥 Health Check: $SERVICE_URL/ping"

# Test the deployment
echo "🧪 Testing the deployment..."
sleep 10

# Test health endpoint
if curl -f "$SERVICE_URL/ping" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
fi

echo "🎉 Your Logistic Regression API is now live on GCP Cloud Run!"
