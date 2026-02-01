import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. DATABASE CONNECTION & SETUP
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 130
APP_BG_COLOR = "#131419"

# Configure the page once at the start
st.set_page_config(page_title="GMS Alambagh", layout="centered")

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
# 1. DYNAMIC CSS GENERATOR
# ==========================================
def inject_css(mode="narrow"):
    # Wide for Admin, Narrow for everything else
    max_w = "1200px" if mode == "wide" else "480px"
    
    st.markdown(f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        
        /* Dynamic Width Control */
        .block-container {{
            max-width: {max_w} !important;
            padding-top: 1.5rem !important;
            margin: auto !important;
        }}

        /* Master Button Styling */
        div.stButton > button {{
            background-color: #faf9f9 !important;
            color: #131419 !important;
            border: 4px solid #fca311 !important;
            border-radius: 22px !important;
            width: 100% !important;
            height: 70px !important;
            font-weight: 900 !important;
            font-size: 17px !important;
            box-shadow: 0 8px 16px rgba(0,0,0,0.6);
            transition: all 0.3s ease-in-out;
            margin-bottom: 10px !important;
        }}
        div.stButton > button:hover {{
            background-color: #a7c957 !important;
            transform: translateY(-3px);
            box-shadow: 0 12px 20px rgba(167, 201, 87, 0.4);
        }}
        div.stButton > button p {{ font-weight: 900 !important; }}

        /* Text Alignment Defaults */
        .hindi-heading {{ color: white; text-align: center; font-weight: 900; font-size: 22px; margin-bottom: 5px; }}
        .english-heading {{ color: white; text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 25px; }}
        
        label {{ color: white !important; font-weight: bold !important; }}
        
        /* Admin Cards */
        .card-box {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }}
        .card {{ padding: 15px; border-radius: 12px; text-align: center; font-weight: 900; color: #131419; min-width: 140px; flex: 1; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page):
    st.session_state.page = page
    st.rerun()

def generate_ref_no(hrms_id, df_grievance):
    date_str = datetime.now().strftime("%Y%m%d")
    count = 1
    if not df_grievance.empty and 'HRMS_ID' in df_grievance.columns:
        count = len(df_grievance[df_grievance['HRMS_ID'] == hrms_id]) + 1
    return f"{date_str}{hrms_id}{str(count).zfill(3)}"

# ==========================================
# 3. PAGE LOGIC
# ==========================================

# --- LANDING PAGE ---
def show_landing():
    inject_css("narrow")
    
    # Use columns to force center alignment physically
    col_l, col_center, col_r = st.columns([1, 8, 1])
    with col_center:
        if os.path.exists(LOGO_PATH):
            # Nested columns to center the image perfectly
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2: st.image(LOGO_PATH, use_container_width=True)
            
        st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
        st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
        
        if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
        if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
        if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION PAGE ---
def show_registration():
    inject_css("narrow")
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">समस्या पंजीकरण</div>', unsafe_allow_html=True)
    
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter HRMS ID*", max_chars=6).upper().strip()
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
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
        
        # Fetch Dropdowns
        try:
            dd_df = pd.DataFrame(get_sheet("DROPDOWN_MAPPINGS").get_all_records())
            designations = ["Select"] + [x for x in dd_df['DESIGNATION_LIST'].dropna().unique().tolist() if x]
            trades = ["Select"] + [x for x in dd_df['TRADE_LIST'].dropna().unique().tolist() if x]
            g_types = ["Select"] + [x for x in dd_df['GRIEVANCE_TYPE_LIST'].dropna().unique().tolist() if x]
        except: designations = trades = g_types = ["Select"]

        emp_no = st.text_input("Employee Number*")
        emp_desig = st.selectbox("Designation*", designations)
        emp_trade = st.selectbox("Trade*", trades)
        emp_sec = st.text_input("Section*")
        g_type = st.selectbox("Grievance Type*", g_types)
        g_text = st.text_area("Complaint Details*", max_chars=1000)

        c1, c2, c3 = st.columns([0.5, 2, 0.5])
        with c2:
            if st.button("📤 Grievance जमा करें"):
                if not any(x in [None, "", "Select"] for x in [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]):
                    try:
                        ws = get_sheet("GRIEVANCE")
                        df_g = pd.DataFrame(ws.get_all_records())
                        ref_no = generate_ref_no(st.session_state.active_hrms, df_g)
                        new_row = [ref_no, datetime.now().strftime("%d-%m-%Y %H:%M"), st.session_state.active_hrms, st.session_state.found_emp_name, 
                                   emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "NEW", "N/A", "N/A"]
                        ws.append_row(new_row)
                        st.success(f"✅ Registered! Ref No: {ref_no}")
                        st.balloons()
                        st.session_state.hrms_verified = False
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error("⚠️ All fields are required.")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏠 Back to Home"):
            st.session_state.hrms_verified = False
            go_to('landing')

# --- STATUS CHECK ---
def show_status():
    inject_css("narrow")
    st.markdown('<div class="hindi-heading">Grievance Status</div>', unsafe_allow_html=True)
    ref_in = st.text_input("Enter Reference Number*").strip()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔍 Check Status"):
            try:
                df = pd.DataFrame(get_sheet("GRIEVANCE").get_all_records())
                match = df[df['REFERENCE_NO'].astype(str) == ref_in]
                if not match.empty:
                    res = match.iloc[0]
                    st.info(f"**Status:** {res['STATUS']}")
                    st.write(f"**Remark:** {res['OFFICER_REMARK']}")
                else: st.error("❌ Not Found")
            except: st.error("Error fetching data.")
            
        if st.button("🏠 Back to Home"): go_to('landing')

# --- LOGIN PAGE ---
def show_login():
    inject_css("narrow")
    st.markdown('<div class="hindi-heading">Superuser Login</div>', unsafe_allow_html=True)
    
    locked = st.session_state.super_verified
    s_hrms = st.text_input("Enter HRMS ID", value=st.session_state.active_super.get('HRMS_ID', ""), disabled=locked).upper().strip()
    
    c1, c2, c3 = st.columns([0.5, 2, 0.5])
    with c2:
        if not st.session_state.super_verified:
            if st.button("👤 Find User"):
                try:
                    df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
                    match = df[df['HRMS_ID'] == s_hrms]
                    if not match.empty:
                        st.session_state.active_super = match.iloc[0].to_dict()
                        st.session_state.super_verified = True
                        st.rerun()
                    else: st.error("User not found.")
                except: st.error("DB Error")
        else:
            st.success(f"✅ {st.session_state.active_super['NAME']}")
            key = st.text_input("Password", type="password")
            if st.button("🔓 Login"):
                if str(key) == str(st.session_state.active_super['LOGIN_KEY']):
                    role = st.session_state.active_super['ROLE'].upper()
                    if role == "ADMIN": go_to('admin_dashboard')
                    elif role == "OFFICER": go_to('officer_dashboard')
                    elif role == "BOTH": go_to('role_selection')
                else: st.error("Invalid Key")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏠 Back to Home"):
            st.session_state.super_verified = False
            go_to('landing')

# --- ADMIN DASHBOARD ---
def show_admin():
    inject_css("wide")
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#fca311; font-weight:bold; margin-bottom:20px;">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())

    # Master Oversight Cards
    st.markdown(f"""
    <div class="card-box">
        <div class="card" style="background:white;">Total: {len(df)}</div>
        <div class="card" style="background:#3498db; color:white;">NEW: {len(df[df['STATUS']=='NEW'])}</div>
        <div class="card" style="background:#f1c40f;">PROCESS: {len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="card" style="background:#2ecc71; color:white;">RESOLVED: {len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1: f_hrms = st.text_input("Filter HRMS").upper()
    with c2: f_name = st.text_input("Filter Name")
    with c3: f_sec = st.text_input("Filter Section")
    with c4: show_new = st.checkbox("Show Only 'NEW'")

    f_df = df.copy()
    if f_hrms: f_df = f_df[f_df['HRMS_ID'].str.contains(f_hrms, na=False)]
    if f_name: f_df = f_df[f_df['EMP_NAME'].str.contains(f_name, case=False, na=False)]
    if f_sec: f_df = f_df[f_df['SECTION'].str.contains(f_sec, case=False, na=False)]
    if show_new: f_df = f_df[f_df['STATUS'] == 'NEW']

    # Action Table
    off_df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
    officers = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])].iterrows()]

    st.markdown("---")
    for i, row in f_df.iterrows():
        c1, c2, c3 = st.columns([1.5, 5, 2.5])
        with c1:
            color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
            st.write(f"**Ref:** {row['REFERENCE_NO']}")
            st.markdown(f"<span style='color:{color}; font-weight:900;'>{row['STATUS']}</span>", unsafe_allow_html=True)
        with c2:
            st.write(f"**{row['EMP_NAME']}** ({row['HRMS_ID']}) | {row['SECTION']}")
            st.write(f"_{row['GRIEVANCE_TEXT']}_")
        with c3:
            if row['STATUS'] == "NEW":
                sel = st.selectbox("Assign", officers, key=f"adm_{i}")
                if sel != "Select Officer":
                    now = datetime.now().strftime("%d-%m-%Y %H:%M")
                    # Update Cells: Columns 11 (Status) and 12 (Remark/Marked)
                    # Note: Row index in GSheets is i + 2 (1-based + header)
                    # BUT 'i' here is from filtered df, so we must find real index. 
                    # For simplicity in this snippets, we assume standard order or direct access.
                    # Ideally: Use Unique Ref ID to find row.
                    cell = ws_g.find(str(row['REFERENCE_NO']))
                    ws_g.update_cell(cell.row, 11, "UNDER PROCESS")
                    ws_g.update_cell(cell.row, 12, f"Marked to: {sel} at {now}")
                    st.success("Assigned!")
                    st.rerun()
            else:
                st.info(f"📍 {row['MARKED_OFFICER']}")
        st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if st.session_state.page == 'landing': show_landing()
elif st.session_state.page == 'new_form': show_registration()
elif st.session_state.page == 'status_check': show_status()
elif st.session_state.page == 'login': show_login()
elif st.session_state.page == 'admin_dashboard': show_admin()
elif st.session_state.page == 'role_selection':
    inject_css("narrow")
    st.markdown('<div class="hindi-heading">Select Dashboard</div>', unsafe_allow_html=True)
    if st.button("🛠️ Admin Dashboard"): go_to('admin_dashboard')
    if st.button("📋 Officer Dashboard"): go_to('officer_dashboard')
