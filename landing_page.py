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

# Button Master Controls
BTN_HEIGHT = "70px"        
BTN_WIDTH = "300px"         
BTN_BG_COLOR = "#faf9f9"
BTN_TEXT_COLOR = "#131419"
BTN_BORDER_COLOR = "#fca311"
BTN_BORDER_WIDTH = "4px"
BTN_ROUNDNESS = "22px"
BTN_HOVER_COLOR = "#a7c957" # Greenish hover
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

    /* Main Container */
    .block-container {{
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    /* Vertical Block Alignment */
    [data-testid="stVerticalBlock"] {{ 
        width: 100% !important; 
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
    }}

    /* BUTTON STYLING & HOVER FIX */
    .stButton {{ width: 100% !important; display: flex !important; justify-content: center !important; }}

    div.stButton > button {{
        background-color: {BTN_BG_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        border: {BTN_BORDER_WIDTH} solid {BTN_BORDER_COLOR} !important;
        border-radius: {BTN_ROUNDNESS} !important;
        width: {BTN_WIDTH} !important; 
        max-width: 100% !important;
        height: {BTN_HEIGHT} !important;
        margin: 10px 0px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Explicit Hover State */
    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        border-color: {BTN_TEXT_COLOR} !important;
        color: {BTN_TEXT_COLOR} !important;
        transform: scale(1.02) !important;
    }}

    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important; 
        margin: 0 !important;
    }}

    /* Text & Labels */
    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; text-align: center; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; text-align: center; }}
    label {{ color: {LABEL_COLOR} !important; font-weight: bold; font-size: 15px; width: 100%; text-align: left; }}
    
    .err-msg {{ color: #FF4B4B; font-size: 13px; font-weight: bold; margin-top: -10px; margin-bottom: 10px; width: 100%; text-align: left; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=LOGO_WIDTH)
    st.markdown('<div class="hindi-heading">सवारी डिब्बा कारखाना, आलमबाग, लखनऊ</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">Grievance Management System</div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): go_to('new_form')
    if st.button("🔍 ग्रीवांस की वर्तमान स्थिति जानें"): go_to('status_check')
    if st.button("🔐 Officer/ Admin Login"): go_to('login')

# --- PAGE 2: REGISTRATION ---
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">समस्या पंजीकरण</div>', unsafe_allow_html=True)

    if not st.session_state.hrms_verified:
        hrms_id = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6, placeholder="HRMS ID").upper().strip()
        if st.button("Verify ID / सत्यापित करें"):
            if len(hrms_id) == 6 and hrms_id.isalpha():
                try:
                    df = pd.DataFrame(get_sheet("EMPLOYEE_MAPPING").get_all_records())
                    match = df[df['HRMS_ID'] == hrms_id]
                    if not match.empty:
                        st.session_state.found_emp_name = match.iloc[0]['EMPLOYEE_NAME']
                        st.session_state.hrms_verified = True
                        st.session_state.active_hrms = hrms_id
                        st.rerun()
                    else: st.error("❌ HRMS ID not found.")
                except Exception as e: st.error(f"Mapping Error: {e}")
            else: st.error("⚠️ Use 6 CAPITAL alphabets.")
    
    else:
        st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
        
        try:
            dd_df = pd.DataFrame(get_sheet("DROPDOWN_MAPPINGS").get_all_records())
            designations = ["Select"] + [x for x in dd_df['DESIGNATION_LIST'].dropna().unique().tolist() if x]
            trades = ["Select"] + [x for x in dd_df['TRADE_LIST'].dropna().unique().tolist() if x]
            g_types = ["Select"] + [x for x in dd_df['GRIEVANCE_TYPE_LIST'].dropna().unique().tolist() if x]
        except:
            designations = trades = g_types = ["Select"]

        emp_name = st.text_input("Employee Name (कर्मचारी का नाम)*", value=st.session_state.found_emp_name, disabled=True)
        
        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        if not emp_no and 'tried_submit' in st.session_state: st.markdown('<p class="err-msg">⚠️ Required</p>', unsafe_allow_html=True)

        emp_desig = st.selectbox("Employee Designation (कर्मचारी का पद)*", designations)
        if emp_desig == "Select" and 'tried_submit' in st.session_state: st.markdown('<p class="err-msg">⚠️ Select Designation</p>', unsafe_allow_html=True)

        emp_trade = st.selectbox("Employee Trade (कर्मचारी का ट्रेड)*", trades)
        if emp_trade == "Select" and 'tried_submit' in st.session_state: st.markdown('<p class="err-msg">⚠️ Select Trade</p>', unsafe_allow_html=True)

        emp_sec = st.text_input("Employee Section (कर्मचारी का कार्यस्थल)*")
        if not emp_sec and 'tried_submit' in st.session_state: st.markdown('<p class="err-msg">⚠️ Section Required</p>', unsafe_allow_html=True)

        g_type = st.selectbox("Grievance Type (समस्या का प्रकार)*", g_types)
        if g_type == "Select" and 'tried_submit' in st.session_state: st.markdown('<p class="err-msg">⚠️ Select Type</p>', unsafe_allow_html=True)

        g_text = st.text_area("Brief of Grievance (समस्या का विवरण)*", max_chars=1000)
        if not g_text and 'tried_submit' in st.session_state: st.markdown('<p class="err-msg">⚠️ Details Required</p>', unsafe_allow_html=True)

        if st.button("Grievance जमा करें।"):
            st.session_state.tried_submit = True
            if not any(x in [None, "", "Select"] for x in [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]):
                now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                ref_no = "REF" + datetime.now().strftime("%y%m%d%H%M%S")
                try:
                    # NEW is the default status here
                    new_row = [ref_no, now, st.session_state.active_hrms, st.session_state.found_emp_name, 
                               emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "NEW", "N/A", "N/A"]
                    get_sheet("grievance").append_row(new_row)
                    st.success(f"Grievance Submitted! Ref No: {ref_no}")
                    st.balloons()
                    st.session_state.hrms_verified = False
                    if 'tried_submit' in st.session_state: del st.session_state.tried_submit
                except Exception as e: st.error(f"Submission Failed: {e}")
            else: st.rerun()

    if st.button("⬅️ Back to Home"):
        st.session_state.hrms_verified = False
        if 'tried_submit' in st.session_state: del st.session_state.tried_submit
        go_to('landing')

# --- PAGE 3: STATUS CHECK ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">Grievance Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">वर्तमान स्थिति जानें</div>', unsafe_allow_html=True)
    ref_input = st.text_input("Enter Reference Number*", placeholder="REFXXXXXXXX").strip()
    if st.button("🔍 Check Status"):
        if ref_input:
            try:
                df = pd.DataFrame(get_sheet("grievance").get_all_records())
                match = df[df['REFERENCE_NO'].astype(str) == ref_input]
                if not match.empty:
                    res = match.iloc[0]
                    st.markdown("---")
                    st.success(f"Record Found: {res['EMP_NAME']}")
                    st.info(f"**Status:** {res['STATUS']}")
                    st.warning(f"**Remark:** {res['OFFICER_REMARK']}")
                else: st.error("No record found.")
            except Exception as e: st.error(f"Error: {e}")
    if st.button("⬅️ Back to Home"): go_to('landing')

# --- PAGE 4: ADMIN LOGIN ---
elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Officer Login</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')
