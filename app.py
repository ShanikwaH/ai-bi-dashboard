import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import google.generativeai as genai
import json
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="AI-Powered Business Intelligence Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Google Analytics
components.html("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-C9N4L7M92T"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-C9N4L7M92T');
</script>
""", height=0)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .ai-response {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4285f4;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .ai-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = None
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None
if 'model_name' not in st.session_state:
    st.session_state.model_name = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Configure Gemini AI
def configure_gemini(api_key, model_name='gemini-1.5-flash'):
    """Configure Gemini AI with API key"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Test the connection
        test = model.generate_content("Hello")
        
        return model
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Try: 1) Check API key, 2) Enable billing, 3) Use gemini-1.5-flash")
        return None

# Generate AI insights
def generate_ai_insights(df, question=None):
    """Generate insights using Gemini AI"""
    if st.session_state.gemini_model is None:
        return "Please configure Gemini API key first."
    
    try:
        # Prepare data summary for AI
        summary = f"""
        Dataset Overview:
        - Total Rows: {len(df)}
        - Total Columns: {len(df.columns)}
        - Columns: {', '.join(df.columns.tolist())}
        
        Numeric Columns Statistics:
        {df.describe().to_string()}
        
        Data Types:
        {df.dtypes.to_string()}
        
        Missing Values:
        {df.isnull().sum().to_string()}
        
        Sample Data (first 5 rows):
        {df.head().to_string()}
        """
        
        if question:
            prompt = f"""You are a data analyst expert. Based on the following dataset information, answer this question:
            
Question: {question}

Dataset Information:
{summary}

Provide a detailed, actionable analysis with specific insights and recommendations."""
        else:
            prompt = f"""You are a data analyst expert. Analyze the following dataset and provide:
1. Key insights and patterns
2. Potential issues or anomalies
3. Business recommendations
4. Suggested next steps for analysis

Dataset Information:
{summary}

Provide a comprehensive analysis."""
        
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"Error generating insights: {str(e)}"

# Generate forecast interpretation
def interpret_forecast(historical_data, forecast_data, method_name):
    """Use AI to interpret forecast results"""
    if st.session_state.gemini_model is None:
        return "AI interpretation not available. Please configure Gemini API key."
    
    try:
        prompt = f"""You are a business analyst. Interpret the following forecast results:

Forecasting Method: {method_name}
Historical Data Average: {historical_data.mean():.2f}
Historical Data Trend: {'Increasing' if historical_data.iloc[-10:].mean() > historical_data.iloc[:10].mean() else 'Decreasing'}
Forecast Average: {np.mean(forecast_data):.2f}
Forecast Range: {np.min(forecast_data):.2f} to {np.max(forecast_data):.2f}

Provide:
1. Interpretation of the forecast
2. Reliability assessment
3. Business implications
4. Risk factors to consider
5. Actionable recommendations

Keep the response concise but insightful."""
        
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating interpretation: {str(e)}"

# Generate automated report
def generate_automated_report(df):
    """Generate comprehensive AI report"""
    if st.session_state.gemini_model is None:
        return "Please configure Gemini API key first."
    
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        report_data = f"""
        Generate a comprehensive executive business intelligence report for the following dataset:
        
        Dataset Metrics:
        - Total Records: {len(df)}
        - Date Range: {df[df.columns[0]].min()} to {df[df.columns[0]].max() if pd.api.types.is_datetime64_any_dtype(df[df.columns[0]]) else 'N/A'}
        - Numeric Columns: {', '.join(numeric_cols)}
        
        Statistical Summary:
        {df[numeric_cols].describe().to_string()}
        
        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Findings (bullet points)
        3. Trends Analysis
        4. Performance Metrics Assessment
        5. Risk Factors
        6. Strategic Recommendations
        7. Next Steps
        
        Format as a professional business report.
        """
        
        response = st.session_state.gemini_model.generate_content(report_data)
        return response.text
    except Exception as e:
        return f"Error generating report: {str(e)}"

# Helper Functions
def generate_sample_data():
    """Generate sample sales data for demonstration"""
    np.random.seed(42)
    dates = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
    
    df = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.normal(50000, 15000, len(dates)).cumsum() / 100 + 10000,
        'Units_Sold': np.random.poisson(100, len(dates)),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
        'Product_Category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Home'], len(dates)),
        'Customer_Satisfaction': np.random.uniform(3.5, 5.0, len(dates))
    })
    
    df['Revenue'] = df['Revenue'].round(2)
    df['Customer_Satisfaction'] = df['Customer_Satisfaction'].round(2)
    
    return df

