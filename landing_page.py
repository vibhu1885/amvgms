import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ==========================================
# 0. GOOGLE SHEETS CONNECTION SETUP
# ==========================================
def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Pulling credentials directly from Streamlit Secrets
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    # Open the workbook and specific sheet
    sheet = client.open("Grievance_DB").worksheet(sheet_name)
    return sheet

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

    div.stButton > button:hover {{ background-color: {BTN_HOVER_COLOR} !important; transform: translateY(-2px); }}

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
    
    .err-text {{ color: #e63946; font-size: 14px; text-align: center; font-weight: bold; margin-bottom: 10px; }}
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

    if not st.session_state.hrms_verified:
        hrms_id = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6, placeholder="HRMS ID").upper().strip()
        
        if st.button("Verify ID / सत्यापित करें"):
            if len(hrms_id) == 6 and hrms_id.isalpha():
                try:
                    mapping_ws = get_sheet("EMPLOYEE_MAPPING")
                    df = pd.DataFrame(mapping_ws.get_all_records())
                    match = df[df['HRMS_ID'] == hrms_id]
                    
                    if not match.empty:
                        st.session_state.found_emp_name = match.iloc[0]['EMPLOYEE_NAME']
                        st.session_state.hrms_verified = True
                        st.session_state.active_hrms = hrms_id
                        st.rerun()
                    else:
                        st.error("❌ HRMS ID not found in mapping sheet.")
                except Exception as e:
                    st.error(f"Error connecting to Sheets: {e}")
            else:
                st.error("⚠️ Invalid Format! Use 6 CAPITAL alphabets.")
    
    else:
        # FORM SECTION - Appears after verification
        st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
        
        try:
            dd_ws = get_sheet("DROPDOWN_MAPPINGS")
            dd_df = pd.DataFrame(dd_ws.get_all_records())
            designations = ["Select"] + dd_df['DESIGNATION'].dropna().unique().tolist()
            trades = ["Select"] + dd_df['TRADE'].dropna().unique().tolist()
            g_types = ["Select"] + dd_df['GRIEVANCE_TYPE'].dropna().unique().tolist()
        except:
            designations = trades = g_types = ["Select", "Error Loading"]

        emp_name = st.text_input("Employee Name (कर्मचारी का नाम)*", value=st.session_state.found_emp_name, disabled=True)
        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        emp_desig = st.selectbox("Employee Designation (कर्मचारी का पद)*", designations)
        emp_trade = st.selectbox("Employee Trade (कर्मचारी का ट्रेड)*", trades)
        emp_sec = st.text_input("Employee Section (कर्मचारी का कार्यस्थल)*")
        g_type = st.selectbox("Grievance Type (समस्या का प्रकार)*", g_types)
        g_text = st.text_area("Brief of Grievance (समस्या का विवरण)*", max_chars=1000)

        if st.button("✅ Submit Grievance"):
            form_data = [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]
            if any(x in [None, "", "Select"] for x in form_data):
                st.markdown('<p class="err-text">⚠️ All fields marked with * are mandatory!</p>', unsafe_allow_html=True)
            else:
                now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                ref_no = "REF" + datetime.now().strftime("%y%m%d%H%M%S")
                try:
                    grievance_ws = get_sheet("grievance")
                    new_row = [ref_no, now, st.session_state.active_hrms, st.session_state.found_emp_name, 
                               emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "Pending", "N/A", "N/A"]
                    grievance_ws.append_row(new_row)
                    st.success(f"Grievance Submitted! Ref No: {ref_no}")
                    st.balloons()
                except Exception as e:
                    st.error(f"Submission failed: {e}")

    if st.button("⬅️ Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- OTHER PAGES ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">Check Status</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')

elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Admin Login</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')
