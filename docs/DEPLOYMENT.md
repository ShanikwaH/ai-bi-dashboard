# Deployment Guide

Complete deployment guide for the Streamlit BI Dashboard on various platforms.

## 📋 Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [GitHub Deployment](#github-deployment)
- [Streamlit Community Cloud](#streamlit-community-cloud)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Setup](#cicd-setup)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Security Checklist

- [ ] All secrets moved to environment variables
- [ ] `.env` and `secrets.toml` in `.gitignore`
- [ ] HTTPS/SSL configured
- [ ] CORS settings configured properly
- [ ] API rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] Security headers configured

### Performance Checklist

- [ ] Caching enabled and configured
- [ ] Large file handling optimized
- [ ] Database connection pooling configured
- [ ] Static assets compressed
- [ ] CDN configured (if applicable)
- [ ] Load testing completed
- [ ] Performance benchmarks met

### Code Quality Checklist

- [ ] All tests passing (`pytest tests/`)
- [ ] Code linted (`flake8 .`)
- [ ] Code formatted (`black .`)
- [ ] Type checking passed (`mypy .`)
- [ ] Dependencies up to date
- [ ] No hardcoded secrets
- [ ] Error handling implemented
- [ ] Logging configured

### Documentation Checklist

- [ ] README.md updated
- [ ] API documentation complete
- [ ] Deployment guide reviewed
- [ ] Configuration documented
- [ ] Changelog updated
- [ ] Release notes prepared

---

## GitHub Deployment

### 1. Repository Setup

```bash
# Initialize git repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Streamlit BI Dashboard v1.0.0"

# Create repository on GitHub (via web interface)
# Then connect local to remote
git remote add origin https://github.com/your-username/streamlit-bi-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Repository Structure

```
streamlit-bi-dashboard/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # CI pipeline
│   │   ├── deploy.yml          # Deployment pipeline
│   │   └── security.yml        # Security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml
├── .gitignore
├── README.md
├── LICENSE
└── [project files]
```

### 3. GitHub Actions for CI/CD

**File:** `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Format check with black
      run: |
        black --check .
    
    - name: Type check with mypy
      run: |
        mypy .
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check
        bandit -r . -f json -o bandit-report.json
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: bandit-report.json
```

### 4. Automated Deployment

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/
    
    - name: Build Docker image
      run: |
        docker build -t streamlit-bi-dashboard:${{ github.sha }} .
    
    - name: Push to Docker Hub
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag streamlit-bi-dashboard:${{ github.sha }} yourusername/streamlit-bi-dashboard:latest
        docker push yourusername/streamlit-bi-dashboard:latest
    
    - name: Deploy to Streamlit Cloud
      run: |
        # Trigger deployment webhook
        curl -X POST ${{ secrets.STREAMLIT_DEPLOY_WEBHOOK }}
```

### 5. Branch Protection Rules

Configure on GitHub:
1. Go to Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require pull request reviews (1+ approvals)
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Include administrators
   - ✅ Require linear history

---

## Streamlit Community Cloud

### 1. Prepare for Deployment

**Ensure files exist:**
```bash
# Required files
├── app.py                    # Main entry point
├── requirements.txt          # Dependencies
├── packages.txt             # System dependencies (optional)
└── .streamlit/
    └── config.toml          # Streamlit config (optional)
```

**requirements.txt:**
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
prophet>=1.1.5
scikit-learn>=1.3.0
```

**packages.txt (if needed):**
```
build-essential
```

### 2. Deploy to Streamlit Cloud

**Step 1: Push to GitHub**
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

**Step 2: Deploy via Web Interface**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `your-username/streamlit-bi-dashboard`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

**Step 3: Configure Secrets**
1. In app settings, go to "Secrets"
2. Add secrets in TOML format:

```toml
# Database
[database]
host = "your-db-host"
port = 5432
username = "db-user"
password = "db-password"

# API Keys
[api]
openai_key = "sk-..."
anthropic_key = "sk-ant-..."

