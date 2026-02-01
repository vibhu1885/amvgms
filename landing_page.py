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

st.set_page_config(page_title="GMS Alambagh", layout="wide") # Changed to Wide for Table

# ==========================================
# STRICT ALIGNMENT ENGINE (CSS)
# ==========================================
custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
    }}

    /* Header & Headings */
    .admin-title {{ color: white; font-size: 35px; font-weight: bold; text-align: center; margin-bottom: 10px; }}
    .welcome-msg {{ color: #fca311; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 20px; }}
    
    /* Oversight Cards */
    .card-container {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }}
    .card {{ padding: 15px 25px; border-radius: 15px; text-align: center; font-weight: bold; color: #131419; min-width: 150px; }}
    .card-blue {{ background-color: #3498db; }}
    .card-yellow {{ background-color: #f1c40f; }}
    .card-green {{ background-color: #2ecc71; }}
    .card-white {{ background-color: #ecf0f1; }}

    /* Table Styling */
    [data-testid="stTable"] {{ background-color: white; border-radius: 10px; overflow: hidden; }}
    
    /* Centering UI */
    .center-content {{ display: flex; flex-direction: column; align-items: center; width: 100%; }}
    
    /* Button Styles from Master 2 */
    .stButton {{ display: flex; justify-content: center; width: 100% !important; }}
    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        font-weight: 900 !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# NAVIGATION & STATE
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def go_to(page_name):
    st.session_state.page = page_name

# ==========================================
# PAGE CONTENT
# ==========================================

# (Landing, Registration, Status Check, and Login pages stay the same as Master Code 2)

# --- ADMIN DASHBOARD ---
if st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="admin-title">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    # 1. Fetch Data
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())
    
    # 2. Master Oversight Cards
    total = len(df)
    unmarked = len(df[df['STATUS'] == 'NEW'])
    under_p = len(df[df['STATUS'] == 'UNDER PROCESS'])
    resolved = len(df[df['STATUS'] == 'RESOLVED'])

    st.markdown(f"""
    <div class="card-container">
        <div class="card card-white">Total: {total}</div>
        <div class="card card-blue">NEW: {unmarked}</div>
        <div class="card card-yellow">UNDER PROCESS: {under_p}</div>
        <div class="card card-green">RESOLVED: {resolved}</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Filters
    col1, col2, col3 = st.columns(3)
    with col1: f_hrms = st.text_input("Filter by HRMS ID").upper()
    with col2: f_name = st.text_input("Filter by Name")
    with col3: f_sec = st.text_input("Filter by Section")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1: show_unmarked = st.button("🚩 Show Unmarked Grievances")
    with btn_col2: show_all = st.button("📋 Show All Grievances")

    # Apply Filters
    filtered_df = df.copy()
    if f_hrms: filtered_df = filtered_df[filtered_df['HRMS_ID'].str.contains(f_hrms, na=False)]
    if f_name: filtered_df = filtered_df[filtered_df['EMP_NAME'].str.contains(f_name, case=False, na=False)]
    if f_sec: filtered_df = filtered_df[filtered_df['SECTION'].str.contains(f_sec, case=False, na=False)]
    
    if show_unmarked: filtered_df = filtered_df[filtered_df['STATUS'] == 'NEW']

    # 4. Action Table
    st.markdown("---")
    
    # Fetch Officer List for Dropdown
    off_df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
    valid_officers = off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])]
    officer_options = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in valid_officers.iterrows()]

    # Iterate through rows to create the display
    for index, row in filtered_df.iterrows():
        # Define Color Coding
        status_color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
        
        with st.container():
            t_col1, t_col2, t_col3 = st.columns([1, 4, 2])
            with t_col1:
                st.markdown(f"**Ref:** {row['REFERENCE_NO']}")
                st.markdown(f"<span style='color:{status_color}; font-weight:bold;'>{row['STATUS']}</span>", unsafe_allow_html=True)
            
            with t_col2:
                st.write(f"**Emp:** {row['EMP_NAME']} | **Type:** {row['GRIEVANCE_TYPE']}")
                st.write(f"**Complaint:** {row['GRIEVANCE_TEXT']}")
            
            with t_col3:
                if row['STATUS'] == "NEW":
                    selected_off = st.selectbox(f"Mark to Officer", officer_options, key=f"off_{index}")
                    if selected_off != "Select Officer":
                        # UPDATE LOGIC
                        now_mark = datetime.now().strftime("%d-%m-%Y %H:%M")
                        row_idx = index + 2 # +1 for header, +1 for 0-index
                        ws_g.update_cell(row_idx, 11, "UNDER PROCESS")
                        ws_g.update_cell(row_idx, 12, f"{selected_off} at {now_mark}")
                        st.success(f"Assigned to {selected_off}")
                        st.rerun()
                else:
                    st.info(f"📍 {row['MARKED_OFFICER']}")

    if st.button("🚪 Logout"): go_to('landing')

# (Other dashboards and landing logic remain identical to previous Master Code)
