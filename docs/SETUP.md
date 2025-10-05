# Setup Guide - Streamlit BI Dashboard

Complete installation and configuration guide for development, testing, and production environments.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 500MB free space
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+

### Recommended for Production
- **OS**: Linux (Ubuntu 20.04 LTS or newer)
- **Python**: 3.10 or 3.11
- **RAM**: 8GB minimum (16GB+ for large datasets)
- **Storage**: 2GB+ free space
- **CPU**: 4+ cores
- **Network**: Stable internet connection for cloud deployment

### Software Dependencies
```bash
# Check Python version
python --version  # Should be 3.9+

# Check pip version
pip --version  # Should be 21.0+

# Optional but recommended
git --version
docker --version
```

---

## Installation Methods

### Method 1: Quick Install (Recommended)

**For Users - Get Started in 5 Minutes**

```bash
# Clone the repository
git clone https://github.com/your-username/streamlit-bi-dashboard.git
cd streamlit-bi-dashboard

# Run setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create virtual environment
- Install dependencies
- Set up configuration files
- Run initial tests
- Launch the application

### Method 2: Manual Installation

**For Developers - Full Control**

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/streamlit-bi-dashboard.git
cd streamlit-bi-dashboard
```

#### Step 2: Create Virtual Environment

**Using venv (Python built-in)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**Using conda (Alternative)**
```bash
# Create conda environment
conda create -n bi-dashboard python=3.10

# Activate environment
conda activate bi-dashboard
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

#### Step 4: Verify Installation
```bash
# Run tests
pytest tests/

# Check Streamlit installation
streamlit --version

# Verify imports
python -c "import streamlit, pandas, prophet; print('All imports successful!')"
```

### Method 3: Docker Installation

**For Production - Containerized Deployment**

#### Step 1: Build Docker Image
```bash
# Build the image
docker build -t streamlit-bi-dashboard:latest .

# Or use docker-compose
docker-compose build
```

#### Step 2: Run Container
```bash
# Run with docker
docker run -p 8501:8501 streamlit-bi-dashboard:latest

# Or use docker-compose
docker-compose up
```

#### Step 3: Access Application
```
http://localhost:8501
```

### Method 4: One-Line Install

**Quick Test - No Git Required**

```bash
curl -sSL https://raw.githubusercontent.com/your-username/streamlit-bi-dashboard/main/install.sh | bash
```

---

## Development Setup

### 1. Project Structure

```
streamlit-bi-dashboard/
├── app.py                      # Main application entry point
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                    # Package setup (optional)
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── pytest.ini                 # Pytest configuration
├── docker-compose.yml         # Docker compose config
├── Dockerfile                 # Docker image definition
│
├── pages/                     # Streamlit pages
│   ├── 1_📊_Overview.py
│   ├── 2_📈_Charts.py
│   ├── 3_🔮_Forecasting.py
│   └── 4_🤖_AI_Insights.py
│
├── components/                # Reusable UI components
│   ├── __init__.py
│   ├── charts.py
│   ├── metrics.py
│   └── filters.py
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_processor.py
│   ├── forecasting.py
│   ├── insights.py
│   └── export.py
│
├── models/                    # ML models
│   ├── __init__.py
│   ├── prophet_model.py
│   ├── arima_model.py
│   └── ensemble.py
│
├── data/                      # Sample data files
│   ├── sample_sales.csv
│   ├── sample_inventory.csv
│   └── README.md
│
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_forecasting.py
│   └── test_insights.py
│
├── docs/                      # Documentation
│   ├── API.md
│   ├── SETUP.md
│   └── SECURITY.md
│
└── .streamlit/               # Streamlit config
    ├── config.toml
    └── secrets.toml
```

### 2. Install Development Tools

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# This includes:
# - pytest (testing)
# - black (code formatting)
# - flake8 (linting)
# - mypy (type checking)
# - pre-commit (git hooks)
```

