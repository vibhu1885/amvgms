import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. SETUP
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 110 # Slightly smaller to fit side-by-side
APP_BG_COLOR = "#131419"

# Initialize State
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

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
# 1. LAYOUT CONFIGURATION
# ==========================================
st.set_page_config(page_title="GMS Alambagh", layout="wide")

# Determine Width: 1200px for Admin, 480px for Mobile Views
container_max_width = "1200px" if st.session_state.page == 'admin_dashboard' else "480px"

st.markdown(f"""
<style>
    /* HIDE HEADER/FOOTER */
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    /* MAIN CONTAINER: THE 480px LOCK */
    .block-container {{
        max-width: {container_max_width} !important;
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: 0 auto !important;
    }}

    /* HEADER ALIGNMENT (For Landing Page Side-by-Side) */
    .header-text {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }}

    /* HEADINGS */
    .hindi-heading {{ text-align: left; color: white; font-weight: 900; font-size: 18px; line-height: 1.2; margin-bottom: 5px; }}
    .english-heading {{ text-align: left; color: #fca311; font-weight: bold; font-size: 14px; margin-bottom: 0px; }}
    
    /* CENTERED HEADINGS (For other pages) */
    .centered-hindi {{ text-align: center; color: white; font-weight: 900; font-size: 22px; margin-bottom: 5px; }}
    .centered-english {{ text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 30px; }}

    /* INPUTS: LEFT ALIGNED TEXT, WHITE LABELS */
    .stTextInput label, .stSelectbox label, .stTextArea label {{
        color: white !important;
        font-weight: bold !important;
        text-align: left !important;
        display: block !important;
        width: 100%;
    }}
    .stTextInput, .stSelectbox, .stTextArea {{ width: 100% !important; }}

    /* BUTTONS: STRICT 300PX WIDTH & CENTERED */
    .stButton {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div.stButton > button {{
        background-color: #faf9f9 !important;
        color: #131419 !important;
        border: 4px solid #fca311 !important;
        border-radius: 20px !important;
        
        /* STRICT SIZE LOCK */
        width: 300px !important; 
        height: 70px !important;
        
        font-weight: 900 !important;
        font-size: 18px !important;
        margin: 10px auto !important; /* Physically centers the 300px button */
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    div.stButton > button:hover {{
        background-color: #a7c957 !important;
        transform: scale(1.02);
    }}
    div.stButton > button p {{ font-weight: 900 !important; margin: 0 !important; }}

    /* ADMIN CARDS */
    .card-box {{ display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
    .card {{ 
        background: white; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: 900; 
        color: #131419; 
        min-width: 140px; 
        flex: 1; 
    }}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
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

# --- PAGE 1: LANDING (Horizontal Layout) ---
if st.session_state.page == 'landing':
    
    # Create 2 Columns: Left for Logo, Right for Text
    # col_logo is narrow, col_text takes rest
    col_logo, col_text = st.columns([1, 2.5])
    
    with col_logo:
        if os.path.exists(LOGO_PATH): 
            st.image(LOGO_PATH, width=LOGO_WIDTH)
            
    with col_text:
        # Using custom class to vertically center text if needed
        st.markdown(
            """
            <div class="header-text">
                <div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>
                <div class="english-heading">Grievance Management System</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.write("") # Spacer
    st.write("---") # Visual separator
    st.write("") 

    # Buttons (Will be exactly 300px and centered due to CSS)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="centered-hindi">Grievance Registration</div>', unsafe_allow_html=True)
    
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter HRMS ID (HRMS आईडी)*", max_chars=6).upper().strip()
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
                    new_row = [ref_no, datetime.now().strftime("%d-%m-%Y %H:%M"), st.session_state.active_hrms, st.session_state.found_emp_name, 
                               emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "NEW", "N/A", "N/A"]
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
    st.markdown('<div class="centered-hindi">Grievance Status</div>', unsafe_allow_html=True)
    ref_in = st.text_input("Enter Reference Number").strip()
    
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

# --- PAGE 4: LOGIN ---
elif st.session_state.page == 'login':
    st.markdown('<div class="centered-hindi">Superuser Login</div>', unsafe_allow_html=True)
    
    locked = st.session_state.super_verified
    s_hrms = st.text_input("Enter HRMS ID", value=st.session_state.active_super.get('HRMS_ID', ""), disabled=locked).upper().strip()
    
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

    if st.button("🏠 Back to Home"):
        st.session_state.super_verified = False
        go_to('landing')

# --- PAGE 5: ADMIN DASHBOARD (WIDE) ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="centered-hindi" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#fca311; font-weight:bold; margin-bottom:20px;">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())

    # Oversight
    st.markdown(f"""
    <div class="card-box">
        <div class="card" style="background:white;">TOTAL<br>{len(df)}</div>
        <div class="card" style="background:#3498db; color:white;">NEW<br>{len(df[df['STATUS']=='NEW'])}</div>
        <div class="card" style="background:#f1c40f;">PROCESS<br>{len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="card" style="background:#2ecc71; color:white;">RESOLVED<br>{len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1: f_hrms = st.text_input("Filter HRMS").upper()
    with c2: f_name = st.text_input("Filter Name")
    with c3: f_sec = st.text_input("Filter Section")
    with c4: 
        st.write("") 
        show_new = st.checkbox("Show 'NEW' Only")

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
        ac1, ac2, ac3 = st.columns([1.5, 5, 2.5])
        
        with ac1:
            color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
            st.write(f"**Ref:** {row['REFERENCE_NO']}")
            st.markdown(f"<span style='color:{color}; font-weight:900;'>{row['STATUS']}</span>", unsafe_allow_html=True)
            
        with ac2:
            st.write(f"**{row['EMP_NAME']}** | {row['SECTION']}")
            st.caption(f"{row['GRIEVANCE_TEXT']}")
            
        with ac3:
            if row['STATUS'] == "NEW":
                sel = st.selectbox("Assign", officers, key=f"adm_{i}")
                if sel != "Select Officer":
                    now = datetime.now().strftime("%d-%m-%Y %H:%M")
                    try:
                        cell = ws_g.find(str(row['REFERENCE_NO']))
                        ws_g.update_cell(cell.row, 11, "UNDER PROCESS")
                        ws_g.update_cell(cell.row, 12, f"Marked to: {sel} at {now}")
                        st.success("Assigned!")
                        st.rerun()
                    except: st.error("Update Failed")
            else:
                st.info(f"📍 {row['MARKED_OFFICER']}")
        st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.super_verified = False
        go_to('landing')
