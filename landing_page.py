import streamlit as st
import os

# ==========================================
# CENTRAL CONTROL PANEL (STYLING)
# ==========================================
# 1. Logo & Image Controls
LOGO_PATH = "assets/office_logo.png" 
LOGO_WIDTH = 150 

# 2. Background & Global Colors
APP_BG_COLOR = "#0E1117"  
HEADING_COLOR = "#FFFFFF" 
LABEL_COLOR = "#FAFAFA"   

# 3. Button Master Controls
BTN_BG_COLOR = "#262730"
BTN_TEXT_COLOR = "#FFFFFF"
BTN_BORDER_COLOR = "#4F8BF9"
BTN_BORDER_WIDTH = "1px"
BTN_ROUNDNESS = "12px"
BTN_HOVER_COLOR = "#4F8BF9"
BTN_TEXT_SIZE = "16px"
BTN_FONT_WEIGHT = "bold"
BTN_ALIGNMENT = "center"

# 4. Label & Text Controls
LABEL_FONT_SIZE = "18px"
HEADING_FONT_SIZE_HI = "26px" 
HEADING_FONT_SIZE_EN = "20px"

# 5. Alignment Controls
CONTENT_MAX_WIDTH = "480px"
# Vertical centering logic: 
# We use 'vh' (viewport height) to ensure it centers based on the phone screen size.
VIEWPORT_HEIGHT = "90vh" 

# ==========================================
# INJECTED CSS (FOR ALL PAGES)
# ==========================================
st.set_page_config(page_title="GMS Alambagh", layout="centered")

custom_css = f"""
<style>
    /* 1. Global Background */
    .stApp {{
        background-color: {APP_BG_COLOR};
    }}
    
    /* 2. Main Container - Vertical Centering Logic */
    .block-container {{
        max-width: {CONTENT_MAX_WIDTH} !important;
        padding: 0rem 1rem !important;
        margin: auto;
        min-height: {VIEWPORT_HEIGHT};
        display: flex;
        flex-direction: column;
        justify-content: center; /* This centers everything vertically */
    }}

    /* 3. Global Label & Text Styling */
    .stMarkdown, p, label {{
        color: {LABEL_COLOR} !important;
        font-size: {LABEL_FONT_SIZE} !important;
    }}

    /* 4. Heading Styles */
    .hindi-heading {{
        color: {HEADING_COLOR};
        font-size: {HEADING_FONT_SIZE_HI};
        font-weight: bold;
        text-align: center;
        line-height: 1.3;
        margin-top: 10px;
    }}
    
    .english-heading {{
        color: {HEADING_COLOR};
        font-size: {HEADING_FONT_SIZE_EN};
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }}

    /* 5. BUTTON MASTER STYLING */
    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: 100% !important;
        padding: 15px 5px !important;
        font-size: {BTN_TEXT_SIZE} !important;
        font-weight: {BTN_FONT_WEIGHT} !important;
        text-align: {BTN_ALIGNMENT} !important;
        margin-bottom: 10px;
        transition: 0.3s;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        border-color: {BTN_TEXT_COLOR} !important;
    }}

    /* 6. Center Logo */
    [data-testid="stImage"] {{
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }}
    
    /* Hide Streamlit Header/Footer for a cleaner 'App' look */
    header, footer {{
        visibility: hidden;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# MULTI-PAGE NAVIGATION STATE
# ==========================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'

def change_page(page_name):
    st.session_state.current_page = page_name

# ==========================================
# PAGE LOGIC
# ==========================================

# --- PAGE 1: LANDING ---
if st.session_state.current_page == 'landing':
    # 1. Office Logo
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=LOGO_WIDTH)
    else:
        st.error(f"Missing: {LOGO_PATH}")

    # 2. Headings
    st.markdown(f'<div class="hindi-heading">सवारी डिब्बा कारखाना,<br>आलमबाग, लखनऊ.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    
    # 3. Buttons
    if st.button("नया Grievance दर्ज करें"):
        change_page('new_form')

    if st.button("पहले से दर्ज ग्रीवांस की वर्तमान स्थिति जानें"):
        change_page('status_check')

    if st.button("Officer/ Admin Login"):
        change_page('login')

# --- SUBSEQUENT PAGES ---
elif st.session_state.current_page == 'new_form':
    st.markdown('<div class="hindi-heading">New Grievance</div>', unsafe_allow_html=True)
    # Form logic will go here
    if st.button("← Back to Home"):
        change_page('landing')

elif st.session_state.current_page == 'status_check':
    st.markdown('<div class="hindi-heading">Check Status</div>', unsafe_allow_html=True)
    if st.button("← Back to Home"):
        change_page('landing')

elif st.session_state.current_page == 'login':
    st.markdown('<div class="hindi-heading">Admin Login</div>', unsafe_allow_html=True)
    if st.button("← Back to Home"):
        change_page('landing')