### 3. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### 4. Configure IDE

**VS Code Settings** (`.vscode/settings.json`)
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

**PyCharm Settings**
1. File → Settings → Tools → Python Integrated Tools
2. Set Default test runner to "pytest"
3. Enable "Black" as formatter
4. Enable "Flake8" for linting

### 5. Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test
streamlit run app.py

# 3. Run tests
pytest tests/ -v

# 4. Format code
black .
flake8 .

# 5. Commit changes
git add .
git commit -m "feat: add your feature"

# 6. Push and create PR
git push origin feature/your-feature-name
```

---

## Production Setup

### Option 1: Streamlit Community Cloud (Free)

#### Step 1: Prepare Repository
```bash
# Ensure these files exist:
# - app.py (main app)
# - requirements.txt (dependencies)
# - .streamlit/config.toml (optional config)

# Push to GitHub
git push origin main
```

#### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select repository and branch
5. Set main file path: `app.py`
6. Click "Deploy"

#### Step 3: Configure Secrets
In Streamlit Cloud dashboard:
1. Go to App Settings → Secrets
2. Add secrets in TOML format:
```toml
[database]
host = "your-db-host"
port = 5432
username = "db-user"
password = "db-password"

[api]
openai_key = "your-api-key"
```

### Option 2: Docker + Cloud Platform

#### AWS EC2 Deployment

**Step 1: Launch EC2 Instance**
```bash
# Launch Ubuntu 20.04 instance
# Type: t3.medium or larger
# Security Group: Allow port 8501
```

**Step 2: Install Docker**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@ec2-instance-ip

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
```

