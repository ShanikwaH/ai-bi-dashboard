# Getting Started with Streamlit BI Dashboard

Welcome! This guide will help you set up and start using the AI-Powered Streamlit Business Intelligence Dashboard in just a few minutes.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Your First Dashboard](#your-first-dashboard)
- [Understanding the Interface](#understanding-the-interface)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, ensure you have:

### Required
- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- **Basic understanding of CSV/Excel files**

### Optional but Recommended
- **Virtual environment tool** (venv, conda, or virtualenv)
- **Git** - For cloning the repository
- **Code editor** (VS Code, PyCharm, or similar)

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **Browser**: Chrome, Firefox, Safari, or Edge (latest version)

---

## Installation

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/streamlit-bi-dashboard.git

# Navigate to project directory
cd streamlit-bi-dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Download ZIP

1. Download the ZIP file from [GitHub](https://github.com/your-repo)
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder
4. Follow steps 3-6 from Method 1

### Method 3: pip Install (Coming Soon)

```bash
pip install streamlit-bi-dashboard
```

---

## Quick Start

### Step 1: Launch the Application

```bash
# Ensure you're in the project directory with activated virtual environment
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

### Step 2: Open in Browser

The app should automatically open in your default browser. If not, navigate to:
```
http://localhost:8501
```

### Step 3: Upload Your Data

1. Click on **"Browse files"** or drag-and-drop your data file
2. Supported formats: CSV, Excel (.xlsx, .xls)
3. Wait for the upload to complete

**Sample Data**: Use `sample_data/sales_data.csv` included in the repository to test

---

## Your First Dashboard

Let's create your first dashboard using sample sales data!

### Step-by-Step Tutorial

#### 1. **Data Upload**
```bash
# The sample data is located at:
data/sample_sales.csv
```
- Click **"Upload Data"** in the sidebar
- Select `sample_sales.csv`
- You'll see a preview of your data

#### 2. **Data Overview**
The dashboard automatically shows:
- **Dataset shape**: Number of rows and columns
- **Column types**: Numeric, categorical, datetime
- **Missing values**: Highlighted in red
- **Statistical summary**: Mean, median, std, etc.

#### 3. **Explore Visualizations**
Navigate through tabs:
- **📊 Overview**: Key metrics and data quality
- **📈 Charts**: Interactive visualizations
- **🔮 Forecasting**: Time series predictions
- **🎯 Insights**: AI-generated insights

#### 4. **Create a Chart**
```python
# In the Charts tab:
1. Select chart type (Line, Bar, Scatter, etc.)
2. Choose X-axis column (e.g., "Date")
3. Choose Y-axis column (e.g., "Sales")
4. Optional: Add color grouping
5. Click "Generate Chart"
```

#### 5. **Run a Forecast**
```python
# In the Forecasting tab:
1. Select date column
2. Select metric to forecast (e.g., "Revenue")
3. Choose forecast periods (e.g., 30 days)
4. Select model (Exponential Smoothing, ARIMA, etc.)
5. Click "Generate Forecast"
```

---

## Understanding the Interface

### Main Navigation

#### Sidebar (Left)
- **📁 Data Upload**: Load your datasets
- **⚙️ Settings**: Configure dashboard preferences
- **📊 Data Selection**: Choose active dataset
- **🔧 Filters**: Apply data filters

#### Main Panel (Center)
- **Tab Navigation**: Switch between features
- **Interactive Charts**: Zoom, pan, download
- **Data Tables**: Sortable and searchable
- **Metric Cards**: KPIs and summaries

#### Header (Top)
- **App Title**: Current project name
- **Help Icon**: Quick documentation
- **Theme Toggle**: Light/dark mode

### Key Features

#### 1. Data Profiling
Automatically analyzes your data:
- Data types and quality
- Missing value detection
- Outlier identification
- Distribution analysis

#### 2. Visualization Builder
Create charts with ease:
- 15+ chart types
- Custom color schemes
- Interactive legends
- Export to PNG/SVG

#### 3. Forecasting Engine
Predict future trends:
- Multiple algorithms (ES, ARIMA, Prophet)
- Confidence intervals
- Model comparison
- Forecast accuracy metrics

#### 4. AI Insights
Automated insights generation:
- Trend detection
- Anomaly alerts
- Pattern recognition
- Correlation analysis

---

## Common Use Cases

### Use Case 1: Sales Analysis

```python
# Upload: monthly_sales.csv
# Columns: Date, Product, Region, Sales, Units

Steps:
1. Upload sales data
2. Go to Charts → Select "Sales Trends"
3. Create line chart: Date vs Sales
4. Add filter: Region = "North America"
5. Generate forecast for next quarter
```

### Use Case 2: Marketing Campaign Performance

```python
# Upload: campaign_data.csv
# Columns: Date, Campaign, Impressions, Clicks, Conversions, Spend

Steps:
1. Upload campaign data
2. Calculate CTR: Clicks / Impressions
3. Create scatter plot: Spend vs Conversions
4. Identify top-performing campaigns
5. Forecast conversion trends
```

### Use Case 3: Inventory Management

```python
# Upload: inventory_data.csv
# Columns: Date, Product_ID, Stock_Level, Demand, Supplier

Steps:
1. Upload inventory data
2. Identify low stock items (Stock_Level < 100)
3. Forecast demand for next 30 days
4. Generate reorder recommendations
5. Export report as PDF
```

### Use Case 4: Financial Reporting

```python
# Upload: financial_data.csv
# Columns: Date, Revenue, Expenses, Profit, Category

Steps:
1. Upload financial data
2. Create KPI dashboard (Revenue, Profit Margin)
3. Visualize monthly trends
4. Compare categories with bar charts
5. Forecast quarterly revenue
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Application Won't Start
```bash
# Error: ModuleNotFoundError
Solution:
pip install -r requirements.txt --upgrade

# Error: Port already in use
Solution:
streamlit run app.py --server.port 8502
```

#### Issue 2: Data Upload Fails
```bash
# Error: File format not supported
Solution:
- Ensure file is .csv, .xlsx, or .xls
- Check file isn't corrupted
- Try with sample_data/sales_data.csv first

# Error: File too large
Solution:
- Reduce file size (<200MB)
- Use data sampling
- Consider database connection instead
```

#### Issue 3: Forecast Not Generating
```bash
# Error: Insufficient data
Solution:
- Ensure at least 30 data points
- Check date column is properly formatted
- Verify no missing values in target column

# Error: Model failed to converge
Solution:
- Try different forecasting model
- Check for outliers in data
- Ensure data is properly sorted by date
```

#### Issue 4: Chart Not Displaying
```bash
# Error: No data to display
Solution:
- Clear filters in sidebar
- Check column selection
- Refresh the page (Ctrl+R or Cmd+R)
```

### Getting Help

If you're still stuck:

1. **Check Documentation**: See `/docs` folder
2. **GitHub Issues**: Search existing issues
3. **Discussions**: Ask the community
4. **Email Support**: mailto:support@streamlit-bi.com

---

## Next Steps

### Beginner Track
1. ✅ Complete this getting started guide
2. 📖 Read [AI_TUTORIAL.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/AI_TUTORIAL.md) for AI features
3. 📊 Explore [FORECASTING.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/FORECASTING.md) for predictions
4. 🎬 Watch our [YouTube tutorials](https://youtube.com/streamlitbi)

### Intermediate Track
1. 🔌 Connect to SQL databases
2. 🎨 Customize dashboard themes
3. 📈 Build advanced visualizations
4. 🤖 Train custom ML models

### Advanced Track
1. 🏗️ Contribute to the project (see [CONTRIBUTING.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/CONTRIBUTING.md))
2. 🔧 Extend with custom components
3. 🚀 Deploy to production
4. 🌐 Integrate with APIs

### Learning Resources

#### Video Tutorials
- [15-Minute Quick Start](https://youtube.com/watch?v=xxx)
- [Building Your First Dashboard](https://youtube.com/watch?v=xxx)
- [Advanced Forecasting Techniques](https://youtube.com/watch?v=xxx)

#### Blog Posts
- [Building an AI-Powered BI Dashboard](https://medium.com/@shanikwa.lhaynes/xxx)
- [Time Series Forecasting for Business](https://analyticsbyshanikwa.com/forecasting)
- [Data Visualization Best Practices](https://blog.streamlit-bi.com)

#### Documentation
- [API Reference](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/API.md)
- [Configuration Guide](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/CONFIGURATION.md)
- [Deployment Guide](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/DEPLOYMENT.md)

---

## Quick Reference

### Essential Commands
```bash
# Start app
streamlit run app.py

# Start on different port
streamlit run app.py --server.port 8502

# Enable debug mode
streamlit run app.py --logger.level=debug

# Clear cache
streamlit cache clear
```

### Keyboard Shortcuts
- `R` - Rerun the app
- `C` - Clear cache
- `?` - Show keyboard shortcuts
- `⌘/Ctrl + Shift + F` - Search

### File Structure
```
streamlit-bi-dashboard/
├── app.py                 # Main application
├── pages/                 # Multi-page components
│   ├── 1_📊_Overview.py
│   ├── 2_📈_Charts.py
│   └── 3_🔮_Forecasting.py
├── data/                  # Sample datasets
├── utils/                 # Helper functions
└── docs/                  # Documentation
```

---

## Success Checklist

- [ ] Python 3.9+ installed
- [ ] Repository cloned or downloaded
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] App runs successfully on localhost:8501
- [ ] Sample data uploaded
- [ ] First chart created
- [ ] First forecast generated
- [ ] Familiar with navigation

**Congratulations!** 🎉 You're now ready to build powerful BI dashboards!

---

**Need Help?** Join our community:
- 💬 [Discussions](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)
- 🐛 [Report Issues](https://github.com/ShanikwaH/ai-bi-dashboard/issues)
- 📧 [Email](mailto:support@streamlit-bi.com)
