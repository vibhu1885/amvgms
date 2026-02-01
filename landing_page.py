import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. SECURE GOOGLE SHEETS CONNECTION
# ==========================================
def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Secrets not found!")
        st.stop()
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Grievance_DB").worksheet(sheet_name)

# ==========================================
# GLOBAL STYLE CONSTANTS
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 130
APP_BG_COLOR = "#131419"
HEADING_COLOR = "#FFFFFF"
BTN_BG = "#faf9f9"
BTN_TEXT = "#131419"
BTN_BORDER = "#fca311"
BTN_HOVER = "#a7c957"

# ==========================================
# 1. PAGE-SPECIFIC CSS INJECTORS
# ==========================================

def inject_landing_css():
    """Strict Centering for Landing and Login"""
    st.markdown(f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        .block-container {{ max-width: 480px !important; padding-top: 2rem !important; margin: auto; }}
        
        /* Logo Center Lock */
        [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
        [data-testid="stImage"] img {{ margin: 0 auto !important; }}
        
        /* Button Center Lock */
        .stButton {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
        div.stButton > button {{
            background-color: {BTN_BG} !important; color: {BTN_TEXT} !important;
            border: 4px solid {BTN_BORDER} !important; border-radius: 22px !important;
            width: 300px !important; height: 70px !important; margin: 15px auto !important;
            font-weight: 900 !important; font-size: 17px !important;
            box-shadow: 0 8px 16px rgba(0,0,0,0.6) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }}
        div.stButton > button:hover {{ background-color: {BTN_HOVER} !important; transform: translateY(-4px) !important; }}
        div.stButton > button p {{ font-weight: 900 !important; color: {BTN_TEXT} !important; margin: 0 !important; }}

        .hindi-heading, .english-heading {{ text-align: center !important; width: 100%; color: white; }}
    </style>
    """, unsafe_allow_html=True)

def inject_form_css():
    """Centering for Logo/Buttons but Left-Align for Labels"""
    st.markdown(f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        .block-container {{ max-width: 480px !important; padding-top: 2rem !important; margin: auto; }}
        
        [data-testid="stImage"], .stButton {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
        div.stButton > button {{
            background-color: {BTN_BG} !important; color: {BTN_TEXT} !important;
            border: 4px solid {BTN_BORDER} !important; border-radius: 22px !important;
            width: 300px !important; height: 70px !important; margin: 15px auto !important;
            font-weight: 900 !important;
        }}
        
        /* Form Label Left Alignment */
        label {{ text-align: left !important; color: white !important; font-weight: bold !important; width: 100% !important; display: block; }}
        .stTextInput, .stSelectbox, .stTextArea {{ text-align: left !important; }}
        .hindi-heading, .english-heading {{ text-align: center !important; width: 100%; color: white; }}
    </style>
    """, unsafe_allow_html=True)

def inject_admin_css():
    """Wide Layout for Dashboard Tables"""
    st.markdown(f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        .block-container {{ max-width: 1200px !important; padding-top: 1.5rem !important; }}
        .hindi-heading {{ text-align: center !important; color: white; font-size: 35px !important; font-weight: 900; }}
        
        /* Card Styling */
        .card-box {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }}
        .card {{ padding: 12px; border-radius: 10px; text-align: center; font-weight: 900; color: #131419; min-width: 140px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. STATE & NAVIGATION
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 3. PAGE ROUTING
# ==========================================

st.set_page_config(page_title="GMS Alambagh", layout="centered")

# --- LANDING ---
if st.session_state.page == 'landing':
    inject_landing_css()
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading" style="font-size:22px; font-weight:900;">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading" style="font-size:18px;">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION ---
elif st.session_state.page == 'new_form':
    inject_form_css()
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter HRMS ID*", max_chars=6).upper().strip()
        if st.button("🔎 Verify ID"):
            try:
                df = pd.DataFrame(get_sheet("EMPLOYEE_MAPPING").get_all_records())
                match = df[df['HRMS_ID'] == hrms_in]
                if not match.empty:
                    st.session_state.found_emp_name = match.iloc[0]['EMPLOYEE_NAME']
                    st.session_state.hrms_verified = True
                    st.session_state.active_hrms = hrms_in
                    st.rerun()
                else: st.error("❌ HRMS ID not found.")
            except Exception as e: st.error(f"Error: {e}")
    else:
        st.success(f"✅ Employee: {st.session_state.found_emp_name}")
        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        # Rest of your registration fields (designation, trade, etc.)
        if st.button("📤 Grievance जमा करें"):
            st.success("Submitting...")
    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- LOGIN ---
elif st.session_state.page == 'login':
    inject_landing_css()
    st.markdown('<div class="hindi-heading">Superuser Login</div>', unsafe_allow_html=True)
    locked = st.session_state.super_verified
    s_hrms = st.text_input("Enter Your HRMS ID", value=st.session_state.active_super.get('HRMS_ID', ""), disabled=locked).upper().strip()
    if not st.session_state.super_verified:
        if st.button("👤 Find User"):
            try:
                df_off = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
                match = df_off[df_off['HRMS_ID'] == s_hrms]
                if not match.empty:
                    st.session_state.active_super = match.iloc[0].to_dict()
                    st.session_state.super_verified = True
                    st.rerun()
                else: st.error("❌ HRMS ID not found.")
            except Exception as e: st.error(f"Error: {e}")
    else:
        st.success(f"✅ {st.session_state.active_super['NAME']}")
        key = st.text_input("Enter Key", type="password")
        if st.button("🔓 Login"):
            if str(key) == str(st.session_state.active_super['LOGIN_KEY']):
                role = st.session_state.active_super['ROLE'].upper()
                if role == "ADMIN": go_to('admin_dashboard')
                elif role == "OFFICER": go_to('officer_dashboard')
                elif role == "BOTH":
