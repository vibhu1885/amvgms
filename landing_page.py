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
        st.error("❌ Secrets 'gcp_service_account' not found!")
        st.stop()
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Grievance_DB").worksheet(sheet_name)

# ==========================================
# CENTRAL CONTROL PANEL (STYLING)
# ==========================================
LOGO_PATH = "assets/office_logo.png" 
LOGO_WIDTH = 130 
APP_BG_COLOR = "#131419"  
HEADING_COLOR = "#FFFFFF" 
LABEL_COLOR = "#FFFFFF"   

# Button Master Controls
BTN_HEIGHT = "70px"        
BTN_WIDTH = "300px"         
BTN_BG_COLOR = "#faf9f9"
BTN_TEXT_COLOR = "#131419"
BTN_BORDER_COLOR = "#fca311"
BTN_BORDER_WIDTH = "4px"
BTN_ROUNDNESS = "22px"
BTN_HOVER_COLOR = "#a7c957"
BTN_TEXT_SIZE = "17px"     
BTN_FONT_WEIGHT = "900"    

st.set_page_config(page_title="GMS Alambagh", layout="centered")

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    [data-testid="stVerticalBlock"] {{ width: 100% !important; align-items: center !important; }}

    [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}

    .stButton {{ width: 100% !important; display: flex !important; justify-content: center !important; }}

    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        max-width: 100% !important;
        height: {BTN_HEIGHT} !important;
        margin: 12px auto !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-4px) scale(1.03) !important;
    }}

    div.stButton > button p {{ font-size: {BTN_TEXT_SIZE} !important; font-weight: {BTN_FONT_WEIGHT} !important; }}

    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; text-align: center; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; text-align: center; }}
    label {{ color: {LABEL_COLOR} !important; font-weight: bold; text-align: center; width: 100%; display: block; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# PAGE NAVIGATION & STATE
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'found_emp_name' not in st.session_state: st.session_state.found_emp_name = ""

# Superuser Session States
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name

# ==========================================
# PAGE CONTENT
# ==========================================

# --- LANDING PAGE ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION PAGE ---
elif st.session_state.page == 'new_form':
    # [Registration code from previous master remains here...]
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')

# --- STATUS CHECK PAGE ---
elif st.session_state.page == 'status_check':
    # [Status code from previous master remains here...]
    st.markdown('<div class="hindi-heading">Grievance Status</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')

# --- SUPERUSER LOGIN PAGE ---
elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Superuser Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">अधिकारी लॉगिन</div>', unsafe_allow_html=True)

    # 1. HRMS ID Verification Section
    hrms_disabled = st.session_state.super_verified
    s_hrms = st.text_input("Enter Your HRMS ID", value=st.session_state.active_super.get('HRMS_ID', ""), disabled=hrms_disabled).upper().strip()

    if not st.session_state.super_verified:
        if st.button("Find User / यूजर खोजें"):
            try:
                df_off = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
                match = df_off[df_off['HRMS_ID'] == s_hrms]
                
                if not match.empty:
                    user_data = match.iloc[0].to_dict()
                    st.session_state.active_super = user_data
                    st.session_state.super_verified = True
                    st.rerun()
                else:
                    st.error("❌ HRMS ID not found in Officer Mapping.")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # 2. User Found & Key Verification
    else:
        u = st.session_state.active_super
        st.success(f"✅ User Found: {u['NAME']} ({u['RANK']})")
        
        login_key = st.text_input("Enter Login Key", type="password")
        
        if st.button("Login / लॉगिन करें"):
            if str(login_key) == str(u['LOGIN_KEY']):
                role = u['ROLE'].upper()
                
                if role == "ADMIN":
                    go_to('admin_dashboard')
                elif role == "OFFICER":
                    go_to('officer_dashboard')
                elif role == "BOTH":
                    go_to('role_selection')
                st.rerun()
            else:
                st.error("❌ Invalid Login Key.")

    if st.button("⬅️ Back to Home"):
        st.session_state.super_verified = False
        st.session_state.active_super = {}
        go_to('landing')

# --- ROLE SELECTION PAGE (For BOTH role) ---
elif st.session_state.page == 'role_selection':
    st.markdown('<div class="hindi-heading">Select Dashboard</div>', unsafe_allow_html=True)
    st.info(f"Welcome {st.session_state.active_super['NAME']}, please choose a view:")
    
    if st.button("🛠️ Admin Dashboard"):
        go_to('admin_dashboard')
        st.rerun()
        
    if st.button("📋 Officer Dashboard"):
        go_to('officer_dashboard')
        st.rerun()

# --- DASHBOARD PLACEHOLDERS ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading">Admin Dashboard</div>', unsafe_allow_html=True)
    if st.button("Logout"): go_to('landing')

elif st.session_state.page == 'officer_dashboard':
    st.markdown('<div class="hindi-heading">Officer Dashboard</div>', unsafe_allow_html=True)
    if st.button("Logout"): go_to('landing')
