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

# Always start with centered layout for Landing/Forms
st.set_page_config(page_title="GMS Alambagh", layout="centered")

# ==========================================
# DYNAMIC ALIGNMENT ENGINE (STRICT)
# ==========================================
# We use a conditional max-width: wide for Admin, narrow for others
max_width = "1000px" if st.session_state.get('page') == 'admin_dashboard' else "480px"

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: {max_width} !important;
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    /* STRICT IMAGE/LOGO CENTERING */
    [data-testid="stImage"] {{ 
        display: flex !important; 
        justify-content: center !important; 
        width: 100% !important; 
    }}
    [data-testid="stImage"] > img {{ margin: 0 auto !important; }}

    /* STRICT BUTTON CENTERING & BOLDNESS */
    .stButton {{ 
        width: 100% !important; 
        display: flex !important; 
        justify-content: center !important; 
    }}
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
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 10px 20px rgba(167, 201, 87, 0.4) !important;
    }}
    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important;
        margin: 0 !important;
    }}

    /* HEADING & LABEL CENTERING */
    .hindi-heading, .english-heading, label, .stMarkdown p {{
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }}
    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; line-height: 1.4; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
    label {{ color: {LABEL_COLOR} !important; font-weight: bold; margin-top: 10px; }}

    /* Admin Specific Card UI */
    .card-container {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }}
    .card {{ padding: 12px 20px; border-radius: 10px; text-align: center; font-weight: bold; color: #131419; min-width: 140px; }}
    .card-blue {{ background-color: #3498db; }}
    .card-yellow {{ background-color: #f1c40f; }}
    .card-green {{ background-color: #2ecc71; }}
    .card-white {{ background-color: #ffffff; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# STATE & LOGIC
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
# PAGE ROUTING
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
        # Full form fields (Designation, Trade, etc.) would go here...
        st.success(f"✅ Employee: {st.session_state.found_emp_name}")
        if st.button("📤 Grievance जमा करें"):
             st.info("Submission logic active.")
    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- PAGE 4: LOGIN ---
elif st.session_state.page == 'login':
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
        st.success(f"✅ {st.session_state.active_super['NAME']} ({st.session_state.active_super['RANK']})")
        key = st.text_input("Enter Login Key", type="password")
        if st.button("🔓 Login"):
            if str(key) == str(st.session_state.active_super['LOGIN_KEY']):
                role = st.session_state.active_super['ROLE'].upper()
                if role == "ADMIN": go_to('admin_dashboard')
                elif role == "OFFICER": go_to('officer_dashboard')
                elif role == "BOTH": go_to('role_selection')
                st.rerun()
            else: st.error("❌ Invalid Key.")
    if st.button("🏠 Back to Home"):
        st.session_state.super_verified = False
        go_to('landing')

# --- ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown(f'<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: <b>{st.session_state.active_super.get("NAME")}</b></div>', unsafe_allow_html=True)
    
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    
    st.markdown(f"""
    <div class="card-container">
        <div class="card card-white">Total: {len(df)}</div>
        <div class="card card-blue">NEW: {len(df[df['STATUS'] == 'NEW'])}</div>
        <div class="card card-yellow">UNDER PROCESS: {len(df[df['STATUS'] == 'UNDER PROCESS'])}</div>
        <div class="card card-green">RESOLVED: {len(df[df['STATUS'] == 'RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Table logic continues...
    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
