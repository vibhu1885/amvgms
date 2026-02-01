import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# ⚙️ GLOBAL CONFIG & ROUTER
# ==========================================
st.set_page_config(layout="wide", page_title="Railway GMS", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "LANDING"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# Global Hide UI Elements
st.markdown("<style>[data-testid='stSidebar'], [data-testid='stHeader'], footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# ==========================================
# 🏠 SANDBOX: LANDING PAGE
# ==========================================
def show_landing():
    st.markdown("""
        <style>
        .stApp { background-color: #091327 !important; }
        [data-testid="stVerticalBlock"] { align-items: center !important; justify-content: center !important; text-align: center !important; }
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
# 🔍 SANDBOX: STATUS LOGIN & VIEW
# ==========================================
def show_status():
    st.markdown("""
        <style>
        .stApp { background-color: #091327 !important; }
        [data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 800 !important; color: white !important; }
        .status-card { background: rgba(255,255,255,0.05); border-left: 5px solid #fca311; padding: 15px; border-radius: 10px; margin-bottom: 15px; text-align: left; }
        .reg-container { width: 500px; max-width: 95%; margin: 0 auto; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:white; text-align:center;'>Grievance Status</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="reg-container">', unsafe_allow_html=True)
        search_id = st.text_input("अपनी HRMS ID दर्ज करें (Status देखने के लिए)").upper().strip()
        
        if st.button("🔍 Search Status"):
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(worksheet="GRIEVANCE", ttl="0")
            results = df[df['HRMS_ID'].astype(str).str.strip().upper() == search_id]
            
            if results.empty:
                st.warning("No records found for this ID.")
            else:
                for _, row in results.iterrows():
                    st.markdown(f"""
                        <div class="status-card">
                            <b style="color:#fca311;">REF: {row['REFERENCE_NO']}</b><br>
                            <span style="color:white;">Status: <b>{row['STATUS']}</b></span><br>
                            <p style="color:#adb5bd; font-size:14px; margin-top:5px;">{row['GRIEVANCE_TEXT']}</p>
                        </div>
                    """, unsafe_allow_html=True)
        
        if st.button("⬅️ Back"): navigate_to("LANDING")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🔐 SANDBOX: OFFICER LOGIN
# ==========================================
def show_login():
    st.markdown("""
        <style>
        .stApp { background-color: #091327 !important; }
        [data-testid="stWidgetLabel"] p { font-size: 16px !important; font-weight: 800 !important; color: white !important; }
        .login-box { width: 400px; max-width: 90%; margin: 0 auto; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='color:white; text-align:center;'>Officer Login</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        user = st.text_input("HRMS ID").upper().strip()
        pwd = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if user == "ADMIN" and pwd == "1234": # Placeholder logic
                st.success("Welcome, Admin")
            else:
                st.error("Invalid Credentials")
                
        if st.button("⬅️ Back"): navigate_to("LANDING")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚦 MAIN ROUTER EXECUTION
# ==========================================
if st.session_state.page == "LANDING":
    show_landing()
elif st.session_state.page == "REGISTRATION":
    # (Registration function from previous turn)
    pass 
elif st.session_state.page == "STATUS_LOGIN":
    show_status()
elif st.session_state.page == "OFFICER_LOGIN":
    show_login()
