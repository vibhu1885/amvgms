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

# Button Master Controls
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
# THE "TOTAL LOCK" ALIGNMENT ENGINE (CSS)
# ==========================================
max_w = "1000px" if st.session_state.get('page') == 'admin_dashboard' else "480px"

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    /* Main App Container */
    .block-container {{
        max-width: {max_w} !important;
        padding-top: 2rem !important;
        margin: auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    /* Target the vertical block that wraps everything */
    [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; /* This centers the children of the block */
    }}

    /* --- LOGO: CENTER LOCK --- */
    [data-testid="stImage"] {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }}

    /* --- BUTTONS: CENTER LOCK --- */
    .stButton {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}

    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        height: {BTN_HEIGHT} !important;
        margin: 12px auto !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.5) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 12px 20px rgba(167, 201, 87, 0.5) !important;
    }}

    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important;
        color: {BTN_TEXT_COLOR} !important;
    }}

    /* --- FORM FIELDS: LEFT ALIGN LABELS --- */
    /* We override the center-align for labels and inputs specifically */
    .stTextInput, .stSelectbox, .stTextArea, .stMarkdown {{
        width: 100% !important;
        text-align: left !important;
    }}
    
    label {{
        color: {LABEL_COLOR} !important;
        font-weight: bold !important;
        text-align: left !important;
        display: block !important;
        width: 100% !important;
        margin-top: 10px !important;
    }}

    /* Headings stay centered */
    .hindi-heading, .english-heading {{
        text-align: center !important;
        width: 100% !important;
        color: {HEADING_COLOR};
        font-weight: 900;
    }}
    .hindi-heading {{ font-size: 22px; line-height: 1.4; }}
    .english-heading {{ font-size: 18px; margin-bottom: 20px; }}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# PAGE ROUTING & CONTENT
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'

def go_to(p): st.session_state.page = p

# --- LANDING PAGE ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH): 
        st.image(LOGO_PATH, width=LOGO_WIDTH)
    
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- OTHER PAGES (Placeholders for routing) ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    # The labels here will be left-aligned due to the label { text-align: left } rule
    st.text_input("Sample Field (Left Aligned)")
    if st.button("🏠 Back to Home"): go_to('landing')

elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading" style="font-size:35px;">Admin Dashboard</div>', unsafe_allow_html=True)
    if st.button("🚪 Logout"): go_to('landing')
