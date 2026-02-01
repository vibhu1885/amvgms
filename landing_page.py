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
BTN_BORDER_WIDTH = "1.5px"
BTN_ROUNDNESS = "10px"
BTN_HOVER_COLOR = "#4F8BF9"
BTN_TEXT_SIZE = "16px"
BTN_FONT_WEIGHT = "bold"
BTN_ALIGNMENT = "center"

# 4. Label & Text Controls
LABEL_FONT_SIZE = "18px"
HEADING_FONT_SIZE_HI = "24px" 
HEADING_FONT_SIZE_EN = "18px"

# ==========================================
# INJECTED CSS (FOR ALL PAGES)
# ==========================================
st.set_page_config(page_title="GMS Alambagh", layout="centered")

custom_css = f"""
<style>
    /* Hide Streamlit elements */
    header, footer, #tabs-b6-tab-0, [data-testid="stHeader"] {{
        visibility: hidden;
        height: 0;
    }}

    /* Force background and remove padding from main container */
    .stApp {{
        background-color: {APP_BG_COLOR};
    }}

    /* The Main Center Logic */
    .block-container {{
        max-width: 480px !important;
        padding: 0 !important;
        height: 100vh !important;
        display: flex !important;
        align-items: center !important; /* Vertical center */
        justify-content: center !important; /* Horizontal center */
    }}

    /* This wrapper ensures all elements inside are stacked vertically */
    .center-wrapper {{
        width: 100%;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }}

    /* Global Label Styling */
    label, p, .stMarkdown {{
        color: {LABEL_COLOR} !important;
        font-size: {LABEL_FONT_SIZE};
    }}

    /* Heading Styles */
    .hindi-heading {{
        color: {HEADING_COLOR};
        font-size: {HEADING_FONT_SIZE_HI};
        font-weight: bold;
        line-height: 1.3;
        margin: 15px 0 5px 0;
    }}
    
    .english-heading {{
        color: {HEADING_COLOR};
        font-size: {HEADING_FONT_SIZE_EN};
        font-weight: bold;
        margin-bottom: 30px;
    }}

    /* BUTTON MASTER STYLING */
    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: 100% !important;
        padding: 14px 0px !important;
        font-size: {BTN_TEXT_SIZE} !important;
        font-weight: {BTN_FONT_WEIGHT} !important;
        margin-bottom: 12px;
        transition: 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        border-color: {BTN_TEXT_COLOR} !important;
    }}

    /* Center Logo inside the wrapper */
    .logo-container {{
        display: flex;
        justify-content: center;
        width: 100%;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# NAVIGATION LOGIC
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def go_to(page_name):
    st.session_state.page = page_name

# ==========================================
# MAIN APP WRAPPER (This forces centering)
# ==========================================
with st.container():
    # Start the custom div wrapper
    st.markdown('<div class="center-wrapper">', unsafe_allow_html=True)

    # --- PAGE 1: LANDING ---
    if st.session_state.page == 'landing':
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=LOGO_WIDTH)
        
        st.markdown(f'<div class="hindi-heading">सवारी डिब्बा कारखाना,<br>आलमबाग, लखनऊ.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
        
        if st.button("नया Grievance दर्ज करें"):
            go_to('new_form')

        if st.button("पहले से दर्ज ग्रीवांस की वर्तमान स्थिति जानें"):
            go_to('status_check')

        if st.button("Officer/ Admin Login"):
            go_to('login')

    # --- PAGE 2: NEW FORM ---
    elif st.session_state.page == 'new_form':
        st.markdown('<div class="hindi-heading">नया विवरण भरें</div>', unsafe_allow_html=True)
        # Note: Form fields stay centered because of the wrapper
        st.text_input("नाम (Name)")
        if st.button("Submit"):
            pass
        if st.button("← Back"):
            go_to('landing')

    # --- PAGE 3: STATUS ---
    elif st.session_state.page == 'status_check':
        st.markdown('<div class="hindi-heading">स्थिति जांचें</div>', unsafe_allow_html=True)
        st.text_input("Grievance ID")
        if st.button("← Back"):
            go_to('landing')

    # --- PAGE 4: LOGIN ---
    elif st.session_state.page == 'login':
        st.markdown('<div class="hindi-heading">Login</div>', unsafe_allow_html=True)
        st.text_input("Admin ID")
        st.text_input("Password", type="password")
        if st.button("← Back"):
            go_to('landing')

    # End the custom div wrapper
    st.markdown('</div>', unsafe_allow_html=True)
