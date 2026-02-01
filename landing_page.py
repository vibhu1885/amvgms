import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# ⚙️ GLOBAL CONFIG
# ==========================================
st.set_page_config(layout="wide", page_title="Railway GMS", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "LANDING"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# Global Hide (Sidebar & Header)
st.markdown("<style>[data-testid='stSidebar'], [data-testid='stHeader'], footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# ==========================================
# 🏠 SANDBOX 1: LANDING PAGE
# ==========================================
def show_landing():
    # Landing Specific CSS
    st.markdown("""
        <style>
        .stApp { background-color: #091327 !important; }
        [data-testid="stVerticalBlock"] { align-items: center !important; justify-content: center !important; text-align: center !important; }
        
        /* Large Iconic Buttons */
        div.stButton > button {
            width: 420px !important; max-width: 90% !important; height: 85px !important;
            background-color: #e5e5e5 !important; color: #14213d !important;
            border-radius: 20px !important; border: 3px solid #fca311 !important;
            margin: 15px auto !important; font-weight: 1000 !important; font-size: 22px !important;
            box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:white; margin-top:50px;'>कैरिज वर्कशॉप, आलमाग, लखनऊ<br>Grievance Management System</h1>", unsafe_allow_html=True)
    
    if st.button("📝 नया Grievance दर्ज करें"): navigate_to("REGISTRATION")
    if st.button("🔍 स्थिति देखें"): navigate_to("STATUS_LOGIN")
    if st.button("🔐 Officer Login"): navigate_to("OFFICER_LOGIN")

# ==========================================
# 📝 SANDBOX 2: REGISTRATION
# ==========================================
def show_registration():
    # Registration Specific CSS (16px Labels)
    st.markdown("""
        <style>
        .stApp { background-color: #091327 !important; }
        [data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 800 !important; color: white !important; text-align: left !important; }
        
        /* Compact Form Buttons */
        div.stButton > button, div.stFormSubmitButton > button {
            width: 100% !important; height: 55px !important;
            background-color: #fca311 !important; color: #14213d !important;
            border-radius: 12px !important; font-weight: 800 !important;
        }
        .reg-container { width: 480px; max-width: 95%; margin: 0 auto; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:white; text-align:center;'>Registration Form</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="reg-container">', unsafe_allow_html=True)
        with st.form("reg_form"):
            hrms = st.text_input("HRMS ID").upper().strip()
            g_type = st.selectbox("समस्या का प्रकार*", ["Electrical", "Mechanical", "Quarter", "Medical"])
            desc = st.text_area("विवरण*", max_chars=100)
            
            if st.form_submit_button("Submit (दर्ज करें)"):
                if not hrms or not desc:
                    st.error("Please fill all fields")
                else:
                    st.session_state.last_ref = f"REF-{datetime.now().strftime('%y%m%d%H%M')}"
                    navigate_to("SUCCESS")
        
        if st.button("⬅️ Back to Home"): navigate_to("LANDING")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ✅ SANDBOX 3: SUCCESS PAGE
# ==========================================
def show_success():
    # Success Specific CSS
    st.markdown("""
        <style>
        .stApp { background-color: #091327 !important; }
        .success-card { text-align: center; margin-top: 80px; }
        .balanced-title { color: #a5be00; font-size: 38px; font-weight: 1000; }
        .ref-box-yellow { 
            background-color: #fca311; color: #14213d; 
            padding: 20px 40px; border-radius: 20px; 
            font-size: 30px; font-weight: 1000; display: inline-block;
            margin: 30px 0; font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)

    ref = st.session_state.get('last_ref', 'N/A')
    st.markdown(f"""
        <div class="success-card">
            <div class="balanced-title">सफलतापूर्वक दर्ज!</div>
            <div style="color:white; font-size:20px;">आपका Grievance नंबर नीचे दिया गया है:</div>
            <div class="ref-box-yellow">{ref}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Home"): navigate_to("LANDING")

# ==========================================
# 🚦 MAIN ROUTER EXECUTION
# ==========================================
if st.session_state.page == "LANDING":
    show_landing()
elif st.session_state.page == "REGISTRATION":
    show_registration()
elif st.session_state.page == "SUCCESS":
    show_success()
# (Add status and login functions here as we build them)
