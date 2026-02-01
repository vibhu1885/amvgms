import streamlit as st
import base64
import os

st.set_page_config(layout="wide", page_title="Railway GMS", initial_sidebar_state="collapsed")

# ==========================================
# 🖼️ LOGO LOADER LOGIC
# ==========================================
def get_base64_logo(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_data = get_base64_logo("assets/office_logo.png")

# ==========================================
# 🎨 STYLE MODULE (BG: #091327 | Font: 1000 Bold)
# ==========================================
st.markdown(f"""
    <style>
    .stApp {{ background-color: #091327 !important; }}
    [data-testid="stSidebar"], [data-testid="stHeader"], footer {{ visibility: hidden !important; }}
    
    [data-testid="stVerticalBlock"] {{ 
        display: flex !important; align-items: center !important; justify-content: center !important; 
    }}

    /* 💎 ICONIC BUTTON STYLE RESTORED */
    div.stButton > button {{
        width: 420px !important; max-width: 90% !important; height: 85px !important;
        background-color: #e5e5e5 !important; color: #14213d !important;
        border-radius: 20px !important; border: 3px solid #fca311 !important;
        margin: 15px auto !important; 
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
    }}

    /* 🛡️ FONT SIZE & BOLDNESS LOCK */
    div.stButton > button p {{ 
        font-size: 22px !important; 
        font-weight: 1000 !important; 
        color: #14213d !important; 
    }}

    div.stButton > button:hover {{
        background-color: #a5be00 !important;
        border-color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- UI DISPLAY ---
if logo_data:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_data}" width="180" style="filter: drop-shadow(2px 4px 8px rgba(0,0,0,0.6)); margin-bottom:20px;"></div>', unsafe_allow_html=True)

st.markdown("<h1 style='color:white; text-align:center; font-family:sans-serif; font-weight:900;'>कैरिज वर्कशॉप, आलमाग<br>Grievance Management System</h1>", unsafe_allow_html=True)

# --- NAVIGATION BUTTONS ---
if st.button("📝 नया Grievance दर्ज करें"):
    st.switch_page("pages/1_Registration.py")

if st.button("🔍 स्थिति देखें"):
    st.switch_page("pages/3_Status_Login.py")

if st.button("🔐 Officer Login"):
    st.switch_page("pages/5_Admin_Login.py")
