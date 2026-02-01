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

# ==========================================
# STRICT ALIGNMENT ENGINE (CSS)
# ==========================================
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
        justify-content: flex-start !important;
    }}

    [data-testid="stVerticalBlock"] {{ 
        width: 100% !important; 
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
    [data-testid="stImage"] > img {{ margin: 0 auto !important; }}

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
        border-color: {BTN_BG_COLOR} !important;
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 10px 20px rgba(167, 201, 87, 0.4) !important;
    }}

    div.stButton > button p {{ font-size: {BTN_TEXT_SIZE} !important; font-weight: {BTN_FONT_WEIGHT} !important; }}

    .hindi-heading, .english-heading, label, .stMarkdown p {{
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }}

    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; line-height: 1.4; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
    label {{ color: {LABEL_COLOR} !important; font-weight: bold; margin-top: 10px; }}
    
    .err-msg {{ color: #FF4B4B; font-size: 13px; font-weight: bold; margin-top: -10px; margin-bottom: 10px; text-align: center; width: 100%; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# NAVIGATION & SESSION STATES
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name

def generate_ref_no(hrms_id, df_grievance):
    date_str = datetime.now().strftime("%Y%m%d")
    count = 1
    if not df_grievance.empty and 'HRMS_ID' in df_grievance.columns:
        count = len(df_grievance[df_grievance['HRMS_ID'] == hrms_id]) + 1
    return f"{date_str}{hrms_id}{str(count).zfill(3)}"

# ==========================================
# PAGE CONTENT
# ==========================================

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
    st.markdown('<div class="english-heading">समस्या पंजीकरण</div>', unsafe_allow_html=True)
    if not st.session_state.hrms_verified:
        hrms_input = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6).upper().strip()
        if st.button("Verify ID / सत्यापित करें"):
            if len(hrms_input) == 6 and hrms_input.isalpha():
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
        # Registration form fields (Designation, Trade, etc.) would follow here as per Master 1
        if st.button("⬅️ Back to Home"):
            st.session_state.hrms_verified = False
            go_to('landing')

# --- PAGE 3: STATUS CHECK ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">Grievance Status</div>', unsafe_allow_html=True)
    ref_input = st.text_input("Enter Reference Number*", placeholder="e.g. 20260201ABCDEF001").strip()
    if st.button("🔍 Check Status"):
        if ref_input:
            try:
                df = pd.DataFrame(get_sheet("GRIEVANCE").get_all_records())
                match = df[df['REFERENCE_NO'].astype(str) == ref_input]
                if not match.empty:
                    res = match.iloc[0]
                    st.success(f"Status: {res['STATUS']}")
                    st.info(f"**Officer Remark:** {res['OFFICER_REMARK']}")
                else: st.error("No record found.")
            except Exception as e: st.error(f"Error: {e}")
    if st.button("⬅️ Back to Home"): go_to('landing')

# --- PAGE 4: SUPERUSER LOGIN ---
elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Superuser Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">अधिकारी लॉगिन</div>', unsafe_allow_html=True)

    hrms_locked = st.session_state.super_verified
    s_hrms = st.text_input("Enter Your HRMS ID", value=st.session_state.active_super.get('HRMS_ID', ""), disabled=hrms_locked).upper().strip()

    if not st.session_state.super_verified:
        if st.button("Find User / यूजर खोजें"):
            try:
                df_off = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
                match = df_off[df_off['HRMS_ID'] == s_hrms]
                if not match.empty:
                    st.session_state.active_super = match.iloc[0].to_dict()
                    st.session_state.super_verified = True
                    st.rerun()
                else: st.error("❌ HRMS ID not found in Officer Mapping.")
            except Exception as e: st.error(f"Database Error: {e}")
    else:
        u = st.session_state.active_super
        st.success(f"✅ USER Found: {u['NAME']}, {u['RANK']}")
        
        login_key = st.text_input("Enter Key", type="password")
        if st.button("Login / लॉगिन करें"):
            if str(login_key) == str(u['LOGIN_KEY']):
                role = u['ROLE'].upper()
                if role == "ADMIN": go_to('admin_dashboard')
                elif role == "OFFICER": go_to('officer_dashboard')
                elif role == "BOTH": go_to('role_selection')
                st.rerun()
            else: st.error("❌ Invalid Key.")

    if st.button("⬅️ Back to Home"):
        st.session_state.super_verified = False
        st.session_state.active_super = {}
        go_to('landing')

# --- PAGE 5: ROLE SELECTION ---
elif st.session_state.page == 'role_selection':
    st.markdown(f'<div class="hindi-heading">Welcome {st.session_state.active_super["NAME"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Choose Dashboard</div>', unsafe_allow_html=True)
    if st.button("🛠️ Admin Dashboard"): go_to('admin_dashboard')
    if st.button("📋 Officer Dashboard"): go_to('officer_dashboard')

# --- DASHBOARDS ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading">Admin Dashboard</div>', unsafe_allow_html=True)
    if st.button("Logout"): go_to('landing')

elif st.session_state.page == 'officer_dashboard':
    st.markdown('<div class="hindi-heading">Officer Dashboard</div>', unsafe_allow_html=True)
    if st.button("Logout"): go_to('landing')
