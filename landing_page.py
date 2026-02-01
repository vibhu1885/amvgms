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
LOGO_WIDTH = 130
APP_BG_COLOR = "#131419"

# Page Config
st.set_page_config(page_title="GMS Alambagh", layout="wide")

# ==========================================
# 1. THE "RESTORED STYLE" CSS ENGINE
# ==========================================
# Wide for Admin, Narrow (500px) for Forms
content_width = "1200px" if st.session_state.get('page') == 'admin_dashboard' else "550px"

st.markdown(f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}
    
    /* 1. Main Container: Centered */
    .block-container {{
        max-width: {content_width} !important;
        padding-top: 2rem !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    /* 2. Logo Centering */
    [data-testid="stImage"] {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-bottom: 10px;
    }}
    [data-testid="stImage"] img {{ margin: 0 auto !important; }}

    /* 3. HEADINGS (Centered & White) */
    .hindi-heading {{ 
        text-align: center !important; 
        color: white !important; 
        font-weight: 900 !important; 
        font-size: 24px !important; 
        width: 100%;
        margin-bottom: 5px;
    }}
    .english-heading {{ 
        text-align: center !important; 
        color: white !important; 
        font-weight: bold !important; 
        font-size: 18px !important; 
        margin-bottom: 25px; 
        width: 100%;
    }}

    /* 4. BUTTONS (Restored Boldness & Colors) */
    .stButton {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div.stButton > button {{
        background-color: #faf9f9 !important;
        color: #131419 !important; /* Dark Text */
        border: 4px solid #fca311 !important; /* Orange Border */
        border-radius: 22px !important;
        width: 300px !important; 
        height: 70px !important;
        margin: 10px auto !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.6);
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: #a7c957 !important;
        transform: translateY(-3px);
    }}
    /* FORCE TEXT STYLING INSIDE BUTTON */
    div.stButton > button p {{ 
        font-size: 20px !important;    /* Larger Font */
        font-weight: 900 !important;   /* Extra Bold */
        color: #131419 !important;     /* Force Dark Color */
        margin: 0 !important;
    }}

    /* 5. INPUTS (Text Starts Left, Labels Centered) */
    /* Labels centered */
    label {{
        text-align: center !important;
        width: 100% !important;
        color: white !important;
        font-weight: bold !important;
        display: block !important;
    }}
    /* Input text starts from LEFT */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{ 
        text-align: left !important; 
        color: #131419 !important;
    }}

    /* 6. ADMIN CARDS */
    .card-box {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; width: 100%; }}
    .card {{ padding: 15px; border-radius: 12px; text-align: center; font-weight: 900; color: #131419; min-width: 150px; flex: 1; }}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE & HELPERS
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'super_verified' not in st.session_state: st.session_state.super_verified = False
if 'active_super' not in st.session_state: st.session_state.active_super = {}

def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" not in st.secrets:
        st.error("❌ Secrets not found!")
        st.stop()
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Grievance_DB").worksheet(sheet_name)

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
# 3. PAGE CONTENT
# ==========================================

# --- LANDING PAGE ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION PAGE ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    
    if not st.session_state.hrms_verified:
        hrms_in = st.text_input("Enter HRMS ID (HRMS आईडी दर्ज करें)", max_chars=6).upper().strip()
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
            designations = ["Select
