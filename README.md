# Mortgage Default Prediction API

FastAPI service for predicting mortgage default risk using **real mortgage data structure**.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create model:**
   ```bash
   python create_model.py
   ```

3. **Run API:**
   ```bash
   python main.py
   ```

4. **Test API:**
   ```bash
   python test_api.py
   ```

## API Usage

### Single Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 750,
    "OrigUPB": 250000,
    "OrigInterestRate": 3.75,
    "OrigLoanTerm": 360,
    "DTI": 28,
    "LTV": 80,
    "OCLTV": 80,
    "MIP": 0,
    "Units": 1,
    "NumBorrowers": 2,
    "PropertyState": "CA",
    "PropertyType": "SF",
    "PostalCode": "90210",
    "MSA": "31080",
    "FirstTimeHomebuyer": "N",
    "Occupancy": "O",
    "LoanPurpose": "P",
    "Channel": "R",
    "PPM": "N",
    "ProductType": "FRM",
    "FirstPaymentDate": 202301,
    "MaturityDate": 205212,
    "SellerName": "WELLS",
    "ServicerName": "WELLS",
    "MonthsDelinquent": 0,
    "MonthsInRepayment": 12
  }'
```

### Response
```json
{
  "prediction": 0
}
```

## Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /predict` - Single prediction
- `POST /predict-batch` - Batch predictions  
- `GET /model-info` - Model information
- `GET /docs` - Interactive API documentation

## Features

- **27 mortgage features**: Complete mortgage data structure matching LoanExport.csv
- **Binary classification**: Simple 0/1 prediction output
- **Batch processing**: Up to 100 mortgages per request
- **Input validation**: Comprehensive mortgage field validation
- **Real data structure**: Matches actual mortgage industry standards

## Deployment

### Docker
```bash
docker build -t loan-api .
docker run -p 8000:8000 loan-api
```

### Railway (Free)
1. Push to GitHub
2. Connect to [Railway](https://railway.app/)
3. Deploy automatically

## Project Structure
```
loan-default-api/
├── main.py           # FastAPI application
├── create_model.py   # Model creation
├── test_api.py       # API tests
├── requirements.txt  # Dependencies
├── Dockerfile        # Container config
├── Procfile         # Railway deployment
└── README.md        # This file
```

## License
MIT License