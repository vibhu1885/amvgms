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
# THE "TOTAL LOCK" ALIGNMENT ENGINE (CSS)
# ==========================================
max_w = "1100px" if st.session_state.get('page') == 'admin_dashboard' else "480px"

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: {max_w} !important;
        padding-top: 2rem !important;
        margin: auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    /* Global Block - Force Everything to Center by Default */
    [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    /* --- LOGO: CENTER LOCK --- */
    [data-testid="stImage"] {{
        display: flex !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }}

    /* --- BUTTONS: CENTER LOCK & BOLD FX --- */
    .stButton {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}

    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        height: {BTN_HEIGHT} !important;
        margin: 12px auto !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.6) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 12px 25px rgba(167, 201, 87, 0.5) !important;
    }}

    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important;
        color: {BTN_TEXT_COLOR} !important;
    }}

    /* --- FORM FIELDS: FORCE LEFT ALIGN FOR INPUTS/LABELS --- */
    /* Target the container of text inputs, selectboxes, and text areas */
    [data-testid="stFormSubmitButton"], .stTextInput, .stSelectbox, .stTextArea {{
        align-self: flex-start !important;
        width: 100% !important;
    }}

    label {{
        color: {LABEL_COLOR} !important;
        font-weight: bold !important;
        text-align: left !important;
        display: block !important;
        width: 100% !important;
        margin-top: 10px !important;
    }}
    
    .stMarkdown div p {{ text-align: left !important; }} /* Keep markdown descriptions left */

    /* Headings stay centered */
    .hindi-heading, .english-heading {{
        text-align: center !important;
        width: 100% !important;
        color: {HEADING_COLOR};
        font-weight: 900;
        display: block !important;
    }}
    .hindi-heading {{ font-size: 24px; line-height: 1.4; }}
    .english-heading {{ font-size: 18px; margin-bottom: 20px; }}

    /* Admin Card Styles */
    .card-container {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; width: 100%; }}
    .card {{ padding: 15px; border-radius: 12px; text-align: center; font-weight: 900; color: #131419; min-width: 150px; flex: 1; }}
    .card-blue {{ background-color: #3498db; }}
    .card-yellow {{ background-color: #f1c40f; }}
    .card-green {{ background-color: #2ecc71; }}
    .card-white {{ background-color: #ffffff; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# LOGIC & NAVIGATION
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(p): st.session_state.page = p

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
        # Registration form fields (Designation, Trade, etc.) logic...
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
                r = st.session_state.active_super['ROLE'].upper()
                if r == "ADMIN": go_to('admin_dashboard')
                elif r == "OFFICER": go_to('officer_dashboard')
                elif r == "BOTH": go_to('role_selection')
                st.rerun()
            else: st.error("❌ Invalid Key.")
    if st.button("🏠 Back to Home"):
        st.session_state.super_verified = False
        go_to('landing')

# --- PAGE 5: ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:38px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: <b>{st.session_state.active_super.get("NAME")}</b></div>', unsafe_allow_html=True)
    
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    
    # Oversight
    st.markdown(f"""
    <div class="card-container">
        <div class="card card-white">TOTAL<br>{len(df)}</div>
        <div class="card card-blue">NEW<br>{len(df[df['STATUS']=='NEW'])}</div>
        <div class="card card-yellow">PROCESS<br>{len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="card card-green">RESOLVED<br>{len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Table & Marking Logic...
    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
