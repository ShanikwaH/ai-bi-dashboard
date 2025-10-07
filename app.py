import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import google.generativeai as genai
import json
import os
import sys
import traceback
from streamlit.components.v1 import html

# Optional: Load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is not required to run the app

# Configure error handling
def handle_error(e: Exception):
    """Handle exceptions and display user-friendly error messages"""
    error_msg = str(e)
    if "connection" in error_msg.lower():
        st.error("❌ Connection error. Please check your internet connection.")
    elif "permission" in error_msg.lower():
        st.error("❌ Permission denied. Please check your API key and permissions.")
    elif "not found" in error_msg.lower():
        st.error("❌ Resource not found. Please check your file paths and configurations.")
    else:
        st.error(f"❌ An error occurred: {error_msg}")
    
    if os.getenv('STREAMLIT_DEBUG', '').lower() == 'true':
        st.code(traceback.format_exc())

# Startup health check
try:
    # Verify critical packages
    import streamlit
    import pandas
    import plotly
    import google.generativeai
except ImportError as e:
    st.error(f"❌ Required package not found: {str(e)}")
    st.info("Please check requirements.txt and reinstall dependencies.")
    sys.exit(1)

# Page configuration
st.set_page_config(
    page_title="AI-Powered Business Intelligence Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    # Try to get API key from environment variables
    st.session_state.gemini_api_key = os.getenv('GEMINI_API_KEY')
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None
if 'model_name' not in st.session_state:
    st.session_state.model_name = 'gemini-1.5-flash'  # Set default model
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to get client's local time
def get_client_time():
    """Get the client's local time using JavaScript"""
    js_code = """
    <script>
    const now = new Date();
    const timestamp = now.toISOString();
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const localDatetime = now.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
    
    // Send data to Streamlit
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        timestamp: timestamp,
        timezone: timezone,
        localDatetime: localDatetime
    }, '*');
    </script>
    """
    return js_code

# Configure Gemini AI
def configure_gemini(api_key, model_name='gemini-1.5-flash'):
    """Configure Gemini AI with API key"""
    if not api_key:
        st.error("🔑 Please provide a Gemini API key.")
        st.info("Set GEMINI_API_KEY in:\n- Local: .env file\n- Streamlit Cloud: Secrets management")
        return None

    try:
        # Clean the API key (remove any whitespace)
        api_key = api_key.strip()
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Validate API key format
        if len(api_key) < 20:  # Basic validation
            st.error("🔑 Invalid API key format. Please check your key.")
            return None
            
        # Initialize model with error handling
        try:
            model = genai.GenerativeModel(model_name)
        except Exception as e:
            st.error(f"❌ Error initializing model: {str(e)}")
            st.info(f"Make sure '{model_name}' is a valid model name.")
            return None
        
        # Test the connection with a timeout
        try:
            test = model.generate_content("Test connection")
            st.success("✅ Successfully connected to Gemini AI")
            return model
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg:
                st.error("💰 API quota exceeded. Please check your billing settings.")
            elif "permission" in error_msg or "unauthorized" in error_msg:
                st.error("🚫 API key doesn't have proper permissions.")
                st.info("Please verify your API key and ensure it has the necessary permissions.")
            elif "timeout" in error_msg:
                st.error("⏱️ Connection timeout. Please try again.")
                st.info("This might be a temporary issue with the Gemini AI service.")
            else:
                st.error(f"❌ Error testing connection: {str(e)}")
            
            st.info("Troubleshooting steps:\n"
                   "1. Verify API key is correct\n"
                   "2. Check billing is enabled\n"
                   "3. Ensure you're using a supported model\n"
                   "4. Check your internet connection")
            return None
            
    except Exception as e:
        handle_error(e)  # Use our central error handler
        return None

# Generate AI insights
def generate_ai_insights(df, question=None):
    """Generate insights using Gemini AI"""
    if df is None:
        return "Please upload a dataset first."
        
    if st.session_state.gemini_model is None:
        return "Please configure Gemini API key first."
    
    try:
        if df.empty:
            return "The uploaded dataset is empty. Please check your data."
            
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


def generate_industry_agnostic_data_df(rows):
    """Generate industry-agnostic business data as DataFrame - complex and messy"""
    import random
    
    departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations', 'Customer Service', 'R&D', 'Legal', 'Logistics']
    statuses = ['Active', 'Pending', 'Completed', 'Cancelled', 'On Hold', 'In Progress', 'Review', 'Approved', None, 'ACTIVE', 'active']
    priorities = ['High', 'Medium', 'Low', 'Critical', 'Normal', None, 'HIGH', 'high']
    categories = ['Project', 'Task', 'Initiative', 'Request', 'Issue', 'Improvement', 'Maintenance', None]
    locations = ['New York', 'London', 'Tokyo', 'Singapore', 'Sydney', 'Toronto', 'Berlin', 'Paris', 'Mumbai', 'São Paulo', None, 'NYC', 'N/A']
    
    data = []
    base_date = datetime(2020, 1, 1)
    
    for i in range(1, min(rows + 1, 1000001)):  # Cap at 1,000,000
        record_id = f"REC{i:010d}"
        
        # Introduce messy dates
        if random.random() < 0.05:  # 5% null dates
            created_date = None
            updated_date = None
        else:
            created_date = (base_date + timedelta(days=random.randint(0, 1825))).strftime('%Y-%m-%d')
            days_later = random.randint(0, 365)
            updated_date = (datetime.strptime(created_date, '%Y-%m-%d') + timedelta(days=days_later)).strftime('%Y-%m-%d')
        
        department = random.choice(departments)
        status = random.choice(statuses)
        priority = random.choice(priorities)
        category = random.choice(categories)
        location = random.choice(locations)
        
        # Messy numeric data with nulls and inconsistencies
        budget = round(random.uniform(1000, 500000), 2) if random.random() > 0.08 else None
        actual_cost = round(random.uniform(500, 600000), 2) if random.random() > 0.1 else None
        
        # Messy percentage data
        completion_pct = round(random.uniform(0, 100), 1) if random.random() > 0.07 else None
        
        # Messy employee counts
        team_size = random.randint(1, 50) if random.random() > 0.06 else None
        
        # Rating with inconsistencies
        rating = round(random.uniform(1, 5), 1) if random.random() > 0.12 else None
        
        # Messy text fields
        notes = random.choice([
            'Follow up needed',
            'Waiting for approval',
            'In progress - see attached',
            '',
            None,
            'TBD',
            'N/A',
            'Contact John for details',
            'URGENT!!!',
            'na'
        ])
        
        # Owner field with inconsistencies
        owner = random.choice([
            f'user{random.randint(1, 500)}@company.com',
            f'User {random.randint(1, 500)}',
            None,
            'TBD',
            'Unassigned',
            '',
            'N/A'
        ])
        
        data.append([
            record_id, created_date, updated_date, department, category, 
            status, priority, location, budget, actual_cost, 
            completion_pct, team_size, rating, owner, notes
        ])
        
        # Add some duplicate records (2% chance)
        if random.random() < 0.02 and i > 100:
            data.append(data[-1])
    
    df = pd.DataFrame(data, columns=[
        'record_id', 'created_date', 'updated_date', 'department', 'category',
        'status', 'priority', 'location', 'budget', 'actual_cost',
        'completion_percentage', 'team_size', 'rating', 'owner', 'notes'
    ])
    
    return df

def generate_manufacturing_data_df(rows):
    """Generate manufacturing operations data as DataFrame - complex and messy"""
    import random
    
    plants = ['Plant A', 'Plant B', 'Plant C', 'Plant D', 'Plant E', None, 'PLANT A', 'plant_a']
    production_lines = ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6', None]
    product_types = ['Widget-A', 'Widget-B', 'Gadget-X', 'Component-12', 'Assembly-Z', 'Part-456', None]
    shifts = ['Day', 'Night', 'Evening', 'DAY', 'day', None, 'Swing']
    quality_statuses = ['Pass', 'Fail', 'Pending', 'Rework', 'Scrap', None, 'PASS', 'pass']
    machine_statuses = ['Running', 'Idle', 'Maintenance', 'Breakdown', 'Setup', None, 'RUNNING']
    suppliers = ['Supplier-A', 'Supplier-B', 'Supplier-C', 'Supplier-D', 'Supplier-E', None, 'TBD']
    
    data = []
    base_date = datetime(2022, 1, 1)
    
    for i in range(1, min(rows + 1, 1000001)):  # Cap at 1,000,000
        batch_id = f"BATCH{i:012d}"
        
        # Messy timestamps
        if random.random() < 0.04:
            production_date = None
            start_time = None
            end_time = None
        else:
            production_date = (base_date + timedelta(days=random.randint(0, 1095))).strftime('%Y-%m-%d')
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            start_time = f"{hour:02d}:{minute:02d}:00"
            duration = random.randint(30, 480)  # 30 min to 8 hours
            end_hour = (hour + duration // 60) % 24
            end_minute = (minute + duration % 60) % 60
            end_time = f"{end_hour:02d}:{end_minute:02d}:00"
        
        plant = random.choice(plants)
        line = random.choice(production_lines)
        product = random.choice(product_types)
        shift = random.choice(shifts)
        
        # Messy production quantities
        planned_qty = random.randint(100, 10000) if random.random() > 0.05 else None
        actual_qty = random.randint(50, 10000) if random.random() > 0.06 else None
        defect_qty = random.randint(0, 500) if random.random() > 0.08 else None
        
        # Calculate yield with inconsistencies
        if actual_qty and planned_qty and planned_qty > 0:
            yield_pct = round((actual_qty / planned_qty) * 100, 2)
            # Add some data errors
            if random.random() < 0.03:
                yield_pct = round(random.uniform(100, 150), 2)  # Impossible yield
        else:
            yield_pct = None
        
        quality_status = random.choice(quality_statuses)
        machine_status = random.choice(machine_statuses)
        
        # Messy machine metrics
        machine_id = f"MCH{random.randint(1, 200):04d}" if random.random() > 0.04 else None
        downtime_mins = random.randint(0, 480) if random.random() > 0.1 else None
        temperature = round(random.uniform(15, 95), 1) if random.random() > 0.09 else None
        pressure = round(random.uniform(50, 300), 1) if random.random() > 0.09 else None
        
        # Cost data with inconsistencies
        material_cost = round(random.uniform(100, 50000), 2) if random.random() > 0.07 else None
        labor_cost = round(random.uniform(50, 5000), 2) if random.random() > 0.08 else None
        
        supplier = random.choice(suppliers)
        
        # Messy operator data
        operator_id = f"OPR{random.randint(1, 500):05d}" if random.random() > 0.06 else None
        
        # Notes with inconsistencies
        notes = random.choice([
            'Normal operation',
            'Machine calibration needed',
            'Quality issues detected',
            '',
            None,
            'TBD',
            'SEE SUPERVISOR',
            'Material shortage',
            'na',
            'N/A'
        ])
        
        data.append([
            batch_id, production_date, start_time, end_time, plant, line,
            product, shift, planned_qty, actual_qty, defect_qty, yield_pct,
            quality_status, machine_id, machine_status, downtime_mins,
            temperature, pressure, material_cost, labor_cost, supplier,
            operator_id, notes
        ])
        
        # Add duplicate records (1.5% chance)
        if random.random() < 0.015 and i > 100:
            data.append(data[-1])
    
    df = pd.DataFrame(data, columns=[
        'batch_id', 'production_date', 'start_time', 'end_time', 'plant', 'production_line',
        'product_type', 'shift', 'planned_quantity', 'actual_quantity', 'defect_quantity', 'yield_percentage',
        'quality_status', 'machine_id', 'machine_status', 'downtime_minutes',
        'temperature_celsius', 'pressure_psi', 'material_cost', 'labor_cost', 'supplier',
        'operator_id', 'notes'
    ])
    
    return df

def generate_operations_data_df(rows):
    """Generate operations/logistics data as DataFrame - complex and messy"""
    import random
    
    warehouses = ['WH-North', 'WH-South', 'WH-East', 'WH-West', 'WH-Central', None, 'WH-NORTH', 'wh_north']
    carriers = ['FedEx', 'UPS', 'DHL', 'USPS', 'Local Courier', None, 'TBD', 'fedex']
    shipment_types = ['Standard', 'Express', 'Overnight', 'Economy', 'Priority', None, 'STANDARD']
    statuses = ['Delivered', 'In Transit', 'Pending', 'Delayed', 'Cancelled', 'Lost', 'Returned', None, 'DELIVERED']
    regions = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West Coast', 'International', None]
    order_types = ['B2B', 'B2C', 'Internal', 'Return', 'Exchange', None, 'b2b']
    
    data = []
    base_date = datetime(2021, 1, 1)
    
    for i in range(1, min(rows + 1, 1000001)):  # Cap at 1,000,000
        order_id = f"ORD{i:012d}"
        shipment_id = f"SHIP{i:012d}" if random.random() > 0.05 else None
        tracking_num = f"TRK{random.randint(1000000000, 9999999999)}" if random.random() > 0.08 else None
        
        # Messy dates
        if random.random() < 0.04:
            order_date = None
            ship_date = None
            delivery_date = None
        else:
            order_date = (base_date + timedelta(days=random.randint(0, 1460))).strftime('%Y-%m-%d')
            ship_delay = random.randint(0, 14)
            ship_date = (datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=ship_delay)).strftime('%Y-%m-%d')
            
            # Delivery date (sometimes before ship date - data error)
            if random.random() < 0.02:
                delivery_delay = random.randint(-5, 0)  # Data error: delivered before shipped
            else:
                delivery_delay = random.randint(1, 21)
            
            if random.random() > 0.15:  # 15% no delivery date yet
                delivery_date = (datetime.strptime(ship_date, '%Y-%m-%d') + timedelta(days=delivery_delay)).strftime('%Y-%m-%d')
            else:
                delivery_date = None
        
        warehouse = random.choice(warehouses)
        carrier = random.choice(carriers)
        shipment_type = random.choice(shipment_types)
        status = random.choice(statuses)
        region = random.choice(regions)
        order_type = random.choice(order_types)
        
        # Messy package metrics
        weight_kg = round(random.uniform(0.1, 500), 2) if random.random() > 0.06 else None
        
        # Dimension inconsistencies
        length_cm = round(random.uniform(5, 200), 1) if random.random() > 0.07 else None
        width_cm = round(random.uniform(5, 150), 1) if random.random() > 0.07 else None
        height_cm = round(random.uniform(5, 150), 1) if random.random() > 0.07 else None
        
        # Calculate volume with potential errors
        if length_cm and width_cm and height_cm:
            volume_cm3 = round(length_cm * width_cm * height_cm, 2)
        else:
            volume_cm3 = None
        
        # Quantity data
        items_count = random.randint(1, 100) if random.random() > 0.05 else None
        
        # Cost data with inconsistencies
        shipping_cost = round(random.uniform(5, 500), 2) if random.random() > 0.08 else None
        insurance_cost = round(random.uniform(0, 100), 2) if random.random() > 0.12 else None
        
        # Distance
        distance_km = round(random.uniform(10, 15000), 1) if random.random() > 0.1 else None
        
        # Customer data
        customer_id = f"CUST{random.randint(1, 50000):08d}" if random.random() > 0.04 else None
        
        # Destination
        destination_zip = f"{random.randint(10000, 99999)}" if random.random() > 0.06 else None
        
        # Priority with inconsistencies
        priority = random.choice(['High', 'Medium', 'Low', 'Critical', None, 'HIGH', 'high'])
        
        # Delivery attempts
        delivery_attempts = random.randint(1, 5) if random.random() > 0.15 else None
        
        # Damaged flag with inconsistencies
        is_damaged = random.choice([True, False, None, 'Yes', 'No', 'TRUE', 'false', 1, 0])
        
        # Notes
        notes = random.choice([
            'Standard delivery',
            'Customer not home',
            'Left at door',
            'Signature required',
            '',
            None,
            'URGENT',
            'Handle with care',
            'na',
            'N/A',
            'See tracking for details'
        ])
        
        data.append([
            order_id, shipment_id, tracking_num, order_date, ship_date, delivery_date,
            warehouse, carrier, shipment_type, status, region, order_type,
            weight_kg, length_cm, width_cm, height_cm, volume_cm3, items_count,
            shipping_cost, insurance_cost, distance_km, customer_id, destination_zip,
            priority, delivery_attempts, is_damaged, notes
        ])
        
        # Add duplicate records (1% chance)
        if random.random() < 0.01 and i > 100:
            data.append(data[-1])
    
    df = pd.DataFrame(data, columns=[
        'order_id', 'shipment_id', 'tracking_number', 'order_date', 'ship_date', 'delivery_date',
        'warehouse', 'carrier', 'shipment_type', 'status', 'region', 'order_type',
        'weight_kg', 'length_cm', 'width_cm', 'height_cm', 'volume_cm3', 'items_count',
        'shipping_cost', 'insurance_cost', 'distance_km', 'customer_id', 'destination_zip',
        'priority', 'delivery_attempts', 'is_damaged', 'notes'
    ])
    
    return df

def generate_government_data_df(rows):
    """Generate government/public sector data as DataFrame - complex and messy"""
    import random
    
    departments = ['Public Works', 'Education', 'Health Services', 'Transportation', 'Parks & Recreation', 
                   'Public Safety', 'Housing', 'Environmental', 'Finance', 'Administration', None, 'PUBLIC WORKS']
    request_types = ['Service Request', 'Permit', 'License', 'Complaint', 'Information', 'Inspection',
                     'Violation', 'Application', None, 'SERVICE REQUEST']
    statuses = ['Open', 'Closed', 'In Progress', 'Pending', 'Approved', 'Denied', 'On Hold', 
                'Under Review', None, 'CLOSED', 'closed']
    priorities = ['High', 'Medium', 'Low', 'Emergency', 'Routine', None, 'HIGH', 'high']
    channels = ['Online', 'Phone', 'In-Person', 'Email', 'Mail', 'Mobile App', None, 'ONLINE']
    districts = ['District 1', 'District 2', 'District 3', 'District 4', 'District 5', 
                 'District 6', None, 'DISTRICT 1', 'Dist-1']
    categories = ['Infrastructure', 'Environmental', 'Public Safety', 'Administrative', 
                  'Health', 'Education', 'Housing', None]
    
    data = []
    base_date = datetime(2019, 1, 1)
    
    for i in range(1, min(rows + 1, 1000001)):  # Cap at 1,000,000
        case_id = f"CASE{i:012d}"
        reference_num = f"REF{random.randint(100000000, 999999999)}" if random.random() > 0.06 else None
        
        # Messy dates
        if random.random() < 0.05:
            submitted_date = None
            assigned_date = None
            resolved_date = None
        else:
            submitted_date = (base_date + timedelta(days=random.randint(0, 2190))).strftime('%Y-%m-%d')
            
            if random.random() > 0.1:
                assign_delay = random.randint(0, 30)
                assigned_date = (datetime.strptime(submitted_date, '%Y-%m-%d') + timedelta(days=assign_delay)).strftime('%Y-%m-%d')
            else:
                assigned_date = None
            
            if random.random() > 0.25:  # 25% still open
                if assigned_date:
                    resolve_delay = random.randint(1, 365)
                    resolved_date = (datetime.strptime(assigned_date, '%Y-%m-%d') + timedelta(days=resolve_delay)).strftime('%Y-%m-%d')
                else:
                    resolved_date = None
            else:
                resolved_date = None
        
        department = random.choice(departments)
        request_type = random.choice(request_types)
        status = random.choice(statuses)
        priority = random.choice(priorities)
        channel = random.choice(channels)
        district = random.choice(districts)
        category = random.choice(categories)
        
        # Messy location data
        address = f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Park', 'Elm', 'Maple'])} {random.choice(['St', 'Ave', 'Blvd', 'Rd', 'Dr'])}" if random.random() > 0.08 else None
        zip_code = f"{random.randint(10000, 99999)}" if random.random() > 0.07 else None
        
        # GPS coordinates with inconsistencies
        latitude = round(random.uniform(25.0, 49.0), 6) if random.random() > 0.12 else None
        longitude = round(random.uniform(-125.0, -65.0), 6) if random.random() > 0.12 else None
        
        # Citizen data
        citizen_id = f"CIT{random.randint(1, 500000):010d}" if random.random() > 0.1 else None
        
        # Staff assignment
        assigned_to = random.choice([
            f'staff{random.randint(1, 200)}@gov.local',
            f'Employee {random.randint(1, 200)}',
            None,
            'Unassigned',
            'TBD',
            ''
        ])
        
        # Response time in hours with outliers
        if submitted_date and resolved_date:
            days_diff = (datetime.strptime(resolved_date, '%Y-%m-%d') - 
                        datetime.strptime(submitted_date, '%Y-%m-%d')).days
            response_time_hrs = days_diff * 24 + random.randint(0, 23)
            # Add some outliers
            if random.random() < 0.02:
                response_time_hrs = random.randint(-100, 0)  # Negative time - data error
        else:
            response_time_hrs = None
        
        # Cost estimate
        estimated_cost = round(random.uniform(0, 100000), 2) if random.random() > 0.15 else None
        actual_cost = round(random.uniform(0, 120000), 2) if random.random() > 0.2 else None
        
        # Satisfaction rating
        satisfaction = random.randint(1, 5) if random.random() > 0.3 else None
        
        # Inspection flag
        requires_inspection = random.choice([True, False, None, 'Yes', 'No', 'TRUE', 1, 0])
        
        # Follow-up needed
        follow_up = random.choice([True, False, None, 'Yes', 'No', 1, 0])
        
        # Fiscal year
        fiscal_year = random.choice(['FY2019', 'FY2020', 'FY2021', 'FY2022', 'FY2023', 'FY2024', None, '2023', 'FY 2023'])
        
        # Description
        description = random.choice([
            'Pothole repair needed',
            'Street light out',
            'Permit application',
            'Noise complaint',
            'Park maintenance',
            'Building inspection required',
            '',
            None,
            'TBD',
            'See attached documents',
            'URGENT - immediate attention needed',
            'na',
            'N/A'
        ])
        
        # Resolution notes
        resolution = random.choice([
            'Completed successfully',
            'Issue resolved',
            'Pending additional review',
            'Referred to another department',
            '',
            None,
            'IN PROGRESS',
            'Waiting for parts',
            'na'
        ]) if status in ['Closed', 'Resolved', 'Completed'] or random.random() < 0.3 else None
        
        data.append([
            case_id, reference_num, submitted_date, assigned_date, resolved_date,
            department, request_type, status, priority, channel, district, category,
            address, zip_code, latitude, longitude, citizen_id, assigned_to,
            response_time_hrs, estimated_cost, actual_cost, satisfaction,
            requires_inspection, follow_up, fiscal_year, description, resolution
        ])
        
        # Add duplicate records (2% chance)
        if random.random() < 0.02 and i > 100:
            data.append(data[-1])
    
    df = pd.DataFrame(data, columns=[
        'case_id', 'reference_number', 'submitted_date', 'assigned_date', 'resolved_date',
        'department', 'request_type', 'status', 'priority', 'channel', 'district', 'category',
        'address', 'zip_code', 'latitude', 'longitude', 'citizen_id', 'assigned_to',
        'response_time_hours', 'estimated_cost', 'actual_cost', 'satisfaction_rating',
        'requires_inspection', 'follow_up_needed', 'fiscal_year', 'description', 'resolution_notes'
    ])
    
    return df


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

def clear_unused_sample_data(keep_key=None):
    """Clear unused sample datasets from session state to free memory"""
    sample_keys = [
        'sales_df_sample', 'healthcare_df_sample', 'finance_df_sample',
        'industry_agnostic_df_sample', 'manufacturing_df_sample',
        'operations_df_sample', 'government_df_sample'
    ]
    
    for key in sample_keys:
        if key != keep_key and key in st.session_state:
            st.session_state[key] = None

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
                st.dataframe(df.head(10), use_container_width=True)
                
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
        
        # Initialize session state for all datasets
        if 'sales_df_sample' not in st.session_state:
            st.session_state.sales_df_sample = None
        if 'healthcare_df_sample' not in st.session_state:
            st.session_state.healthcare_df_sample = None
        if 'finance_df_sample' not in st.session_state:
            st.session_state.finance_df_sample = None
        if 'industry_agnostic_df_sample' not in st.session_state:
            st.session_state.industry_agnostic_df_sample = None
        if 'manufacturing_df_sample' not in st.session_state:
            st.session_state.manufacturing_df_sample = None
        if 'operations_df_sample' not in st.session_state:
            st.session_state.operations_df_sample = None
        if 'government_df_sample' not in st.session_state:
            st.session_state.government_df_sample = None
        
        # === SALES DATA ===
        st.markdown("### 💼 Sales Sample Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Sales transactions with products, prices, and regional data")
        with col2:
            sales_rows = st.number_input("Rows", min_value=100, max_value=25000, value=5000, step=1000, key="sales_sample_rows")
        
        if st.button("Generate Sales Data", type="primary", key="gen_sales_sample"):
            with st.spinner("Generating sales data..."):
                clear_unused_sample_data('sales_df_sample')  # Free memory
                st.session_state.sales_df_sample = generate_sales_data_df(sales_rows)
                st.session_state.df = st.session_state.sales_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.sales_df_sample):,} sales records!")
            st.rerun()
        
        if st.session_state.sales_df_sample is not None:
            st.dataframe(st.session_state.sales_df_sample.head(10), use_container_width=True)
            csv = st.session_state.sales_df_sample.to_csv(index=False).encode('utf-8')
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
            healthcare_rows = st.number_input("Rows", min_value=100, max_value=25000, value=5000, step=1000, key="healthcare_sample_rows")
        
        if st.button("Generate Healthcare Data", type="primary", key="gen_healthcare_sample"):
            with st.spinner("Generating healthcare data..."):
                clear_unused_sample_data('healthcare_df_sample')  # Free memory
                st.session_state.healthcare_df_sample = generate_healthcare_data_df(healthcare_rows)
                st.session_state.df = st.session_state.healthcare_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.healthcare_df_sample):,} patient records!")
            st.rerun()
        
        if st.session_state.healthcare_df_sample is not None:
            st.dataframe(st.session_state.healthcare_df_sample.head(10), use_container_width=True)
            csv = st.session_state.healthcare_df_sample.to_csv(index=False).encode('utf-8')
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
            finance_rows = st.number_input("Rows", min_value=100, max_value=25000, value=5000, step=1000, key="finance_sample_rows")
        
        if st.button("Generate Finance Data", type="primary", key="gen_finance_sample"):
            with st.spinner("Generating finance data..."):
                clear_unused_sample_data('finance_df_sample')  # Free memory
                st.session_state.finance_df_sample = generate_finance_data_df(finance_rows)
                st.session_state.df = st.session_state.finance_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.finance_df_sample):,} transactions!")
            st.rerun()
        
        if st.session_state.finance_df_sample is not None:
            st.dataframe(st.session_state.finance_df_sample.head(10), use_container_width=True)
            csv = st.session_state.finance_df_sample.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Finance CSV",
                data=csv,
                file_name="finance_sample.csv",
                mime="text/csv",
                key="download_finance_sample"
            )
        
        st.markdown("---")
        
        # === INDUSTRY-AGNOSTIC DATA ===
        st.markdown("### 🌐 Industry-Agnostic Business Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Complex business records: projects, budgets, teams, ratings - messy & realistic")
        with col2:
            agnostic_rows = st.number_input("Rows", min_value=100, max_value=50000, value=10000, step=5000, key="agnostic_sample_rows")
        
        if agnostic_rows > 25000:
            st.warning("⚠️ Large datasets may cause memory issues on Streamlit Cloud. Consider using ≤25,000 rows.")
        
        if st.button("Generate Industry-Agnostic Data", type="primary", key="gen_agnostic_sample"):
            with st.spinner(f"Generating {agnostic_rows:,} records... This may take a moment for large datasets..."):
                clear_unused_sample_data('industry_agnostic_df_sample')  # Free memory
                st.session_state.industry_agnostic_df_sample = generate_industry_agnostic_data_df(agnostic_rows)
                st.session_state.df = st.session_state.industry_agnostic_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.industry_agnostic_df_sample):,} business records!")
            st.rerun()
        
        if st.session_state.industry_agnostic_df_sample is not None:
            st.dataframe(st.session_state.industry_agnostic_df_sample.head(10), use_container_width=True)
            
            # Show data quality summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Missing Values", st.session_state.industry_agnostic_df_sample.isnull().sum().sum())
            with col2:
                st.metric("Duplicates", st.session_state.industry_agnostic_df_sample.duplicated().sum())
            with col3:
                st.metric("Data Quality", f"{((1 - st.session_state.industry_agnostic_df_sample.isnull().sum().sum() / (len(st.session_state.industry_agnostic_df_sample) * len(st.session_state.industry_agnostic_df_sample.columns))) * 100):.1f}%")
            
            csv = st.session_state.industry_agnostic_df_sample.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Industry-Agnostic CSV",
                data=csv,
                file_name="industry_agnostic_sample.csv",
                mime="text/csv",
                key="download_agnostic_sample"
            )
        
        st.markdown("---")
        
        # === MANUFACTURING DATA ===
        st.markdown("### 🏭 Manufacturing Operations Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Production batches, quality metrics, machine data, yield rates - complex & messy")
        with col2:
            manufacturing_rows = st.number_input("Rows", min_value=100, max_value=50000, value=10000, step=5000, key="manufacturing_sample_rows")
        
        if manufacturing_rows > 25000:
            st.warning("⚠️ Large datasets may cause memory issues on Streamlit Cloud. Consider using ≤25,000 rows.")
        
        if st.button("Generate Manufacturing Data", type="primary", key="gen_manufacturing_sample"):
            with st.spinner(f"Generating {manufacturing_rows:,} records... This may take a moment for large datasets..."):
                clear_unused_sample_data('manufacturing_df_sample')  # Free memory
                st.session_state.manufacturing_df_sample = generate_manufacturing_data_df(manufacturing_rows)
                st.session_state.df = st.session_state.manufacturing_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.manufacturing_df_sample):,} production records!")
            st.rerun()
        
        if st.session_state.manufacturing_df_sample is not None:
            st.dataframe(st.session_state.manufacturing_df_sample.head(10), use_container_width=True)
            
            # Show data quality summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Missing Values", st.session_state.manufacturing_df_sample.isnull().sum().sum())
            with col2:
                st.metric("Duplicates", st.session_state.manufacturing_df_sample.duplicated().sum())
            with col3:
                st.metric("Data Quality", f"{((1 - st.session_state.manufacturing_df_sample.isnull().sum().sum() / (len(st.session_state.manufacturing_df_sample) * len(st.session_state.manufacturing_df_sample.columns))) * 100):.1f}%")
            
            csv = st.session_state.manufacturing_df_sample.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Manufacturing CSV",
                data=csv,
                file_name="manufacturing_sample.csv",
                mime="text/csv",
                key="download_manufacturing_sample"
            )
        
        st.markdown("---")
        
        # === OPERATIONS DATA ===
        st.markdown("### 📦 Operations & Logistics Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Shipments, tracking, warehouses, delivery metrics - complex & messy")
        with col2:
            operations_rows = st.number_input("Rows", min_value=100, max_value=50000, value=10000, step=5000, key="operations_sample_rows")
        
        if operations_rows > 25000:
            st.warning("⚠️ Large datasets may cause memory issues on Streamlit Cloud. Consider using ≤25,000 rows.")
        
        if st.button("Generate Operations Data", type="primary", key="gen_operations_sample"):
            with st.spinner(f"Generating {operations_rows:,} records... This may take a moment for large datasets..."):
                clear_unused_sample_data('operations_df_sample')  # Free memory
                st.session_state.operations_df_sample = generate_operations_data_df(operations_rows)
                st.session_state.df = st.session_state.operations_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.operations_df_sample):,} shipment records!")
            st.rerun()
        
        if st.session_state.operations_df_sample is not None:
            st.dataframe(st.session_state.operations_df_sample.head(10), use_container_width=True)
            
            # Show data quality summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Missing Values", st.session_state.operations_df_sample.isnull().sum().sum())
            with col2:
                st.metric("Duplicates", st.session_state.operations_df_sample.duplicated().sum())
            with col3:
                st.metric("Data Quality", f"{((1 - st.session_state.operations_df_sample.isnull().sum().sum() / (len(st.session_state.operations_df_sample) * len(st.session_state.operations_df_sample.columns))) * 100):.1f}%")
            
            csv = st.session_state.operations_df_sample.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Operations CSV",
                data=csv,
                file_name="operations_sample.csv",
                mime="text/csv",
                key="download_operations_sample"
            )
        
        st.markdown("---")
        
        # === GOVERNMENT DATA ===
        st.markdown("### 🏛️ Government & Public Sector Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Service requests, permits, citizen cases, response times - complex & messy")
        with col2:
            government_rows = st.number_input("Rows", min_value=100, max_value=50000, value=10000, step=5000, key="government_sample_rows")
        
        if government_rows > 25000:
            st.warning("⚠️ Large datasets may cause memory issues on Streamlit Cloud. Consider using ≤25,000 rows.")
        
        if st.button("Generate Government Data", type="primary", key="gen_government_sample"):
            with st.spinner(f"Generating {government_rows:,} records... This may take a moment for large datasets..."):
                clear_unused_sample_data('government_df_sample')  # Free memory
                st.session_state.government_df_sample = generate_government_data_df(government_rows)
                st.session_state.df = st.session_state.government_df_sample  # Set as active dataset
            st.success(f"✅ Generated {len(st.session_state.government_df_sample):,} public sector records!")
            st.rerun()
        
        if st.session_state.government_df_sample is not None:
            st.dataframe(st.session_state.government_df_sample.head(10), use_container_width=True)
            
            # Show data quality summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Missing Values", st.session_state.government_df_sample.isnull().sum().sum())
            with col2:
                st.metric("Duplicates", st.session_state.government_df_sample.duplicated().sum())
            with col3:
                st.metric("Data Quality", f"{((1 - st.session_state.government_df_sample.isnull().sum().sum() / (len(st.session_state.government_df_sample) * len(st.session_state.government_df_sample.columns))) * 100):.1f}%")
            
            csv = st.session_state.government_df_sample.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Government CSV",
                data=csv,
                file_name="government_sample.csv",
                mime="text/csv",
                key="download_government_sample"
            )
        
        st.info("💡 **Tip:** Download these files and place them in `tests/data/` for permanent use")
        st.info("⚠️ **Note:** These datasets contain realistic data quality issues including missing values, duplicates, inconsistent formatting, and data entry errors - perfect for testing data cleaning and validation workflows!")
        st.info("🌐 **Cloud Note:** For Streamlit Community Cloud, datasets ≤25,000 rows recommended to avoid memory issues.")


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
            if st.button("🤖 Generate AI Insights", type="primary"):
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
            send_button = st.button("Send", type="primary")
        
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
            
            st.dataframe(col_info, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Data Sample")
            st.dataframe(df.head(20), use_container_width=True)
        
        with tab2:
            st.subheader("Statistical Summary")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
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
                st.dataframe(quality_df, use_container_width=True)
                
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
                st.dataframe(corr_df, use_container_width=True)
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
                    
                    st.dataframe(grouped, use_container_width=True)
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
                        if st.button("Interpret Moving Average Forecast", key="interpret_ma"):
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
                        if st.button("Interpret Exponential Smoothing Forecast", key="interpret_es"):
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
                st.dataframe(fdata['forecast_df'], use_container_width=True)
                
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
                    
                    st.dataframe(stats_df, use_container_width=True)
                    
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
                    st.dataframe(outliers, use_container_width=True)
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
            if st.button("🤖 Generate AI Report", type="primary"):
                with st.spinner("AI is generating your comprehensive report... This may take a minute."):
                    report = generate_automated_report(df)
                    st.session_state.generated_report = report
                    # Store the current time when report is generated
                    st.session_state.report_timestamp = datetime.now()
                    st.session_state.report_timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
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
            
            # Get client's local time for display
            st.markdown("---")
            st.markdown("#### 📅 Report Timestamp")
            
            # Use HTML/JavaScript to display local time
            local_time_html = f"""
            <div style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 10px;">
                <strong>Generated (Your Local Time):</strong> <span id="localTime"></span>
                <script>
                    // Get the server timestamp from session state
                    const serverTime = new Date("{st.session_state.report_timestamp.isoformat()}");
                    
                    // Format in user's local timezone
                    const options = {{
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: false
                    }};
                    
                    const localTimeStr = serverTime.toLocaleString('en-US', options);
                    document.getElementById('localTime').textContent = localTimeStr;
                </script>
            </div>
            """
            st.markdown(local_time_html, unsafe_allow_html=True)
            
            # Download report
            col1, col2 = st.columns(2)
            
            # Get timestamp from session state
            report_time = st.session_state.get('report_timestamp', datetime.now())
            
            with col1:
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=st.session_state.generated_report,
                    file_name=f"ai_report_{report_time.strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Create formatted report with metrics
                # Note: Downloads will use server time in filename, but include timezone info in content
                full_report = f"""
AI-POWERED BUSINESS INTELLIGENCE REPORT
Generated: {report_time.strftime('%Y-%m-%d %H:%M:%S')} UTC
Note: View timestamp in your local timezone in the dashboard
========================================

{st.session_state.generated_report}

========================================
DATASET STATISTICS
========================================
Total Records: {len(df)}
Total Columns: {len(df.columns)}
Date Range: {df.iloc[:, 0].min() if len(df) > 0 else 'N/A'} to {df.iloc[:, 0].max() if len(df) > 0 else 'N/A'}

Generated by AI-Powered BI Dashboard
Report Generation Time (UTC): {report_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
                st.download_button(
                    label="📥 Download Full Report (TXT)",
                    data=full_report,
                    file_name=f"full_ai_report_{report_time.strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
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
                csv = df.to_csv(index=False).encode('utf-8')
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
        st.dataframe(df.head(10), use_container_width=True)

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
