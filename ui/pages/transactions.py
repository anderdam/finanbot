# pages/transactions.py
import streamlit as st
import requests
from datetime import datetime


def show_add_transaction(api_base: str):
    st.header("Add Transaction")
    with st.form("tx_form"):
        amount = st.number_input("Amount", format="%.2f")
        description = st.text_input("Description")
        occurred_at = st.date_input("Occurred at", value=datetime.today())
        is_income = st.radio("Type", ["Expense", "Income"]) == "Income"
        submit = st.form_submit_button("Create")
    if submit:
        payload = {
            "amount": float(amount) if is_income else -abs(float(amount)),
            "description": description,
            "occurred_at": occurred_at.isoformat(),
        }
        try:
            r = requests.post(f"{api_base}/transactions/", json=payload, timeout=5)
            if r.status_code in (200, 201):
                st.success("Transaction created.")
                st.json(r.json())
            else:
                st.error(f"Failed: {r.status_code} {r.text}")
        except Exception as exc:
            st.error(f"Error contacting backend: {exc}")


def show_list_transactions(api_base: str):
    st.header("Transactions")
    col1, col2 = st.columns([1, 3])
    with col1:
        limit = st.number_input("Limit", min_value=1, max_value=500, value=50)
        offset = st.number_input("Offset", min_value=0, value=0)
        refresh = st.button("Refresh")
    with col2:
        search = st.text_input("Search description (simple contains)")
        print(search)
    if refresh or True:
        params = {"limit": limit, "offset": offset}
        try:
            r = requests.get(f"{api_base}/transactions/", params=params, timeout=5)
        except Exception as exc:
            st.error(f"Backend error: {exc}")
            return
        if r.status_code != 200:
            st.error(f"Failed to list: {r.status_code} {r.text}")
            return
        rows = r.json()
        for tx in rows:
            st.write(
                f"{tx.get('id')} — {tx.get('occurred_at', '')} — "
                f"${tx.get('amount'):.2f} — {tx.get('description')}"
            )
