import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. DATABASE CONNECTION
# ==========================================
def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Grievance_DB").worksheet(sheet_name)

# ==========================================
# CONSTANTS & GLOBAL STYLING
# ==========================================
LOGO_PATH = "assets/office_logo.png"
LOGO_WIDTH = 130

st.set_page_config(page_title="GMS Alambagh", layout="centered")

# This is the ONE CSS block that handles the Button Design and Dark Theme
st.markdown(f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: #131419; }}
    
    /* Center the main container */
    .block-container {{ max-width: 500px !important; padding-top: 2rem !important; }}

    /* Master Button Design */
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
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{ background-color: #a7c957 !important; transform: translateY(-3px); }}
    div.stButton > button p {{ font-weight: 900 !important; }}

    /* Heading Alignment */
    .hindi-heading, .english-heading {{ text-align: center !important; color: white; }}
    label {{ color: white !important; font-weight: bold !important; text-align: left !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# LOGIC & NAVIGATION
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
def go_to(p): st.session_state.page = p

# --- LANDING PAGE ---
if st.session_state.page == 'landing':
    # We use columns to create a "Center Stage" (300px wide area)
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        # 1. Logo
        if os.path.exists(LOGO_PATH):
            # Inner columns to center the logo image itself
            l1, l2, l3 = st.columns([1, 1, 1])
            with l2: st.image(LOGO_PATH, width=LOGO_WIDTH)
        
        # 2. Headings
        st.markdown('<div class="hindi-heading" style="font-size:22px; font-weight:900;">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
        st.markdown('<div class="english-heading" style="font-size:18px;">Grievance Management System</div>', unsafe_allow_html=True)
        st.write("") # Spacer
        
        # 3. Buttons (Automatically take full width of col2, which is centered)
        if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
        if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
        if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- REGISTRATION PAGE ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    # Form fields will be left-aligned by default
    hrms = st.text_input("Enter HRMS ID*")
    
    # Navigation button centered at the bottom
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏠 Back to Home"): go_to('landing')

# --- ADMIN DASHBOARD ---
elif st.session_state.page == 'admin_dashboard':
    st.markdown('<div class="hindi-heading">Admin Dashboard</div>', unsafe_allow_html=True)
    # Table logic goes here
    if st.button("🚪 Logout"): go_to('landing')
