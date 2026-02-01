import streamlit as st
import base64
import os

# ==========================================
# 🎨 STYLE SETTINGS
# ==========================================
LOGO_FILENAME = "assets/office_logo.png" 
LOGO_SIZE = 180                         
LOGO_MARGIN = "20px"                    
H_TEXT = "कैरिज वर्कशॉप, आलमाग, लखनऊ<br>Grievance Management System"
H_COLOR = "white"; H_SIZE = "32px"; H_FONT = "'Trebuchet MS', sans-serif"; H_WEIGHT = "900"

B_MAX_WIDTH, B_WIDTH_MOBILE, B_HEIGHT = "420px", "90%", "85px"
B_TEXT_COLOR, B_BG_COLOR, B_FONT_SIZE, B_FONT_WEIGHT = "#14213d", "#e5e5e5", "22px", "1000"
B_ROUNDNESS, B_BORDER_WIDTH, B_BORDER_COLOR = "20px", "3px", "#fca311"

# ==========================================
# 🌈 BACKGROUND CONTROL ENGINE
# ==========================================
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0e1117"  # Default Dark

# Small UI for color selection at the very top
cols = st.columns([8, 2])
with cols[1]:
    new_bg = st.color_picker("Page BG", st.session_state.bg_color, key="bg_picker")
    st.session_state.bg_color = new_bg

# ==========================================
# ⚙️ CSS ENGINE
# ==========================================
st.set_page_config(layout="wide", page_title="Railway Grievance System", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
    /* Dynamic Background Injection */
    .stApp {{
        background-color: {st.session_state.bg_color} !important;
    }}

    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"] {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    [data-testid="stVerticalBlock"] {{ 
        display: flex !important; 
        flex-direction: column !important; 
        align-items: center !important; 
        justify-content: center !important; 
        width: 100% !important; 
        text-align: center !important;
    }}

    .header-container {{ text-align: center; margin-top: -20px; margin-bottom: 30px; width: 100%; }}
    .custom-header {{ 
        font-family: {H_FONT}; color: {H_COLOR}; font-size: {H_SIZE}; 
        font-weight: {H_WEIGHT}; line-height: 1.2; text-shadow: 3px 3px 10px rgba(0,0,0,0.8); 
    }}

    @media (max-width: 600px) {{
        .custom-header {{ font-size: 24px !important; }}
        div.stButton > button {{ height: 75px !important; width: 95% !important; }}
        div.stButton > button p {{ font-size: 18px !important; }}
    }}

    div.stButton > button {{
        width: {B_MAX_WIDTH} !important; max-width: {B_WIDTH_MOBILE} !important; height: {B_HEIGHT} !important;
        background-color: {B_BG_COLOR} !important; color: {B_TEXT_COLOR} !important; border-radius: {B_ROUNDNESS} !important;
        border: {B_BORDER_WIDTH} solid {B_BORDER_COLOR} !important; margin: 15px auto !important; 
        transition: all 0.3s ease; box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
        display: flex !important; align-items: center !important; justify-content: center !important;
    }}

    div.stButton > button p {{ font-size: {B_FONT_SIZE} !important; font-weight: {B_FONT_WEIGHT} !important; color: {B_TEXT_COLOR} !important; margin: 0 !important; }}
    div.stButton > button:hover {{ transform: scale(1.02) !important; background-color: #a5be00 !important; border-color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🖼️ LOGO LOADER
# ==========================================
def get_base64_logo(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception: return None
    return None

logo_data = get_base64_logo(LOGO_FILENAME)

# ==========================================
# 🧭 LANDING UI
# ==========================================
logo_tag = f'<img src="data:image/png;base64,{logo_data}" style="width:{LOGO_SIZE}px; max-width: 60%; margin-bottom:{LOGO_MARGIN}; filter: drop-shadow(2px 4px 8px rgba(0,0,0,0.6));">' if logo_data else ""

st.markdown(f"""
    <div class="header-container">
        {logo_tag}
        <div class="custom-header">{H_TEXT}</div>
    </div>
""", unsafe_allow_html=True)

if st.button("📝 नया Grievance दर्ज करें"):
    st.switch_page("pages/1_Registration.py")

if st.button("🔍 Grievance की स्थिति देखें"):
    st.switch_page("pages/3_Status_Login.py")

if st.button("🔐 Officer/ Admin Login"):
    st.switch_page("pages/5_Admin_Login.py")
