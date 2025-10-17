import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO, StringIO
import numpy as np
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Advanced SQL CSV Cleaner",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .sql-editor {
        font-family: 'Courier New', monospace;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'con' not in st.session_state:
    st.session_state.con = duckdb.connect(':memory:')
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None

# Advanced SQL Templates
ADVANCED_SQL_TEMPLATES = {
    "Custom Query": {
        "sql": "",
        "description": "Write your own SQL query"
    },
    "Remove Duplicates": {
        "sql": "SELECT DISTINCT * FROM uploaded_data",
        "description": "Remove all duplicate rows"
    },
    "Remove Duplicates (Keep First)": {
        "sql": """SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY {columns} ORDER BY {order_col}) as rn
    FROM uploaded_data
) WHERE rn = 1""",
        "description": "Remove duplicates but keep the first occurrence",
        "requires_columns": True
    },
    "Remove Null Rows (Any Column)": {
        "sql": "SELECT * FROM uploaded_data WHERE {null_check}",
        "description": "Remove rows where any column has NULL values",
        "dynamic": True
    },
    "Remove Null Rows (Specific Columns)": {
        "sql": "SELECT * FROM uploaded_data WHERE {columns_not_null}",
        "description": "Remove rows where specific columns have NULL",
        "requires_columns": True
    },
    "Trim All Text Columns": {
        "sql": "SELECT {trimmed_columns} FROM uploaded_data",
        "description": "Remove leading/trailing whitespace from all text columns",
        "dynamic": True
    },
    "Standardize Text (Uppercase)": {
        "sql": "SELECT {upper_columns} FROM uploaded_data",
        "description": "Convert all text columns to uppercase",
        "dynamic": True
    },
    "Standardize Text (Lowercase)": {
        "sql": "SELECT {lower_columns} FROM uploaded_data",
        "description": "Convert all text columns to lowercase",
        "dynamic": True
    },
    "Remove Empty Strings": {
        "sql": "SELECT * FROM uploaded_data WHERE {empty_check}",
        "description": "Remove rows with empty string values",
        "dynamic": True
    },
    "Fill Null with Default": {
        "sql": "SELECT {filled_columns} FROM uploaded_data",
        "description": "Replace NULL values with defaults (0 for numbers, 'Unknown' for text)",
        "dynamic": True
    },
    "Fill Null with Mean (Numeric)": {
        "sql": """SELECT {filled_mean_columns} FROM uploaded_data""",
        "description": "Replace NULL numeric values with column mean",
        "dynamic": True
    },
    "Fill Null with Forward Fill": {
        "sql": """SELECT {forward_fill_columns} FROM uploaded_data""",
        "description": "Fill NULL values with the previous non-null value",
        "dynamic": True
    },
    "Remove Outliers (IQR Method)": {
        "sql": """WITH stats AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {column}) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {column}) as q3
    FROM uploaded_data
),
bounds AS (
    SELECT 
        q1 - 1.5 * (q3 - q1) as lower_bound,
        q3 + 1.5 * (q3 - q1) as upper_bound
    FROM stats
)
SELECT * FROM uploaded_data, bounds
WHERE {column} BETWEEN lower_bound AND upper_bound""",
        "description": "Remove statistical outliers using IQR method",
        "requires_columns": True
    },
    "Remove Outliers (Z-Score)": {
        "sql": """WITH stats AS (
    SELECT 
        AVG({column}) as mean,
        STDDEV({column}) as std
    FROM uploaded_data
)
SELECT * FROM uploaded_data, stats
WHERE ABS(({column} - mean) / std) <= 3""",
        "description": "Remove outliers beyond 3 standard deviations",
        "requires_columns": True
    },
    "Aggregate by Group": {
        "sql": """SELECT 
    {group_by_column},
    COUNT(*) as count,
    AVG({numeric_column}) as avg_value,
    MIN({numeric_column}) as min_value,
    MAX({numeric_column}) as max_value
FROM uploaded_data
GROUP BY {group_by_column}
ORDER BY count DESC""",
        "description": "Group and aggregate data",
        "requires_columns": True
    },
    "Date Range Filter": {
        "sql": "SELECT * FROM uploaded_data WHERE {date_column} BETWEEN '{start_date}' AND '{end_date}'",
        "description": "Filter data by date range",
        "requires_columns": True
    },
    "Pivot Data": {
        "sql": """SELECT * FROM (
    PIVOT uploaded_data
    ON {pivot_column}
    USING SUM({value_column})
)""",
        "description": "Pivot table transformation",
        "requires_columns": True
    },
    "Window Function - Running Total": {
        "sql": """SELECT *,
    SUM({column}) OVER (ORDER BY {order_column}) as running_total
FROM uploaded_data""",
        "description": "Calculate running total",
        "requires_columns": True
    },
    "Window Function - Rank": {
        "sql": """SELECT *,
    ROW_NUMBER() OVER (ORDER BY {column} DESC) as rank,
    PERCENT_RANK() OVER (ORDER BY {column} DESC) as percentile
FROM uploaded_data""",
        "description": "Rank rows by column value",
        "requires_columns": True
    },
    "Text Pattern Matching": {
        "sql": "SELECT * FROM uploaded_data WHERE {column} LIKE '%{pattern}%'",
        "description": "Filter by text pattern",
        "requires_columns": True
    },
    "Regex Pattern Matching": {
        "sql": "SELECT * FROM uploaded_data WHERE regexp_matches({column}, '{regex_pattern}')",
        "description": "Filter using regular expressions",
        "requires_columns": True
    },
    "Email Validation": {
        "sql": """SELECT * FROM uploaded_data 
WHERE regexp_matches({email_column}, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')""",
        "description": "Keep only valid email addresses",
        "requires_columns": True
    },
    "Phone Number Standardization": {
        "sql": """SELECT 
    regexp_replace({phone_column}, '[^0-9]', '', 'g') as standardized_phone,
    * EXCLUDE ({phone_column})
FROM uploaded_data""",
        "description": "Standardize phone numbers (remove non-digits)",
        "requires_columns": True
    },
    "Complete Data Cleaning Pipeline": {
        "sql": """WITH cleaned AS (
    SELECT DISTINCT * FROM uploaded_data
    WHERE {null_check}
),
trimmed AS (
    SELECT {trimmed_columns} FROM cleaned
),
final AS (
    SELECT * FROM trimmed WHERE {empty_check}
)
SELECT * FROM final""",
        "description": "Full pipeline: remove duplicates, nulls, trim, and remove empties",
        "dynamic": True
    }
}