# Email (for reports)
[email]
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "your-email@gmail.com"
smtp_password = "app-password"
```

### 3. Custom Domain (Optional)

1. Go to app settings → "Custom domain"
2. Add your domain: `dashboard.yourdomain.com`
3. Configure DNS:
   ```
   Type: CNAME
   Name: dashboard
   Value: your-app.streamlit.app
   ```

### 4. Automatic Redeployment

Streamlit Cloud automatically redeploys on:
- Push to main branch
- Changes to requirements.txt
- Changes to app code

---

## Docker Deployment

### 1. Create Dockerfile

**Dockerfile:**
```dockerfile
# Use official Python runtime
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_KEY=${API_KEY}
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=bi_dashboard
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

volumes:
  redis-data:
  postgres-data:

networks:
  app-network:
    driver: bridge
```

### 3. Build and Run

```bash
# Build image
docker build -t streamlit-bi-dashboard:latest .

# Run container
docker run -p 8501:8501 \
  -e DATABASE_URL=${DATABASE_URL} \
  -e API_KEY=${API_KEY} \
  streamlit-bi-dashboard:latest

# Or use docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 4. Production Docker Setup

**nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server app:8501;
    }

    server {
        listen 80;
        server_name dashboard.yourdomain.com;
        
        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name dashboard.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # WebSocket support
        location /_stcore/stream {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }
    }
}
```

---

## Cloud Platforms

### AWS Deployment (EC2 + RDS)

**Step 1: Launch EC2 Instance**
```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx
```

**Step 2: Setup EC2**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@ec2-instance-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-username/streamlit-bi-dashboard.git
cd streamlit-bi-dashboard

# Create .env file
nano .env
# Add your environment variables

# Deploy
docker-compose up -d
```

**Step 3: Configure RDS**
```bash
# Create RDS instance via AWS Console or CLI
aws rds create-db-instance \
  --db-instance-identifier bi-dashboard-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword \
  --allocated-storage 20

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://admin:YourPassword@rds-endpoint:5432/bi_dashboard
```

### Google Cloud Platform (Cloud Run)

**Step 1: Prepare for Cloud Run**

**Dockerfile (Cloud Run optimized):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run uses PORT environment variable
CMD streamlit run app.py \
    --server.port=${PORT:-8080} \
    --server.address=0.0.0.0 \
    --server.headless=true
```

**Step 2: Deploy to Cloud Run**
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy streamlit-bi-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=${DATABASE_URL},API_KEY=${API_KEY}

# Get service URL
gcloud run services describe streamlit-bi-dashboard \
  --region us-central1 \
  --format 'value(status.url)'
```

### Azure (App Service)

**Step 1: Create App Service**
```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create resource group
az group create --name bi-dashboard-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name bi-dashboard-plan \
  --resource-group bi-dashboard-rg \
  --is-linux \
  --sku B1

# Create web app
az webapp create \
  --resource-group bi-dashboard-rg \
  --plan bi-dashboard-plan \
  --name streamlit-bi-dashboard \
  --runtime "PYTHON:3.10"
```

**Step 2: Deploy**
```bash
# Configure deployment from GitHub
az webapp deployment source config \
  --name streamlit-bi-dashboard \
  --resource-group bi-dashboard-rg \
  --repo-url https://github.com/your-username/streamlit-bi-dashboard \
  --branch main \
  --manual-integration

# Set environment variables
az webapp config appsettings set \
  --resource-group bi-dashboard-rg \
  --name streamlit-bi-dashboard \
  --settings DATABASE_URL=${DATABASE_URL} API_KEY=${API_KEY}

# Set startup command
az webapp config set \
  --resource-group bi-dashboard-rg \
  --name streamlit-bi-dashboard \
  --startup-file "streamlit run app.py --server.port=8000 --server.address=0.0.0.0"
```

### Heroku

**Step 1: Prepare for Heroku**

**Procfile:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.10.12
```

**Step 2: Deploy**
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create streamlit-bi-dashboard

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Set config vars
heroku config:set API_KEY=your-api-key

# Deploy
git push heroku main

# Open app
heroku open

# View logs
heroku logs --tail
```

---

## Kubernetes Deployment

### 1. Kubernetes Manifests

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: streamlit-bi-dashboard
  labels:
    app: bi-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bi-dashboard
  template:
    metadata:
      labels:
        app: bi-dashboard
    spec:
      containers:
      - name: app
        image: yourusername/streamlit-bi-dashboard:latest
        ports:
        - containerPort: 8501
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 10
          periodSeconds: 5
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: bi-dashboard-service
spec:
  selector:
    app: bi-dashboard
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8501
  type: LoadBalancer
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bi-dashboard-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - dashboard.yourdomain.com
    secretName: dashboard-tls
  rules:
  - host: dashboard.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bi-dashboard-service
            port:
              number: 80
