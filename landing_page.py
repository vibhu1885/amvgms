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
# STRICT ALIGNMENT ENGINE (STRICT CENTER LOGO/BTN, LEFT LABELS)
# ==========================================
custom_css = f"""
<style>
    header, footer, [data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .stApp {{ background-color: {APP_BG_COLOR}; }}

    .block-container {{
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        margin: 0 auto !important;
    }}

    /* STRICT LOGO CENTERING */
    [data-testid="stImage"] {{ 
        display: flex !important; 
        justify-content: center !important; 
        width: 100% !important; 
    }}

    /* STRICT BUTTON CENTERING + BOLDNESS + SHADOW */
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
        margin: 15px auto !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.6) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div.stButton > button:hover {{
        background-color: {BTN_HOVER_COLOR} !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 25px rgba(167, 201, 87, 0.4) !important;
    }}
    div.stButton > button p {{ 
        font-size: {BTN_TEXT_SIZE} !important; 
        font-weight: {BTN_FONT_WEIGHT} !important; 
        color: {BTN_TEXT_COLOR} !important;
    }}

    /* STRICT LEFT ALIGN FOR LABELS & INPUTS */
    [data-testid="stVerticalBlock"] {{ align-items: flex-start !important; }}
    label {{ 
        color: {LABEL_COLOR} !important; 
        font-weight: bold !important; 
        text-align: left !important; 
        width: 100% !important;
        display: block !important;
    }}
    
    .hindi-heading, .english-heading {{ text-align: center !important; width: 100% !important; }}
    .hindi-heading {{ color: {HEADING_COLOR}; font-size: 20px; font-weight: 900; }}
    .english-heading {{ color: {HEADING_COLOR}; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
    .err-msg {{ color: #FF4B4B; font-size: 13px; font-weight: bold; text-align: left !important; width: 100%; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# NAVIGATION & LOGIC
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'hrms_verified' not in st.session_state: st.session_state.hrms_verified = False

def go_to(page_name):
    st.session_state.page = page_name

def generate_ref_no(hrms_id, df_grievance):
    date_str = datetime.now().strftime("%Y%m%d")
    count = 1
    if not df_grievance.empty and 'HRMS_ID' in df_grievance.columns:
        count = len(df_grievance[df_grievance['HRMS_ID'] == hrms_id]) + 1
    return f"{date_str}{hrms_id}{str(count).zfill(3)}"

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
        hrms_input = st.text_input("Enter HRMS ID (अपनी HRMS ID दर्ज करें)*", max_chars=6).upper().strip()
        if st.button("Verify ID / सत्यापित करें"):
            if len(hrms_input) == 6 and hrms_input.isalpha():
                try:
                    df = pd.DataFrame(get_sheet("EMPLOYEE_MAPPING").get_all_records())
                    match = df[df['HRMS_ID'] == hrms_input]
                    if not match.empty:
                        st.session_state.found_emp_name = match.iloc[0]['EMPLOYEE_NAME']
                        st.session_state.hrms_verified = True
                        st.session_state.active_hrms = hrms_input
                        st.rerun()
                    else: st.error("❌ HRMS ID not found.")
                except Exception as e: st.error(f"Error: {e}")
    else:
        st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
        try:
            dd_df = pd.DataFrame(get_sheet("DROPDOWN_MAPPINGS").get_all_records())
            designations = ["Select"] + [x for x in dd_df['DESIGNATION_LIST'].dropna().unique().tolist() if x]
            trades = ["Select"] + [x for x in dd_df['TRADE_LIST'].dropna().unique().tolist() if x]
            g_types = ["Select"] + [x for x in dd_df['GRIEVANCE_TYPE_LIST'].dropna().unique().tolist() if x]
        except:
            designations = trades = g_types = ["Select"]

        emp_no = st.text_input("Employee Number (कर्मचारी संख्या)*")
        emp_desig = st.selectbox("Employee Designation (कर्मचारी का पद)*", designations)
        emp_trade = st.selectbox("Employee Trade (कर्मचारी का ट्रेड)*", trades)
        emp_sec = st.text_input("Employee Section (कर्मचारी का कार्यस्थल)*")
        g_type = st.selectbox("Grievance Type (समस्या का प्रकार)*", g_types)
        g_text = st.text_area("Brief of Grievance (समस्या का विवरण)*", max_chars=1000)

        if st.button("Grievance जमा करें।"):
            if not any(x in [None, "", "Select"] for x in [emp_no, emp_desig, emp_trade, emp_sec, g_type, g_text]):
                try:
                    ws = get_sheet("GRIEVANCE")
                    df_g = pd.DataFrame(ws.get_all_records())
                    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    ref_no = generate_ref_no(st.session_state.active_hrms, df_g)
                    
                    new_row = [ref_no, now, st.session_state.active_hrms, st.session_state.found_emp_name, 
                               emp_no, emp_sec, emp_desig, emp_trade, g_type, g_text, "NEW", "N/A", "N/A"]
                    ws.append_row(new_row)
                    st.success(f"Registered! Ref No: {ref_no}")
                    st.balloons()
                    st.session_state.hrms_verified = False
                except Exception as e: st.error(f"Failed: {e}")

    if st.button("⬅️ Back to Home"):
        st.session_state.hrms_verified = False
        go_to('landing')

# --- PAGE 3: STATUS CHECK ---
elif st.session_state.page == 'status_check':
    st.markdown('<div class="hindi-heading">Grievance Status</div>', unsafe_allow_html=True)
    ref_input = st.text_input("Enter Reference Number*", placeholder="e.g. 20260201ABCDEF001").strip()
    if st.button("🔍 Check Status"):
        if ref_input:
            try:
                df = pd.DataFrame(get_sheet("GRIEVANCE").get_all_records())
                match = df[df['REFERENCE_NO'].astype(str) == ref_input]
                if not match.empty:
                    res = match.iloc[0]
                    st.success(f"Status: {res['STATUS']}")
                    st.info(f"**Officer Remark:** {res['OFFICER_REMARK']}")
                else: st.error("No record found.")
            except Exception as e: st.error(f"Error: {e}")
    if st.button("⬅️ Back to Home"): go_to('landing')

elif st.session_state.page == 'login':
    st.markdown('<div class="hindi-heading">Superuser Login</div>', unsafe_allow_html=True)
    if st.button("⬅️ Back to Home"): go_to('landing')
