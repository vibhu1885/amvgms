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
LABEL_COLOR = "#FFFFFF"

# Button Settings
BTN_BG = "#faf9f9"
BTN_TEXT = "#131419"
BTN_BORDER = "#fca311"
BTN_HOVER = "#a7c957"

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
    count = len(df_grievance[df_grievance['HRMS_ID'] == hrms_id]) + 1
    return f"{date_str}{hrms_id}{str(count).zfill(3)}"

# ==========================================
# 1. PAGE LAYOUT DEFINITIONS (CSS)
# ==========================================

def inject_layout(mode="centered"):
    """
    mode='centered': strictly for landing/login. Everything centered.
    mode='form': labels left-aligned, logo/buttons centered.
    mode='wide': for Admin/Officer tables.
    """
    max_w = "480px" if mode != "wide" else "1200px"
    label_align = "left" if mode == "form" else "center"
    
    css = f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        .block-container {{ max-width: {max_w} !important; padding-top: 2rem !important; margin: auto; }}
        
        /* Logo & Button Centering */
        [data-testid="stImage"], .stButton {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
        [data-testid="stImage"] img {{ margin: 0 auto !important; }}
        
        /* Master Button Style */
        div.stButton > button {{
            background-color: {BTN_BG} !important; color: {BTN_TEXT} !important;
            border: 4px solid {BTN_BORDER} !important; border-radius: 22px !important;
            width: 300px !important; height: 70px !important; margin: 12px auto !important;
            font-weight: 900 !important; font-size: 17px !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.5);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }}
        div.stButton > button:hover {{ background-color: {BTN_HOVER} !important; transform: translateY(-4px) scale(1.03) !important; }}

        /* Text Alignments */
        .hindi-heading, .english-heading {{ text-align: center !important; color: white; width: 100%; }}
        label {{ text-align: {label_align} !important; color: white !important; font-weight: bold !important; width: 100% !important; display: block; }}
        
        /* Admin Cards */
        .card-box {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }}
        .card {{ padding: 15px; border-radius: 12px; text-align: center; font-weight: 900; color: #131419; min-width: 140px; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 2. PAGE ROUTING
# ==========================================

# --- LANDING PAGE ---
if st.session_state.page == 'landing':
    inject_layout("centered")
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading" style="font-size:22px; font-weight:900;">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading" style="font-size:18px;">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION PAGE ---
elif st.session_state.page == 'new_form':
    inject_layout("form")
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6).upper().strip()
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
        # Form inputs (Left Aligned)
        emp_no = st.text_input("Employee Number*")
        # [Dropdowns and text areas would go here]
        if st.button("📤 Grievance जमा करें"):
            st.info("Form logic active...")
    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- SUPERUSER LOGIN ---
elif st.session_state.page == 'login':
    inject_layout("centered")
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
    inject_layout("wide")
    st.markdown('<div class="hindi-heading" style="font-size:35px; font-weight:900;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#fca311; font-weight:bold; font-size:20px;">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    
    # Master Oversight
    st.markdown(f"""
    <div class="card-box">
        <div class="card" style="background:#ffffff;">Total<br>{len(df)}</div>
        <div class="card" style="background:#3498db;">NEW<br>{len(df[df['STATUS']=='NEW'])}</div>
        <div class="card" style="background:#f1c40f;">PROCESS<br>{len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="card" style="background:#2ecc71;">RESOLVED<br>{len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    c1, c2, c3 = st.columns(3)
    with c1: f_hrms = st.text_input("Filter HRMS").upper()
    with c2: f_name = st.text_input("Filter Name")
    with c3: f_sec = st.text_input("Filter Section")

    # Selection Buttons
    b1, b2 = st.columns(2)
    with b1: show_new = st.button("🚩 Show Unmarked")
    with b2: show_all = st.button("📋 Show All")

    # Filter Logic
    f_df = df.copy()
    if f_hrms: f_df = f_df[f_df['HRMS_ID'].str.contains(f_hrms, na=False)]
    if f_name: f_df = f_df[f_df['EMP_NAME'].str.contains(f_name, case=False, na=False)]
    if f_sec: f_df = f_df[f_df['SECTION'].str.contains(f_sec, case=False, na=False)]
    if show_new: f_df = f_df[f_df['STATUS'] == 'NEW']

    # Action Table
    off_df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
    officers = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])].iterrows()]

    for i, row in f_df.iterrows():
        st.markdown("---")
        t_col1, t_col2, t_col3 = st.columns([2, 6, 4])
        with t_col1:
            color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
            st.markdown(f"**Ref:** {row['REFERENCE_NO']}")
            st.markdown(f"<span style='color:{color}; font-weight:900;'>{row['STATUS']}</span>", unsafe_allow_html=True)
        with t_col2:
            st.write(f"**{row['EMP_NAME']}** | {row['SECTION']}")
            st.write(f"_{row['GRIEVANCE_TEXT']}_")
        with t_col3:
            if row['STATUS'] == "NEW":
                sel = st.selectbox("Assign to Officer", officers, key=f"adm_{i}")
                if sel != "Select Officer":
                    now = datetime.now().strftime("%d-%m-%Y %H:%M")
                    ws_g.update_cell(i+2, 11, "UNDER PROCESS")
                    ws_g.update_cell(i+2, 12, f"Marked to: {sel} at {now}")
                    st.success("Assigned!")
                    st.rerun()
            else:
                st.info(f"📍 {row['MARKED_OFFICER']}")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
