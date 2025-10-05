# API Documentation - Streamlit BI Dashboard

Complete API reference for developers integrating with or extending the BI Dashboard.

## 📋 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Data API](#data-api)
- [Forecasting API](#forecasting-api)
- [Insights API](#insights-api)
- [Export API](#export-api)
- [Webhook Integration](#webhook-integration)
- [Python SDK](#python-sdk)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

### Base URL

```
# Development
http://localhost:8501/api

# Production
https://your-domain.com/api
```

### API Versions

- **Current Version**: v1
- **Supported Versions**: v1
- **Deprecated**: None

### Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Request successful",
  "timestamp": "2025-10-05T12:00:00Z",
  "version": "1.0.0"
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "date_column",
      "reason": "Column does not exist in dataset"
    }
  },
  "timestamp": "2025-10-05T12:00:00Z"
}
```

---

## Authentication

### API Key Authentication

Generate an API key from the dashboard settings.

**Header Format:**
```http
Authorization: Bearer YOUR_API_KEY
X-API-Key: YOUR_API_KEY
```

**Example:**
```python
import requests

headers = {
    'Authorization': 'Bearer sk-1234567890abcdef',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8501/api/v1/data', headers=headers)
```

### OAuth 2.0 (Enterprise)

For enterprise deployments:

```python
# Get access token
token_response = requests.post(
    'https://your-domain.com/oauth/token',
    data={
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'grant_type': 'client_credentials'
    }
)

access_token = token_response.json()['access_token']

# Use token
headers = {'Authorization': f'Bearer {access_token}'}
```

---

## Data API

### Upload Data

Upload a dataset for analysis.

**Endpoint:** `POST /api/v1/data/upload`

**Request:**
```python
import requests

url = 'http://localhost:8501/api/v1/data/upload'
files = {'file': open('sales_data.csv', 'rb')}
headers = {'Authorization': 'Bearer YOUR_API_KEY'}

response = requests.post(url, files=files, headers=headers)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dataset_id": "ds_abc123",
    "filename": "sales_data.csv",
    "rows": 1000,
    "columns": 5,
    "size_bytes": 45000,
    "upload_timestamp": "2025-10-05T12:00:00Z",
    "columns_info": [
      {"name": "date", "type": "datetime64[ns]"},
      {"name": "revenue", "type": "float64"},
      {"name": "units", "type": "int64"}
    ]
  }
}
```

### Get Dataset Info

Retrieve information about a dataset.

**Endpoint:** `GET /api/v1/data/{dataset_id}`

**Request:**
```python
response = requests.get(
    'http://localhost:8501/api/v1/data/ds_abc123',
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "dataset_id": "ds_abc123",
    "filename": "sales_data.csv",
    "rows": 1000,
    "columns": 5,
    "created_at": "2025-10-05T12:00:00Z",
    "last_accessed": "2025-10-05T13:30:00Z",
    "schema": {
      "date": "datetime64[ns]",
      "revenue": "float64",
      "units": "int64",
      "region": "object",
      "product": "object"
    },
    "statistics": {
      "revenue": {
        "mean": 15000,
        "median": 14500,
        "std": 3000,
        "min": 5000,
        "max": 30000
      }
    }
  }
}
```

### Query Data

Query dataset with filters.

**Endpoint:** `POST /api/v1/data/{dataset_id}/query`

**Request:**
```python
query = {
    "filters": [
        {"column": "region", "operator": "eq", "value": "North"},
        {"column": "revenue", "operator": "gt", "value": 10000}
    ],
    "columns": ["date", "revenue", "product"],
    "limit": 100,
    "offset": 0,
    "sort_by": "date",
    "sort_order": "desc"
}