def generate_dynamic_sql(template_name, df):
    """Generate SQL with column-specific logic"""
    template = ADVANCED_SQL_TEMPLATES[template_name]
    sql = template["sql"]
    
    if not template.get("dynamic"):
        return sql
    
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    all_cols = df.columns.tolist()
    
    # Generate trimmed columns
    if "{trimmed_columns}" in sql:
        trimmed = [f"TRIM({col}) AS {col}" if col in text_cols else col for col in all_cols]
        sql = sql.replace("{trimmed_columns}", ", ".join(trimmed))
    
    # Generate uppercase columns
    if "{upper_columns}" in sql:
        upper = [f"UPPER(TRIM({col})) AS {col}" if col in text_cols else col for col in all_cols]
        sql = sql.replace("{upper_columns}", ", ".join(upper))
    
    # Generate lowercase columns
    if "{lower_columns}" in sql:
        lower = [f"LOWER(TRIM({col})) AS {col}" if col in text_cols else col for col in all_cols]
        sql = sql.replace("{lower_columns}", ", ".join(lower))
    
    # Generate null check
    if "{null_check}" in sql:
        null_checks = [f"{col} IS NOT NULL" for col in all_cols]
        sql = sql.replace("{null_check}", " AND ".join(null_checks))
    
    # Generate empty string check
    if "{empty_check}" in sql:
        empty_checks = [f"{col} != ''" for col in text_cols]
        if empty_checks:
            sql = sql.replace("{empty_check}", " AND ".join(empty_checks))
        else:
            sql = sql.replace("WHERE {empty_check}", "")
    
    # Generate filled columns (default values)
    if "{filled_columns}" in sql:
        filled = []
        for col in all_cols:
            if col in numeric_cols:
                filled.append(f"COALESCE({col}, 0) AS {col}")
            elif col in text_cols:
                filled.append(f"COALESCE({col}, 'Unknown') AS {col}")
            else:
                filled.append(col)
        sql = sql.replace("{filled_columns}", ", ".join(filled))
    
    # Generate filled columns (mean)
    if "{filled_mean_columns}" in sql:
        filled_mean = []
        for col in all_cols:
            if col in numeric_cols:
                filled_mean.append(f"COALESCE({col}, (SELECT AVG({col}) FROM uploaded_data)) AS {col}")
            else:
                filled_mean.append(col)
        sql = sql.replace("{filled_mean_columns}", ", ".join(filled_mean))
    
    # Generate forward fill columns
    if "{forward_fill_columns}" in sql:
        forward_fill = []
        for col in all_cols:
            forward_fill.append(f"""COALESCE({col}, 
                LAG({col}) IGNORE NULLS OVER (ORDER BY rowid)) AS {col}""")
        sql = sql.replace("{forward_fill_columns}", ", ".join(forward_fill))
    
    return sql