**Step 3: Deploy Application**
```bash
# Clone repository
git clone https://github.com/your-username/streamlit-bi-dashboard.git
cd streamlit-bi-dashboard

# Create .env file
nano .env
# Add your environment variables

# Start application
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**Step 4: Set Up Reverse Proxy (Nginx)**
```bash
# Install Nginx
sudo apt install nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/streamlit
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Step 5: Set Up SSL (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Option 3: Heroku Deployment

#### Step 1: Prepare Files

**Create `Procfile`:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Create `setup.sh`:**
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

#### Step 2: Deploy
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# Open app
heroku open
```

### Option 4: Google Cloud Run

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Build and deploy
gcloud run deploy streamlit-bi-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Configuration

### Streamlit Configuration

**File:** `.streamlit/config.toml`

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501

[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
toolbarMode = "minimal"

[runner]
magicEnabled = true
fastReruns = true
```

### Application Configuration

**File:** `config.yaml`

```yaml
app:
  name: "AI-Powered BI Dashboard"
  version: "1.0.0"
  debug: false

data:
  max_upload_size_mb: 200
  allowed_extensions:
    - csv
    - xlsx
    - xls
  sample_data_path: "data/sample_sales.csv"

forecasting:
  default_model: "prophet"
  max_forecast_days: 365
  confidence_level: 0.95
  models:
    - exponential_smoothing
    - arima
    - sarima
    - prophet
    - lstm

cache:
  enabled: true
  ttl_seconds: 3600
  max_size_mb: 500

logging:
  level: "INFO"
  file: "logs/app.log"
  rotation: "1 day"
  retention: "7 days"
```

---

## Database Setup

### PostgreSQL (Optional)

If using database storage instead of file uploads:

#### Step 1: Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql
```

#### Step 2: Create Database
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE bi_dashboard;
CREATE USER bi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bi_dashboard TO bi_user;
\q
```

#### Step 3: Configure Connection
```python
# In utils/db_connector.py
import sqlalchemy
import os

def get_db_connection():
    db_url = os.getenv('DATABASE_URL')
    engine = sqlalchemy.create_engine(db_url)
    return engine

# Usage
engine = get_db_connection()
df = pd.read_sql("SELECT * FROM sales", con=engine)
```

---

## Environment Variables

### Create `.env` File

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env
```

### Required Variables

```bash
# Application
APP_NAME="AI-Powered BI Dashboard"
APP_VERSION="1.0.0"
DEBUG=False
SECRET_KEY="your-secret-key-here"

# Database (if using)
DATABASE_URL="postgresql://user:password@localhost:5432/bi_dashboard"
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# API Keys (if using)
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."

# Storage
UPLOAD_FOLDER="uploads"
MAX_UPLOAD_SIZE_MB=200

# Cache
REDIS_URL="redis://localhost:6379/0"  # if using Redis
CACHE_TTL=3600

# Email (for reports)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"

# Security
ALLOWED_HOSTS="localhost,127.0.0.1,your-domain.com"
ENABLE_HTTPS=True
SESSION_COOKIE_SECURE=True
```

### Load Environment Variables

**In `app.py`:**
```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
debug_mode = os.getenv('DEBUG', 'False') == 'True'
db_url = os.getenv('DATABASE_URL')
api_key = os.getenv('OPENAI_API_KEY')
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use
```bash
# Error: Address already in use
# Solution: Use different port
streamlit run app.py --server.port 8502

# Or kill process on port 8501
# On macOS/Linux:
lsof -ti:8501 | xargs kill -9

# On Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### Issue 2: Module Not Found
```bash
# Error: ModuleNotFoundError: No module named 'prophet'
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt

# If still fails, install individually
pip install prophet --no-cache-dir
```

#### Issue 3: Prophet Installation Fails
```bash
# On Windows, install C++ build tools first
# Download from: https://visualstudio.microsoft.com/downloads/

# On macOS with M1/M2
arch -arm64 pip install prophet

# On Linux
sudo apt-get install python3-dev
pip install prophet
```

#### Issue 4: Memory Error with Large Files
```bash
# Increase Streamlit memory limit
streamlit run app.py --server.maxUploadSize=500

# Or in config.toml
[server]
maxUploadSize = 500
```

#### Issue 5: Slow Performance
```bash
# Enable caching
# In your functions:
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Clear cache if needed
streamlit cache clear
```

#### Issue 6: Docker Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t streamlit-bi-dashboard .

# Check logs
docker logs <container-id>
```

### Getting Help

If you encounter issues:

1. **Check Documentation**
   - [Getting Started Guide](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/GETTING_STARTED.md)
   - [API Documentation](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/API.md)
   - [Security Guide](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/SECURITY.md)

2. **Search Issues**
   - [GitHub Issues](https://github.com/ShanikwaH/ai-bi-dashboard/issues)
   - Look for similar problems

3. **Ask Community**
   - [GitHub Discussions](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)

4. **Report Bug**
   - Use bug report template
   - Include error messages
   - Provide system information

---

## Health Checks

### Verify Installation

```bash
# Run health check script
python scripts/health_check.py
```

**Expected Output:**
```
✅ Python version: 3.10.5
✅ Streamlit version: 1.28.0
✅ All dependencies installed
✅ Configuration files present
✅ Sample data accessible
✅ Database connection successful
✅ Cache system operational

All checks passed! ✨
```

### Test Application

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_forecasting.py -v

# Run integration tests
pytest tests/integration/ -v
```

---

## Next Steps

After successful setup:

1. ✅ **Verify Installation**: Run health checks
2. 📚 **Read Documentation**: Review [GETTING_STARTED.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/GETTING_STARTED.md)
3. 🎓 **Try Tutorial**: Follow [AI_TUTORIAL.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/AI_TUTORIAL.md)
4. 🚀 **Deploy**: Choose production deployment method
5. 🤝 **Contribute**: See [CONTRIBUTING.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/CONTRIBUTING.md)

---

**Need Help?** Join our community:
- 💬 [Discussions](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)
- 🐛 [Issues](https://github.com/ShanikwaH/ai-bi-dashboard/issues)
- 📧 [Email](mailto:support@streamlit-bi.com)