response = requests.post(
    'http://localhost:8501/api/v1/data/ds_abc123/query',
    json=query,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "rows": [
      {
        "date": "2025-10-01",
        "revenue": 15000,
        "product": "Product A"
      },
      ...
    ],
    "total_count": 250,
    "returned_count": 100,
    "has_more": true
  }
}
```

### Delete Dataset

**Endpoint:** `DELETE /api/v1/data/{dataset_id}`

**Request:**
```python
response = requests.delete(
    'http://localhost:8501/api/v1/data/ds_abc123',
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

---

## Forecasting API

### Create Forecast

Generate a forecast for a dataset.

**Endpoint:** `POST /api/v1/forecast/create`

**Request:**
```python
forecast_config = {
    "dataset_id": "ds_abc123",
    "date_column": "date",
    "metric_column": "revenue",
    "model": "prophet",  # Options: prophet, arima, sarima, exponential_smoothing, lstm
    "forecast_periods": 30,
    "confidence_level": 0.95,
    "parameters": {
        "yearly_seasonality": True,
        "weekly_seasonality": True,
        "seasonality_mode": "multiplicative",
        "changepoint_prior_scale": 0.05
    },
    "include_history": True
}

response = requests.post(
    'http://localhost:8501/api/v1/forecast/create',
    json=forecast_config,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "forecast_id": "fc_xyz789",
    "dataset_id": "ds_abc123",
    "model": "prophet",
    "status": "completed",
    "created_at": "2025-10-05T12:00:00Z",
    "forecast": {
      "predictions": [
        {
          "date": "2025-11-01",
          "yhat": 16500,
          "yhat_lower": 15200,
          "yhat_upper": 17800
        },
        ...
      ],
      "metrics": {
        "mape": 7.2,
        "rmse": 1200,
        "mae": 950,
        "r2": 0.92
      },
      "components": {
        "trend": [...],
        "yearly": [...],
        "weekly": [...]
      }
    }
  }
}
```

### Get Forecast

Retrieve a completed forecast.

**Endpoint:** `GET /api/v1/forecast/{forecast_id}`

**Request:**
```python
response = requests.get(
    'http://localhost:8501/api/v1/forecast/fc_xyz789',
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

### Compare Models

Compare multiple forecasting models.

**Endpoint:** `POST /api/v1/forecast/compare`

**Request:**
```python
comparison = {
    "dataset_id": "ds_abc123",
    "date_column": "date",
    "metric_column": "revenue",
    "models": ["prophet", "arima", "sarima"],
    "forecast_periods": 30,
    "validation_split": 0.2
}

response = requests.post(
    'http://localhost:8501/api/v1/forecast/compare',
    json=comparison,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "comparison_id": "cmp_123",
    "models": [
      {
        "model": "prophet",
        "metrics": {
          "mape": 7.2,
          "rmse": 1200,
          "mae": 950,
          "r2": 0.92,
          "training_time_seconds": 3.5
        },
        "rank": 1
      },
      {
        "model": "sarima",
        "metrics": {
          "mape": 8.1,
          "rmse": 1350,
          "mae": 1020,
          "r2": 0.89,
          "training_time_seconds": 8.2
        },
        "rank": 2
      }
    ],
    "recommendation": {
      "best_model": "prophet",
      "reason": "Lowest MAPE and fastest training time"
    }
  }
}
```

---

## Insights API

### Generate Insights

Generate AI-powered insights from data.

**Endpoint:** `POST /api/v1/insights/generate`

**Request:**
```python
insights_config = {
    "dataset_id": "ds_abc123",
    "analysis_types": [
        "trend",
        "seasonality",
        "anomaly",
        "correlation"
    ],
    "metric_columns": ["revenue", "units"],
    "sensitivity": "medium"  # low, medium, high
}

