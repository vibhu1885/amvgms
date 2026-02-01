import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
import os
from datetime import datetime

# ==========================================
# 🎨 STYLE SETTINGS (Locked & Permanent)
# ==========================================
LOGO_FILENAME = "assets/office_logo.png" 
LOGO_SIZE = 180                         
LOGO_MARGIN = "20px"                    
H_TEXT = "कैरिज वर्कशॉप, आलमाग, लखनऊ<br>Grievance Management System"
H_COLOR = "white"; H_SIZE = "32px"; H_FONT = "'Trebuchet MS', sans-serif"; H_WEIGHT = "900"
REG_FORM_WIDTH = "480px"
B_MAX_WIDTH, B_WIDTH_MOBILE, B_HEIGHT = "420px", "90%", "85px"
B_TEXT_COLOR, B_BG_COLOR, B_FONT_SIZE, B_FONT_WEIGHT = "#14213d", "#e5e5e5", "22px", "1000"
B_ROUNDNESS, B_BORDER_WIDTH, B_BORDER_COLOR = "20px", "3px", "#fca311"

# ==========================================
# ⚙️ CSS ENGINE (STRICT CENTERING & THEME)
# ==========================================
st.set_page_config(layout="wide", page_title="Railway Grievance System")

st.markdown(f"""
    <style>
    /* 🛡️ BACKGROUND COLOR LOCK */
    .stApp {{ background-color: #091327 !important; }}

    [data-testid="stVerticalBlock"] {{ 
        display: flex !important; 
        flex-direction: column !important; 
        align-items: center !important; 
        justify-content: center !important; 
        width: 100% !important; 
        text-align: center !important;
    }}

    .header-container {{ text-align: center; margin-top: 10px; margin-bottom: 30px; width: 100%; }}
    .logo-img {{ width: {LOGO_SIZE}px; max-width: 60%; height: auto; margin-bottom: {LOGO_MARGIN}; filter: drop-shadow(2px 4px 8px rgba(0,0,0,0.6)); }}
    .custom-header {{ font-family: {H_FONT}; color: {H_COLOR}; font-size: {H_SIZE}; font-weight: {H_WEIGHT}; line-height: 1.2; text-shadow: 3px 3px 10px rgba(0,0,0,0.8); }}
    
    /* 🛡️ 16px LABEL LOCK */
    [data-testid="stWidgetLabel"] p {{ font-size: 16px !important; font-weight: 800 !important; color: white !important; text-align: left !important; }}
    
    /* ICONIC BUTTON STYLE */
    div.stButton > button, div.stFormSubmitButton > button {{
        width: {B_MAX_WIDTH} !important; max-width: {B_WIDTH_MOBILE} !important; height: {B_HEIGHT} !important;
        background-color: {B_BG_COLOR} !important; color: {B_TEXT_COLOR} !important; border-radius: {B_ROUNDNESS} !important;
        border: {B_BORDER_WIDTH} solid {B_BORDER_COLOR} !important; margin: 15px auto !important; 
        transition: all 0.3s ease; box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    }}
    div.stButton > button p, div.stFormSubmitButton > button p {{ font-size: {B_FONT_SIZE} !important; font-weight: {B_FONT_WEIGHT} !important; color: {B_TEXT_COLOR} !important; margin: 0 !important; }}

    /* Refined Layout Containers */
    .st-key-reg_page_col, .st-key-status_container, .st-key-login_container, .st-key-choice_container {{ 
        max-width: {REG_FORM_WIDTH} !important; margin: 0 auto !important; padding: 10px; 
    }}

    /* UI Hide Elements */
    header, footer, #MainMenu {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================
def get_base64_logo(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_data = get_base64_logo(LOGO_FILENAME)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name): 
    return conn.read(worksheet=name, ttl="0")

def clean_val(val, fallback="Pending"):
    return fallback if pd.isna(val) or str(val).strip().lower() == 'nan' or not str(val).strip() else str(val)

# Router State
if "page" not in st.session_state: st.session_state.page = "LANDING"
if "user" not in st.session_state: st.session_state.user = None

# ==========================================
# 🧭 PAGE ROUTER
# ==========================================

# --- 1. LANDING ---
if st.session_state.page == "LANDING":
    logo_tag = f'<img src="data:image/png;base64,{logo_data}" class="logo-img">' if logo_data else ""
    st.markdown(f'<div class="header-container">{logo_tag}<div class="custom-header">{H_TEXT}</div></div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): st.session_state.page = "REG"; st.rerun()
    if st.button("🔍 Grievance की स्थिति देखें"): st.session_state.page = "STATUS"; st.rerun()
    if st.button("🔐 Officer/ Admin Login"): st.session_state.page = "LOGIN"; st.rerun()

# --- 2. REGISTRATION ---
elif st.session_state.page == "REG":
    st.markdown(f'<div class="header-container"><div class="custom-header">Grievance Registration</div></div>', unsafe_allow_html=True)
    with st.container(key="reg_page_col"):
        if "last_ref" not in st.session_state:
            hrms_id = st.text_input("HRMS ID दर्ज करें।").upper().strip()
            # Logic for data entry goes here...
            if st.button("Back"): st.session_state.page = "LANDING"; st.rerun()
        else:
            # Success UI here...
            pass

# --- 3. STATUS TRACKING ---
elif st.session_state
