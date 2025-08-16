# Logistic Regression FastAPI Service

A production-ready FastAPI service for deploying scikit-learn Logistic Regression models with comprehensive input validation, error handling, and health monitoring.

## Features

- 🚀 **FastAPI** with automatic API documentation
- 🔒 **Input validation** using Pydantic models
- 🏥 **Health check** endpoint for monitoring
- 🐳 **Docker** support for easy deployment
- 🔧 **Environment variable** configuration
- 🛡️ **Error handling** and graceful degradation
- 🌐 **CORS** enabled for demo purposes
- 📊 **Prediction probabilities** included in responses

## Quick Start

### Prerequisites

- Python 3.8+
- Your trained Logistic Regression model saved as `model.joblib`

### Local Development Setup

1. **Clone and navigate to the service directory:**
   ```bash
   cd lr_fastapi_service
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Place your model file:**
   ```bash
   # Copy your trained model to the service directory
   cp /path/to/your/model.joblib .
   ```

5. **Run the service:**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/ping

### Testing the API

#### Health Check
```bash
curl http://localhost:8000/ping
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "model.joblib"
}
```

#### Make a Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"age": 30, "salary": 60000}'
```

Expected response:
```json
{
  "prediction": 1,
  "probability": 0.75,
  "features": {
    "age": 30.0,
    "salary": 60000.0
  }
}
```

#### Get Model Information
```bash
curl http://localhost:8000/model-info
```

## Docker Deployment

### Build the Docker Image

```bash
docker build -t lr-fastapi-service .
```

### Run with Docker

```bash
# Basic run
docker run -p 8000:8000 lr-fastapi-service

# With custom model path
docker run -p 8000:8000 \
  -e MODEL_PATH=/app/models/custom_model.joblib \
  -v /path/to/your/model:/app/models/custom_model.joblib \
  lr-fastapi-service
```

### Docker Compose (Optional)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  lr-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=model.joblib
    volumes:
      - ./model.joblib:/app/model.joblib:ro
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## API Endpoints

### `GET /`
- **Description**: Root endpoint
- **Response**: Service status message

### `GET /ping`
- **Description**: Health check endpoint
- **Response**: Service health status and model loading status

### `POST /predict`
- **Description**: Make predictions
- **Input**: JSON with `age` and `salary` fields
- **Response**: Prediction result with probability

### `GET /model-info`
- **Description**: Get information about the loaded model
- **Response**: Model type, classes, and feature count

## Configuration

### Environment Variables

- `MODEL_PATH`: Path to the model file (default: `model.joblib`)
- `PYTHONPATH`: Python path (default: `/app`)

### Input Validation

The API validates input data using Pydantic models:
- `age`: Must be between 0 and 120
- `salary`: Must be positive

## Production Deployment

### Using Gunicorn (Recommended for Production)

1. **Install gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Create a gunicorn configuration file `gunicorn.conf.py`:**
   ```python
   # Gunicorn configuration
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 50
   timeout = 30
   keepalive = 2
   preload_app = True
   ```

3. **Run with gunicorn:**
   ```bash
   gunicorn main:app -c gunicorn.conf.py
   ```

### Production Considerations

1. **Security:**
   - Disable CORS or configure specific origins
   - Use HTTPS in production
   - Implement authentication/authorization
   - Run container as non-root user (already configured in Dockerfile)

2. **Monitoring:**
   - Add logging to external systems (ELK stack, etc.)
   - Implement metrics collection (Prometheus, etc.)
   - Set up health checks and alerting

3. **Performance:**
   - Use multiple workers with gunicorn
   - Implement caching for model predictions
   - Consider model serving optimizations (ONNX, etc.)

4. **Model Management:**
   - Pin library versions to match training environment
   - Implement model versioning
   - Set up model retraining pipelines

### Example Production Dockerfile

```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY main.py .
COPY model.joblib .

ENV PATH=/root/.local/bin:$PATH
ENV MODEL_PATH=model.joblib

EXPOSE 8000
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Troubleshooting

### Common Issues

1. **Model not found:**
   - Ensure `model.joblib` is in the correct location
   - Check `MODEL_PATH` environment variable
   - Verify file permissions

2. **Import errors:**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify virtual environment activation

3. **Prediction errors:**
   - Ensure input features match training data
   - Check model file integrity
   - Verify scikit-learn version compatibility

### Logs

The service logs important events including:
- Model loading status
- Prediction requests and results
- Error details

Check logs for debugging:
```bash
# Docker logs
docker logs <container_id>

# Local logs
tail -f /var/log/your-app.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
