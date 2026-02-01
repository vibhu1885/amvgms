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
BTN_BG = "#faf9f9"
BTN_TEXT = "#131419"
BTN_BORDER = "#fca311"

# ==========================================
# PAGE-SPECIFIC CSS (STRICT)
# ==========================================

def apply_global_styles(mode="narrow"):
    max_w = "1200px" if mode == "wide" else "500px"
    st.markdown(f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        .block-container {{ max-width: {max_w} !important; padding-top: 2rem !important; margin: auto; }}
        
        /* Master Button Style - Forced Bold & Shadows */
        div.stButton > button {{
            background-color: {BTN_BG} !important; color: {BTN_TEXT} !important;
            border: 4px solid {BTN_BORDER} !important; border-radius: 22px !important;
            width: 100% !important; height: 70px !important;
            font-weight: 900 !important; font-size: 17px !important;
            box-shadow: 0 8px 16px rgba(0,0,0,0.6) !important;
            transition: all 0.4s ease-in-out !important;
        }}
        div.stButton > button:hover {{ background-color: #a7c957 !important; transform: translateY(-4px); }}
        div.stButton > button p {{ font-weight: 900 !important; color: {BTN_TEXT} !important; }}

        /* Text Alignments */
        .hindi-heading, .english-heading {{ text-align: center !important; color: white; width: 100%; }}
        label {{ text-align: left !important; color: white !important; font-weight: bold !important; }}
        
        /* Dashboard Cards */
        .card-box {{ display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }}
        .card {{ padding: 15px; border-radius: 12px; text-align: center; font-weight: 900; color: #131419; min-width: 140px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# STATE & NAVIGATION
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

st.set_page_config(page_title="GMS Alambagh", layout="centered")

# ==========================================
# PAGE ROUTING
# ==========================================

# --- LANDING PAGE ---
if st.session_state.page == 'landing':
    apply_global_styles("narrow")
    
    # PHYSICAL LOCK: Using columns to force the center
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        if os.path.exists(LOGO_PATH):
            # Inner column for logo to be exactly centered
            l_1, l_2, l_3 = st.columns([1, 1.2, 1])
            with l_2: st.image(LOGO_PATH, width=LOGO_WIDTH)
            
        st.markdown('<div class="hindi-heading" style="font-size:22px; font-weight:900;">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
        st.markdown('<div class="english-heading" style="font-size:18px;">Grievance Management System</div>', unsafe_allow_html=True)
        
        # Every button inside col2 is now physically locked to the center 80% of the 500px container
        if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
        if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
        if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION PAGE ---
elif st.session_state.page == 'new_form':
    apply_global_styles("narrow")
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter HRMS ID*", max_chars=6).upper().strip()
        # Small columns for the verify button to keep it centered
        v1, v2, v3 = st.columns([1, 2, 1])
        with v2:
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
        emp_no = st.text_input("Employee Number*")
        # Rest of form...
        if st.button("📤 Grievance जमा करें"): st.info("Processing...")
        
    b1, b2, b3 = st.columns([1, 2, 1])
    with b2:
        if st.button("🏠 Back to Home"):
            st.session_state.hrms_verified = False
            go_to('landing')

# --- ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    apply_global_styles("wide")
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#fca311; font-weight:bold;">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    
    st.markdown(f"""
    <div class="card-box">
        <div class="card" style="background:white;">Total: {len(df)}</div>
        <div class="card" style="background:#3498db; color:white;">NEW: {len(df[df['STATUS']=='NEW'])}</div>
        <div class="card" style="background:#f1c40f;">PROCESS: {len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="card" style="background:#2ecc71; color:white;">RESOLVED: {len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)

    # Simplified table logic
    for i, row in df.iterrows():
        st.markdown("---")
        c1, c2, c3 = st.columns([2, 5, 3])
        with c1: st.write(f"**Ref:** {row['REFERENCE_NO']}")
        with c2: st.write(f"**{row['EMP_NAME']}**\n{row['GRIEVANCE_TEXT']}")
        with c3:
            if row['STATUS'] == "NEW":
                if st.button("Mark Process", key=f"mark_{i}"):
                    ws_g.update_cell(i+2, 11, "UNDER PROCESS")
                    st.rerun()
            else: st.info(row['STATUS'])

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
