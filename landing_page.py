import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
import os
from datetime import datetime

# ==========================================
# 🎨 STYLE SETTINGS (Hardcoded & Permanent)
# ==========================================
LOGO_FILENAME = "assets/office_logo.png" 
LOGO_SIZE = 180                          
H_TEXT = "कैरिज वर्कशॉप, आलमाग, लखनऊ<br>Grievance Management System"
BG_COLOR = "#091327"

# Button & Form Styles
B_STYLE = f"""
    <style>
    .stApp {{ background-color: {BG_COLOR} !important; }}
    header, footer, #MainMenu {{visibility: hidden !important;}}

    /* Global Centering */
    [data-testid="stVerticalBlock"] {{ 
        display: flex !important; align-items: center !important; justify-content: center !important; 
        width: 100% !important; text-align: center !important;
    }}

    /* 🛡️ 16px Label Lock */
    [data-testid="stWidgetLabel"] p {{ font-size: 16px !important; font-weight: 800 !important; color: white !important; }}
    
    /* Iconic Landing & Form Buttons */
    div.stButton > button, div.stFormSubmitButton > button {{
        width: 420px !important; max-width: 90% !important; height: 85px !important;
        background-color: #e5e5e5 !important; color: #14213d !important;
        border-radius: 20px !important; border: 3px solid #fca311 !important;
        margin: 15px auto !important; font-weight: 1000 !important; font-size: 22px !important;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    }}
    
    /* Card Styles for Status */
    .status-card {{ background: rgba(255, 255, 255, 0.08); border-left: 6px solid #fca311; border-radius: 12px; padding: 20px; margin-bottom: 20px; text-align: left; width: 100%; }}
    </style>
"""
st.set_page_config(layout="wide", page_title="Railway GMS")
st.markdown(B_STYLE, unsafe_allow_html=True)

# ==========================================
# ⚙️ HELPERS & STATE
# ==========================================
if "page" not in st.session_state: st.session_state.page = "LANDING"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def get_base64_logo(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
logo_data = get_base64_logo(LOGO_FILENAME)

# Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Google Sheets Connection Failed.")
    st.stop()

# ==========================================
# 🏠 PAGE 1: LANDING
# ==========================================
def show_landing():
    logo_tag = f'<img src="data:image/png;base64,{logo_data}" width="{LOGO_SIZE}">' if logo_data else ""
    st.markdown(f"""
        <div style='text-align:center;'>
            {logo_tag}
            <h1 style='color:white; font-size:32px; font-weight:900;'>{H_TEXT}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 नया Grievance दर्ज करें"): navigate_to("REGISTRATION")
    if st.button("🔍 स्थिति देखें (Status Check)"): navigate_to("STATUS")
    if st.button("🔐 Officer Login"): navigate_to("LOGIN")

# ==========================================
# 📝 PAGE 2: REGISTRATION
# ==========================================
def show_registration():
    st.markdown("<h2 style='color:white;'>Grievance Registration</h2>", unsafe_allow_html=True)
    
    with st.container():
        # Narrow container for form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            hrms = st.text_input("अपनी HRMS ID दर्ज करें।").upper().strip()
            with st.form("reg"):
                emp_no = st.text_input("Employee Number*")
                g_type = st.selectbox("समस्या का प्रकार*", ["Electrical", "Mechanical", "Quarter", "Medical", "Establishment"])
                desc = st.text_area("समस्या का विवरण (Max 100 chars)*", max_chars=100)
                if st.form_submit_button("Submit"):
                    if not hrms or not desc:
                        st.error("Please fill all required fields.")
                    else:
                        st.session_state.ref_id = f"REF-{datetime.now().strftime('%M%S')}"
                        navigate_to("SUCCESS")
            
            if st.button("⬅️ Back"): navigate_to("LANDING")

# ==========================================
# ✅ PAGE 3: SUCCESS
# ==========================================
def show_success():
    st.markdown(f"""
        <div style='text-align:center; margin-top:50px;'>
            <h1 style='color:#a5be00; font-size:40px;'>सफलतापूर्वक दर्ज!</h1>
            <p style='color:white; font-size:20px;'>Your Reference ID is:</p>
            <div style='background:#fca311; color:#14213d; padding:20px; border-radius:15px; font-size:35px; font-weight:900; display:inline-block;'>
                {st.session_state.get('ref_id', 'N/A')}
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🏠 Back to Home"): navigate_to("LANDING")

# ==========================================
# 🔍 PAGE 4: STATUS VIEW
# ==========================================
def show_status():
    st.markdown("<h2 style='color:white;'>Check Grievance Status</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_id = st.text_input("Enter HRMS ID").upper().strip()
        if st.button("🔍 Search"):
            st.markdown(f"""
                <div class='status-card'>
                    <b style='color:#fca311;'>REF: 20250101XYZ</b><br>
                    <span style='color:white;'>Status: <b style='color:#a5be00;'>RESOLVED</b></span><br>
                    <p style='color:#ccc;'>Remark: Problem fixed by Electrical department.</p>
                </div>
            """, unsafe_allow_html=True)
        if st.button("⬅️ Back"): navigate_to("LANDING")

# ==========================================
# 🚦 MAIN ROUTER (THE CONTROLLER)
# ==========================================
if st.session_state.page == "LANDING":
    show_landing()
elif st.session_state.page == "REGISTRATION":
    show_registration()
elif st.session_state.page == "SUCCESS":
    show_success()
elif st.session_state.page == "STATUS":
    show_status()
elif st.session_state.page == "LOGIN":
    # Placeholder for Login Page
    st.write("Login Screen Coming Soon")
    if st.button("Back"): navigate_to("LANDING")
