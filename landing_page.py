import streamlit as st
import os
from datetime import datetime

# ==========================================
# CENTRAL CONTROL PANEL (STYLING)
# ==========================================
LOGO_PATH = "assets/office_logo.png" 
LOGO_WIDTH = 130 
APP_BG_COLOR = "#131419"  
HEADING_COLOR = "#FFFFFF" 
LABEL_COLOR = "#FFFFFF"   

# Button Styling
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

# Label Styling
LABEL_FONT_SIZE = "18px"

# ==========================================
# THE GLOBAL ALIGNMENT ENGINE (CSS)
# ==========================================
st.set_page_config(page_title="GMS Alambagh", layout="centered")

custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

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

    [data-testid="stVerticalBlock"] {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }}

    [data-testid="stImage"] {{ display: flex !important; justify-content: center !important; width: 100% !important; margin-bottom: 6px !important; }}

    .stButton {{ width: 100% !important; display: flex !important; justify-content: center !important; }}

    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        height: {BTN_HEIGHT} !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        margin: 10px 0px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}

    div.stButton > button p {{
        font-size: {BTN_TEXT_SIZE} !important;
        font-weight: {BTN_FONT_WEIGHT} !important;
        color: {BTN_TEXT_COLOR} !important;
    }}

    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-2px);
    }}

    .hindi-heading, .english-heading, p, label, .stMarkdown {{
        text-align: center !important;
        width: 100% !important;
        color: {LABEL_COLOR} !important;
    }}

    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; margin-top: 0px; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: bold; margin-bottom: 20px; }}

    [data-testid="stTextInput"], [data-testid="stTextArea"], [data-testid="stSelectbox"] {{
        width: 100% !important;
    }}
    
    /* Error text styling */
    .err-text {{ color: #e63946; font-size: 14px; margin-top: -10px; margin-bottom: 10px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# MOCK DATABASE FUNCTIONS (Link your API here)
# ==========================================
def get_dropdown_options(column_name):
    # Logic to pull from DROPDOWN_MAPPINGS sheet
    # Returning lists for now
    options = {
        "Designation": ["Select", "SSE", "JE", "Technician", "Helper"],
        "Trade": ["Select", "Fitter", "Welder", "Painter", "Carpenter"],
        "GrievanceType": ["Select", "Leave", "Salary", "Quarter", "Transfer"]
    }
    return options.get(column_name, ["Select"])

# ==========================================
# PAGE NAVIGATION & STATE
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'found_emp_name' not in st.session_state: st.session_state.found_emp_name = ""

def go_to(page_name):
    st.session_state.page = page_name

# ==========================================
# PAGE CONTENT
# ==========================================

# --- PAGE 1: LANDING ---
if st.session_state.page == 'landing':
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading" style="font-size:18px;">समस्या पंजीकरण</div>', unsafe_allow_html=True)

    # 1. HRMS Verification Section
    if not st.session_state.hrms_verified:
        hrms_input = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6, placeholder="HRMS ID").upper().strip()
        if st.button("Verify ID / सत्यापित करें"):
            if len(hrms_input) == 6 and hrms_input.isalpha():
                # Actual lookup logic for EMPLOYEE_MAPPING here
                if hrms_input == "ABCDEF": # Test Case
                    st.session_state.found_emp_name = "Maitri Singh"
                    st.session_state.hrms_verified = True
                    st.rerun()
                else:
                    st.error("❌ HRMS ID not found.")
            else:
                st.error("⚠️ Invalid Format! Use 6 CAPITAL alphabets.")
    
    # 2. Form Section (Appears after verification)
    else:
        st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
        
        emp_name = st.text_input("Employee Name (कर्मचारी का नाम)*", value=st.session_state.found_emp_name, disabled=True)
        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*", placeholder="Numbers/Letters only")
        
        designations = get_dropdown_options("Designation")
        emp_desig = st.selectbox("Employee Designation (कर्मचारी का पद)*", designations)
        
        trades = get_dropdown_options("Trade")
        emp_trade = st.selectbox("Employee Trade (कर्मचारी का ट्रेड)*", trades)
        
        emp_sec = st.text_input("Employee Section (कर्मचारी का कार्यस्थल)*")
        
        g_types = get_dropdown_options("GrievanceType")
        g_type = st.selectbox("Grievance Type (समस्या का प्रकार)*", g_types)
        
        g_text = st.text_area("Brief of Grievance (समस्या का विवरण)*", max_chars=1000, height=150)

        # Submit Logic
        if st.button("✅ Submit Grievance"):
            # Check mandatory fields
            errors = []
            if not emp_no: errors.append("Employee Number is required.")
            if emp_desig == "Select": errors.append("Please select Designation.")
            if emp_trade == "Select": errors.append("Please select Trade.")
            if not emp_sec: errors.append("Section is required.")
            if g_type == "Select": errors.append("Please select Grievance Type.")
            if not g_text: errors.append("Brief of Grievance is required.")

            if errors:
                for err in errors:
                    st.markdown(f'<p class="err-text">{err}</p>', unsafe_allow_html=True)
            else:
                # TIMESTAMP LOGIC
                submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ref_no = "REF" + datetime.now().strftime("%y%m%d%H%M%S")
                
                # --- DATA COLLECTION FOR EXCEL ---
                # data = [ref_no, submission_time, hrms_input, emp_name, emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "Pending", "N/A", "N/A"]
                # send_to_sheet(data)
                
                st.success(f"Grievance Registered! Ref No: {ref_no}")
                st.balloons()

    if st.button("⬅️ Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- OTHER PAGES ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">स्थिति जांचें</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')

elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Admin Login</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')
