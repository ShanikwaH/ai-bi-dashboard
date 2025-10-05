import streamlit as st

st.set_page_config(
    page_title="AI BI Dashboard",
    page_icon="🤖",
    layout="wide"
)

try:
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime, timedelta
    import io
    import json
except Exception as e:
    st.error(f"Import error: {e}")
    st.stop()

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except:
    GENAI_AVAILABLE = False
    genai = None

# Initialize session state
for key in ['df', 'gemini_api_key', 'gemini_model', 'model_name', 'chat_history']:
    if key not in st.session_state:
        st.session_state[key] = None if key != 'chat_history' else []

st.title("AI-Powered BI Dashboard")
st.write("App is running!")

if GENAI_AVAILABLE:
    st.success("Google Generative AI is available")
else:
    st.warning("Google Generative AI is not available")

st.write(f"Pandas version: {pd.__version__}")
st.write(f"Streamlit version: {st.__version__}")

# Simple test
if st.button("Generate Test Data"):
    df = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100)
    })
    st.dataframe(df.head())
    st.success("Test data generated successfully!")
