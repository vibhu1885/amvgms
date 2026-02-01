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

if 'page' not in st.session_state: st.session_state.page = 'landing'

st.set_page_config(
    page_title="GMS Alambagh", 
    layout="wide" if st.session_state.page == 'admin_dashboard' else "centered"
)

# ==========================================
# THE "TOTAL CENTER LOCK" CSS ENGINE
# ==========================================
max_w = "1200px" if st.session_state.page == 'admin_dashboard' else "480px"

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: {max_w} !important;
        padding-top: 1.5rem !important;
        margin: auto !important;
    }}

    /* --- LOGO: CENTER LOCK --- */
    [data-testid="stImage"] {{
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    [data-testid="stImage"] img {{ margin: 0 auto !important; }}

    /* --- BUTTONS: CENTER LOCK & BOLD TEXT --- */
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

    /* --- FORM FIELDS: LEFT ALIGN LABELS --- */
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
# NAVIGATION & STATE
# ==========================================
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# PAGE ROUTING
# ==========================================

# --- PAGE 1: LANDING ---
if st.session_state.page == 'landing':
    # Additional centering for the Logo
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
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
        try:
            dd_df = pd.DataFrame(get_sheet("DROPDOWN_MAPPINGS").get_all_records())
            designations = ["Select"] + [x for x in dd_df['DESIGNATION_LIST'].dropna().unique().tolist() if x]
            trades = ["Select"] + [x for x in dd_df['TRADE_LIST'].dropna().unique().tolist() if x]
            g_types = ["Select"] + [x for x in dd_df['GRIEVANCE_TYPE_LIST'].dropna().unique().tolist() if x]
        except:
            designations = trades = g_types = ["Select"]

        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        emp_desig = st.selectbox("Employee Designation*", designations)
        emp_trade = st.selectbox("Employee Trade*", trades)
        emp_sec = st.text_input("Employee Section*")
        g_type = st.selectbox("Grievance Type*", g_types)
        g_text = st.text_area("Brief of Grievance*", max_chars=1000)

        if st.button("📤 Grievance जमा करें"):
            if not any(x in [None, "", "Select"] for x in [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]):
                try:
                    ws = get_sheet("GRIEVANCE")
                    df_g = pd.DataFrame(ws.get_all_records())
                    count = len(df_g[df_g['HRMS_ID'] == st.session_state.active_hrms]) + 1
                    ref_no = f"{datetime.now().strftime('%Y%m%d')}{st.session_state.active_hrms}{str(count).zfill(3)}"
                    new_row = [ref_no, datetime.now().strftime("%d-%m-%Y %H:%M"), st.session_state.active_hrms, st.session_state.found_emp_name, 
                               emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "NEW", "N/A", "N/A"]
                    ws.append_row(new_row)
                    st.success(f"✅ Registered! Ref No: {ref_no}")
                    st.balloons()
                    st.session_state.hrms_verified = False
                except Exception as e: st.error(f"Error: {e}")
    if st.button("🏠 Back to Home"):
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
                    st.markdown(f"### Status: {res['STATUS']}")
                    st.info(f"**Remarks:** {res['OFFICER_REMARK']}")
                else: st.error("❌ No record found.")
            except Exception as e: st.error(f"Error: {e}")
    if st.button("🏠 Back to Home"): go_to('landing')

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
        st.session_state.active_super = {}
        go_to('landing')

# --- PAGE 5: ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#fca311; font-weight:bold;">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)
    
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    
    st.markdown(f"""
    <div class="card-box">
        <div class="card" style="background:white;">Total: {len(df)}</div>
        <div class="card" style="background:#3498db; color:white;">NEW: {len(df[df['STATUS']=='NEW'])}</div>
        <div class="card" style="background:#f1c40f;">UNDER PROCESS: {len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="card" style="background:#2ecc71; color:white;">RESOLVED: {len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Selection buttons and Table
    off_df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
    officers = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])].iterrows()]
    
    for i, row in df.iterrows():
        st.markdown("---")
        c1, c2, c3 = st.columns([2, 5, 3])
        with c1: st.write(f"**Ref:** {row['REFERENCE_NO']}\n**Status:** {row['STATUS']}")
        with c2: st.write(f"**{row['EMP_NAME']}**\n{row['GRIEVANCE_TEXT']}")
        with c3:
            if row['STATUS'] == "NEW":
                sel = st.selectbox("Assign", officers, key=f"adm_{i}")
                if sel != "Select Officer":
                    row_idx = i + 2
                    now = datetime.now().strftime("%d-%m-%Y %H:%M")
                    ws_g.update_cell(row_idx, 11, "UNDER PROCESS")
                    ws_g.update_cell(row_idx, 12, f"Marked to: {sel} at {now}")
                    st.rerun()
            else:
                st.info(f"📍 {row['MARKED_OFFICER']}")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
