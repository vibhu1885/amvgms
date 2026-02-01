import streamlit as st
import os
import pandas as pd
import time
import pytz
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. SETUP & TIMEZONE
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 130
APP_BG_COLOR = "#131419"

# Initialize State
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}
if 'admin_filter' not in st.session_state: st.session_state.admin_filter = 'ALL'
if 'officer_filter' not in st.session_state: st.session_state.officer_filter = 'ALL'

# --- TIMEZONE HELPER ---
def get_ist_time():
    """Returns current time in Indian Standard Time."""
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime("%d-%m-%Y %H:%M")

def get_ist_date_str():
    """Returns YYYYMMDD in IST for Ref No generation."""
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime("%Y%m%d")

# DATABASE CONNECT
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
# 1. LAYOUT & CSS CONFIGURATION
# ==========================================
st.set_page_config(page_title="GMS Alambagh", layout="wide")

# Container Logic: Wide for Dashboards, Narrow for Forms
is_dashboard = st.session_state.page in ['admin_dashboard', 'officer_dashboard']
container_max_width = "1200px" if is_dashboard else "480px"

st.markdown(f"""
<style>
    /* HIDE HEADER/FOOTER */
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    /* 1. MAIN CONTAINER */
    .block-container {{
        max-width: {container_max_width} !important;
        padding-top: 2rem !important;
        margin: 0 auto !important;
    }}

    /* 2. LOGO */
    [data-testid="stImage"] {{ display: flex; justify-content: center; width: 100%; margin-bottom: 15px; }}
    [data-testid="stImage"] img {{ margin: 0 auto; }}

    /* 3. HEADINGS */
    .hindi-heading {{ text-align: center; color: white; font-weight: 900; font-size: 22px; width: 100%; }}
    .english-heading {{ text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 30px; width: 100%; }}
    .welcome-msg {{ text-align: center; color: #fca311; font-weight: 900; font-size: 24px; margin-bottom: 25px; width: 100%; }}

    /* 4. INPUTS */
    .stTextInput label, .stSelectbox label, .stTextArea label {{
        color: white !important; font-weight: bold !important; text-align: left !important; display: block !important; width: 100%;
    }}
    .stTextInput, .stSelectbox, .stTextArea {{ width: 100% !important; }}

    /* 5. BUTTONS (300px Fixed) */
    div.stButton > button {{
        background-color: #faf9f9 !important;
        color: #131419 !important;
        border: 4px solid #fca311 !important;
        border-radius: 20px !important;
        width: 300px !important; 
        height: 70px !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        letter-spacing: 0.5px !important;
        margin: 10px auto !important; 
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease-in-out !important;
    }}
    
    div.stButton > button:hover {{
        background-color: #a7c957 !important;
        color: #fff !important;
        border-color: #a7c957 !important;
        transform: translateY(-4px) scale(1.02) !important;
    }}
    
    div.stButton > button p {{ 
        font-weight: 900 !important; 
        font-size: 20px !important;
        margin: 0 !important; 
    }}
    
    /* 6. SCORECARDS */
    .score-container {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }}
    .score-card {{
        flex: 1; min-width: 150px; padding: 15px; border-radius: 12px; text-align: center;
        color: #131419; font-weight: 900; box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }}
    .score-number {{ font-size: 28px; line-height: 1.2; }}
    .score-label {{ font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}

    /* 7. TABLE ROW STYLING */
    .detail-label {{ color: #fca311; font-weight: bold; font-size: 14px; }}
    .detail-val {{ color: white; font-weight: normal; font-size: 14px; margin-bottom: 5px; }}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def go_to(page):
    st.session_state.page = page
    st.rerun()

def generate_ref_no(hrms_id, df_grievance):
    date_str = get_ist_date_str()
    count = 1
    if not df_grievance.empty and 'HRMS_ID' in df_grievance.columns:
        count = len(df_grievance[df_grievance['HRMS_ID'] == hrms_id]) + 1
    return f"{date_str}{hrms_id}{str(count).zfill(3)}"

# ==========================================
# 3. PAGE LOGIC
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
        hrms_in = st.text_input("Enter HRMS ID (HRMS आईडी)*", max_chars=6).upper().strip()
        if st.button("🔎 Verify ID"):
            if not hrms_in: st.warning("⚠️ Enter HRMS ID.")
            else:
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
        st.success(f"✅ Verified: {st.session_state.found_emp_name}")
        
        try:
            dd_df = pd.DataFrame(get_sheet("DROPDOWN_MAPPINGS").get_all_records())
            designations = ["Select"] + [x for x in dd_df['DESIGNATION_LIST'].dropna().unique().tolist() if x]
            trades = ["Select"] + [x for x in dd_df['TRADE_LIST'].dropna().unique().tolist() if x]
            g_types = ["Select"] + [x for x in dd_df['GRIEVANCE_TYPE_LIST'].dropna().unique().tolist() if x]
        except: designations = trades = g_types = ["Select"]

        emp_no = st.text_input("Employee Number")
        emp_desig = st.selectbox("Designation", designations)
        emp_trade = st.selectbox("Trade", trades)
        emp_sec = st.text_input("Section")
        g_type = st.selectbox("Grievance Type", g_types)
        g_text = st.text_area("Complaint Details", max_chars=1000)

        if st.button("📤 Grievance जमा करें"):
            if not any(x in [None, "", "Select"] for x in [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]):
                try:
                    ws = get_sheet("GRIEVANCE")
                    df_g = pd.DataFrame(ws.get_all_records())
                    ref_no = generate_ref_no(st.session_state.active_hrms, df_g)
                    now_ist = get_ist_time()
                    new_row = [ref_no, now_ist, st.session_state.active_hrms, st.session_state.found_emp_name, 
                               emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "NEW", "N/A", "N/A", "N/A", "N/A"]
                    # N/A placeholders for: Marked Officer, Assign Date, Officer Remark, Resolve Date
                    ws.append_row(new_row)
                    st.success(f"✅ Registered! Ref No: {ref_no}")
                    st.balloons()
                    st.session_state.hrms_verified = False
                except Exception as e: st.error(f"Error: {e}")
            else: st.error("⚠️ All fields are required.")

    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- PAGE 3: STATUS CHECK ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">Grievance Status</div>', unsafe_allow_html=True)
    ref_in = st.text_input("Enter Reference Number").strip()
    
    if st.button("🔍 Check Status"):
        if not ref_in: st.warning("⚠️ Enter Reference Number.")
        else:
            try:
                df = pd.DataFrame(get_sheet("GRIEVANCE").get_all_records())
                match = df[df['REFERENCE_NO'].astype(str) == ref_in]
                if not match.empty:
                    res = match.iloc[0]
                    st.info(f"**Status:** {res['STATUS']}")
                    st.write(f"**Remark:** {res.get('OFFICER_REMARK', 'N/A')}")
                else: st.error("❌ Not Found")
            except: st.error("Error fetching data.")
    
    if st.button("🏠 Back to Home"): go_to('landing')

# --- PAGE 4: LOGIN ---
elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Superuser Login</div>', unsafe_allow_html=True)
    
    locked = st.session_state.super_verified
    s_hrms = st.text_input("Enter HRMS ID", value=st.session_state.active_super.get('HRMS_ID', ""), disabled=locked).upper().strip()
    
    if not st.session_state.super_verified:
        if st.button("👤 Find User"):
            if not s_hrms:
                st.warning("⚠️ Please enter an HRMS ID.")
            else:
                with st.spinner("Fetching Details..."):
                    try:
                        df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
                        match = df[df['HRMS_ID'] == s_hrms]
                        if not match.empty:
                            st.session_state.active_super = match.iloc[0].to_dict()
                            st.session_state.super_verified = True
                            st.rerun()
                        else: st.error("❌ User not found.")
                    except: st.error("Connection Error.")
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

    if st.button("🏠 Back to Home"):
        st.session_state.super_verified = False
        go_to('landing')

# --- PAGE 5: ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())

    # Scorecards
    count_total = len(df)
    count_new = len(df[df['STATUS']=='NEW'])
    count_process = len(df[df['STATUS']=='UNDER PROCESS'])
    count_resolved = len(df[df['STATUS']=='RESOLVED'])

    st.markdown(f"""
    <div class="score-container">
        <div class="score-card" style="background-color: #3498db; color: white;">
            <div class="score-number">{count_new}</div><div class="score-label">NEW</div>
        </div>
        <div class="score-card" style="background-color: #f1c40f;">
            <div class="score-number">{count_process}</div><div class="score-label">UNDER PROCESS</div>
        </div>
        <div class="score-card" style="background-color: #2ecc71; color: white;">
            <div class="score-number">{count_resolved}</div><div class="score-label">RESOLVED</div>
        </div>
        <div class="score-card" style="background-color: white;">
            <div class="score-number">{count_total}</div><div class="score-label">TOTAL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    st.write("### 🔽 Filter Data")
    filter_choice = st.radio("View Status:", options=["ALL", "NEW", "UNDER PROCESS", "RESOLVED"], horizontal=True, key="admin_rad")
    f_df = df.copy()
    if filter_choice != 'ALL': f_df = f_df[f_df['STATUS'] == filter_choice]

    # Table
    off_df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
    officers = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])].iterrows()]

    st.markdown("---")
    if f_df.empty: st.info("No records found.")
    else:
        for i, row in f_df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 4, 2])
                color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
                c1.markdown(f"**Ref:** `{row['REFERENCE_NO']}`")
                c2.markdown(f"**Status:** <span style='color:{color}; font-weight:bold;'>{row['STATUS']}</span>", unsafe_allow_html=True)
                c3.markdown(f"📅 {row['DATE_TIME']}")
                
                d1, d2, d3 = st.columns(3)
                d1.markdown(f"Name: **{row['EMP_NAME']}**<br>HRMS: {row['HRMS_ID']}", unsafe_allow_html=True)
                d2.markdown(f"Desig: {row['DESIGNATION']}<br>Section: {row['SECTION']}", unsafe_allow_html=True)
                d3.markdown(f"Type: {row['GRIEVANCE_TYPE']}", unsafe_allow_html=True)
                
                st.info(f"**Description:** {row['GRIEVANCE_TEXT']}")

                if row['STATUS'] == "NEW":
                    sel = st.selectbox("Assign To:", officers, key=f"adm_{i}")
                    if sel != "Select Officer":
                        try:
                            now = get_ist_time()
                            cell = ws_g.find(str(row['REFERENCE_NO']))
                            ws_g.update_cell(cell.row, 11, "UNDER PROCESS")
                            ws_g.update_cell(cell.row, 12, sel) # Col 12: Name
                            ws_g.update_cell(cell.row, 13, now) # Col 13: Date
                            st.success("Assigned!")
                            time.sleep(0.5)
                            st.rerun()
                        except: st.error("Update Failed")
                else:
                    assign_date = row.get('ASSIGN_DATE', row.get('OFFICER_REMARK', 'N/A')) # Compatibility
                    st.markdown(f"**Assigned To:** {row['MARKED_OFFICER']} | **Date:** {assign_date}")
                st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')

