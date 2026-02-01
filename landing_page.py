import streamlit as st
import base64
import os

st.set_page_config(layout="wide", page_title="Railway GMS", initial_sidebar_state="collapsed")

# --- Page Style Module ---
st.markdown("""
    <style>
    .stApp { background-color: #091327 !important; }
    [data-testid="stSidebar"], [data-testid="stHeader"], footer { visibility: hidden !important; }
    
    [data-testid="stVerticalBlock"] { 
        display: flex !important; align-items: center !important; justify-content: center !important; 
    }

    /* Large Landing Buttons */
    div.stButton > button {
        width: 420px !important; max-width: 90% !important; height: 85px !important;
        background-color: #e5e5e5 !important; color: #14213d !important;
        border-radius: 20px !important; border: 3px solid #fca311 !important;
        margin: 15px auto !important; font-weight: 1000 !important; font-size: 22px !important;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:white; text-align:center;'>कैरिज वर्कशॉप, आलमाग<br>Grievance Management System</h1>", unsafe_allow_html=True)

# Direct Page Linking
if st.button("📝 नया Grievance दर्ज करें"):
    st.switch_page("pages/1_Registration.py")

if st.button("🔍 स्थिति देखें"):
    st.switch_page("pages/3_Status_Login.py")

if st.button("🔐 Officer Login"):
    st.switch_page("pages/5_Admin_Login.py")
