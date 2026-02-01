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

    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; text-align: center; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: bold; margin-bottom: 20px; text-align: center; }}

    .err-text {{ color: #e63946; font-size: 14px; text-align: center; margin-bottom: 5px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# DATABASE LOOKUP LOGIC
# ==========================================
def check_hrms_id(search_id):
    """
    This is where your Google Sheets API integration goes.
    You will load the sheet 'EMPLOYEE_MAPPING' and look for HRMS_ID.
    """
    # Replace this mock dictionary with your actual sheet reading logic
    # Example: df = read_google_sheet("EMPLOYEE_MAPPING")
    # result = df[df['HRMS_ID'] == search_id]
    
    mapping_data = {
        "ABCDEF": "Maitri Singh",
        "RWAILW": "Rajesh Kumar",
        "LKOAMV": "Suresh Yadav"
    }
    return mapping_data.get(search_id, None)

def get_dropdown_options(sheet_name, column_name):
    # This will pull lists from your DROPDOWN_MAPPINGS sheet
    return ["Select", "Option 1", "Option 2", "Option 3"] # Mock

# ==========================================
# PAGE NAVIGATION & STATE
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False
if 'found_emp_name' not in st.session_state: st.session_state.found_emp_name = ""
if 'active_hrms' not in st.session_state: st.session_state.active_hrms = ""

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

    # 1. HRMS Verification Section (Disappears after success)
    if not st.session_state.hrms_verified:
        hrms_input = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6, placeholder="HRMS ID").upper().strip()
        
        if st.button("Verify ID / सत्यापित करें"):
            if len(hrms_input) == 6 and hrms_input.isalpha():
                # CALL THE DATABASE FUNCTION
                employee_name = check_hrms_id(hrms_input)
                
                if employee_name:
                    st.session_state.found_emp_name = employee_name
                    st.session_state.active_hrms = hrms_input
                    st.session_state.hrms_verified = True
                    st.rerun() # Refresh to hide this section and show the form
                else:
                    st.error("❌ HRMS ID not found in mapping sheet.")
            else:
                st.error("⚠️ Invalid Format! Use 6 CAPITAL alphabets.")
    
    # 2. Form Section (Appears only after verification)
    else:
        st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
        
        emp_name = st.text_input("Employee Name (कर्मचारी का नाम)*", value=st.session_state.found_emp_name, disabled=True)
        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        emp_desig = st.selectbox("Employee Designation (कर्मचारी का पद)*", get_dropdown_options("DROPDOWN_MAPPINGS", "Designation"))
        emp_trade = st.selectbox("Employee Trade (कर्मचारी का ट्रेड)*", get_dropdown_options("DROPDOWN_MAPPINGS", "Trade"))
        emp_sec = st.text_input("Employee Section (कर्मचारी का कार्यस्थल)*")
        g_type = st.selectbox("Grievance Type (समस्या का प्रकार)*", get_dropdown_options("DROPDOWN_MAPPINGS", "Grievance"))
        g_text = st.text_area("Brief of Grievance (समस्या का विवरण)*", max_chars=1000)

        if st.button("✅ Submit Grievance"):
            # Mandatory Check Logic
            fields = [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]
            if any(f == "" or f == "Select" for f in fields):
                st.markdown('<p class="err-text">⚠️ All fields marked with * are mandatory!</p>', unsafe_allow_html=True)
            else:
                # TIMESTAMP & GOOGLE SHEETS SUBMISSION
                now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                # write_to_grievance_sheet(...)
                st.success("Grievance Submitted Successfully!")
                st.balloons()

    if st.button("⬅️ Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')
