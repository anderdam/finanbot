# pages/dashboard.py
import streamlit as st
import requests
from datetime import datetime


def show_dashboard(api_base: str):
    st.title("📊 FinanBot Dashboard")
    st.sidebar.header("Select Month")
    year = st.sidebar.selectbox("Year", list(range(2025, datetime.now().year + 1)))
    month = st.sidebar.selectbox("Month", list(range(1, 13)))
    st.subheader("Monthly Summary")
    summary_url = f"{api_base}/transactions/summary?year={year}&month={month}"
    try:
        r = requests.get(summary_url, timeout=5)
    except Exception:
        r = None
    if r is not None and r.status_code == 200:
        s = r.json()
        st.metric("Total Income", f"${s.get('total_income', 0):.2f}")
        st.metric("Total Expense", f"${s.get('total_expense', 0):.2f}")
        st.metric("Net Balance", f"${s.get('net_balance', 0):.2f}")
        st.write("### Top Categories")
        top = s.get("top_categories", {})
        if top:
            st.bar_chart(top)
        else:
            st.write("No category data")
    else:
        st.warning("No data available for this period or backend unreachable.")

    st.subheader("Alerts")
    try:
        ar = requests.get(f"{api_base}/transactions/alerts", timeout=5)
    except Exception:
        ar = None
    if ar is not None and ar.status_code == 200:
        alerts = ar.json()
        risk_score = alerts.get("risk_score", 0)
        try:
            score = float(risk_score)
            if score <= 1:
                score *= 100
        except Exception:
            score = 0
        st.progress(min(max(int(score), 0), 100))
        for msg in alerts.get("messages", []):
            st.error(msg)
    else:
        st.info("No alerts or backend unreachable.")
