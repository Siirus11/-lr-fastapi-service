# 🚀 GCP Cloud Run Deployment Guide

This guide will help you deploy your Logistic Regression FastAPI service to Google Cloud Platform using Cloud Run.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI (gcloud)** installed
3. **Docker** installed locally
4. **Your trained model** (`model.joblib`)

## 🔧 Setup Steps

### 1. Install Google Cloud CLI

**Windows:**
```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**macOS/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
```

### 3. Create a GCP Project (if you don't have one)

```bash
# List existing projects
gcloud projects list

# Create new project (optional)
gcloud projects create your-unique-project-id --name="Logistic Regression API"

# Set the project
gcloud config set project your-unique-project-id
```

### 4. Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build API (for CI/CD)
gcloud services enable cloudbuild.googleapis.com
```

## 🚀 Deployment Options

### Option 1: Quick Deployment (Manual)

1. **Update the deployment script:**
   ```bash
   # Edit deploy.sh and replace PROJECT_ID with your actual project ID
   PROJECT_ID="your-actual-project-id"
   ```

2. **Run the deployment:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Option 2: Step-by-Step Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t gcr.io/YOUR_PROJECT_ID/lr-fastapi-service .
   ```

2. **Push to Container Registry:**
   ```bash
   docker push gcr.io/YOUR_PROJECT_ID/lr-fastapi-service
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy lr-fastapi-service \
       --image gcr.io/YOUR_PROJECT_ID/lr-fastapi-service \
       --platform managed \
       --region us-central1 \
       --allow-unauthenticated \
       --memory 1Gi \
       --cpu 1 \
       --max-instances 10 \
       --port 8080
   ```

### Option 3: Automated CI/CD with Cloud Build

1. **Connect your repository to Cloud Build**
2. **Push your code to trigger automatic deployment**

## 🔍 Testing Your Deployment

### 1. Get Your Service URL

```bash
gcloud run services describe lr-fastapi-service --region=us-central1 --format="value(status.url)"
```

### 2. Test the API

```bash
# Health check
curl https://your-service-url/ping

# Make a prediction
curl -X POST "https://your-service-url/predict" \
     -H "Content-Type: application/json" \
     -d '{"age": 30, "salary": 60000, "education_level": 2}'
```

### 3. Access API Documentation

Open in your browser: `https://your-service-url/docs`

## 📊 Monitoring & Logging

### View Logs

```bash
# View real-time logs
gcloud logs tail --service=lr-fastapi-service

# View specific log entries
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lr-fastapi-service"
```

### Monitor Performance

1. Go to **Cloud Run** in GCP Console
2. Select your service
3. View metrics like:
   - Request count
   - Response time
   - Error rate
   - Memory usage

## 🔧 Configuration Options

### Environment Variables

```bash
gcloud run services update lr-fastapi-service \
    --set-env-vars MODEL_PATH=model.joblib,LOG_LEVEL=INFO
```

### Scaling Configuration

```bash
gcloud run services update lr-fastapi-service \
    --min-instances 1 \
    --max-instances 20 \
    --cpu 2 \
    --memory 2Gi
```

### Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service lr-fastapi-service \
    --domain your-domain.com \
    --region us-central1
```

## 💰 Cost Optimization

### Estimated Costs (Cloud Run)
- **Free tier**: 2 million requests/month
- **After free tier**: ~$0.40 per million requests
- **Memory**: ~$0.00002400 per GB-second
- **CPU**: ~$0.00002400 per vCPU-second

### Cost Optimization Tips
1. Set `--min-instances 0` for serverless scaling
2. Use appropriate memory/CPU limits
3. Monitor usage with Cloud Monitoring
4. Set up billing alerts

## 🔒 Security Best Practices

### 1. Authentication (Recommended for Production)

```bash
# Remove public access
gcloud run services update lr-fastapi-service \
    --no-allow-unauthenticated

# Add IAM authentication
gcloud run services add-iam-policy-binding lr-fastapi-service \
    --member="user:your-email@gmail.com" \
    --role="roles/run.invoker"
```

### 2. HTTPS Only

Cloud Run automatically provides HTTPS certificates.

### 3. Environment Variables

Store sensitive data in Secret Manager:

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create my-secret --data-file=-

# Use in Cloud Run
gcloud run services update lr-fastapi-service \
    --set-env-vars SECRET_VALUE=my-secret:latest
```

## 🚨 Troubleshooting

### Common Issues

1. **"Permission denied"**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **"Image not found"**
   ```bash
   # Rebuild and push
   docker build -t gcr.io/YOUR_PROJECT_ID/lr-fastapi-service .
   docker push gcr.io/YOUR_PROJECT_ID/lr-fastapi-service
   ```

3. **"Service unavailable"**
   ```bash
   # Check logs
   gcloud logs tail --service=lr-fastapi-service
   ```

4. **"Model not found"**
   - Ensure `model.joblib` is in the Docker image
   - Check `MODEL_PATH` environment variable

### Useful Commands

```bash
# List all services
gcloud run services list

# Delete service
gcloud run services delete lr-fastapi-service

# Update service
gcloud run services update lr-fastapi-service --image=NEW_IMAGE

# View service details
gcloud run services describe lr-fastapi-service
```

## 🎉 Success!

Once deployed, your API will be available at:
- **Service URL**: `https://your-service-url`
- **API Docs**: `https://your-service-url/docs`
- **Health Check**: `https://your-service-url/ping`

Your Logistic Regression model is now running in production on Google Cloud Platform! 🚀
