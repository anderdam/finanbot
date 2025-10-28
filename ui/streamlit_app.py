import streamlit as st
import requests
from datetime import datetime


API_BASE = "http://localhost:8000"  # Adjust if running elsewhere

st.set_page_config(page_title="FinanBot Dashboard", layout="wide")

st.title("📊 FinanBot Personal Finance Tracker")

# --- Date Selection ---
st.sidebar.header("Select Month")
year = st.sidebar.selectbox("Year", list(range(2022, datetime.now().year + 1)))
month = st.sidebar.selectbox("Month", list(range(1, 13)))

# --- Summary ---
st.subheader("Monthly Summary")
summary_url = f"{API_BASE}/transactions/summary?year={year}&month={month}"
summary_resp = requests.get(summary_url)

if summary_resp.status_code == 200:
    summary = summary_resp.json()
    st.metric("Total Income", f"${summary['total_income']:.2f}")
    st.metric("Total Expense", f"${summary['total_expense']:.2f}")
    st.metric("Net Balance", f"${summary['net_balance']:.2f}")

    st.write("### Top Categories")
    st.bar_chart(summary["top_categories"])
else:
    st.warning("No data available for this period.")

# --- Alerts ---
st.subheader("Alerts")
alerts_resp = requests.get(f"{API_BASE}/transactions/alerts")

if alerts_resp.status_code == 200:
    alerts = alerts_resp.json()
    st.progress(alerts["risk_score"])
    for msg in alerts["messages"]:
        st.error(msg)
else:
    st.warning("Could not fetch alerts.")