def generate_sales_data_df(rows):
    """Generate sales data as DataFrame"""
    import random
    
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam', 'Desk', 'Chair']
    categories = ['Electronics', 'Accessories', 'Furniture']
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    data = []
    for i in range(1, rows + 1):
        product = random.choice(products)
        category = random.choice(categories)
        quantity = random.randint(1, 10)
        price = round(random.uniform(50, 1000), 2)
        total = round(quantity * price, 2)
        date = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))).strftime('%Y-%m-%d')
        customer_id = f"CUST{random.randint(1, 5000):06d}"
        region = random.choice(regions)
        
        data.append([i, date, product, category, quantity, price, total, customer_id, region])
    
    return pd.DataFrame(data, columns=['transaction_id', 'date', 'product', 'category', 'quantity', 'price', 'total', 'customer_id', 'region'])

def generate_healthcare_data_df(rows):
    """Generate healthcare data as DataFrame"""
    import random
    
    diagnoses = ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Pneumonia', 'Bronchitis', 'Fracture', 'Migraine']
    genders = ['M', 'F', 'Other']
    insurances = ['Medicare', 'Medicaid', 'Private', 'Uninsured']
    
    data = []
    for i in range(1, rows + 1):
        patient_id = f"PAT{i:08d}"
        admission_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))
        treatment_days = random.randint(1, 14)
        discharge_date = admission_date + timedelta(days=treatment_days)
        diagnosis = random.choice(diagnoses)
        age = random.randint(18, 98)
        gender = random.choice(genders)
        cost = round(random.uniform(1000, 50000), 2)
        insurance = random.choice(insurances)
        
        data.append([
            patient_id,
            admission_date.strftime('%Y-%m-%d'),
            discharge_date.strftime('%Y-%m-%d'),
            diagnosis,
            age,
            gender,
            treatment_days,
            cost,
            insurance
        ])
    
    return pd.DataFrame(data, columns=['patient_id', 'admission_date', 'discharge_date', 'diagnosis', 'age', 'gender', 'treatment_days', 'cost', 'insurance'])

def generate_finance_data_df(rows):
    """Generate finance data as DataFrame"""
    import random
    
    types = ['Debit', 'Credit', 'Transfer', 'ATM', 'Payment']
    currencies = ['USD', 'EUR', 'GBP', 'JPY']
    merchants = ['Amazon', 'Walmart', 'Target', 'Starbucks', 'Shell', 'Restaurant', 'Online Store', 'Grocery']
    
    balance = 10000.0
    data = []
    
    for i in range(1, rows + 1):
        txn_id = f"TXN{i:010d}"
        timestamp = (datetime(2024, 1, 1) + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )).isoformat()
        account_id = f"ACC{random.randint(1, 10000):08d}"
        txn_type = random.choice(types)
        amount = round(random.uniform(10, 2000), 2)
        
        if txn_type in ['Debit', 'ATM', 'Payment']:
            balance -= amount
        else:
            balance += amount
        
        currency = random.choice(currencies)
        merchant = random.choice(merchants)
        
        data.append([txn_id, timestamp, account_id, txn_type, amount, round(balance, 2), currency, merchant])
        
        if i % 10000 == 0:
            balance = 10000 + random.uniform(0, 5000)
    
    return pd.DataFrame(data, columns=['transaction_id', 'timestamp', 'account_id', 'transaction_type', 'amount', 'balance', 'currency', 'merchant'])

def calculate_kpis(df, date_col, value_col):
    """Calculate key performance indicators"""
    df_sorted = df.sort_values(date_col)
    
    total = df[value_col].sum()
    mean = df[value_col].mean()
    median = df[value_col].median()
    std = df[value_col].std()
    
    if len(df) > 30:
        recent = df_sorted.tail(30)[value_col].mean()
        previous = df_sorted.head(30)[value_col].mean()
        growth_rate = ((recent - previous) / previous * 100) if previous != 0 else 0
    else:
        growth_rate = 0
    
    return {
        'total': total,
        'mean': mean,
        'median': median,
        'std': std,
        'growth_rate': growth_rate
    }

def moving_average_forecast(series, window=7, periods=30):
    """Simple moving average forecast"""
    ma = series.rolling(window=window).mean()
    last_ma = ma.iloc[-1]
    forecast = [last_ma] * periods
    return forecast

