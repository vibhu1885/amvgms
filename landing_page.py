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
        st.error("❌ Secrets 'gcp_service_account' not found!")
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

st.set_page_config(page_title="GMS Alambagh", layout="centered")

# ==========================================
# STRICT ALIGNMENT ENGINE (STRICT CENTER LOGO/BTN, LEFT LABELS)
# ==========================================
custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
    }}

    /* STRICT LOGO CENTERING */
    [data-testid="stImage"] {{ 
        display: flex !important; 
        justify-content: center !important; 
        width: 100% !important; 
    }}

    /* STRICT BUTTON CENTERING + BOLDNESS + SHADOW */
    .stButton {{ 
        width: 100% !important; 
        display: flex !important; 
        justify-content: center !important; 
    }}
    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        height: {BTN_HEIGHT} !important;
        margin: 15px auto !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.6) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 25px rgba(167, 201, 87, 0.4) !important;
    }}
    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important; 
        color: {BTN_TEXT_COLOR} !important;
    }}

    /* STRICT LEFT ALIGN FOR LABELS & INPUTS */
    [data-testid="stVerticalBlock"] {{ align-items: flex-start !important; }}
    label {{ 
        color: {LABEL_COLOR} !important; 
        font-weight: bold !important; 
        text-align: left !important; 
        width: 100% !important;
        display: block !important;
    }}
    
    .hindi-heading, .english-heading {{ text-align: center !important; width: 100% !important; }}
    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
    .err-msg {{ color: #FF4B4B; font-size: 13px; font-weight: bold; text-align: left !important; width: 100%; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# NAVIGATION & LOGIC
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False

def go_to(page_name):
    st.session_state.page = page_name

def generate_ref_no(hrms_id, df_grievance):
    date_str = datetime.now().strftime("%Y%m%d")
    count = 1
    if not df_grievance.empty and 'HRMS_ID' in df_grievance.columns:
        count = len(df_grievance[df_grievance['HRMS_ID'] == hrms_id]) + 1
    return f"{date_str}{hrms_id}{str(count).zfill(3)}"

# ==========================================
# PAGE CONTENT
# ==========================================

# --- PAGE 1: LANDING ---
if st.session_state.page ==
