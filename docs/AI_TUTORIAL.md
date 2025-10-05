# AI-Powered Features Tutorial

Learn how to leverage artificial intelligence and machine learning capabilities in your Streamlit BI Dashboard to automate insights, predictions, and decision-making.

## 📋 Table of Contents
- [Introduction to AI Features](#introduction-to-ai-features)
- [Auto-Insights Generation](#auto-insights-generation)
- [Natural Language Queries](#natural-language-queries)
- [Anomaly Detection](#anomaly-detection)
- [Predictive Analytics](#predictive-analytics)
- [Automated Report Generation](#automated-report-generation)
- [Best Practices](#best-practices)

---

## Introduction to AI Features

Our dashboard includes several AI-powered capabilities that work automatically or with minimal configuration:

### Core AI Components
1. **Auto-Insights Engine** - Automatically discovers patterns
2. **Anomaly Detection** - Identifies unusual data points
3. **Natural Language Interface** - Query data with plain English
4. **Predictive Models** - Forecast future trends
5. **Smart Recommendations** - Suggests next steps

### How AI Enhances Your Analysis
- **Speed**: Reduces analysis time from hours to seconds
- **Accuracy**: Detects patterns humans might miss
- **Automation**: Continuous monitoring without manual effort
- **Accessibility**: No coding or statistical knowledge required

---

## Auto-Insights Generation

### Overview
The Auto-Insights feature automatically analyzes your data and generates actionable insights without any manual configuration.

### How It Works

#### Step 1: Enable Auto-Insights
```python
# In your dashboard sidebar:
1. Upload your data
2. Navigate to "🤖 AI Insights" tab
3. Click "Generate Insights"
```

#### Step 2: Review Insights
The AI engine will analyze:
- **Trends**: Rising or declining patterns
- **Correlations**: Relationships between variables
- **Outliers**: Unusual values or events
- **Seasonality**: Recurring patterns
- **Distributions**: Data spread and shape

#### Step 3: Insight Categories

**1. Trend Insights**
```
Example Output:
"📈 Sales increased by 23% over the last quarter"
"📉 Customer churn rate declined by 8% month-over-month"
"⚡ Website traffic shows accelerating growth (+15% week-over-week)"
```

**2. Correlation Insights**
```
Example Output:
"🔗 Strong positive correlation (0.87) between Marketing Spend and Revenue"
"⚠️ Negative correlation (-0.65) between Price and Units Sold"
"💡 Customer satisfaction scores correlate with repeat purchase rate (0.72)"
```

**3. Anomaly Insights**
```
Example Output:
"🚨 Sales on Dec 15 were 340% above normal (possible outlier)"
"⚡ Sudden spike in customer complaints detected on Oct 1"
"📊 Unusual pattern: Revenue dropped 45% with no change in traffic"
```

**4. Comparative Insights**
```
Example Output:
"🏆 Product A outperforms Product B by 56% in conversion rate"
"📍 North region shows 2x higher growth than South region"
"⏰ Weekend sales average 30% higher than weekdays"
```

### Practical Example

**Scenario**: Analyzing Monthly Sales Data

```python
# Data uploaded: monthly_sales.csv
# Columns: Date, Revenue, Marketing_Spend, Units_Sold, Region

Auto-Insights Generated:

1. "📈 Revenue grew 34% YoY, with acceleration in Q3"

2. "🔗 Strong correlation (r=0.89) between marketing spend 
   and revenue suggests effective campaigns"

3. "🚨 August revenue 45% below trend - investigate supply 
   chain disruptions"

4. "🏆 North region accounts for 52% of total revenue, 
   growing at 2.3x company average"

5. "💡 Every $1 in marketing spend generates $4.20 in 
   revenue (ROI: 320%)"

6. "📊 Revenue shows strong weekly seasonality, peaking 
   on Thursdays (28% above average)"
```

### Customization Options

#### Insight Sensitivity
```python
# Adjust how sensitive the AI is to detecting patterns:
Sensitivity Levels:
- Low: Only major patterns (>20% changes)
- Medium: Moderate patterns (>10% changes) [Default]
- High: Minor patterns (>5% changes)
```

#### Focus Areas
```python
# Select specific analysis types:
✓ Trend Analysis
✓ Correlation Discovery
✓ Anomaly Detection
✓ Seasonality Analysis
□ Forecast Validation
□ Segment Analysis
```

---

## Natural Language Queries

### Overview
Ask questions about your data in plain English - no SQL or coding required!

### Getting Started

#### Step 1: Access NL Query Interface
```python
# In the dashboard:
1. Go to "💬 Ask Your Data" tab
2. Your uploaded data is automatically available
3. Type your question in the text box
```

#### Step 2: Example Queries

**Basic Questions**
```
Q: "What are my total sales?"
A: Total sales: $2,456,789
   [Shows: Summary card with total]

Q: "How many customers do I have?"
A: Total customers: 15,432
   Active customers: 12,876
   [Shows: Metric breakdown]

Q: "What is the average order value?"
A: Average order value: $127.45
   Median: $98.20
   [Shows: Distribution chart]
```

**Trend Questions**
```
Q: "Show me sales trends over time"
A: [Generates: Line chart with sales by month]
   Key insight: 15% growth trend detected

Q: "How is revenue changing?"
A: [Shows: Revenue trend with +18% YoY growth]
   Current month: $456K (+12% vs last month)

Q: "What are my top selling products?"
A: [Displays: Top 10 products with sales figures]
   1. Product A: $234K (19% of total)
   2. Product B: $189K (15% of total)
```

**Comparison Questions**
```
Q: "Compare sales between regions"
A: [Generates: Bar chart by region]
   North: $1.2M (48%)
   South: $750K (30%)
   East: $506K (22%)

Q: "How does this month compare to last month?"
A: Current month: $456K
   Last month: $412K
   Change: +10.7% (📈 $44K increase)

Q: "Which products have declining sales?"
A: [Lists: 3 products with negative trends]
   Product X: -23% vs last quarter
   Product Y: -15% vs last quarter
```

**Advanced Analytics**
```
Q: "Predict next month's revenue"
A: [Shows: Forecast visualization]
   Predicted: $485K
   Confidence interval: $460K - $510K
   Based on: ARIMA model (95% confidence)

Q: "Find correlations in my data"
A: [Displays: Correlation matrix heatmap]
   Top correlation: Marketing Spend ↔ Revenue (0.87)

Q: "Detect anomalies in my sales data"
A: [Highlights: 4 anomalies detected]
   Oct 15: +340% spike (special promotion?)
   Nov 3: -45% drop (system outage?)
```

### Tips for Better Results

#### ✅ Do's
- Use specific time periods: "last quarter" vs "recently"
- Name exact columns: "revenue" not "money"
- Ask one question at a time
- Use common business terms

#### ❌ Don'ts
- Avoid vague terms: "stuff", "things"
- Don't use technical jargon unless it's in your data
- Avoid compound questions
- Don't expect data you haven't uploaded

### Query Types Supported

| Query Type | Example | Output |
|------------|---------|--------|
| Aggregation | "What's the total revenue?" | Metric card |
| Filtering | "Show sales over $1000" | Filtered table |
| Grouping | "Sales by region" | Chart by category |
| Trending | "Revenue over time" | Time series chart |
| Ranking | "Top 10 customers" | Ranked list |
| Prediction | "Forecast next quarter" | Forecast chart |
| Comparison | "This year vs last year" | Comparison view |

---

## Anomaly Detection

### Overview
Automatically identify unusual patterns, outliers, and anomalies in your data that may require attention.

### How Anomaly Detection Works

#### Algorithm Types

**1. Statistical Methods**
- Z-score detection (values >3 std dev from mean)
- IQR method (values outside 1.5×IQR range)
- Moving average deviation

**2. Machine Learning Methods**
- Isolation Forest
- Local Outlier Factor (LOF)
- One-Class SVM

**3. Time Series Anomalies**
- Unexpected spikes or drops
- Pattern breaks
- Seasonal deviations

### Setting Up Anomaly Detection

#### Step 1: Configure Detection
```python
# In Anomaly Detection tab:
1. Select metric to monitor (e.g., "Daily Revenue")
2. Choose detection method:
   - Automatic (recommended)
   - Statistical (Z-score, IQR)
   - ML-based (Isolation Forest)
3. Set sensitivity:
   - Low: Only extreme anomalies
   - Medium: Standard detection [Default]
   - High: Detect minor deviations
```

#### Step 2: Review Anomalies
```python
# System displays:
Anomaly Report:
┌─────────────┬──────────────┬──────────┬────────────┐
│ Date        │ Metric Value │ Expected │ Deviation  │
├─────────────┼──────────────┼──────────┼────────────┤
│ Oct 15, 2025│ $234,500     │ $68,000  │ +245% 🔴   │
│ Sep 3, 2025 │ $12,300      │ $67,500  │ -82%  🔴   │
│ Aug 22, 2025│ $98,700      │ $70,200  │ +41%  🟡   │
└─────────────┴──────────────┴──────────┴────────────┘
```

### Practical Applications

#### Use Case 1: Sales Monitoring
```python
Scenario: Detect unusual sales patterns

Setup:
- Metric: Daily Sales Revenue
- Method: Time Series (ARIMA-based)
- Alert threshold: >2 standard deviations

Results:
🔴 Critical Anomaly Detected:
   Date: December 15, 2025
   Sales: $345,000 (expected: $75,000)
   Possible cause: Black Friday promotion?
   
🟡 Warning Anomaly:
   Date: November 3, 2025
   Sales: $32,000 (expected: $68,000)
   Possible cause: Website downtime?
```

#### Use Case 2: Quality Control
```python
Scenario: Monitor product defect rates

Setup:
- Metric: Defect Rate
- Method: Statistical (Control Charts)
- Baseline: 2.3% average defect rate

Results:
🚨 Anomaly Alert:
   Defect rate spiked to 8.7% on Oct 1
   Root cause investigation recommended
   Affected batch: LOT-2024-10-001
```

#### Use Case 3: Customer Behavior
```python
Scenario: Identify unusual user activity

Setup:
- Metric: Daily Active Users
- Method: Isolation Forest
- Training period: Last 90 days

Results:
⚡ Unusual Pattern Detected:
   Oct 10: 45% drop in DAU
   Correlation: Server outage logged
   Recovery: Normal activity resumed Oct 11
```

### Real-Time Alerts

#### Configure Notifications
```python
Alert Settings:
├── Email Notifications
│   ✓ Send to: team@company.com
│   ✓ Frequency: Immediate
│   ✓ Include: Anomaly details + chart
│
├── Slack Integration
│   ✓ Channel: #data-alerts
│   ✓ Mention: @data-team
│
└── Dashboard Alerts
    ✓ Show banner on homepage
    ✓ Highlight in visualizations
```

---

## Predictive Analytics

### Overview
Use machine learning models to forecast future trends and make data-driven predictions.

### Available Models

#### 1. Time Series Forecasting
**Best for**: Sales forecasts, demand planning, trend prediction

**Models Available**:
- **ARIMA/SARIMA**: Classical statistical method
- **Exponential Smoothing**: Trend and seasonality
- **Prophet**: Facebook's forecasting tool (best for daily data)
- **LSTM**: Deep learning for complex patterns

#### 2. Classification Models
**Best for**: Customer churn, lead scoring, category prediction

**Models Available**:
- **Logistic Regression**: Simple, interpretable
- **Random Forest**: High accuracy, handles non-linear relationships
- **XGBoost**: State-of-the-art gradient boosting
- **Neural Networks**: Complex pattern recognition

#### 3. Regression Models
**Best for**: Price prediction, value estimation

**Models Available**:
- **Linear Regression**: Simple relationships
- **Ridge/Lasso**: Regularized models
- **Gradient Boosting**: Non-linear relationships

### Tutorial: Sales Forecasting

#### Step-by-Step Guide

**Step 1: Prepare Data**
```python
# Required columns:
- Date column (daily, weekly, or monthly)
- Metric to forecast (e.g., Revenue, Units)
- Optional: Additional features (marketing spend, etc.)

# Data requirements:
- Minimum 30 historical data points
- No large gaps in dates
- Clean, numeric target variable
```

**Step 2: Select Model**
```python
# In Forecasting tab:
1. Choose forecasting model:
   □ Auto (AI selects best model) ✓ [Recommended]
   □ ARIMA (statistical approach)
   □ Prophet (seasonal patterns)
   □ LSTM (complex patterns)

2. Set parameters:
   - Forecast horizon: 30 days
   - Confidence level: 95%
   - Include uncertainty: Yes
```

**Step 3: Train and Evaluate**
```python
# Model Training Output:
Training Model: Prophet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Model Performance:
├── MAPE: 8.3% (Excellent)
├── RMSE: $12,450
├── R²: 0.91
└── Cross-validation: 5-fold

Feature Importance:
1. Historical trend: 45%
2. Weekly seasonality: 28%
3. Marketing spend: 18%
4. Day of week: 9%
```

**Step 4: Generate Forecast**
```python
# Forecast Output:
30-Day Revenue Forecast:
┌────────────┬───────────┬─────────────┬─────────────┐
│ Date       │ Forecast  │ Lower Bound │ Upper Bound │
├────────────┼───────────┼─────────────┼─────────────┤
│ Nov 1, 2025│ $67,500   │ $62,100     │ $72,900     │
│ Nov 2, 2025│ $68,200   │ $62,700     │ $73,700     │
│ ...        │ ...       │ ...         │ ...         │
│ Nov 30,2025│ $75,300   │ $68,800     │ $81,800     │
└────────────┴───────────┴─────────────┴─────────────┘

Total 30-Day Forecast: $2,145,000
Growth vs Last Period: +12.5%
```

### Tutorial: Churn Prediction

#### Predicting Customer Churn

**Step 1: Prepare Features**
```python
# Required data:
Features (X):
- Customer tenure (months)
- Monthly charges
- Total charges
- Contract type
- Support tickets
- Usage patterns

Target (y):
- Churned (Yes/No)
```

**Step 2: Build Model**
```python
# In ML Models tab:
1. Select "Classification"
2. Choose target: "Churned"
3. Select features (all relevant columns)
4. Model: XGBoost (recommended for tabular data)
5. Train model
```

**Step 3: Evaluate Results**
```python
Model Performance:
├── Accuracy: 87.3%
├── Precision: 82.1%
├── Recall: 79.5%
├── F1-Score: 80.8%
└── AUC-ROC: 0.91

Feature Importance:
1. Tenure: 32%
2. Monthly charges: 24%
3. Contract type: 18%
4. Support tickets: 15%
5. Usage decline: 11%
```

**Step 4: Make Predictions**
```python
# Apply model to new customers:
High Risk Customers (>70% churn probability):
┌─────────────┬───────────────┬─────────────────┐
│ Customer ID │ Churn Risk    │ Recommendation  │
├─────────────┼───────────────┼─────────────────┤
│ CUST-10234  │ 89%          │ Retention offer │
│ CUST-10567  │ 76%          │ Check-in call   │
│ CUST-10891  │ 72%          │ Survey feedback │
└─────────────┴───────────────┴─────────────────┘

Estimated Revenue at Risk: $234,500
```

---

## Automated Report Generation

### Overview
Generate comprehensive, professional reports automatically using AI.

### Report Types

#### 1. Executive Summary
```python
# Auto-generated content:
Executive Summary - October 2024

Key Metrics:
- Revenue: $2.4M (+18% YoY)
- Active Customers: 15,432 (+12%)
- Conversion Rate: 3.2% (+0.4pp)

Top Insights:
1. Strong Q4 momentum with accelerating growth
2. Marketing ROI improved to 320% (best in 2 years)
3. North region driving 48% of total revenue
4. Product A maintains market leadership

Risk Factors:
- Increasing customer acquisition costs (+23%)
- Churn rate uptick in mid-tier segment (+2.1pp)

Recommendations:
1. Increase investment in North region
2. Launch retention campaign for at-risk customers
3. Optimize marketing spend allocation
```

#### 2. Detailed Analytics Report
```python
# Includes:
✓ Data quality assessment
✓ Trend analysis with visualizations
✓ Correlation matrix
✓ Forecast projections
✓ Anomaly highlights
✓ Action items
```

### Generating Reports

#### Step 1: Configure Report
```python
# In Reports tab:
Report Configuration:
├── Type: Executive Summary
├── Period: Last Quarter
├── Sections:
│   ✓ Key Metrics
│   ✓ Trends & Patterns
│   ✓ Forecasts
│   ✓ Recommendations
├── Format: PDF / PowerPoint / HTML
└── Recipients: team@company.com
```

#### Step 2: Review and Export
```python
# AI generates report in ~30 seconds:
✓ Analysis complete
✓ Insights generated
✓ Visualizations created
✓ Narrative written
✓ Report compiled

Export Options:
□ Download PDF
□ Download PowerPoint
□ Email to team
□ Schedule recurring (weekly/monthly)
```

---

## Best Practices

### Data Preparation
1. **Clean Your Data**: Remove duplicates, handle missing values
2. **Consistent Formatting**: Standardize date formats, column names
3. **Sufficient History**: Minimum 30 data points for forecasting
4. **Relevant Features**: Include variables that impact your target metric

### Model Selection
1. **Start Simple**: Try auto-mode first, then customize
2. **Validate Results**: Check model metrics (MAPE, R², etc.)
3. **Compare Models**: Test multiple approaches
4. **Monitor Performance**: Track accuracy over time

### Interpreting AI Insights
1. **Context Matters**: Consider business knowledge alongside AI findings
2. **Verify Anomalies**: Investigate unusual patterns before acting
3. **Confidence Levels**: Pay attention to prediction intervals
4. **Human Oversight**: Use AI as a tool, not a replacement for judgment

### Performance Optimization
1. **Data Sampling**: Use representative samples for large datasets
2. **Feature Selection**: Remove irrelevant columns
3. **Incremental Updates**: Retrain models periodically
4. **Cache Results**: Save time with cached predictions

---

## Next Steps

### Continue Learning
- 📖 Read [FORECASTING.md](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/FORECASTING.md) for advanced forecasting
- 🎬 Watch [AI Features Tutorial Video](https://youtube.com/watch?v=xxx)
- 📝 Read [Building AI-Powered Dashboards](https://medium.com/@shanikwa.lhaynes/xxx)

### Get Support
- 💬 [Community Discussions](https://github.com/ShanikwaH/ai-bi-dashboard/discussions)
- 📧 [Email Support](mailto:ai-support@streamlit-bi.com)
- 📚 [Full Documentation](https://github.com/ShanikwaH/ai-bi-dashboard/blob/main/docs/docs)

---

**Happy Analyzing! 🚀**