# --- PAGE 6: OFFICER DASHBOARD ---
elif st.session_state.page == 'officer_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Officer Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    # 1. Identity Check
    my_name_rank = f"{st.session_state.active_super['NAME']} ({st.session_state.active_super['RANK']})"
    
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())

    # 2. Filter My Grievances
    my_df = df[df['MARKED_OFFICER'] == my_name_rank]

    # 3. Scorecards
    cnt_total = len(my_df)
    cnt_pending = len(my_df[my_df['STATUS']=='UNDER PROCESS'])
    cnt_resolved = len(my_df[my_df['STATUS']=='RESOLVED'])

    st.markdown(f"""
    <div class="score-container">
        <div class="score-card" style="background-color: white;">
            <div class="score-number">{cnt_total}</div><div class="score-label">TOTAL</div>
        </div>
        <div class="score-card" style="background-color: #f1c40f;">
            <div class="score-number">{cnt_pending}</div><div class="score-label">PENDING</div>
        </div>
        <div class="score-card" style="background-color: #2ecc71; color: white;">
            <div class="score-number">{cnt_resolved}</div><div class="score-label">RESOLVED</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Filter
    st.write("### 🔽 Filter My Tasks")
    off_filter = st.radio("Show:", ["ALL", "PENDING", "RESOLVED"], horizontal=True, key="off_rad")
    
    view_df = my_df.copy()
    if off_filter == "PENDING": view_df = view_df[view_df['STATUS'] == 'UNDER PROCESS']
    elif off_filter == "RESOLVED": view_df = view_df[view_df['STATUS'] == 'RESOLVED']

    # 5. Table & Action
    st.markdown("---")
    if view_df.empty: st.info("No tasks found.")
    else:
        for i, row in view_df.iterrows():
            with st.container():
                # Header
                c1, c2, c3 = st.columns([2, 4, 2])
                color = "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
                c1.markdown(f"**Ref:** `{row['REFERENCE_NO']}`")
                c2.markdown(f"**Status:** <span style='color:{color}; font-weight:bold;'>{row['STATUS']}</span>", unsafe_allow_html=True)
                c3.markdown(f"📅 Assigned: {row.get('ASSIGN_DATE', 'N/A')}")

                # Details
                d1, d2, d3 = st.columns(3)
                d1.markdown(f"Name: **{row['EMP_NAME']}**<br>HRMS: {row['HRMS_ID']}", unsafe_allow_html=True)
                d2.markdown(f"Desig: {row['DESIGNATION']}<br>Section: {row['SECTION']}", unsafe_allow_html=True)
                d3.markdown(f"Type: {row['GRIEVANCE_TYPE']}", unsafe_allow_html=True)
                
                st.info(f"**Issue:** {row['GRIEVANCE_TEXT']}")

                # RESOLVE ACTION
                if row['STATUS'] == "UNDER PROCESS":
                    rem_key = f"rem_{i}"
                    # Mandatory Text Box
                    remark = st.text_area("Resolution Remarks (Mandatory)*", key=rem_key)
                    
                    if st.button("✅ Mark as Resolved", key=f"btn_{i}"):
                        if not remark.strip():
                            st.error("⚠️ Please enter resolution remarks.")
                        else:
                            try:
                                now_ist = get_ist_time()
                                cell = ws_g.find(str(row['REFERENCE_NO']))
                                # Update Columns: 
                                # 11=Status, 14=Officer Remark, 15=Resolve Date
                                ws_g.update_cell(cell.row, 11, "RESOLVED")
                                ws_g.update_cell(cell.row, 14, remark)
                                ws_g.update_cell(cell.row, 15, now_ist)
                                st.success("Resolved Successfully!")
                                time.sleep(0.5)
                                st.rerun()
                            except: st.error("Update Error")
                else:
                    # Show Resolution Details
                    st.markdown(f"""
                    <div style="background-color: #2c2e3a; padding: 10px; border-radius: 8px;">
                        <span style="color: #2ecc71; font-weight: bold;">Resolution:</span> {row.get('OFFICER_REMARK', 'N/A')}<br>
                        <span style="color: #2ecc71; font-weight: bold;">Date:</span> {row.get('RESOLVE_DATE', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')

elif st.session_state.page == 'role_selection':
    st.markdown('<div class="hindi-heading">Select Dashboard</div>', unsafe_allow_html=True)
    if st.button("🛠️ Admin Dashboard"): go_to('admin_dashboard')
    if st.button("📋 Officer Dashboard"): go_to('officer_dashboard')
