import streamlit as st
import base64
import os

# --- STYLE SETTINGS ---
LOGO_FILENAME = "assets/office_logo.png"
B_STYLE = """
    div.stButton > button {
        width: 420px !important; max-width: 90% !important; height: 85px !important;
        background-color: #e5e5e5 !important; color: #14213d !important;
        border-radius: 20px !important; border: 3px solid #fca311 !important;
        margin: 15px auto !important; font-weight: 1000 !important; font-size: 22px !important;
    }
"""
st.set_page_config(layout="wide", page_title="Railway GMS", initial_sidebar_state="collapsed")
st.markdown(f"<style>{B_STYLE}</style>", unsafe_allow_html=True)

# --- NAVIGATION HELPER ---
def force_switch(full_path, internal_name):
    try:
        st.switch_page(full_path)
    except:
        try:
            st.switch_page(internal_name)
        except Exception as e:
            st.error(f"Page {internal_name} not found. Check GitHub pages/ folder.")

# --- LANDING UI ---
st.markdown("<h1 style='text-align:center; color:white;'>कैरिज वर्कशॉप, आलमाग<br>Grievance System</h1>", unsafe_allow_html=True)

if st.button("📝 नया Grievance दर्ज करें"):
    force_switch("pages/1_Registration.py", "1_Registration")

if st.button("🔍 स्थिति देखें"):
    force_switch("pages/3_Status_Login.py", "3_Status_Login")

if st.button("🔐 Officer Login"):
    force_switch("pages/5_Admin_Login.py", "5_Admin_Login")
