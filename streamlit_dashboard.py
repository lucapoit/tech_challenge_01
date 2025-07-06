import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

# Set up DB connection
DATABASE_URL = os.getenv("DATABASE_URL")  # set this in Streamlit cloud or .env locally
engine = create_engine(DATABASE_URL)

# Load log data
@st.cache_data(ttl=10)  # refresh every 10 seconds (or manually)
def load_logs():
    with engine.begin() as conn:
        df = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
    return df

# App layout
st.set_page_config(page_title="API Log Dashboard", layout="wide")
st.title("📊 API Log Dashboard")

df = load_logs()

if df.empty:
    st.warning("No logs found.")
    st.stop()

# --- Metrics Section ---
col1, col2 = st.columns(2)

with col1:
    st.metric("🔢 Total Calls", max(df['id']))

with col2:
    last = df.iloc[0]
    st.metric(
        label="🕒 Last Call",
        value=f"{last['endpoint']} → {last['status_code']}",
        delta=last['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    )

st.divider()

# --- Charts Section ---
col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(df, names='endpoint', title='📌 Calls by Endpoint')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(df, names='status_code', title='✅ Status Code Distribution')
    st.plotly_chart(fig2, use_container_width=True)

# --- Optional Table Section ---
with st.expander("📄 Show Raw Log Table"):
    st.dataframe(df, use_container_width=True)
