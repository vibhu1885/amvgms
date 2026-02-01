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

st.set_page_config(page_title="GMS Alambagh", layout="wide") 

# ==========================================
# STRICT ALIGNMENT ENGINE (CSS)
# ==========================================
custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: 1000px !important;
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
    }}

    /* Strict Logo Centering */
    [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
    [data-testid="stImage"] > img {{ margin: 0 auto !important; }}

    /* Strict Button Centering & FX */
    .stButton {{ width: 100% !important; display: flex !important; justify-content: center !important; }}
    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
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

    /* Admin Specific Styles */
    .admin-title {{ color: white; font-size: 38px; font-weight: 900; text-align: center; margin-bottom: 5px; }}
    .welcome-msg {{ color: #fca311; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 25px; }}
    
    .card-container {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }}
    .card {{ padding: 15px 20px; border-radius: 12px; text-align: center; font-weight: bold; color: #131419; min-width: 160px; }}
    .card-blue {{ background-color: #3498db; }}
    .card-yellow {{ background-color: #f1c40f; }}
    .card-green {{ background-color: #2ecc71; }}
    .card-white {{ background-color: #ffffff; }}

    .hindi-heading, .english-heading, label, .stMarkdown p {{ text-align: center !important; width: 100% !important; }}
    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; line-height: 1.4; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
    label {{ color: {LABEL_COLOR} !important; font-weight: bold; margin-top: 10px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# STATE MANAGEMENT
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

# --- LANDING ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION ---
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
        # Form logic here...
        if st.button("📤 Grievance जमा करें"):
            # Placeholder for actual submission logic from Master 2
            st.success("Grievance Submitted!")
            st.session_state.hrms_verified = False
    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- LOGIN ---
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
        u = st.session_state.active_super
        st.success(f"✅ USER Found: {u['NAME']} ({u['RANK']})")
        login_key = st.text_input("Enter Login Key", type="password")
        if st.button("🔓 Login"):
            if str(login_key) == str(u['LOGIN_KEY']):
                role = u['ROLE'].upper()
                if role == "ADMIN": go_to('admin_dashboard')
                elif role == "OFFICER": go_to('officer_dashboard')
                elif role == "BOTH": go_to('role_selection')
                st.rerun()
            else: st.error("❌ Invalid Key.")
    if st.button("🏠 Back to Home"):
        st.session_state.super_verified = False
        st.session_state.active_super = {}
        go_to('landing')

# --- ROLE SELECTION ---
elif st.session_state.page == 'role_selection':
    st.markdown('<div class="hindi-heading">Select Dashboard</div>', unsafe_allow_html=True)
    if st.button("🛠️ Admin Dashboard"): go_to('admin_dashboard')
    if st.button("📋 Officer Dashboard"): go_to('officer_dashboard')

# --- ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="admin-title">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: <b>{st.session_state.active_super.get("NAME")}</b></div>', unsafe_allow_html=True)

    # 1. Oversight Stats
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

    # 2. Filters
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1: f_hrms = st.text_input("Filter HRMS").upper()
    with f_col2: f_name = st.text_input("Filter Name")
    with f_col3: f_sec = st.text_input("Filter Section")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1: show_new = st.button("🚩 Show Unmarked")
    with btn_col2: show_all = st.button("📋 Show All")

    # Filter Logic
    f_df = df.copy()
    if f_hrms: f_df = f_df[f_df['HRMS_ID'].str.contains(f_hrms, na=False)]
    if f_name: f_df = f_df[f_df['EMP_NAME'].str.contains(f_name, case=False, na=False)]
    if f_sec: f_df = f_df[f_df['SECTION'].str.contains(f_sec, case=False, na=False)]
    if show_new: f_df = f_df[f_df['STATUS'] == 'NEW']

    # 3. Action Table
    off_ws = get_sheet("OFFICER_MAPPING")
    off_df = pd.DataFrame(off_ws.get_all_records())
    officers = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])].iterrows()]

    for i, row in f_df.iterrows():
        st.markdown("---")
        c1, c2, c3 = st.columns([2, 5, 3])
        with c1:
            color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
            st.write(f"**Ref:** {row['REFERENCE_NO']}")
            st.markdown(f"<span style='color:{color}; font-weight:900;'>{row['STATUS']}</span>", unsafe_allow_html=True)
        with c2:
            st.write(f"**{row['EMP_NAME']}** ({row['DESIGNATION']})")
            st.write(f"_{row['GRIEVANCE_TEXT']}_")
        with c3:
            if row['STATUS'] == "NEW":
                sel = st.selectbox("Assign To", officers, key=f"sel_{i}")
                if sel != "Select Officer":
                    row_idx = i + 2
                    now = datetime.now().strftime("%d-%m-%Y %H:%M")
                    ws_g.update_cell(row_idx, 11, "UNDER PROCESS")
                    ws_g.update_cell(row_idx, 12, f"Marked to: {sel} at {now}")
                    st.success("Assigned!")
                    st.rerun()
            else:
                st.info(row['MARKED_OFFICER'])

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
