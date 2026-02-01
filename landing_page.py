import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
import os
from datetime import datetime

# ==========================================
# 🎨 STYLE SETTINGS (Locked & Permanent)
# ==========================================
LOGO_FILENAME = "assets/office_logo.png" 
LOGO_SIZE = 180                         
LOGO_MARGIN = "20px"                    
H_TEXT = "कैरिज वर्कशॉप, आलमाग, लखनऊ<br>Grievance Management System"
H_COLOR = "white"; H_SIZE = "32px"; H_FONT = "'Trebuchet MS', sans-serif"; H_WEIGHT = "900"
REG_FORM_WIDTH = "480px"
B_MAX_WIDTH, B_WIDTH_MOBILE, B_HEIGHT = "420px", "90%", "85px"
B_TEXT_COLOR, B_BG_COLOR, B_FONT_SIZE, B_FONT_WEIGHT = "#14213d", "#e5e5e5", "22px", "1000"
B_ROUNDNESS, B_BORDER_WIDTH, B_BORDER_COLOR = "20px", "3px", "#fca311"

# ==========================================
# 🖼️ LOGO LOADER
# ==========================================
def get_base64_logo(file_path):
    try:
        root = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(root, file_path)
        if os.path.exists(full_path):
            # ✅ FIXED: Added 'as' keyword back into the with statement
            with open(full_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception: return None
    return None

logo_data = get_base64_logo(LOGO_FILENAME)

# ==========================================
# ⚙️ CSS ENGINE (STRICT LABEL & UI LOCK)
# ==========================================
st.set_page_config(layout="wide", page_title="Railway Grievance System")
st.markdown(f"""
    <style>
    .header-container {{ text-align: center; margin-top: 10px; margin-bottom: 30px; width: 100%; }}
    .logo-img {{ width: {LOGO_SIZE}px; max-width: 60%; height: auto; margin-bottom: {LOGO_MARGIN}; filter: drop-shadow(2px 4px 8px rgba(0,0,0,0.6)); }}
    .custom-header {{ font-family: {H_FONT}; color: {H_COLOR}; font-size: {H_SIZE}; font-weight: {H_WEIGHT}; line-height: 1.2; text-shadow: 3px 3px 10px rgba(0,0,0,0.8); padding: 0 10px; }}
    
    .st-key-reg_page_col, .st-key-status_container, .st-key-login_container, .st-key-choice_container {{ 
        max-width: {REG_FORM_WIDTH} !important; margin: 0 auto !important; padding: 10px; 
    }}
    
    [data-testid="stWidgetLabel"] p {{ 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        color: white !important; 
        margin-bottom: 8px !important; 
        text-align: left !important;
        width: 100% !important;
    }}
    
    [data-testid="stVerticalBlock"] {{ display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; width: 100% !important; }}
    
    div.stButton > button, div.stFormSubmitButton > button {{
        width: {B_MAX_WIDTH} !important; max-width: {B_WIDTH_MOBILE} !important; height: {B_HEIGHT} !important;
        background-color: {B_BG_COLOR} !important; color: {B_TEXT_COLOR} !important; border-radius: {B_ROUNDNESS} !important;
        border: {B_BORDER_WIDTH} solid {B_BORDER_COLOR} !important; margin: 15px auto !important; transition: all 0.3s ease; box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
        display: flex !important; align-items: center !important; justify-content: center !important;
    }}
    div.stButton > button p, div.stFormSubmitButton > button p {{ font-size: {B_FONT_SIZE} !important; font-weight: {B_FONT_WEIGHT} !important; color: {B_TEXT_COLOR} !important; margin: 0 !important; }}

    .status-card {{ background: rgba(255, 255, 255, 0.08) !important; border-left: 6px solid #fca311 !important; border-radius: 12px !important; padding: 20px !important; margin-bottom: 20px !important; width: 100% !important; text-align: left !important; }}
    .status-id {{ font-weight: 900; color: #fca311; font-size: 16px; }}
    .badge {{ padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 900; text-transform: uppercase; color: white; }}
    .status-new {{ background-color: #007bff; }}
    .status-resolved {{ background-color: #a5be00; }}
    .status-pending {{ background-color: #fca311; color: #14213d; }}
    .type-label {{ color: #fca311; font-weight: 800; font-size: 14px; display: block; margin-top: 5px; }}
    .meta-info {{ font-size: 12px; color: #adb5bd; margin-top: 10px; line-height: 1.5; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; }}
    .remark-box {{ background: rgba(252, 163, 17, 0.1); border-radius: 6px; padding: 10px; margin-top: 8px; color: #fca311; font-weight: 600; font-size: 13px; }}
    
    header, footer, #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
def load_sheet(name): return conn.read(worksheet=name, ttl="0")

def clean_val(val, fallback="Pending"):
    return fallback if pd.isna(val) or str(val).strip().lower() == 'nan' or not str(val).strip() else str(val)

if "page" not in st.session_state: st.session_state.page = "LANDING"
if "user" not in st.session_state: st.session_state.user = None

# ==========================================
# 🧭 PAGES
# ==========================================
if st.session_state.page == "LANDING":
    logo_tag = f'<img src="data:image/png;base64,{logo_data}" class="logo-img">' if logo_data else ""
    st.markdown(f'<div class="header-container">{logo_tag}<div class="custom-header">{H_TEXT}</div></div>', unsafe_allow_html=True)
    if st.button("📝 नया Grievance दर्ज करें"): st.session_state.page = "REG"; st.rerun()
    if st.button("🔍 अपने Grievance की वर्तमान स्थित देखें"): st.session_state.page = "STATUS"; st.rerun()
    if st.button("🔐 Officer/ Admin Login"): st.session_state.page = "LOGIN"; st.rerun()

elif st.session_state.page == "REG":
    st.markdown(f'<div class="header-container"><div class="custom-header">Grievance Registration</div></div>', unsafe_allow_html=True)
    with st.container(key="reg_page_col"):
        if "last_ref" not in st.session_state:
            try:
                emp_df = load_sheet("EMPLOYEE_MAPPING")
                drop_df = load_sheet("DROPDOWN_MAPPINGS")
                drop_df['CATEGORY'] = drop_df['CATEGORY'].astype(str).str.strip().str.upper()
                hrms_id = st.text_input("अपनी HRMS ID दर्ज करें।").upper().strip()
                match = emp_df[emp_df['HRMS_ID'].astype(str).str.strip().str.upper() == hrms_id]
                emp_name = match.iloc[0]['EMPLOYEE_NAME'] if not match.empty else ""
                if emp_name: st.success(f"✅ User Verified: {emp_name}")
                with st.form("reg_form"):
                    st.text_input("Employee Name (कर्मचारी का नाम)", value=emp_name, disabled=True)
                    emp_no = st.text_input("Employee No. (कर्मचारी संख्या)*")
                    d_list = drop_df[drop_df['CATEGORY'] == 'DESIGNATION']['ITEM_VALUE'].dropna().unique().tolist()
                    t_list = drop_df[drop_df['CATEGORY'] == 'TRADE']['ITEM_VALUE'].dropna().unique().tolist()
                    g_list = drop_df[drop_df['CATEGORY'] == 'GRIEVANCE_TYPE']['ITEM_VALUE'].dropna().unique().tolist()
                    st.selectbox("Designation (पद)*", ["--Select--"] + d_list, key="d_val")
                    st.selectbox("Trade (ट्रेड)*", ["--Select--"] + t_list, key="t_val")
                    st.text_input("Section (कार्यस्थल)*", key="s_val")
                    st.selectbox("Grievance Type (समस्या का प्रकार)*", ["--Select--"] + g_list, key="g_type_val")
                    st.text_area("Brief of Grievance (समस्या का संक्षिपत्त विवरण)*", max_chars=100, key="desc")
                    if st.form_submit_button("Submit"):
                        if not emp_name or not st.session_state.desc.strip() or st.session_state.g_type_val == "--Select--":
                            st.error("❌ सभी अनिवार्य क्षेत्र भरें")
                        else:
                            prev_g = load_sheet("GRIEVANCE")
                            ref = f"{datetime.now().strftime('%Y%m%d')}{hrms_id}{str(len(prev_g[prev_g['HRMS_ID']==hrms_id])+1).zfill(3)}"
                            new_entry = pd.DataFrame([{"REFERENCE_NO": ref, "DATE_TIME": datetime.now().strftime("%d-%m-%Y %H:%M"), "HRMS_ID": hrms_id, "EMP_NAME": emp_name, "EMP_NO": emp_no, "DESIGNATION": st.session_state.d_val, "TRADE": st.session_state.t_val, "SECTION": st.session_state.s_val, "GRIEVANCE_TYPE": st.session_state.g_type_val, "GRIEVANCE_TEXT": st.session_state.desc, "STATUS": "NEW", "OFFICER_REMARK": "", "REMARK_BY": ""}])
                            conn.update(worksheet="GRIEVANCE", data=pd.concat([prev_g, new_entry], ignore_index=True))
                            st.session_state.last_ref = ref; st.rerun()
            except Exception as e: st.error(f"Error: {e}")
            if st.button("Back"): st.session_state.page = "LANDING"; st.rerun()
        else:
            st.markdown(f'<div class="success-card-refined"><h1 class="balanced-title">सफलतापूर्वक दर्ज!</h1><div class="ref-id-balanced">{st.session_state.last_ref}</div></div>', unsafe_allow_html=True)
            if st.button("Back to Home"): del st.session_state.last_ref; st.session_state.page = "LANDING"; st.rerun()

elif st.session_state.page == "STATUS":
    st.markdown(f'<div class="header-container"><div class="custom-header">Grievance Status Tracking</div></div>', unsafe_allow_html=True)
    with st.container(key="status_container"):
        search_id = st.text_input("Enter HRMS ID").upper().strip()
        if st.button("Search"):
            data = load_sheet("GRIEVANCE")
            recs = data[data['HRMS_ID'].astype(str).str.strip().str.upper() == search_id].sort_index(ascending=False)
            if not recs.empty:
                for _, row in recs.iterrows():
                    status_raw = clean_val(row.get('STATUS'), "NEW").upper()
                    st.markdown(f"""
                        <div class="status-card">
                            <div class="status-header">
                                <span class="status-id">REF: {row['REFERENCE_NO']}</span>
                                <span class="badge status-{status_raw.lower()}">{status_raw}</span>
                            </div>
                            <span class="type-label">📌 समस्या: {clean_val(row.get('GRIEVANCE_TYPE'), 'General')}</span>
                            <div style="color:white; margin: 15px 0;">{row['GRIEVANCE_TEXT']}</div>
                            <div class="meta-info">
                                📅 <b>दर्ज तिथि:</b> {clean_val(row.get('DATE_TIME'), 'N/A')}<br>
                                👮 <b>संबंधित अधिकारी:</b> {clean_val(row.get('REMARK_BY'), 'Pending')}
                                <div class="remark-box">💬 <b>Officer Remark:</b><br>{clean_val(row.get('OFFICER_REMARK'), 'Awaiting action...')}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.warning("No records found.")
        if st.button("Home"): st.session_state.page = "LANDING"; st.rerun()

elif st.session_state.page == "LOGIN":
    st.markdown(f'<div class="header-container"><div class="custom-header">Officer/ Admin Login</div></div>', unsafe_allow_html=True)
    with st.container(key="login_container"):
        off_df = load_sheet("OFFICER_MAPPING")
        h_input = st.text_input("HRMS ID").upper().strip()
        match = off_df[off_df['HRMS_ID'].astype(str).str.strip().str.upper() == h_input]
        if not match.empty:
            user_row = match.iloc[0]
            st.success(f"✅ User Verified: {user_row['NAME']}")
            with st.form("login_form"):
                k_input = st.text_input("Key", type="password").strip()
                if st.form_submit_button("Login"):
                    try: sheet_key = str(int(float(user_row['LOGIN_KEY']))).strip()
                    except: sheet_key = str(user_row['LOGIN_KEY']).strip()
                    if sheet_key == k_input:
                        st.session_state.user = user_row.to_dict()
                        role_str = str(user_row['ROLE']).strip().upper()
                        if "BOTH" in role_str or "BOT" in role_str or "," in role_str: st.session_state.page = "CHOOSER"
                        elif "ADMIN" in role_str: st.session_state.page = "ADMIN_DASHBOARD"
                        elif "OFFICER" in role_str: st.session_state.page = "OFFICER_DASHBOARD"
                        st.rerun()
                    else: st.error("❌ Invalid Key.")
        if st.button("Back"): st.session_state.page = "LANDING"; st.rerun()

elif st.session_state.page == "CHOOSER":
    st.markdown(f'<div class="header-container"><div class="custom-header">DASHBOARD SELECTOR</div></div>', unsafe_allow_html=True)
    with st.container(key="choice_container"):
        if st.button("📈 OFFICER DASHBOARD"): st.session_state.page = "OFFICER_DASHBOARD"; st.rerun()
        if st.button("🛠️ ADMIN DASHBOARD"): st.session_state.page = "ADMIN_DASHBOARD"; st.rerun()
        if st.button("Logout"): st.session_state.user = None; st.session_state.page = "LANDING"; st.rerun()

elif st.session_state.page == "OFFICER_DASHBOARD" or st.session_state.page == "ADMIN_DASHBOARD":
    st.markdown(f'<div class="header-container"><div class="custom-header">{st.session_state.page.replace("_", " ")}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-msg" style="text-align:center; color:white; font-size:24px; font-weight:bold; margin-bottom:20px;">Welcome, <span style="color:#fca311;">{st.session_state.user["NAME"]}</span></div>', unsafe_allow_html=True)
    
    if st.session_state.page == "ADMIN_DASHBOARD":
        st.subheader("📊 System-Wide Oversight")
        all_g = load_sheet("GRIEVANCE")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Filed", len(all_g))
        c2.metric("Resolved", len(all_g[all_g['STATUS'] == 'RESOLVED']))
        c3.metric("Pending", len(all_g[all_g['STATUS'] != 'RESOLVED']))
        st.dataframe(all_g, use_container_width=True)
        
    if st.button("Logout"): st.session_state.user = None; st.session_state.page = "LANDING"; st.rerun()
