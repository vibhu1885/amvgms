import streamlit as st
import os

# ==========================================
# CENTRAL CONTROL PANEL (STYLING)
# ==========================================
# 1. Logo & Image Controls
LOGO_PATH = "assets/office_logo.png" 
LOGO_WIDTH = 130 

# 2. Background & Global Colors
APP_BG_COLOR = "#131419"  
HEADING_COLOR = "#FFFFFF" 
LABEL_COLOR = "#FFFFFF"   

# 3. Button Master Controls (SIZE & LOOK)
BTN_HEIGHT = "70px"        
BTN_WIDTH = "300px"         
BTN_BG_COLOR = "#faf9f9"
BTN_TEXT_COLOR = "#131419"
BTN_BORDER_COLOR = "#fca311"
BTN_BORDER_WIDTH = "4px"
BTN_ROUNDNESS = "22px"
BTN_HOVER_COLOR = "#a7c957"

# --- FONT CONTROLS ---
BTN_TEXT_SIZE = "17px"     
BTN_FONT_WEIGHT = "900"    

# 4. Label & Text Controls
LABEL_FONT_SIZE = "20px"
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

    /* 2. Main Container */
    .block-container {{
        max-width: 480px !important;
        padding-top: 2rem !important;
        padding-left: 15px !important;
        padding-right: 15px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
        justify-content: flex-start !important; 
    }}

    /* 3. Center blocks */
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

    /* 5. UNIFORM BUTTON STYLING */
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
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 10px 0px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}

    /* Target the text inside the button */
    div.stButton > button p {{
        font-size: {BTN_TEXT_SIZE} !important;
        font-weight: {BTN_FONT_WEIGHT} !important;
        color: {BTN_TEXT_COLOR} !important;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        border-color: {BTN_TEXT_COLOR} !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(79, 139, 249, 0.4);
    }}

    /* 6. Text and Heading Centering */
    .hindi-heading, .english-heading, p, label, .stMarkdown {{
        text-align: center !important;
        width: 100% !important;
        color: {LABEL_COLOR} !important;
    }}

    .hindi-heading {{
        color: {HEADING_COLOR};
        font-size: 20px;
        font-weight: 900;
        margin-top: 0px;
    }}
    
    .english-heading {{
        color: {HEADING_COLOR};
        font-size: {HEADING_FONT_SIZE_EN};
        font-weight: bold;
        margin-bottom: 20px;
    }}

    /* 7. Input Field Styling */
    [data-testid="stTextInput"], [data-testid="stTextArea"] {{
        width: 100% !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# PAGE NAVIGATION & STATE MANAGEMENT
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

if 'hrms_verified' not in st.session_state:
    st.session_state.hrms_verified = False

if 'found_emp_name' not in st.session_state:
    st.session_state.found_emp_name = ""

def go_to(page_name):
    st.session_state.page = page_name

# ==========================================
# PAGE CONTENT (landing_page.py)
# ==========================================

# --- PAGE 1: LANDING ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=LOGO_WIDTH)
    
    st.markdown(f'<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    
    if st.button("📝 नया Grievance दर्ज करें"):
        go_to('new_form')

    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"):
        go_to('status_check')

    if st.button("🔐 Officer/ Admin Login"):
        go_to('login')

# --- PAGE 2: NEW GRIEVANCE REGISTRATION ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading" style="font-size:18px;">शिकायत पंजीकरण</div>', unsafe_allow_html=True)

    # HRMS ID Input Box
    hrms_input = st.text_input(
        "Enter HRMS ID (अपनी HRMS ID दर्ज करें)", 
        max_chars=6,
        placeholder="6-Letter ID"
    ).upper().strip()

    # Verify Button
    if st.button("Verify ID / सत्यापित करें"):
        # Validation Rule
        if len(hrms_input) == 6 and hrms_input.isalpha():
            
            # --- DATABASE LOOKUP (Logic to be linked to your Sheet) ---
            # Search sheet 'EMPLOYEE_MAPPING' for hrms_input
            # For now, using a test ID:
            if hrms_input == "ABCDEF": 
                st.session_state.found_emp_name = "Maitri Singh"
                st.session_state.hrms_verified = True
                st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
            else:
                st.session_state.hrms_verified = False
                st.error("❌ HRMS ID not found in mapping sheet.")
        else:
            st.error("⚠️ Invalid Format! Enter exactly 6 CAPITAL alphabets.")

    # Show Form only if ID is verified
    if st.session_state.hrms_verified:
        st.markdown("---")
        st.info(f"Logging grievance for: **{st.session_state.found_emp_name}**")
        # [Wait for user input to add more form fields here]
        
    # Navigation Back
    if st.button("⬅️ Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- PAGE 3: STATUS CHECK ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">स्थिति जांचें</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Check Grievance Status</div>', unsafe_allow_html=True)
    st.text_input("Token Number / Reference No.")
    if st.button("⬅️ Back to Home"):
        go_to('landing')

# --- PAGE 4: ADMIN LOGIN ---
elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Officer Login</div>', unsafe_allow_html=True)
    st.text_input("HRMS ID / Username")
    st.text_input("Login Key / Password", type="password")
    if st.button("⬅️ Back to Home"):
        go_to('landing')
