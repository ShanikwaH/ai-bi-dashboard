# Configuration Guide

Complete configuration reference for the Streamlit BI Dashboard.

## 📋 Table of Contents

- [Configuration Files](#configuration-files)
- [Streamlit Configuration](#streamlit-configuration)
- [Application Settings](#application-settings)
- [Database Configuration](#database-configuration)
- [Forecasting Models](#forecasting-models)
- [Caching & Performance](#caching--performance)
- [Security Settings](#security-settings)
- [Logging Configuration](#logging-configuration)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)

---

## Configuration Files

### File Locations

```
streamlit-bi-dashboard/
├── .streamlit/
│   ├── config.toml          # Streamlit settings
│   └── secrets.toml         # Sensitive credentials (gitignored)
├── config.yaml              # Application configuration
├── .env                     # Environment variables (gitignored)
└── .env.example             # Environment template
```

### Configuration Priority

Settings are loaded in this order (later overrides earlier):

1. **Default values** (hardcoded in application)
2. **config.yaml** (application settings)
3. **.streamlit/config.toml** (Streamlit settings)
4. **.streamlit/secrets.toml** (secrets)
5. **Environment variables** (highest priority)

---

## Streamlit Configuration

### Basic Settings

**File:** `.streamlit/config.toml`

```toml
[server]
# Server configuration
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

# Upload settings
maxUploadSize = 200
maxMessageSize = 200

# WebSocket settings
enableWebsocketCompression = true
```

### Browser Settings

```toml
[browser]
# Browser behavior
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501
```

### Theme Configuration

```toml
[theme]
# Color scheme
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

# Available fonts:
# - "sans serif"
# - "serif"  
# - "monospace"
```

### Client Settings

```toml
[client]
# Client behavior
showErrorDetails = true
toolbarMode = "minimal"  # Options: auto, developer, viewer, minimal

# Display settings
caching = true
displayEnabled = true
```

### Runner Settings

```toml
[runner]
# Script execution
magicEnabled = true
installTracer = false
fixMatplotlib = true
postScriptGC = true

# Rerun behavior
fastReruns = true
enforceSerializableSessionState = false
```

### Logger Settings

```toml
[logger]
# Logging levels: ERROR, WARNING, INFO, DEBUG
level = "INFO"
messageFormat = "%(asctime)s %(message)s"
```

### Dark Mode Configuration

```toml
[theme]
base = "dark"
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

---

## Application Settings

### Main Configuration

**File:** `config.yaml`

```yaml
# Application Information
app:
  name: "AI-Powered BI Dashboard"
  version: "1.2.0"
  description: "Business Intelligence Dashboard with AI Forecasting"
  debug: false
  timezone: "UTC"
  language: "en"

# Feature Flags
features:
  forecasting: true
  ai_insights: true
  data_export: true
  api_access: true
  multi_user: false
  real_time_updates: false

# UI Configuration
ui:
  theme: "light"  # light, dark, auto
  sidebar_state: "expanded"  # expanded, collapsed, auto
  wide_mode: true
  initial_page: "Overview"
  show_footer: true
  custom_css: "assets/custom.css"
```

### Data Settings

```yaml
data:
  # Upload configuration
  max_upload_size_mb: 200
  allowed_extensions:
    - csv
    - xlsx
    - xls
    - json
    - parquet
  
  # Data processing
  default_encoding: "utf-8"
  date_formats:
    - "%Y-%m-%d"
    - "%m/%d/%Y"
    - "%d/%m/%Y"
    - "%Y-%m-%d %H:%M:%S"
  
  # Data quality
  missing_value_threshold: 0.1  # 10%
  outlier_detection: "iqr"  # iqr, zscore, isolation_forest
  auto_clean: false
  
  # Sampling for large datasets
  sampling:
    enabled: true
    threshold_rows: 1000000
    sample_size: 100000
    method: "random"  # random, stratified, systematic
```

### Visualization Settings

```yaml
visualization:
  # Chart defaults
  default_chart_type: "line"
  color_scheme: "plotly"  # plotly, seaborn, custom
  interactive: true
  
  # Chart configuration
  charts:
    height: 500
    width: null  # auto-width
    show_legend: true
    show_grid: true
    animation: true
  
  # Custom color palettes
  color_palettes:
    primary:
      - "#FF4B4B"
      - "#FFA347"
      - "#FFD43B"
      - "#4CBB17"
      - "#0066FF"
    
    categorical:
      - "#1f77b4"
      - "#ff7f0e"
      - "#2ca02c"
      - "#d62728"
      - "#9467bd"
  
  # Export settings
  export:
    dpi: 300
    format: "png"  # png, svg, pdf
    transparent_background: false
```

---

## Database Configuration

### PostgreSQL

```yaml
database:
  type: "postgresql"
  host: "${DB_HOST}"
  port: 5432
  database: "${DB_NAME}"
  username: "${DB_USER}"
  password: "${DB_PASSWORD}"
  
  # Connection pool
  pool:
    min_size: 1
    max_size: 10
    timeout: 30
    max_lifetime: 3600
  
  # Query settings
  query:
    timeout: 30
    batch_size: 1000
    use_cache: true
```

### MongoDB

```yaml
database:
  type: "mongodb"
  uri: "${MONGODB_URI}"
  database: "${MONGODB_DATABASE}"
  
  # Connection options
  options:
    maxPoolSize: 10
    minPoolSize: 1
    maxIdleTimeMS: 60000
    serverSelectionTimeoutMS: 5000
```

### SQLite (Development)

```yaml
database:
  type: "sqlite"
  path: "data/dashboard.db"
  
  options:
    check_same_thread: false
    timeout: 5.0
```

---

## Forecasting Models

### Model Configuration

```yaml
forecasting:
  # Default settings
  default_model: "prophet"
  max_forecast_days: 365
  confidence_level: 0.95
  min_data_points: 30
  
  # Model-specific settings
  models:
    exponential_smoothing:
      enabled: true
      seasonal_periods: 12
      trend: "add"  # add, mul, None
      seasonal: "add"  # add, mul, None
    
    arima:
      enabled: true
      auto_order: true
      seasonal: false
      information_criterion: "aic"  # aic, bic
      max_p: 5
      max_d: 2
      max_q: 5
    
    sarima:
      enabled: true
      auto_order: true
      seasonal_periods:
        - 7   # weekly
        - 12  # monthly
        - 52  # yearly (weekly data)
      max_P: 2
      max_D: 1
      max_Q: 2
    
    prophet:
      enabled: true
      growth: "linear"  # linear, logistic, flat
      changepoint_prior_scale: 0.05
      seasonality_prior_scale: 10
      holidays_prior_scale: 10
      seasonality_mode: "additive"  # additive, multiplicative
      
      # Seasonality
      yearly_seasonality: "auto"
      weekly_seasonality: "auto"
      daily_seasonality: "auto"
      
      # Holidays
      include_holidays: true
      country_holidays: "US"
    
    lstm:
      enabled: false  # Requires GPU for good performance
      sequence_length: 60
      epochs: 50
      batch_size: 32
      learning_rate: 0.001
      hidden_units: 50
  
  # Ensemble settings
  ensemble:
    enabled: true
    method: "weighted_average"  # simple_average, weighted_average, stacking
    weights:
      prophet: 0.4
      sarima: 0.35
      arima: 0.25
```

### Validation Settings

```yaml
forecasting:
  validation:
    method: "holdout"  # holdout, cross_validation, rolling_window
    test_size: 0.2
    cv_folds: 5
    
    # Metrics to calculate
    metrics:
      - mape
      - rmse
      - mae
      - r2
      - smape
```

---

## Caching & Performance

### Cache Configuration

```yaml
cache:
  # Cache settings
  enabled: true
  backend: "memory"  # memory, redis, disk
  ttl_seconds: 3600
  max_size_mb: 500
  
  # Cache keys
  strategies:
    data_upload: "hash"
    forecasts: "timestamp"
    insights: "hash"
  
  # Redis configuration (if using)
  redis:
    host: "${REDIS_HOST}"
    port: 6379
    db: 0
    password: "${REDIS_PASSWORD}"
    
    # Redis-specific options
    max_connections: 50
    socket_timeout: 5
    socket_connect_timeout: 5
```

### Performance Settings

```yaml
performance:
  # Data processing
  chunk_size: 10000
  parallel_processing: true
  max_workers: 4
  
  # Memory management
  memory_limit_mb: 2048
  gc_threshold: 0.8  # Trigger garbage collection at 80%
  
  # Optimization
  lazy_loading: true
  progressive_rendering: true
  debounce_ms: 300
```

---

## Security Settings

### Authentication

```yaml
security:
  # Authentication
  auth:
    enabled: false
    method: "basic"  # basic, oauth, saml
    session_timeout: 1800  # 30 minutes
    require_https: true
    
    # OAuth settings
    oauth:
      provider: "google"  # google, github, azure
      client_id: "${OAUTH_CLIENT_ID}"
      client_secret: "${OAUTH_CLIENT_SECRET}"
      redirect_uri: "${OAUTH_REDIRECT_URI}"
  
  # API Security
  api:
    enabled: true
    rate_limit:
      enabled: true
      requests_per_minute: 60
      requests_per_day: 1000
    
    # API Keys
    require_api_key: true
    key_rotation_days: 90
```

### Data Security

```yaml
security:
  # Data protection
  data:
    encryption_at_rest: true
    encryption_algorithm: "AES256"
    
    # PII handling
    pii_detection: true
    auto_redact: false
    
    # Data retention
    retention_days: 90
    auto_delete: true
  
  # Input validation
  validation:
    max_string_length: 1000
    allowed_file_types:
      - csv
      - xlsx
    scan_for_malware: true
```

### CORS Configuration

```yaml
security:
  cors:
    enabled: true
    allowed_origins:
      - "https://your-domain.com"
      - "https://app.your-domain.com"
    allowed_methods:
      - GET
      - POST
      - PUT
      - DELETE
    allowed_headers:
      - "*"
    max_age: 3600
```

---

## Logging Configuration

### Logging Settings

```yaml
logging:
  # General settings
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # Output
  outputs:
    - console
    - file
    - syslog  # Optional
  
  # File logging
  file:
    path: "logs/app.log"
    max_size_mb: 100
    backup_count: 10
    rotation: "time"  # time, size
    when: "midnight"
    interval: 1
  
  # Component-specific logging
  loggers:
    forecasting:
      level: "DEBUG"
      file: "logs/forecasting.log"
    
    api:
      level: "INFO"
      file: "logs/api.log"
    
    security:
      level: "WARNING"
      file: "logs/security.log"
  
  # Sensitive data
  mask_sensitive: true
  sensitive_patterns:
    - password
    - api_key
    - secret
    - token
```

### Monitoring & Metrics

```yaml
monitoring:
  # Metrics collection
  metrics:
    enabled: true
    provider: "prometheus"  # prometheus, datadog, custom
    port: 9090
    
    # Metrics to track
    track:
      - request_count
      - request_duration
      - error_rate
      - cache_hit_rate
      - forecast_accuracy
  
  # Health checks
  health_check:
    enabled: true
    endpoint: "/health"
    interval_seconds: 30
    
    # Checks to perform
    checks:
      - database
      - cache
      - disk_space
      - memory
```

---

## Environment Variables

### Required Variables

```bash
# Application
APP_NAME="AI-Powered BI Dashboard"
APP_ENV="production"  # development, staging, production
DEBUG=false

# Database
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"

# Security
SECRET_KEY="your-secret-key-here-change-in-production"
API_KEY="your-api-key"

# External Services (Optional)
OPENAI_API_KEY="sk-..."
REDIS_URL="redis://localhost:6379/0"
```

### Optional Variables

```bash
# Email (for reports)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SMTP_FROM="noreply@your-domain.com"

# Cloud Storage
AWS_ACCESS_KEY_ID="your-access-key"
AWS_SECRET_ACCESS_KEY="your-secret-key"
AWS_S3_BUCKET="your-bucket-name"
AWS_REGION="us-east-1"

# Monitoring
SENTRY_DSN="https://...@sentry.io/..."
DATADOG_API_KEY="your-datadog-key"

# Feature Flags
ENABLE_FORECASTING=true
ENABLE_AI_INSIGHTS=true
ENABLE_API=true
```

### Loading Environment Variables

```python
# In app.py
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Access variables
debug = os.getenv('DEBUG', 'false').lower() == 'true'
db_url = os.getenv('DATABASE_URL')
api_key = os.getenv('API_KEY')

# With defaults
max_upload_mb = int(os.getenv('MAX_UPLOAD_SIZE_MB', '200'))
```

---

## Advanced Configuration

### Multi-Environment Setup

**config/development.yaml**
```yaml
app:
  debug: true
  log_level: "DEBUG"

database:
  type: "sqlite"
  path: "dev.db"

cache:
  enabled: false
```

**config/production.yaml**
```yaml
app:
  debug: false
  log_level: "WARNING"

database:
  type: "postgresql"
  host: "${DB_HOST}"

cache:
  enabled: true
  backend: "redis"
```

**Loading environment-specific config:**
```python
import yaml
import os

env = os.getenv('APP_ENV', 'development')
config_file = f'config/{env}.yaml'

with open(config_file) as f:
    config = yaml.safe_load(f)
```

### Configuration Validation

```python
from pydantic import BaseModel, Field, validator

class AppConfig(BaseModel):
    name: str
    version: str
    debug: bool = False
    
    @validator('version')
    def validate_version(cls, v):
        # Ensure semantic versioning
        parts = v.split('.')
        if len(parts) != 3:
            raise ValueError('Invalid version format')
        return v

class DatabaseConfig(BaseModel):
    type: str = Field(..., regex='^(postgresql|mongodb|sqlite)$')
    host: str
    port: int = Field(gt=0, lt=65536)
    
# Validate configuration
config = AppConfig(**yaml_config['app'])
```

### Dynamic Configuration

```python
import streamlit as st

# Runtime configuration through UI
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Forecast settings
    forecast_model = st.selectbox(
        "Forecasting Model",
        ["prophet", "arima", "sarima"]
    )
    
    confidence = st.slider(
        "Confidence Level",
        min_value=80,
        max_value=99,
        value=95
    ) / 100
    
    # Save to session state
    st.session_state.config = {
        'forecast_model': forecast_model,
        'confidence': confidence
    }
```

### Configuration Templates

**Minimal (Development)**
```yaml
app:
  debug: true

data:
  max_upload_size_mb: 50

forecasting:
  default_model: "prophet"
```

**Standard (Production)**
```yaml
app:
  debug: false
  timezone: "UTC"

database:
  type: "postgresql"
  host: "${DB_HOST}"

security:
  auth:
    enabled: true
  
cache:
  enabled: true
  backend: "redis"

logging:
  level: "INFO"
```

**Enterprise (Full Features)**
```yaml
app:
  debug: false
  
database:
  type: "postgresql"
  pool:
    max_size: 20

security:
  auth:
    enabled: true
    method: "saml"
  api:
    rate_limit:
      enabled: true

monitoring:
  metrics:
    enabled: true
    provider: "datadog"

cache:
  backend: "redis"
  cluster: true
```

---

## Configuration Best Practices

### Security
- ✅ Never commit secrets to version control
- ✅ Use environment variables for sensitive data
- ✅ Rotate API keys regularly
- ✅ Enable encryption in production
- ✅ Use HTTPS for all external communications

### Performance
- ✅ Enable caching for production
- ✅ Configure appropriate connection pools
- ✅ Set reasonable file upload limits
- ✅ Use sampling for large datasets
- ✅ Enable compression where applicable

### Reliability
- ✅ Set appropriate timeouts
- ✅ Configure retry logic for external services
- ✅ Enable health checks
- ✅ Configure proper logging
- ✅ Set up monitoring and alerts

### Development
- ✅ Use different configs for dev/staging/prod
- ✅ Validate configuration on startup
- ✅ Document all configuration options
- ✅ Provide sensible defaults
- ✅ Use configuration templates

---

## Troubleshooting

### Common Issues

**Configuration not loading:**
```bash
# Check file exists and is readable
ls -la .streamlit/config.toml
cat .streamlit/config.toml

# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

**Environment variables not working:**
```bash
# Check .env file is in correct location
ls -la .env

# Verify variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

**Invalid configuration values:**
```python
# Validate configuration
from pydantic import ValidationError

try:
    config = AppConfig(**yaml_config)
except ValidationError as e:
    print(e.json())
```

---

## Configuration Examples

See `config/examples/` directory for:
- Development setup
- Production deployment
- Docker configuration
- Kubernetes configuration
- Cloud platform configs (AWS, Azure, GCP)

---

**Last Updated:** October 5, 2025  
**Version:** 1.2.0

**Need Help?**
- 📚 [Documentation](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/docs)
- 💬 [Community Forum](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)
- 📧 [Support](mailto:support@streamlit-bi.com)