response = requests.post(
    'http://localhost:8501/api/v1/insights/generate',
    json=insights_config,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "insights_id": "in_456",
    "dataset_id": "ds_abc123",
    "generated_at": "2025-10-05T12:00:00Z",
    "insights": [
      {
        "type": "trend",
        "severity": "high",
        "metric": "revenue",
        "message": "Revenue increased by 23% over the last quarter",
        "details": {
          "start_value": 120000,
          "end_value": 147600,
          "change_percent": 23.0,
          "confidence": 0.95
        }
      },
      {
        "type": "anomaly",
        "severity": "high",
        "metric": "revenue",
        "message": "Unusual spike detected on 2025-09-15 (340% above normal)",
        "details": {
          "date": "2025-09-15",
          "value": 52000,
          "expected": 15000,
          "deviation": 340
        }
      },
      {
        "type": "correlation",
        "severity": "medium",
        "message": "Strong positive correlation between revenue and units (r=0.87)",
        "details": {
          "variable1": "revenue",
          "variable2": "units",
          "correlation": 0.87,
          "p_value": 0.001
        }
      }
    ],
    "summary": {
      "total_insights": 8,
      "high_priority": 3,
      "medium_priority": 3,
      "low_priority": 2
    }
  }
}
```

### Anomaly Detection

Detect anomalies in time series data.

**Endpoint:** `POST /api/v1/insights/anomalies`

**Request:**
```python
anomaly_config = {
    "dataset_id": "ds_abc123",
    "metric_column": "revenue",
    "date_column": "date",
    "method": "isolation_forest",  # isolation_forest, statistical, lstm
    "sensitivity": 0.1,  # contamination rate
    "include_scores": True
}

response = requests.post(
    'http://localhost:8501/api/v1/insights/anomalies',
    json=anomaly_config,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "anomalies": [
      {
        "date": "2025-09-15",
        "value": 52000,
        "expected_range": [12000, 18000],
        "anomaly_score": 0.95,
        "severity": "critical"
      },
      {
        "date": "2025-08-03",
        "value": 3000,
        "expected_range": [12000, 18000],
        "anomaly_score": 0.82,
        "severity": "high"
      }
    ],
    "total_anomalies": 12,
    "anomaly_rate": 1.2,
    "method_used": "isolation_forest"
  }
}
```

---

## Export API

### Export Data

Export data in various formats.

**Endpoint:** `POST /api/v1/export/data`

**Request:**
```python
export_config = {
    "dataset_id": "ds_abc123",
    "format": "csv",  # csv, excel, json, parquet
    "filters": [...],
    "columns": ["date", "revenue", "region"],
    "include_metadata": True
}

response = requests.post(
    'http://localhost:8501/api/v1/export/data',
    json=export_config,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "export_id": "exp_789",
    "download_url": "https://your-domain.com/downloads/exp_789.csv",
    "expires_at": "2025-10-06T12:00:00Z",
    "file_size_bytes": 125000,
    "format": "csv"
  }
}
```

### Export Report

Generate and export a report.

**Endpoint:** `POST /api/v1/export/report`

**Request:**
```python
report_config = {
    "dataset_id": "ds_abc123",
    "report_type": "executive_summary",  # executive_summary, detailed_analysis, forecast_report
    "format": "pdf",  # pdf, pptx, html
    "include_sections": [
        "key_metrics",
        "trends",
        "forecast",
        "recommendations"
    ],
    "branding": {
        "company_name": "Acme Corp",
        "logo_url": "https://example.com/logo.png",
        "primary_color": "#1E40AF"
    }
}

