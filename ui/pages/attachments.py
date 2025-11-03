# pages/attachments.py
import streamlit as st
import requests


def show_upload_attachment(api_base: str):
    st.header("Upload Attachment")
    tx_id = st.text_input("Transaction ID (optional)")
    uploaded = st.file_uploader("Choose file", type=None)
    if uploaded:
        if st.button("Upload"):
            files = {"file": (uploaded.name, uploaded.getvalue())}
            data = {}
            if tx_id:
                data["transaction_id"] = tx_id
            try:
                r = requests.post(
                    f"{api_base}/attachments/", files=files, data=data, timeout=10
                )
            except Exception as exc:
                st.error(f"Failed to contact backend: {exc}")
                return
            if r.status_code in (200, 201):
                st.success("Uploaded")
                st.json(r.json())
            else:
                st.error(f"Upload failed: {r.status_code} {r.text}")