def exponential_smoothing_forecast(series, alpha=0.3, periods=30):
    """Exponential smoothing forecast"""
    result = [series.iloc[0]]
    for i in range(1, len(series)):
        result.append(alpha * series.iloc[i] + (1 - alpha) * result[i-1])
    
    last_value = result[-1]
    forecast = [last_value] * periods
    return forecast

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI BI Dashboard")
    st.title("🤖 AI-Powered BI")
    
    # Gemini API Configuration
    with st.expander("⚙️ Configure Gemini AI", expanded=not st.session_state.gemini_api_key):
        api_key = st.text_input(
            "Enter Gemini API Key",
            type="password",
            value=st.session_state.gemini_api_key if st.session_state.gemini_api_key else "",
            help="Get your API key from https://aistudio.google.com/welcome"
        )
        
        model_choice = st.selectbox(
            "Select AI Model",
            ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
            help="Flash is faster & cheaper, Pro is more capable, 2.0 is experimental"
        )
        
        if st.button("Connect to Gemini AI", type="primary"):
            if api_key:
                with st.spinner(f"Connecting to {model_choice}..."):
                    model = configure_gemini(api_key, model_choice)
                    if model:
                        st.session_state.gemini_api_key = api_key
                        st.session_state.gemini_model = model
                        st.session_state.model_name = model_choice
                        st.success(f"✅ Connected to {model_choice}!")
                        st.rerun()
            else:
                st.error("Please enter an API key")
        
        if st.session_state.gemini_api_key:
            current_model = st.session_state.get('model_name', 'gemini-1.5-flash')
            st.success(f"🤖 AI: Connected ({current_model})")
            if st.button("Disconnect"):
                st.session_state.gemini_api_key = None
                st.session_state.gemini_model = None
                st.session_state.model_name = None
                st.rerun()
    
    st.markdown("---")
    
    page = st.radio(
        "Select Module",
        ["🏠 Home", "📁 Data Upload", "🤖 AI Insights", "💬 AI Chat Assistant",
         "🔍 Exploratory Analysis", "📈 Visualizations", "🔮 AI-Enhanced Forecasting", 
         "📊 Statistical Analysis", "📄 AI Report Generator", "📥 Export"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("AI-powered business intelligence with Google Gemini integration for advanced insights and analysis.")

# Main Content
if page == "🏠 Home":
    st.markdown("<div class='main-header'>🤖 AI-Powered Business Intelligence Dashboard</div>", unsafe_allow_html=True)
    
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Configure Gemini AI in the sidebar to unlock AI-powered features!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🤖 AI-Powered Analysis")
        st.write("Get instant insights, ask questions in natural language, and receive AI-generated recommendations.")
        
    with col2:
        st.markdown("### 📊 Advanced Analytics")
        st.write("Comprehensive exploratory data analysis with automated insights and statistical summaries.")
        
    with col3:
        st.markdown("### 🔮 Smart Forecasting")
        st.write("Generate forecasts with AI interpretation and reliability assessments.")
    
    st.markdown("---")
    
    st.markdown("### 🎯 AI-Enhanced Features")
    
    features = {
        "🤖 AI Insights": "Automatic analysis of your data with actionable recommendations",
        "💬 Chat Assistant": "Ask questions about your data in natural language",
        "📄 Automated Reports": "Generate comprehensive executive reports instantly",
        "🔮 Smart Forecasting": "Forecasts with AI-powered interpretation and risk assessment",
        "📊 Interactive Visualizations": "Time series, correlations, and geographic analysis",
        "📥 Export Capabilities": "Download data and AI-generated reports"
    }
    
    for feature, description in features.items():
        st.markdown(f"**{feature}:** {description}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("👈 **Get Started:** Configure your Gemini API key in the sidebar to enable AI features.")
    
    with col2:
        st.success("💡 **Pro Tip:** Start by uploading your data or using sample data, then explore AI Insights!")

elif page == "📁 Data Upload":
    st.header("📁 Data Upload & Management")
    
    tab1, tab2 = st.tabs(["Upload Data", "Use Sample Data"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Upload your CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a file containing your business data"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.df = df
                st.success(f"✅ File uploaded successfully! Loaded {len(df)} rows and {len(df.columns)} columns.")
                
                st.subheader("Data Preview")
                st.dataframe(df.head(10), width='stretch')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(df))
                with col2:
                    st.metric("Total Columns", len(df.columns))
                with col3:
                    st.metric("Missing Values", df.isnull().sum().sum())
                
                # AI Quick Insights
                if st.session_state.gemini_api_key and st.button("🤖 Get AI Quick Insights", type="primary"):
                    with st.spinner("AI is analyzing your data..."):
                        insights = generate_ai_insights(df)
                        st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
                        st.markdown("### 🤖 AI Insights")
                        st.markdown(insights)
                        st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with tab2:
        st.subheader("Generate Sample Data")
        
        # Initialize session state
        if 'sales_df_sample' not in st.session_state:
            st.session_state.sales_df_sample = None
        if 'healthcare_df_sample' not in st.session_state:
            st.session_state.healthcare_df_sample = None
        if 'finance_df_sample' not in st.session_state:
            st.session_state.finance_df_sample = None
        
        # === SALES DATA ===
        st.markdown("### 💼 Sales Sample Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Sales transactions with products, prices, and regional data")
        with col2:
            sales_rows = st.number_input("Rows", min_value=100, max_value=50000, value=10000, step=1000, key="sales_sample_rows")
        
        if st.button("Generate Sales Data", type="primary", key="gen_sales_sample"):
            with st.spinner("Generating sales data..."):
                st.session_state.sales_df_sample = generate_sales_data_df(sales_rows)
                st.session_state.df = st.session_state.sales_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.sales_df_sample):,} sales records!")
        
        if st.session_state.sales_df_sample is not None:
            st.dataframe(st.session_state.sales_df_sample.head(10), use_container_width=True)
            csv = st.session_state.sales_df_sample.to_csv(index=False)
            st.download_button(
                label="📥 Download Sales CSV",
                data=csv,
                file_name="sales_sample.csv",
                mime="text/csv",
                key="download_sales_sample"
            )
        
        st.markdown("---")
        
        # === HEALTHCARE DATA ===
        st.markdown("### 🏥 Healthcare Sample Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Patient records with diagnoses, treatments, and insurance")
        with col2:
            healthcare_rows = st.number_input("Rows", min_value=100, max_value=100000, value=10000, step=5000, key="healthcare_sample_rows")
        
        if st.button("Generate Healthcare Data", type="primary", key="gen_healthcare_sample"):
            with st.spinner("Generating healthcare data..."):
                st.session_state.healthcare_df_sample = generate_healthcare_data_df(healthcare_rows)
                st.session_state.df = st.session_state.healthcare_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.healthcare_df_sample):,} patient records!")
        
        if st.session_state.healthcare_df_sample is not None:
            st.dataframe(st.session_state.healthcare_df_sample.head(10), use_container_width=True)
            csv = st.session_state.healthcare_df_sample.to_csv(index=False)
            st.download_button(
                label="📥 Download Healthcare CSV",
                data=csv,
                file_name="healthcare_sample.csv",
                mime="text/csv",
                key="download_healthcare_sample"
            )
        
        st.markdown("---")
        
        # === FINANCE DATA ===
        st.markdown("### 💳 Finance Sample Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Financial transactions with accounts, merchants, and balances")
        with col2:
            finance_rows = st.number_input("Rows", min_value=100, max_value=100000, value=10000, step=5000, key="finance_sample_rows")
        
        if st.button("Generate Finance Data", type="primary", key="gen_finance_sample"):
            with st.spinner("Generating finance data..."):
                st.session_state.finance_df_sample = generate_finance_data_df(finance_rows)
                st.session_state.df = st.session_state.finance_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.finance_df_sample):,} transactions!")
        
        if st.session_state.finance_df_sample is not None:
            st.dataframe(st.session_state.finance_df_sample.head(10), use_container_width=True)
            csv = st.session_state.finance_df_sample.to_csv(index=False)
            st.download_button(
                label="📥 Download Finance CSV",
                data=csv,
                file_name="finance_sample.csv",
                mime="text/csv",
                key="download_finance_sample"
            )
        
        st.info("💡 **Tip:** Download these files and place them in `tests/data/` for permanent use")