response = requests.post(
    'http://localhost:8501/api/v1/export/report',
    json=report_config,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

---

## Webhook Integration

### Register Webhook

Receive notifications for events.

**Endpoint:** `POST /api/v1/webhooks/register`

**Request:**
```python
webhook_config = {
    "url": "https://your-app.com/webhook",
    "events": [
        "forecast.completed",
        "anomaly.detected",
        "data.uploaded"
    ],
    "secret": "your_webhook_secret",
    "active": True
}

response = requests.post(
    'http://localhost:8501/api/v1/webhooks/register',
    json=webhook_config,
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

**Webhook Payload Example:**
```json
{
  "event": "forecast.completed",
  "timestamp": "2025-10-05T12:00:00Z",
  "data": {
    "forecast_id": "fc_xyz789",
    "dataset_id": "ds_abc123",
    "model": "prophet",
    "mape": 7.2,
    "status": "completed"
  },
  "signature": "sha256=..."
}
```

**Verify Webhook Signature:**
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Python SDK

### Installation

```bash
pip install streamlit-bi-sdk
```

### Quick Start

```python
from streamlit_bi import Client

# Initialize client
client = Client(api_key='YOUR_API_KEY')

# Upload data
dataset = client.upload_data('sales_data.csv')
print(f"Dataset ID: {dataset.id}")

# Create forecast
forecast = client.create_forecast(
    dataset_id=dataset.id,
    date_column='date',
    metric_column='revenue',
    model='prophet',
    periods=30
)

print(f"MAPE: {forecast.metrics['mape']:.2f}%")

# Get insights
insights = client.generate_insights(dataset_id=dataset.id)
for insight in insights:
    print(f"- {insight.message}")

# Export report
report = client.export_report(
    dataset_id=dataset.id,
    format='pdf',
    report_type='executive_summary'
)
report.download('report.pdf')
```

### Advanced Usage

```python
# Custom forecasting parameters
forecast = client.create_forecast(
    dataset_id=dataset.id,
    date_column='date',
    metric_column='revenue',
    model='prophet',
    periods=30,
    parameters={
        'yearly_seasonality': True,
        'weekly_seasonality': True,
        'seasonality_mode': 'multiplicative',
        'changepoint_prior_scale': 0.05,
        'holidays': client.get_holidays('US')
    }
)

# Batch processing
datasets = client.list_datasets()
for dataset in datasets:
    forecast = client.create_forecast(
        dataset_id=dataset.id,
        model='auto'  # Auto-select best model
    )
    print(f"{dataset.name}: MAPE {forecast.metrics['mape']:.2f}%")

# Real-time monitoring
@client.on('anomaly.detected')
def handle_anomaly(event):
    print(f"Anomaly detected: {event.data['message']}")
    # Send alert, create ticket, etc.

client.start_listening()
```

---

## Error Handling

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | Invalid or missing API key | 401 |
| `AUTHORIZATION_ERROR` | Insufficient permissions | 403 |
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `SERVER_ERROR` | Internal server error | 500 |
| `MODEL_ERROR` | Forecasting model failed | 500 |
| `DATA_ERROR` | Data processing error | 400 |

### Error Handling Example

```python
from streamlit_bi import Client, APIError, ValidationError

client = Client(api_key='YOUR_API_KEY')

try:
    forecast = client.create_forecast(
        dataset_id='invalid_id',
        date_column='date',
        metric_column='revenue'
    )
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.details}")
except APIError as e:
    print(f"API error: {e.code} - {e.message}")
    if e.code == 'RATE_LIMIT_EXCEEDED':
        # Wait and retry
        time.sleep(60)
        forecast = client.create_forecast(...)
```

---

## Rate Limiting

### Limits

| Tier | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 60 | 1,000 |
| Pro | 300 | 10,000 |
| Enterprise | 1,000 | Unlimited |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1633449600
```

### Handling Rate Limits

```python
import time

def make_request_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            if e.code == 'RATE_LIMIT_EXCEEDED':
                wait_time = int(e.headers.get('X-RateLimit-Reset', 60))
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

---

## API Changelog

### v1.0.0 (Current)
- Initial API release
- Data upload and management
- Forecasting with multiple models
- Insights generation
- Export functionality

### Upcoming (v1.1.0)
- Batch processing endpoints
- Advanced filtering options
- Real-time streaming support
- GraphQL API

---

**Need Help?**
- 📚 [Full Documentation](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/docs)
- 💬 [Community Support](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)
- 📧 [Email Support](mailto:api-support@streamlit-bi.com)
