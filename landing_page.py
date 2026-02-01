import streamlit as st
import os

# ==========================================
# CENTRAL CONTROL PANEL (STYLING)
# ==========================================
# 1. Logo & Image Controls
LOGO_PATH = "assets/office_logo.png" 
LOGO_WIDTH = 130 

# 2. Background & Global Colors
APP_BG_COLOR = "#121212"  
HEADING_COLOR = "#FFFFFF" 
LABEL_COLOR = "#FFFFFF"   

# 3. Button Master Controls
BTN_BG_COLOR = "#2D2D2D"
BTN_TEXT_COLOR = "#FFFFFF"
BTN_BORDER_COLOR = "#4F8BF9"
BTN_BORDER_WIDTH = "2px"
BTN_ROUNDNESS = "12px"
BTN_HOVER_COLOR = "#4F8BF9"
BTN_TEXT_SIZE = "16px"
BTN_FONT_WEIGHT = "bold"

# 4. Label & Text Controls
LABEL_FONT_SIZE = "18px"
HEADING_FONT_SIZE_HI = "26px" 
HEADING_FONT_SIZE_EN = "20px"

# ==========================================
# THE GLOBAL ALIGNMENT ENGINE (CSS)
# ==========================================
st.set_page_config(page_title="GMS Alambagh", layout="centered")

custom_css = f"""
<style>
    /* 1. Remove all Streamlit padding/header/footer */
    header, footer, [data-testid="stHeader"] {{
        visibility: hidden;
        height: 0;
    }}

    .stApp {{
        background-color: {APP_BG_COLOR};
    }}

    /* 2. Force the main container to be a top-aligned, centered column */
    .block-container {{
        max-width: 480px !important;
        padding-top: 2rem !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; /* Horizontal Center */
        justify-content: flex-start !important; /* Vertical Top */
    }}

    /* 3. Center every single child element within the main block */
    [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    /* 4. Logo Alignment */
    [data-testid="stImage"] {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-bottom: 6px !important;
    }}

    /* 5. Button Alignment and Sizing */
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
        width: 90% !important; /* Adjust width relative to the 480px container */
        padding: 15px 0px !important;
        font-size: {BTN_TEXT_SIZE} !important;
        font-weight: {BTN_FONT_WEIGHT} !important;
        margin: 10px 0px !important;
        transition: 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        border-color: {BTN_TEXT_COLOR} !important;
    }}

    /* 6. Text and Heading Centering */
    .hindi-heading, .english-heading, p, label, .stMarkdown {{
        text-align: center !important;
        width: 100% !important;
    }}

    .hindi-heading {{
        color: {HEADING_COLOR};
        font-size: 20px;
        font-weight: bold;
        line-height: 1.2;
        margin-top: 6px;
    }}
    
    .english-heading {{
        color: {HEADING_COLOR};
        font-size: {HEADING_FONT_SIZE_EN};
        font-weight: bold;
        margin-bottom: 20px;
    }}

    /* 7. Input Field Centering */
    [data-testid="stTextInput"], [data-testid="stTextArea"] {{
        width: 90% !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# PAGE NAVIGATION
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def go_to(page_name):
    st.session_state.page = page_name

# ==========================================
# PAGE CONTENT (landing_page.py)
# ==========================================

if st.session_state.page == 'landing':
    # Logo
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=LOGO_WIDTH)
    
    # Headings
    st.markdown(f'<div class="hindi-heading">सवारी डिब्बा कारखाना,<br>आलमबाग, लखनऊ.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    
    # Buttons - Now strictly aligned to the center axis of the headers
    if st.button("नया Grievance दर्ज करें"):
        go_to('new_form')

    if st.button("पहले से दर्ज ग्रीवांस की वर्तमान स्थिति जानें"):
        go_to('status_check')

    if st.button("Officer/ Admin Login"):
        go_to('login')

elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">विवरण दर्ज करें</div>', unsafe_allow_html=True)
    st.text_input("Grievance Category")
    if st.button("← Back"):
        go_to('landing')

elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">स्थिति जांचें</div>', unsafe_allow_html=True)
    st.text_input("Token Number")
    if st.button("← Back"):
        go_to('landing')

elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Admin</div>', unsafe_allow_html=True)
    st.text_input("Password", type="password")
    if st.button("← Back"):
        go_to('landing')
