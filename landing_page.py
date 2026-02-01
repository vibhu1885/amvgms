import streamlit as st
import os
import pandas as pd
import time
import pytz
import textwrap
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. SETUP & TIMEZONE
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 225
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
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime("%d-%m-%Y %H:%M")

def get_ist_date_str():
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
    [data-testid="stImage"] {{ display: flex; justify-content: center; width: 100%; margin-bottom: 0px; }}
    [data-testid="stImage"] img {{ margin: 0 auto; }}

    /* 3. HEADINGS */
    .hindi-heading {{ text-align: center; color: white; font-weight: 900; font-size: 28px; width: 100%; }}
    .english-heading {{ text-align: center; color: orange; font-weight: bold; font-size: 22px; margin-bottom: 30px; width: 100%; }}
    .welcome-msg {{ text-align: center; color: #fca311; font-weight: 900; font-size: 24px; margin-bottom: 25px; width: 100%; }}

    /* 4. INPUTS */
    .stTextInput label, .stSelectbox label, .stTextArea label {{
        color: white !important; font-weight: bold !important; text-align: left !important; display: block !important; width: 100%;
    }}
    .stTextInput, .stSelectbox, .stTextArea {{ width: 100% !important; }}

    /* 5. BUTTONS (330px Fixed) */
    div.stButton > button {{
        background-color: #faf9f9 !important;
        color: #131419 !important;
        border: 4px solid #fca311 !important;
        border-radius: 20px !important;
        width: 330px !important; 
        height: 70px !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        margin: 10px auto !important; 
        display: block !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease-in-out !important;
    }}
    div.stButton > button:hover {{
        background-color: #a7c957 !important;
        color: #fff !important;
        border-color: #a7c957 !important;
        transform: translateY(-4px) scale(1.04) !important;
    }}
    div.stButton > button p {{ 
        font-weight: 900 !important; 
        font-size: 17px !important;
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

    /* 7. STATUS CARD STYLE (UPDATED) */
    .g-card {{
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        border-left: 10px solid #ccc; /* Will be overridden by inline style */
        color: #131419;
        font-family: sans-serif;
    }}
    .g-ref {{ font-size: 16px; font-weight: 900; color: #b4541a; margin-bottom: 10px; border-bottom: 2px solid rgba(0,0,0,0.1); padding-bottom: 8px; }}
    .g-label {{ font-size: 16px; font-weight: bold; color: #34240c; text-transform: uppercase; margin-top: 12px; letter-spacing: 0.5px; }}
    .g-value {{ font-size: 13px; color: #000; font-weight: 600; line-height: 1.4; }}
    
    /* Action Badges */
    .badge-base {{ display: inline-block; padding: 8px 14px; border-radius: 20px; font-size: 15px; font-weight: 900; margin-top: 5px; border: 1px solid rgba(0,0,0,0.1); }}
    .badge-new {{ background-color: #076db5; color: white; }}
    .badge-process {{ background-color: #eca623; color: white; }}
    .badge-resolved {{ background-color: #00a436; color: white; }}
    
    .remark-box {{
        background-color: rgba(255,255,255,0.6);
        border-left: 5px solid #2ecc71;
        padding: 12px;
        margin-top: 12px;
        color: #000;
        font-weight: 500;
        border-radius: 0 5px 5px 0;
    }}

    /* Table Details */
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
    st.markdown('<div class="english-heading">Grievance Registration</div>', unsafe_allow_html=True)
    
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter your HRMS ID (अपनी HRMS आईडी दर्ज करें)*", max_chars=6).upper().strip()
        if st.button("🔎 Verify User"):
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
        st.success(f"✅ HRMS ID Verified: {st.session_state.found_emp_name}")
        
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
                    ws.append_row(new_row)
                    st.success(f"✅ Registered! Ref No: {ref_no}")
                    st.balloons()
                    st.session_state.hrms_verified = False
                except Exception as e: st.error(f"Error: {e}")
            else: st.error("⚠️ All fields are required.")

    if st.button("🏠 Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- PAGE 3: STATUS CHECK (COLOR CODED BACKGROUNDS) ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">Grievance History</div>', unsafe_allow_html=True)
    hrms_in = st.text_input("Enter Your HRMS ID").upper().strip()
    
    if st.button("🔍 Find Records"):
        if not hrms_in: 
            st.warning("⚠️ Please enter HRMS ID.")
        else:
            try:
                df = pd.DataFrame(get_sheet("GRIEVANCE").get_all_records())
                matches = df[df['HRMS_ID'].astype(str) == hrms_in]
                
                if not matches.empty:
                    st.success(f"Found {len(matches)} Record(s)")
                    matches = matches.iloc[::-1]
                    
                    for i, row in matches.iterrows():
                        status = row['STATUS']
                        
                        # --- DYNAMIC COLOR SCHEME ---
                        bg_color = "#fff"
                        border_color = "#ccc"
                        action_text = ""
                        action_class = ""
                        extra_details = ""
                        
                        if status == "NEW":
                            bg_color = "#e3f2fd" # Light Blue BG
                            border_color = "#1565c0"
                            action_text = "Yet to Assign"
                            action_class = "badge-new"
                        elif status == "UNDER PROCESS":
                            bg_color = "#fff9c4" # Light Yellow BG
                            border_color = "#fbc02d"
                            action_text = "Assigned to Related Officer"
                            action_class = "badge-process"
                            
                            assign_date = row.get('ASSIGN_DATE', 'N/A')
                            extra_details = textwrap.dedent(f"""
                            <div style="margin-top:10px;">
                                <span style="font-weight:900; color:#000;">Assigned On:</span> 
                                <span style="color:#000; font-weight:600;">{assign_date}</span>
                            </div>""")
                        
                        elif status == "RESOLVED":
                            bg_color = "#e8f5e9" # Light Green BG
                            border_color = "#2e7d32"
                            action_text = "Resolved"
                            action_class = "badge-resolved"
                            
                            assign_date = row.get('ASSIGN_DATE', 'N/A')
                            resolve_date = row.get('RESOLVE_DATE', 'N/A')
                            officer = row.get('MARKED_OFFICER', 'N/A')
                            remark = row.get('OFFICER_REMARK', 'N/A')
                            
                            extra_details = textwrap.dedent(f"""
                            <div style="margin-top:10px;">
                                <div>
                                    <span style="font-weight:900; color:#000;">Assigned On:</span> 
                                    <span style="color:#000; font-weight:600;">{assign_date}</span>
                                </div>
                                <div>
                                    <span style="font-weight:900; color:#000;">Resolved On:</span> 
                                    <span style="color:#000; font-weight:600;">{resolve_date}</span>
                                </div>
                                <div class="remark-box">
                                    <b style="color:#000;">Remark by {officer}:</b><br>
                                    "{remark}"
                                </div>
                            </div>""")

                        card_html = textwrap.dedent(f"""
                        <div class="g-card" style="background-color: {bg_color}; border-left-color: {border_color};">
                            <div class="g-ref">Ref No: {row['REFERENCE_NO']}</div>
                            <div class="g-label">Grievance Description</div>
                            <div class="g-value">{row['GRIEVANCE_TEXT']}</div>
                            <div class="g-label">Action Taken</div>
                            <div class="badge-base {action_class}">{action_text}</div>
                            {extra_details}
                        </div>
                        """)
                        
                        st.markdown(card_html, unsafe_allow_html=True)

                else: st.error("❌ No grievances found for this HRMS ID.")
            except Exception as e: st.error(f"Error fetching data: {e}")
    
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
                    assign_date = row.get('ASSIGN_DATE', row.get('OFFICER_REMARK', 'N/A')) 
                    st.markdown(f"""
                    <div style="background-color: #2c2e3a; padding: 10px; border-radius: 8px; border: 1px solid #444;">
                        <span style="color: #fca311; font-weight: bold;">Assigned To:</span> <span style="color: white; font-weight: bold;">{row['MARKED_OFFICER']}</span>
                        <span style="color: #fca311; font-weight: bold; margin-left: 15px;">Date:</span> <span style="color: white;">{assign_date}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')

# --- PAGE 6: OFFICER DASHBOARD ---
elif st.session_state.page == 'officer_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Officer Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    my_name_rank = f"{st.session_state.active_super['NAME']} ({st.session_state.active_super['RANK']})"
    
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    my_df = df[df['MARKED_OFFICER'] == my_name_rank]

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

    st.write("### 🔽 Filter My Tasks")
    off_filter = st.radio("Show:", ["ALL", "PENDING", "RESOLVED"], horizontal=True, key="off_rad")
    
    view_df = my_df.copy()
    if off_filter == "PENDING": view_df = view_df[view_df['STATUS'] == 'UNDER PROCESS']
    elif off_filter == "RESOLVED": view_df = view_df[view_df['STATUS'] == 'RESOLVED']

    st.markdown("---")
    if view_df.empty: st.info("No tasks found.")
    else:
        for i, row in view_df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 4, 2])
                color = "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
                c1.markdown(f"**Ref:** `{row['REFERENCE_NO']}`")
                c2.markdown(f"**Status:** <span style='color:{color}; font-weight:bold;'>{row['STATUS']}</span>", unsafe_allow_html=True)
                c3.markdown(f"📅 Assigned: {row.get('ASSIGN_DATE', 'N/A')}")

                d1, d2, d3 = st.columns(3)
                d1.markdown(f"Name: **{row['EMP_NAME']}**<br>HRMS: {row['HRMS_ID']}", unsafe_allow_html=True)
                d2.markdown(f"Desig: {row['DESIGNATION']}<br>Section: {row['SECTION']}", unsafe_allow_html=True)
                d3.markdown(f"Type: {row['GRIEVANCE_TYPE']}", unsafe_allow_html=True)
                
                st.info(f"**Issue:** {row['GRIEVANCE_TEXT']}")

                if row['STATUS'] == "UNDER PROCESS":
                    rem_key = f"rem_{i}"
                    remark = st.text_area("Resolution Remarks (Mandatory)*", key=rem_key)
                    if st.button("✅ Mark as Resolved", key=f"btn_{i}"):
                        if not remark.strip():
                            st.error("⚠️ Please enter resolution remarks.")
                        else:
                            try:
                                now_ist = get_ist_time()
                                cell = ws_g.find(str(row['REFERENCE_NO']))
                                ws_g.update_cell(cell.row, 11, "RESOLVED")
                                ws_g.update_cell(cell.row, 14, remark)
                                ws_g.update_cell(cell.row, 15, now_ist)
                                st.success("Resolved Successfully!")
                                time.sleep(0.5)
                                st.rerun()
                            except: st.error("Update Error")
                else:
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