elif page == "🤖 AI Insights":
    st.header("🤖 AI-Powered Data Insights")
    
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please configure your Gemini API key in the sidebar to use AI features.")
    elif st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        st.markdown("### Automated Analysis")
        st.write("Let AI analyze your data and provide comprehensive insights, patterns, and recommendations.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Comprehensive Overview", "Trends & Patterns", "Anomaly Detection", 
                 "Performance Analysis", "Predictive Insights"]
            )
        
        with col2:
            if st.button("🤖 Generate AI Insights", type="primary", width='stretch'):
                with st.spinner("AI is analyzing your data... This may take a moment."):
                    
                    if analysis_type == "Comprehensive Overview":
                        insights = generate_ai_insights(df)
                    elif analysis_type == "Trends & Patterns":
                        insights = generate_ai_insights(df, "What are the key trends and patterns in this data? Identify any seasonal patterns or cyclical behaviors.")
                    elif analysis_type == "Anomaly Detection":
                        insights = generate_ai_insights(df, "Identify any anomalies, outliers, or unusual patterns in this data. What could be causing them?")
                    elif analysis_type == "Performance Analysis":
                        insights = generate_ai_insights(df, "Analyze the performance metrics in this data. Which areas are performing well and which need improvement?")
                    else:  # Predictive Insights
                        insights = generate_ai_insights(df, "Based on historical patterns, what predictions can you make about future trends? What factors should we monitor?")
                    
                    st.session_state.last_insights = insights
        
        if 'last_insights' in st.session_state:
            st.markdown("---")
            st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
            st.markdown("### 🤖 AI Analysis Results")
            st.markdown(st.session_state.last_insights)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Download insights
            if st.download_button(
                label="📥 Download AI Insights",
                data=st.session_state.last_insights,
                file_name=f"ai_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            ):
                st.success("Insights downloaded!")

elif page == "💬 AI Chat Assistant":
    st.header("💬 AI Chat Assistant")
    
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please configure your Gemini API key in the sidebar to use the chat assistant.")
    elif st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        st.markdown("### Ask questions about your data in natural language")
        st.info("💡 Examples: 'What are the top performing regions?', 'Explain the revenue trends', 'What factors influence customer satisfaction?'")
        
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for i, (role, message) in enumerate(st.session_state.chat_history):
                if role == "user":
                    st.markdown(f"<div class='chat-message user-message'><b>You:</b> {message}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-message ai-message'><b>🤖 AI:</b> {message}</div>", unsafe_allow_html=True)
        
        # Chat input
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_question = st.text_input(
                "Ask a question about your data:",
                key="chat_input",
                placeholder="e.g., What are the revenue trends over time?"
            )
        
        with col2:
            send_button = st.button("Send", type="primary", width='stretch')
        
        if send_button and user_question:
            # Add user message to history
            st.session_state.chat_history.append(("user", user_question))
            
            # Generate AI response
            with st.spinner("🤖 AI is thinking..."):
                response = generate_ai_insights(df, user_question)
                st.session_state.chat_history.append(("ai", response))
            
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

elif page == "🔍 Exploratory Analysis":
    st.header("🔍 Exploratory Data Analysis")
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        tab1, tab2, tab3 = st.tabs(["📋 Data Summary", "🔢 Statistical Analysis", "🧹 Data Quality"])
        
        with tab1:
            st.subheader("Dataset Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Numeric Columns", len(df.select_dtypes(include=[np.number]).columns))
            with col4:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            st.markdown("---")
            
            st.subheader("Column Information")
            
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes.values,
                'Non-Null Count': df.count().values,
                'Null Count': df.isnull().sum().values,
                'Unique Values': [df[col].nunique() for col in df.columns]
            })
            
            st.dataframe(col_info, width='stretch')
            
            st.markdown("---")
            st.subheader("Data Sample")
            st.dataframe(df.head(20), width='stretch')
        
        with tab2:
            st.subheader("Statistical Summary")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                st.dataframe(df[numeric_cols].describe(), width='stretch')
                
                st.markdown("---")
                st.subheader("Distribution Analysis")
                
                selected_col = st.selectbox("Select column for distribution analysis", numeric_cols)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.histogram(df, x=selected_col, nbins=50, 
                                     title=f"Distribution of {selected_col}",
                                     color_discrete_sequence=['#1f77b4'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.box(df, y=selected_col, 
                               title=f"Box Plot of {selected_col}",
                               color_discrete_sequence=['#ff7f0e'])
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns found in the dataset.")
        
        with tab3:
            st.subheader("Data Quality Report")
            
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df) * 100).round(2)
            
            quality_df = pd.DataFrame({
                'Column': df.columns,
                'Missing Values': missing_data.values,
                'Missing %': missing_pct.values,
                'Data Type': df.dtypes.values
            })
            
            quality_df = quality_df[quality_df['Missing Values'] > 0].sort_values('Missing Values', ascending=False)
            
            if len(quality_df) > 0:
                st.warning(f"Found {len(quality_df)} columns with missing values")
                st.dataframe(quality_df, width='stretch')
                
                fig = px.bar(quality_df, x='Column', y='Missing %',
                           title="Missing Values by Column (%)",
                           color='Missing %',
                           color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No missing values detected in the dataset!")
            
            duplicates = df.duplicated().sum()
            st.metric("Duplicate Rows", duplicates)
            
            if duplicates > 0:
                st.warning(f"Found {duplicates} duplicate rows in the dataset")

elif page == "📈 Visualizations":
    st.header("📈 Interactive Visualizations")
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        viz_type = st.selectbox(
            "Select Visualization Type",
            ["Time Series Analysis", "Category Analysis", "Correlation Analysis", "Geographic Analysis"]
        )
        
        if viz_type == "Time Series Analysis":
            date_cols = [col for col in df.columns if 'date' in col.lower() or df[col].dtype == 'datetime64[ns]']
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if date_cols and numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    date_col = st.selectbox("Select Date Column", date_cols)
                with col2:
                    value_col = st.selectbox("Select Value Column", numeric_cols)
                
                df[date_col] = pd.to_datetime(df[date_col])
                df_sorted = df.sort_values(date_col)
                
                fig = px.line(df_sorted, x=date_col, y=value_col,
                            title=f"{value_col} Over Time",
                            labels={date_col: "Date", value_col: "Value"})
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                kpis = calculate_kpis(df_sorted, date_col, value_col)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total", f"{kpis['total']:,.2f}")
                with col2:
                    st.metric("Average", f"{kpis['mean']:,.2f}")
                with col3:
                    st.metric("Std Dev", f"{kpis['std']:,.2f}")
                with col4:
                    st.metric("Growth Rate", f"{kpis['growth_rate']:,.2f}%")
                
            else:
                st.info("Please ensure your dataset has date and numeric columns for time series analysis.")
        
        elif viz_type == "Category Analysis":
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if categorical_cols and numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    cat_col = st.selectbox("Select Category Column", categorical_cols)
                with col2:
                    val_col = st.selectbox("Select Value Column", numeric_cols)
                
                grouped = df.groupby(cat_col)[val_col].sum().reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(grouped, x=cat_col, y=val_col,
                               title=f"{val_col} by {cat_col}",
                               color=val_col,
                               color_continuous_scale='Blues')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.pie(grouped, values=val_col, names=cat_col,
                               title=f"{val_col} Distribution by {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please ensure your dataset has both categorical and numeric columns.")
        
        elif viz_type == "Correlation Analysis":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                
                fig = px.imshow(corr_matrix,
                              labels=dict(color="Correlation"),
                              x=numeric_cols,
                              y=numeric_cols,
                              color_continuous_scale='RdBu_r',
                              aspect="auto",
                              title="Correlation Heatmap")
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Strongest Correlations")
                
                corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_pairs.append({
                            'Variable 1': corr_matrix.columns[i],
                            'Variable 2': corr_matrix.columns[j],
                            'Correlation': corr_matrix.iloc[i, j]
                        })
                
                corr_df = pd.DataFrame(corr_pairs).sort_values('Correlation', key=abs, ascending=False).head(10)
                st.dataframe(corr_df, width='stretch')
            else:
                st.info("Need at least 2 numeric columns for correlation analysis.")
        
        elif viz_type == "Geographic Analysis":
            if 'Region' in df.columns or 'region' in df.columns:
                region_col = 'Region' if 'Region' in df.columns else 'region'
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    value_col = st.selectbox("Select Value Column", numeric_cols)
                    
                    grouped = df.groupby(region_col)[value_col].agg(['sum', 'mean', 'count']).reset_index()
                    
                    fig = px.bar(grouped, x=region_col, y='sum',
                               title=f"Total {value_col} by Region",
                               color='sum',
                               color_continuous_scale='Viridis')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(grouped, width='stretch')
                else:
                    st.info("No numeric columns available for geographic analysis.")
            else:
                st.info("No geographic/region column found in the dataset.")

elif page == "🔮 AI-Enhanced Forecasting":
    st.header("🔮 AI-Enhanced Time Series Forecasting")
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        date_cols = [col for col in df.columns if 'date' in col.lower() or df[col].dtype == 'datetime64[ns]']
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if date_cols and numeric_cols:
            col1, col2 = st.columns(2)
            with col1:
                date_col = st.selectbox("Select Date Column", date_cols, key="forecast_date_col")
            with col2:
                value_col = st.selectbox("Select Value Column to Forecast", numeric_cols, key="forecast_value_col")
            
            df[date_col] = pd.to_datetime(df[date_col])
            df_sorted = df.sort_values(date_col).copy()
            
            st.subheader("Forecast Parameters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                forecast_periods = st.slider("Forecast Periods", 7, 90, 30, key="forecast_periods")
            with col2:
                ma_window = st.slider("Moving Average Window", 3, 30, 7, key="ma_window")
            with col3:
                es_alpha = st.slider("Smoothing Factor (α)", 0.1, 0.9, 0.3, 0.1, key="es_alpha")
            
            if st.button("Generate Forecast", type="primary"):
                ts_data = df_sorted.groupby(date_col)[value_col].mean().reset_index()
                
                ma_forecast = moving_average_forecast(ts_data[value_col], window=ma_window, periods=forecast_periods)
                es_forecast = exponential_smoothing_forecast(ts_data[value_col], alpha=es_alpha, periods=forecast_periods)
                
                last_date = ts_data[date_col].max()
                future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_periods, freq='D')
                
                forecast_df = pd.DataFrame({
                    'Date': future_dates,
                    'Moving Average': ma_forecast,
                    'Exponential Smoothing': es_forecast
                })
                
                # Store forecast data in session state
                st.session_state.forecast_data = {
                    'ts_data': ts_data,
                    'ma_forecast': ma_forecast,
                    'es_forecast': es_forecast,
                    'forecast_df': forecast_df,
                    'date_col': date_col,
                    'value_col': value_col,
                    'ma_window': ma_window,
                    'es_alpha': es_alpha
                }
            
            # Display forecast if it exists in session state
            if 'forecast_data' in st.session_state:
                fdata = st.session_state.forecast_data
                
                # Plotting
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=fdata['ts_data'][fdata['date_col']],
                    y=fdata['ts_data'][fdata['value_col']],
                    mode='lines',
                    name='Historical Data',
                    line=dict(color='blue', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=fdata['forecast_df']['Date'],
                    y=fdata['forecast_df']['Moving Average'],
                    mode='lines',
                    name=f'MA Forecast (window={fdata["ma_window"]})',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=fdata['forecast_df']['Date'],
                    y=fdata['forecast_df']['Exponential Smoothing'],
                    mode='lines',
                    name=f'ES Forecast (α={fdata["es_alpha"]})',
                    line=dict(color='green', width=2, dash='dot')
                ))
                
                fig.update_layout(
                    title=f"{fdata['value_col']} Forecast",
                    xaxis_title="Date",
                    yaxis_title=fdata['value_col'],
                    height=600,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Forecast summary
                st.subheader("Forecast Summary")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Moving Average Forecast**")
                    st.metric("Average Forecast", f"{np.mean(fdata['ma_forecast']):,.2f}")
                    st.metric("Min Forecast", f"{np.min(fdata['ma_forecast']):,.2f}")
                    st.metric("Max Forecast", f"{np.max(fdata['ma_forecast']):,.2f}")
                
                with col2:
                    st.markdown("**Exponential Smoothing Forecast**")
                    st.metric("Average Forecast", f"{np.mean(fdata['es_forecast']):,.2f}")
                    st.metric("Min Forecast", f"{np.min(fdata['es_forecast']):,.2f}")
                    st.metric("Max Forecast", f"{np.max(fdata['es_forecast']):,.2f}")
                
                # AI Interpretation
                if st.session_state.gemini_api_key:
                    st.markdown("---")
                    st.subheader("🤖 AI Forecast Interpretation")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Interpret Moving Average Forecast", width='stretch', key="interpret_ma"):
                            with st.spinner("AI is analyzing the forecast..."):
                                try:
                                    interpretation = interpret_forecast(fdata['ts_data'][fdata['value_col']], fdata['ma_forecast'], "Moving Average")
                                    st.session_state.ma_interpretation = interpretation
                                except Exception as e:
                                    st.error(f"Error generating interpretation: {str(e)}")
                        
                        # Display interpretation if it exists
                        if 'ma_interpretation' in st.session_state:
                            st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
                            st.markdown(st.session_state.ma_interpretation)
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("Interpret Exponential Smoothing Forecast", width='stretch', key="interpret_es"):
                            with st.spinner("AI is analyzing the forecast..."):
                                try:
                                    interpretation = interpret_forecast(fdata['ts_data'][fdata['value_col']], fdata['es_forecast'], "Exponential Smoothing")
                                    st.session_state.es_interpretation = interpretation
                                except Exception as e:
                                    st.error(f"Error generating interpretation: {str(e)}")
                        
                        # Display interpretation if it exists
                        if 'es_interpretation' in st.session_state:
                            st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
                            st.markdown(st.session_state.es_interpretation)
                            st.markdown("</div>", unsafe_allow_html=True)
                
                # Display forecast table
                st.subheader("Forecast Data")
                st.dataframe(fdata['forecast_df'], width='stretch')
                
                # Clear forecast button
                st.markdown("---")
                if st.button("🗑️ Clear Forecast", type="secondary", help="Remove forecast and interpretations"):
                    if 'forecast_data' in st.session_state:
                        del st.session_state.forecast_data
                    if 'ma_interpretation' in st.session_state:
                        del st.session_state.ma_interpretation
                    if 'es_interpretation' in st.session_state:
                        del st.session_state.es_interpretation
                    st.rerun()
                
        else:
            st.info("Please ensure your dataset has both date and numeric columns for forecasting.")

elif page == "📊 Statistical Analysis":
    st.header("📊 Statistical Analysis")
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Descriptive Statistics", "Trend Analysis", "Outlier Detection"]
        )
        
        if analysis_type == "Descriptive Statistics":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                selected_cols = st.multiselect("Select columns for analysis", numeric_cols, default=numeric_cols[:3])
                
                if selected_cols:
                    stats_df = df[selected_cols].describe().T
                    stats_df['variance'] = df[selected_cols].var()
                    stats_df['skewness'] = df[selected_cols].skew()
                    stats_df['kurtosis'] = df[selected_cols].kurtosis()
                    
                    st.dataframe(stats_df, width='stretch')
                    
                    for col in selected_cols:
                        fig = px.histogram(df, x=col, marginal="box",
                                         title=f"Distribution of {col}",
                                         color_discrete_sequence=['#636EFA'])
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns found for statistical analysis.")
        
        elif analysis_type == "Trend Analysis":
            date_cols = [col for col in df.columns if 'date' in col.lower() or df[col].dtype == 'datetime64[ns]']
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if date_cols and numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    date_col = st.selectbox("Select Date Column", date_cols)
                with col2:
                    value_col = st.selectbox("Select Value Column", numeric_cols)
                
                df[date_col] = pd.to_datetime(df[date_col])
                df_sorted = df.sort_values(date_col)
                
                df_sorted['Rolling_Mean'] = df_sorted[value_col].rolling(window=7).mean()
                df_sorted['Rolling_Std'] = df_sorted[value_col].rolling(window=7).std()
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_sorted[date_col],
                    y=df_sorted[value_col],
                    mode='lines',
                    name='Original',
                    line=dict(color='lightblue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_sorted[date_col],
                    y=df_sorted['Rolling_Mean'],
                    mode='lines',
                    name='7-Day Moving Average',
                    line=dict(color='red', width=2)
                ))
                
                fig.update_layout(
                    title=f"Trend Analysis: {value_col}",
                    xaxis_title="Date",
                    yaxis_title=value_col,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                recent_avg = df_sorted[value_col].tail(30).mean()
                overall_avg = df_sorted[value_col].mean()
                trend = ((recent_avg - overall_avg) / overall_avg * 100)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Average", f"{overall_avg:,.2f}")
                with col2:
                    st.metric("Recent Average (30 days)", f"{recent_avg:,.2f}")
                with col3:
                    st.metric("Trend", f"{trend:+.2f}%", delta=f"{trend:.2f}%")
            else:
                st.info("Need date and numeric columns for trend analysis.")
        
        elif analysis_type == "Outlier Detection":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                selected_col = st.selectbox("Select column for outlier detection", numeric_cols)
                
                Q1 = df[selected_col].quantile(0.25)
                Q3 = df[selected_col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]
                
                st.subheader("Outlier Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Outliers", len(outliers))
                with col2:
                    st.metric("Lower Bound", f"{lower_bound:.2f}")
                with col3:
                    st.metric("Upper Bound", f"{upper_bound:.2f}")
                with col4:
                    st.metric("Outlier %", f"{len(outliers)/len(df)*100:.2f}%")
                
                fig = px.box(df, y=selected_col, title=f"Box Plot with Outliers: {selected_col}",
                           points="outliers")
                st.plotly_chart(fig, use_container_width=True)
                
                if len(outliers) > 0:
                    st.subheader("Outlier Data")
                    st.dataframe(outliers, width='stretch')
            else:
                st.info("No numeric columns found for outlier detection.")

elif page == "📄 AI Report Generator":
    st.header("📄 AI-Powered Report Generator")
    
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please configure your Gemini API key in the sidebar to generate AI reports.")
    elif st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        st.markdown("### Generate Comprehensive Business Intelligence Reports")
        st.write("AI will analyze your data and create a professional executive report with insights, recommendations, and action items.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_type = st.selectbox(
                "Report Type",
                ["Executive Summary", "Detailed Analysis", "Performance Review", "Strategic Insights"]
            )
        
        with col2:
            include_charts = st.checkbox("Include Key Metrics", value=True)
        
        with col3:
            if st.button("🤖 Generate AI Report", type="primary", width='stretch'):
                with st.spinner("AI is generating your comprehensive report... This may take a minute."):
                    report = generate_automated_report(df)
                    st.session_state.generated_report = report
        
        if 'generated_report' in st.session_state:
            st.markdown("---")
            
            # Display report
            st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
            st.markdown("### 📄 Generated Report")
            st.markdown(st.session_state.generated_report)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Show key metrics if requested
            if include_charts:
                st.markdown("---")
                st.subheader("📊 Key Metrics Dashboard")
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if len(numeric_cols) >= 1:
                    cols = st.columns(min(4, len(numeric_cols)))
                    for idx, col_name in enumerate(numeric_cols[:4]):
                        with cols[idx]:
                            st.metric(
                                col_name,
                                f"{df[col_name].mean():,.2f}",
                                delta=f"{df[col_name].std():.2f} σ"
                            )
            
            # Download report
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=st.session_state.generated_report,
                    file_name=f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    width='stretch'
                )
            
            with col2:
                # Create formatted report with metrics
                full_report = f"""
AI-POWERED BUSINESS INTELLIGENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================

{st.session_state.generated_report}

========================================
DATASET STATISTICS
========================================
Total Records: {len(df)}
Total Columns: {len(df.columns)}
Date Range: {df.iloc[:, 0].min() if len(df) > 0 else 'N/A'} to {df.iloc[:, 0].max() if len(df) > 0 else 'N/A'}

Generated by AI-Powered BI Dashboard
"""
                st.download_button(
                    label="📥 Download Full Report (TXT)",
                    data=full_report,
                    file_name=f"full_ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    width='stretch'
                )

elif page == "📥 Export":
    st.header("📥 Export Data & Reports")
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data or generate sample data first!")
    else:
        df = st.session_state.df
        
        st.subheader("Export Options")
        
        export_type = st.radio("Select export format", ["CSV", "Excel", "JSON"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if export_type == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary"
                )
            
            elif export_type == "Excel":
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                
                st.download_button(
                    label="📥 Download as Excel",
                    data=buffer.getvalue(),
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            
            elif export_type == "JSON":
                json_str = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_str,
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    type="primary"
                )
        
        with col2:
            st.info(f"Current dataset: {len(df)} rows × {len(df.columns)} columns")
        
        st.markdown("---")
        st.subheader("Data Preview")
        st.dataframe(df.head(10), width='stretch')

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🤖 AI-Powered Business Intelligence Dashboard | Built with Streamlit & Google Gemini | © 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)



