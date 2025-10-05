import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.title("AI-Powered BI Dashboard")
st.success("✅ App is running successfully!")

st.write("If you see this message, your Streamlit Cloud setup is working correctly.")

# Test imports
try:
    import pandas as pd
    import numpy as np
    import plotly.express as px
    st.success("✅ All basic libraries imported successfully")
except Exception as e:
    st.error(f"Import error: {e}")

try:
    import google.generativeai as genai
    st.success("✅ Google Generative AI imported successfully")
except Exception as e:
    st.warning(f"⚠️ Google Generative AI not available: {e}")
