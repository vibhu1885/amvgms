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
# CENTRAL CONTROL PANEL (STYLING)
# ==========================================
LOGO_PATH = "assets/office_logo.png" 
LOGO_WIDTH = 130 
APP_BG_COLOR = "#131419"  
HEADING_COLOR = "#FFFFFF" 
LABEL_COLOR = "#FFFFFF"   

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

# THE FIX: If we are NOT in Admin, force centered layout
if 'page' not in st.session_state: st.session_state.page = 'landing'

# Set wide only for Admin, otherwise Centered
st.set_page_config(
    page_title="GMS Alambagh", 
    layout="wide" if st.session_state.page == 'admin_dashboard' else "centered"
)

# ==========================================
# THE "RESTORED" ALIGNMENT ENGINE (CSS)
# ==========================================
# We use a strict max-width to lock the landing page look
max_w = "1200px" if st.session_state.page == 'admin_dashboard' else "480px"

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: {max_w} !important;
        padding-top: 1.5rem !important;
        margin: auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    /* LOGO & BUTTON CENTERING: THE FORCED LOCK */
    [data-testid="stImage"], .stButton, [data-testid="stVerticalBlock"] > div:has(div.stButton) {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }}

    [data-testid="stImage"] img {{ margin: 0 auto !important; }}

    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        height: {BTN_HEIGHT} !important;
        margin: 15px auto !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.6) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-4px) scale(1.02) !important;
    }}

    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important; 
        color: {BTN_TEXT_COLOR} !important;
        margin: 0 !important;
    }}

    /* FORM ALIGNMENT: LABELS LEFT */
    [data-testid="stVerticalBlock"] {{ align-items: stretch !important; }}
    label {{ 
        color: {LABEL_COLOR} !important; 
        font-weight: bold !important; 
        text-align: left !important; 
        width: 100% !important; 
        display: block !important;
    }}
    
    .hindi-heading, .english-heading {{ text-align: center !important; width: 100% !important; }}
    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}

    /* Admin Dash Cards */
    .card-box {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }}
    .card {{ padding: 12px; border-radius: 10px; text-align: center; font-weight: 900; color: #131419; min-width: 140px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# STATE & NAVIGATION logic remains same
# ==========================================
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- PAGE 1: LANDING ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    if not st.session_state.hrms_verified:
        hrms_input = st.text_input("Enter HRMS ID*", max_chars=6).upper().strip()
        if st.button("🔎 Verify ID"):
            try:
                df = pd.DataFrame(get_sheet("EMPLOYEE_MAPPING").get_all_records())
                match = df[df['HRMS_ID'] == hrms_input]
                if not match.empty:
                    st.session_state.found_emp_name = match.iloc[0]['EMPLOYEE_NAME']
                    st.session_state.hrms_verified = True
                    st.session_state.active_hrms = hrms_input
                    st.rerun()
                else: st.error("❌ HRMS ID not found.")
            except Exception as e: st.error(f"Error: {e}")
    else:
        st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
        # Form fields go here (Restored in full logic)
        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        # [Rest of selectboxes...]
        if st.button("📤 Grievance जमा करें"):
            st.success("Submitting...")
    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    # The layout wide takes effect here
    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