def create_visualizations(original_df, cleaned_df=None):
    """Create before/after visualizations"""
    
    st.subheader("📊 Data Quality Visualizations")
    
    if cleaned_df is not None:
        tab1, tab2, tab3, tab4 = st.tabs(["Missing Data", "Data Distribution", "Column Statistics", "Data Types"])
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Missing Data", "Data Distribution", "Column Statistics", "Data Types"])
    
    with tab1:
        # Missing data visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Original Data - Missing Values")
            missing_orig = original_df.isnull().sum()
            missing_pct_orig = (missing_orig / len(original_df) * 100).round(2)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=missing_orig.index,
                    y=missing_orig.values,
                    text=missing_pct_orig.values,
                    texttemplate='%{text}%',
                    textposition='outside',
                    marker_color='indianred'
                )
            ])
            fig.update_layout(
                title="Missing Values by Column",
                xaxis_title="Column",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if cleaned_df is not None:
                st.markdown("#### Cleaned Data - Missing Values")
                missing_clean = cleaned_df.isnull().sum()
                missing_pct_clean = (missing_clean / len(cleaned_df) * 100).round(2)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=missing_clean.index,
                        y=missing_clean.values,
                        text=missing_pct_clean.values,
                        texttemplate='%{text}%',
                        textposition='outside',
                        marker_color='lightseagreen'
                    )
                ])
                fig.update_layout(
                    title="Missing Values by Column",
                    xaxis_title="Column",
                    yaxis_title="Count",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Data distribution for numeric columns
        numeric_cols = original_df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            selected_col = st.selectbox("Select column to visualize:", numeric_cols)
            
            if cleaned_df is not None:
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("Original Distribution", "Cleaned Distribution")
                )
                
                fig.add_trace(
                    go.Histogram(x=original_df[selected_col].dropna(), name="Original", marker_color='indianred'),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Histogram(x=cleaned_df[selected_col].dropna(), name="Cleaned", marker_color='lightseagreen'),
                    row=1, col=2
                )
                
                fig.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.histogram(original_df, x=selected_col, title=f"Distribution of {selected_col}")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns found in the dataset")
    
    with tab3:
        # Column statistics comparison
        st.markdown("#### Statistical Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Data**")
            st.dataframe(original_df.describe(), use_container_width=True)
        
        with col2:
            if cleaned_df is not None:
                st.markdown("**Cleaned Data**")
                st.dataframe(cleaned_df.describe(), use_container_width=True)
    
    with tab4:
        # Data types visualization
        dtype_counts_orig = original_df.dtypes.value_counts()
        
        if cleaned_df is not None:
            dtype_counts_clean = cleaned_df.dtypes.value_counts()
            
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "pie"}, {"type": "pie"}]],
                subplot_titles=("Original Data Types", "Cleaned Data Types")
            )
            
            fig.add_trace(
                go.Pie(labels=dtype_counts_orig.index.astype(str), values=dtype_counts_orig.values, name="Original"),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Pie(labels=dtype_counts_clean.index.astype(str), values=dtype_counts_clean.values, name="Cleaned"),
                row=1, col=2
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.pie(values=dtype_counts_orig.values, names=dtype_counts_orig.index.astype(str), 
                        title="Data Types Distribution")
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.title("🧹 Advanced SQL CSV Cleaner & Analyzer")
    st.markdown("Upload your CSV, clean it with SQL, and visualize the results!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Upload section
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])
        
        # Sample data
        if st.button("📊 Load Sample Dataset"):
            sample_data = pd.DataFrame({
                'customer_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11],
                'name': ['  John Doe  ', 'Jane Smith', 'Bob Wilson', 'Alice Brown', None, '', 'Charlie Davis', 'John Doe', '  Eve White  ', 'Frank Black', 'Frank Black', 'Grace Green'],
                'email': ['john@email.com', 'jane@email.com', 'bob@email.com', 'alice@email.com', 'invalid-email', '', 'charlie@email.com', 'john@email.com', 'eve@email.com', 'frank@email.com', 'frank@email.com', 'grace@email.com'],
                'age': [25, 30, 35, 28, None, 22, 150, 25, 31, 29, 29, 27],
                'city': ['New York', 'Los Angeles', None, 'Chicago', 'Boston', '  ', 'Miami', 'New York', 'Seattle', 'Denver', 'Denver', 'Portland'],
                'purchase_amount': [100.50, 250.75, None, 175.25, 89.99, 0, 1200.00, 100.50, 310.20, 145.80, 145.80, 220.15],
                'purchase_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-15', '2024-01-22', '2024-01-23', '2024-01-23', '2024-01-24']
            })
            
            csv_string = sample_data.to_csv(index=False)
            st.download_button(
                "📥 Download Sample CSV",
                data=csv_string,
                file_name="sample_dirty_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.divider()
        
        # Query history
        st.subheader("📜 Query History")
        if st.session_state.query_history:
            for idx, query in enumerate(reversed(st.session_state.query_history[-5:])):
                with st.expander(f"Query {len(st.session_state.query_history) - idx}"):
                    st.code(query, language="sql")
        else:
            st.info("No queries executed yet")
        
        if st.session_state.query_history and st.button("Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.rerun()
        
        st.divider()
        
        # Tips
        st.subheader("💡 Quick Tips")
        st.markdown("""
        - Use templates for common operations
        - Table name: `uploaded_data`
        - DuckDB supports full SQL syntax
        - Visualizations update automatically
        - Download results in multiple formats
        """)
    
    # Main content
    if uploaded_file:
        # Load CSV
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.original_df = df.copy()
            
            # Register with DuckDB
            st.session_state.con.register('uploaded_data', df)
            
            # Data overview
            st.success(f"✅ File uploaded successfully: **{uploaded_file.name}**")
            
            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("📊 Total Rows", f"{len(df):,}")
            with col2:
                st.metric("📋 Columns", len(df.columns))
            with col3:
                st.metric("❌ Missing Values", f"{df.isnull().sum().sum():,}")
            with col4:
                st.metric("🔄 Duplicates", f"{df.duplicated().sum():,}")
            with col5:
                memory_usage = df.memory_usage(deep=True).sum() / 1024**2
                st.metric("💾 Size", f"{memory_usage:.2f} MB")
            
            # Tabs for organization
            tab1, tab2, tab3 = st.tabs(["🔧 Data Cleaning", "📊 Visualizations", "📋 Data Preview"])
            
            with tab1:
                # SQL Editor Section
                st.subheader("✍️ SQL Query Editor")
                
                # Template selection
                col1, col2 = st.columns([2, 1])
                with col1:
                    selected_template = st.selectbox(
                        "Choose a SQL template:",
                        list(ADVANCED_SQL_TEMPLATES.keys()),
                        help="Select a pre-built query or write custom SQL"
                    )
                
                with col2:
                    if selected_template != "Custom Query":
                        template_info = ADVANCED_SQL_TEMPLATES[selected_template]
                        st.info(f"ℹ️ {template_info['description']}")
                
                # Column selection for templates that need it
                selected_columns = None
                if ADVANCED_SQL_TEMPLATES[selected_template].get("requires_columns"):
                    st.markdown("**Configure Template Parameters:**")
                    
                    template_sql = ADVANCED_SQL_TEMPLATES[selected_template]["sql"]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "{column}" in template_sql or "{columns}" in template_sql:
                            selected_columns = st.multiselect(
                                "Select columns:",
                                df.columns.tolist(),
                                help="Choose columns for the operation"
                            )
                    
                    with col2:
                        if "{order_col}" in template_sql or "{order_column}" in template_sql:
                            order_column = st.selectbox("Order by:", df.columns.tolist())
                        
                        if "{group_by_column}" in template_sql:
                            group_column = st.selectbox("Group by:", df.columns.tolist())
                    
                    with col3:
                        if "{numeric_column}" in template_sql:
                            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                            if numeric_cols:
                                numeric_column = st.selectbox("Numeric column:", numeric_cols)
                        
                        if "{pattern}" in template_sql:
                            pattern = st.text_input("Search pattern:", value="example")
                
                # Generate SQL
                if selected_template == "Custom Query":
                    default_query = "SELECT * FROM uploaded_data LIMIT 100"
                else:
                    if ADVANCED_SQL_TEMPLATES[selected_template].get("dynamic"):
                        default_query = generate_dynamic_sql(selected_template, df)
                    else:
                        default_query = ADVANCED_SQL_TEMPLATES[selected_template]["sql"]
                        
                        # Replace placeholders if columns selected
                        if selected_columns and "{columns}" in default_query:
                            default_query = default_query.replace("{columns}", ", ".join(selected_columns))
                        if 'order_column' in locals():
                            default_query = default_query.replace("{order_col}", order_column)
                            default_query = default_query.replace("{order_column}", order_column)
                        if 'group_column' in locals():
                            default_query = default_query.replace("{group_by_column}", group_column)
                        if 'numeric_column' in locals():
                            default_query = default_query.replace("{numeric_column}", numeric_column)
                        if 'pattern' in locals():
                            default_query = default_query.replace("{pattern}", pattern)
                
                # SQL text area
                sql_query = st.text_area(
                    "SQL Query:",
                    value=default_query,
                    height=200,
                    help="Write or modify your SQL query here"
                )
                
                # Advanced options
                with st.expander("⚙️ Advanced Options"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        show_plan = st.checkbox("Show Execution Plan", value=False)
                    with col2:
                        limit_results = st.number_input("Result Limit", 1, 100000, 10000)
                    with col3:
                        auto_viz = st.checkbox("Auto-generate Visualizations", value=True)
                
                # Execute button
                col1, col2, col3 = st.columns([1, 1, 3])
                with col1:
                    execute_btn = st.button("▶️ Execute Query", type="primary", use_container_width=True)
                with col2:
                    if st.button("💾 Save Query", use_container_width=True):
                        st.session_state.query_history.append(sql_query)
                        st.success("Query saved to history!")
                
                # Execute query
                if execute_btn:
                    try:
                        with st.spinner("🔄 Executing SQL query..."):
                            # Execute
                            result = st.session_state.con.execute(sql_query).fetchdf()
                            st.session_state.cleaned_df = result
                            
                            # Add to history
                            if sql_query not in st.session_state.query_history:
                                st.session_state.query_history.append(sql_query)
                            
                            # Show execution plan
                            if show_plan:
                                with st.expander("🔍 Query Execution Plan"):
                                    try:
                                        plan = st.session_state.con.execute(f"EXPLAIN {sql_query}").fetchdf()
                                        st.dataframe(plan, use_container_width=True)
                                    except:
                                        st.warning("Could not generate execution plan")
                            
                            # Success message
                            st.success("✅ Query executed successfully!")
                            
                            # Results metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Result Rows", f"{len(result):,}")
                            with col2:
                                removed = len(df) - len(result)
                                st.metric("Rows Changed", f"{removed:,}", delta=f"{removed}")
                            with col3:
                                st.metric("Columns", len(result.columns))
                            with col4:
                                change_pct = ((len(result) / len(df)) * 100) if len(df) > 0 else 0
                                st.metric("Data Retained", f"{change_pct:.1f}%")
                            
                            # Preview results
                            st.subheader("📊 Query Results Preview")
                            st.dataframe(result.head(limit_results), use_container_width=True)
                            
                            # Data quality comparison
                            st.subheader("📈 Data Quality Comparison")
                            
                            comparison_data = {
                                'Metric': ['Total Rows', 'Total Columns', 'Missing Values', 'Duplicate Rows', 'Memory (MB)'],
                                'Original': [
                                    f"{len(df):,}",
                                    len(df.columns),
                                    f"{df.isnull().sum().sum():,}",
                                    f"{df.duplicated().sum():,}",
                                    f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}"
                                ],
                                'Cleaned': [
                                    f"{len(result):,}",
                                    len(result.columns),
                                    f"{result.isnull().sum().sum():,}",
                                    f"{result.duplicated().sum():,}",
                                    f"{result.memory_usage(deep=True).sum() / 1024**2:.2f}"
                                ],
                                'Change': [
                                    f"{len(result) - len(df):,}",
                                    len(result.columns) - len(df.columns),
                                    f"{result.isnull().sum().sum() - df.isnull().sum().sum():,}",
                                    f"{result.duplicated().sum() - df.duplicated().sum():,}",
                                    f"{(result.memory_usage(deep=True).sum() - df.memory_usage(deep=True).sum()) / 1024**2:.2f}"
                                ]
                            }
                            
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                            
                            # Download section
                            st.subheader("💾 Download Results")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                csv = result.to_csv(index=False)
                                st.download_button(
                                    "📥 CSV",
                                    data=csv,
                                    file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            
                            with col2:
                                buffer = BytesIO()
                                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                    result.to_excel(writer, index=False, sheet_name='Cleaned Data')
                                    df.to_excel(writer, index=False, sheet_name='Original Data')
                                
                                st.download_button(
                                    "📥 Excel",
                                    data=buffer.getvalue(),
                                    file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            
                            with col3:
                                st.download_button(
                                    "📥 SQL",
                                    data=sql_query,
                                    file_name="cleaning_query.sql",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            
                            with col4:
                                # JSON export
                                json_data = result.to_json(orient='records', indent=2)
                                st.download_button(
                                    "📥 JSON",
                                    data=json_data,
                                    file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    mime="application/json",
                                    use_container_width=True
                                )
                            
                    except Exception as e:
                        st.error(f"❌ Error executing query: {str(e)}")
                        st.info("💡 Tip: Check your SQL syntax and ensure table name is 'uploaded_data'")
            
            with tab2:
                # Visualizations
                if st.session_state.cleaned_df is not None:
                    create_visualizations(st.session_state.original_df, st.session_state.cleaned_df)
                else:
                    create_visualizations(st.session_state.original_df)
            
            with tab3:
                # Data preview tabs
                preview_tab1, preview_tab2, preview_tab3 = st.tabs(["Original Data", "Column Details", "Data Profile"])
                
                with preview_tab1:
                    st.dataframe(df, use_container_width=True)
                
                with preview_tab2:
                    # Column information
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes.astype(str),
                        'Non-Null': df.count().values,
                        'Null Count': df.isnull().sum().values,
                        'Null %': (df.isnull().sum() / len(df) * 100).round(2).values,
                        'Unique': [df[col].nunique() for col in df.columns],
                        'Sample Values': [str(df[col].dropna().head(3).tolist()[:3]) for col in df.columns]
                    })
                    st.dataframe(col_info, use_container_width=True, hide_index=True)
                
                with preview_tab3:
                    # Data profiling
                    st.markdown("#### Data Profile Summary")
                    
                    profile_data = {
                        'Characteristic': [
                            'Total Records',
                            'Total Features',
                            'Numeric Features',
                            'Categorical Features',
                            'Boolean Features',
                            'DateTime Features',
                            'Missing Cells',
                            'Missing Cells %',
                            'Duplicate Rows',
                            'Duplicate Rows %',
                            'Total Memory'
                        ],
                        'Value': [
                            f"{len(df):,}",
                            len(df.columns),
                            len(df.select_dtypes(include=[np.number]).columns),
                            len(df.select_dtypes(include=['object']).columns),
                            len(df.select_dtypes(include=['bool']).columns),
                            len(df.select_dtypes(include=['datetime64']).columns),
                            f"{df.isnull().sum().sum():,}",
                            f"{(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100):.2f}%",
                            f"{df.duplicated().sum():,}",
                            f"{(df.duplicated().sum() / len(df) * 100):.2f}%",
                            f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
                        ]
                    }
                    
                    st.dataframe(pd.DataFrame(profile_data), use_container_width=True, hide_index=True)
        
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.info("💡 Make sure your file is a valid CSV format")
    
    else:
        # Welcome screen
        st.info("👆 Upload a CSV file from the sidebar to get started!")
        
        # Feature showcase
        st.subheader("🌟 Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 🔧 Data Cleaning
            - 25+ SQL templates
            - Custom query editor
            - Duplicate removal
            - Null value handling
            - Text standardization
            - Outlier detection
            """)
        
        with col2:
            st.markdown("""
            #### 📊 Visualizations
            - Missing data analysis
            - Distribution plots
            - Statistical summaries
            - Before/after comparison
            - Data type analysis
            - Interactive charts
            """)
        
        with col3:
            st.markdown("""
            #### 💾 Export Options
            - CSV download
            - Excel with multiple sheets
            - JSON export
            - SQL query export
            - Query history
            - Data profiling report
            """)
        
        # SQL cheat sheet
        with st.expander("📚 SQL Cleaning Cheat Sheet"):
            st.markdown("""
            ### Quick Reference Guide
            
            **Remove Duplicates:**
            ```sql
            SELECT DISTINCT * FROM uploaded_data
            ```
            
            **Remove Nulls:**
            ```sql
            SELECT * FROM uploaded_data 
            WHERE column1 IS NOT NULL AND column2 IS NOT NULL
            ```
            
            **Trim Whitespace:**
            ```sql
            SELECT TRIM(column_name) AS column_name FROM uploaded_data
            ```
            
            **Fill Nulls with Default:**
            ```sql
            SELECT COALESCE(column_name, 'default_value') AS column_name 
            FROM uploaded_data
            ```
            
            **Remove Outliers (IQR):**
            ```sql
            WITH stats AS (
                SELECT 
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as q1,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as q3
                FROM uploaded_data
            )
            SELECT * FROM uploaded_data, stats
            WHERE value BETWEEN q1 - 1.5*(q3-q1) AND q3 + 1.5*(q3-q1)
            ```
            
            **Standardize Text:**
            ```sql
            SELECT UPPER(TRIM(column_name)) AS column_name 
            FROM uploaded_data
            ```
            
            **Validate Email:**
            ```sql
            SELECT * FROM uploaded_data 
            WHERE regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
            ```
            """)

if __name__ == "__main__":
    main()
