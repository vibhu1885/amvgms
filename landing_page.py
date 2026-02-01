import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. DATABASE & GLOBAL CONSTANTS
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 130
APP_BG_COLOR = "#131419"

def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Grievance_DB").worksheet(sheet_name)

# ==========================================
# 1. THE LAYOUT LOCK (CSS)
# ==========================================
def apply_layout(page_type="standard"):
    # Admin gets wide view (1200px), everyone else stays locked to your 480px centering
    max_width = "1200px" if page_type == "admin" else "480px"
    label_align = "left" if page_type == "form" else "center"
    
    st.markdown(f"""
    <style>
        header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
        .stApp {{ background-color: {APP_BG_COLOR}; }}
        .block-container {{ max-width: {max_width} !important; padding-top: 1.5rem !important; margin: 0 auto !important; display: flex !important; flex-direction: column !important; align-items: center !important; }}
        [data-testid="stVerticalBlock"] {{ width: 100% !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; }}
        [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
        [data-testid="stImage"] > img {{ margin: 0 auto !important; }}
        
        .stButton {{ width: 100% !important; display: flex !important; justify-content: center !important; }}
        div.stButton > button {{
            background-color: #faf9f9 !important; color: #131419 !important;
            border: 4px solid #fca311 !important; border-radius: 22px !important;
            width: 300px !important; height: 70px !important; margin: 12px auto !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4); font-weight: 900 !important;
        }}
        div.stButton > button:hover {{ background-color: #a7c957 !important; transform: translateY(-4px) scale(1.03) !important; }}
        div.stButton > button p {{ font-size: 17px !important; font-weight: 900 !important; margin: 0 !important; }}

        .hindi-heading, .english-heading, label, .stMarkdown p {{ text-align: {label_align} !important; width: 100% !important; display: block !important; }}
        .hindi-heading {{ color: white; font-size: 20px; font-weight: 900; text-align: center !important; }}
        .english-heading {{ color: white; font-size: 18px; font-weight: bold; text-align: center !important; margin-bottom: 20px; }}
        label {{ color: white !important; font-weight: bold; margin-top: 10px; }}

        /* Admin Specific Components */
        .admin-card-container {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; width: 100%; }}
        .admin-card {{ padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; color: #131419; min-width: 150px; flex: 1; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. PAGE FUNCTIONS
# ==========================================

def show_landing():
    apply_layout("standard")
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

def show_registration():
    apply_layout("form")
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    if not st.session_state.hrms_verified:
        hrms_input = st.text_input("Enter HRMS ID*", max_chars=6).upper().strip()
        if st.button("🔎 Verify ID"):
            # ... (Your verified logic here)
            st.session_state.hrms_verified = True # Simulated for space
            st.rerun()
    else:
        st.success(f"✅ Employee Found")
        st.text_input("Employee Number*")
        # All your selectboxes and logic go here
        if st.button("🏠 Back to Home"):
            st.session_state.hrms_verified = False
            go_to('landing')

def show_admin_dashboard():
    apply_layout("admin")
    st.markdown('<div class="hindi-heading" style="font-size:32px;">Admin Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#fca311; font-weight:bold; font-size:20px;">Welcome: {st.session_state.active_super.get("NAME")}</div>', unsafe_allow_html=True)

    # Fetch Data
    ws_g = get_sheet("GRIEVANCE")
    df = pd.DataFrame(ws_g.get_all_records())

    # 1. Master Oversight (Colors Locked)
    st.markdown(f"""
    <div class="admin-card-container">
        <div class="admin-card" style="background:#FFFFFF;">TOTAL: {len(df)}</div>
        <div class="admin-card" style="background:#3498db; color:white;">NEW: {len(df[df['STATUS']=='NEW'])}</div>
        <div class="admin-card" style="background:#f1c40f;">PROCESS: {len(df[df['STATUS']=='UNDER PROCESS'])}</div>
        <div class="admin-card" style="background:#2ecc71; color:white;">RESOLVED: {len(df[df['STATUS']=='RESOLVED'])}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Action Table
    off_df = pd.DataFrame(get_sheet("OFFICER_MAPPING").get_all_records())
    officers = ["Select Officer"] + [f"{r['NAME']} ({r['RANK']})" for _, r in off_df[off_df['ROLE'].isin(['OFFICER', 'BOTH'])].iterrows()]

    for i, row in df.iterrows():
        st.markdown("---")
        c1, c2, c3 = st.columns([2, 5, 3])
        with c1:
            color = "#3498db" if row['STATUS'] == "NEW" else "#f1c40f" if row['STATUS'] == "UNDER PROCESS" else "#2ecc71"
            st.markdown(f"**Ref:** {row['REFERENCE_NO']}")
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>{row['STATUS']}</span>", unsafe_allow_html=True)
        with c2:
            st.write(f"**{row['EMP_NAME']}** | {row['GRIEVANCE_TYPE']}")
            st.write(f"_{row['GRIEVANCE_TEXT']}_")
        with c3:
            if row['STATUS'] == "NEW":
                sel = st.selectbox("Mark to Officer", officers, key=f"adm_{i}")
                if sel != "Select Officer":
                    now = datetime.now().strftime("%d-%m-%Y %H:%M")
                    ws_g.update_cell(i+2, 11, "UNDER PROCESS")
                    ws_g.update_cell(i+2, 12, f"Marked to: {sel} at {now}")
                    st.rerun()
            else: st.info(f"📍 {row['MARKED_OFFICER']}")

    if st.button("🚪 Logout"): go_to('landing')

# ==========================================
# 3. ROUTING & STATE
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
def go_to(page): st.session_state.page = page

st.set_page_config(page_title="GMS Alambagh", layout="centered")

if st.session_state.page == 'landing': show_landing()
elif st.session_state.page == 'new_form': show_registration()
elif st.session_state.page == 'admin_dashboard': show_admin_dashboard()
# ... (Add other page functions for login and status check similarly)
