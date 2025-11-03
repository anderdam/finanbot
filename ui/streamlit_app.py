# streamlit_app.py (main dashboard + simple nav if not using multipage)
import os
import streamlit as st
from pages.dashboard import show_dashboard
from pages.transactions import show_add_transaction, show_list_transactions
from pages.users import show_add_user, show_list_users
from pages.attachments import show_upload_attachment

API_BASE = os.getenv("FINANBOT_BACKEND_URL", "http://finanbot:8000").rstrip("/") + "/v1"
st.set_page_config(page_title="FinanBot Dashboard", layout="wide")

st.sidebar.title("FinanBot")
page = st.sidebar.selectbox(
    "Go to",
    [
        "Dashboard",
        "Add transaction",
        "List transactions",
        "Upload attachment",
        "Add user",
        "List users",
    ],
)
if page == "Dashboard":
    show_dashboard(API_BASE)
elif page == "Add transaction":
    show_add_transaction(API_BASE)
elif page == "List transactions":
    show_list_transactions(API_BASE)
elif page == "Upload attachment":
    show_upload_attachment(API_BASE)
elif page == "Add user":
    show_add_user(API_BASE)
elif page == "List users":
    show_list_users(API_BASE)