```

### 2. Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace bi-dashboard

# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url=${DATABASE_URL} \
  --from-literal=api-key=${API_KEY} \
  -n bi-dashboard

# Apply manifests
kubectl apply -f deployment.yaml -n bi-dashboard
kubectl apply -f service.yaml -n bi-dashboard
kubectl apply -f ingress.yaml -n bi-dashboard

# Check status
kubectl get pods -n bi-dashboard
kubectl get services -n bi-dashboard
kubectl get ingress -n bi-dashboard

# View logs
kubectl logs -f deployment/streamlit-bi-dashboard -n bi-dashboard
```

---

## CI/CD Setup

### GitHub Actions Complete Pipeline

**File:** `.github/workflows/full-pipeline.yml`

```yaml
name: Full CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

env:
  DOCKER_IMAGE: yourusername/streamlit-bi-dashboard
  KUBERNETES_NAMESPACE: bi-dashboard

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        push: true
        tags: |
          ${{ env.DOCKER_IMAGE }}:latest
          ${{ env.DOCKER_IMAGE }}:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        echo "Deploying to staging..."

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    steps:
    - uses: actions/checkout@v3
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/streamlit-bi-dashboard \
          app=${{ env.DOCKER_IMAGE }}:${{ github.sha }} \
          -n ${{ env.KUBERNETES_NAMESPACE }}
        kubectl rollout status deployment/streamlit-bi-dashboard \
          -n ${{ env.KUBERNETES_NAMESPACE }}
```

---

## Monitoring & Maintenance

### 1. Health Monitoring

**Health check endpoint:**
```python
# In app.py
import streamlit as st
from datetime import datetime

# Add health check page
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.2.0"
    }

# Expose at /_health
if st.experimental_get_query_params().get("health"):
    st.json(health_check())
    st.stop()
```

### 2. Logging

**Centralized logging:**
```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log application events
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### 3. Metrics

**Prometheus metrics:**
```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

# Start metrics server
start_http_server(9090)

# Track metrics
request_count.inc()
with request_duration.time():
    # Process request
    pass
```

### 4. Backup Strategy

```bash
# Database backup
pg_dump -h localhost -U user bi_dashboard > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * /path/to/backup.sh

# Backup to S3
aws s3 cp backup.sql s3://your-bucket/backups/
```

---

## Troubleshooting

### Common Deployment Issues

**1. Port conflicts**
```bash
# Check if port is in use
lsof -i :8501

# Kill process
kill -9 <PID>

# Use different port
streamlit run app.py --server.port=8502
```

**2. Memory issues**
```bash
# Increase container memory
docker run -m 4g streamlit-bi-dashboard

# Kubernetes
resources:
  limits:
    memory: "4Gi"
```

**3. SSL/HTTPS issues**
```bash
# Generate self-signed cert (dev only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Use Let's Encrypt (production)
certbot certonly --standalone -d dashboard.yourdomain.com
```

**4. Database connection failures**
```python
# Test connection
import psycopg2
try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected successfully")
except Exception as e:
    print(f"Connection failed: {e}")
```

---

## Rollback Procedures

### Docker Rollback
```bash
# List previous versions
docker images yourusername/streamlit-bi-dashboard

# Rollback to previous version
docker-compose down
docker-compose up -d yourusername/streamlit-bi-dashboard:previous-tag
```

### Kubernetes Rollback
```bash
# View rollout history
kubectl rollout history deployment/streamlit-bi-dashboard -n bi-dashboard

# Rollback to previous version
kubectl rollout undo deployment/streamlit-bi-dashboard -n bi-dashboard

# Rollback to specific revision
kubectl rollout undo deployment/streamlit-bi-dashboard --to-revision=2 -n bi-dashboard
```

---

**Last Updated:** October 5, 2025  
**Version:** 1.2.0

**Need Help?**
- 📚 [Setup Guide](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/SETUP.md)
- 🔧 [Configuration](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/CONFIGURATION.md)
- 💬 [Community Support](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)
- 📧 [Email](mailto:devops@streamlit-bi.com)
