import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64
import os
from datetime import datetime

# ==========================================
# 🎨 STYLE SETTINGS
# ==========================================
LOGO_FILENAME = "assets/office_logo.png" 
LOGO_SIZE = 180                          
H_TEXT = "कैरिज वर्कशॉप, आलबाग, लखनऊ<br>Grievance Management System"
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
            with open(full_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception: return None
    return None

logo_data = get_base64_logo(LOGO_FILENAME)

# ==========================================
# ⚙️ CSS ENGINE
# ==========================================
st.set_page_config(layout="wide", page_title="Railway Grievance System")
st.markdown(f"""
    <style>
    .header-container {{ text-align: center; margin-top: 10px; margin-bottom: 30px; width: 100%; }}
    .logo-img {{ width: {LOGO_SIZE}px; max-width: 60%; height: auto; margin-bottom: 20px; filter: drop-shadow(2px 4px 8px rgba(0,0,0,0.6)); }}
    .custom-header {{ font-family: {H_FONT}; color: {H_COLOR}; font-size: {H_SIZE}; font-weight: {H_WEIGHT}; line-height: 1.2; text-shadow: 3px 3px 10px rgba(0,0,0,0.8); padding: 0 10px; }}
    
    .st-key-reg_page_col, .st-key-status_container, .st-key-login_container, .st-key-choice_container {{ 
        max-width: {REG_FORM_WIDTH} !important; margin: 0 auto !important; 
    }}
    
    [data-testid="stWidgetLabel"] p {{ font-size: 16px !important; font-weight: 800 !important; color: white !important; }}
    
    div.stButton > button, div.stFormSubmitButton > button {{
        width: {B_MAX_WIDTH} !important; max-width: {B_WIDTH_MOBILE} !important; height: {B_HEIGHT} !important;
        background-color: {B_BG_COLOR} !important; color: {B_TEXT_COLOR} !important; border-radius: {B_ROUNDNESS} !important;
        border: {B_BORDER_WIDTH} solid {B_BORDER_COLOR} !important; margin: 15px auto !important; font-weight: {B_FONT_WEIGHT} !important;
    }}

    .status-card {{ background: rgba(255, 255, 255, 0.08); border-left: 6px solid #fca311; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
    .status-id {{ font-weight: 900; color: #fca311; }}
    .badge {{ padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 900; color: white; }}
    .status-new {{ background-color: #007bff; }}
    .status-resolved {{ background-color: #28a745; }}
    .status-pending {{ background-color: #fca311; color: #14213d; }}
    
    .success-card-refined {{ background: #1a1a1a; padding: 40px; border-radius: 20px; text-align: center; border: 2px solid #28a745; }}
    .ref-id-balanced {{ font-size: 28px; color: #fca311; font-weight: 900; margin: 20px 0; }}
    
    header, footer, #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📊 DATA CONNECTIONS
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name): 
    return conn.read(worksheet=name, ttl="0")

def clean_val(val, fallback="Pending"):
    if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']: return fallback
    return str(val).strip()

if "page" not in st.session_state: st.session_state.page = "LANDING"
if "user" not in st.session_state: st.session_state.user = None

# ==========================================
# 🧭 APP LOGIC
# ==========================================

# 1. LANDING PAGE
if st.session_state.page == "LANDING":
    logo_tag = f'<img src="data:image/png;base64,{logo_data}" class="logo-img">' if logo_data else ""
    st.markdown(f'<div class="header-container">{logo_tag}<div class="custom-header">{H_TEXT}</div></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("📝 नया Grievance दर्ज करें"): 
            st.session_state.page = "REG"; st.rerun()
        if st.button("🔍 Grievance की स्थिति देखें"): 
            st.session_state.page = "STATUS"; st.rerun()
        if st.button("🔐 Officer/ Admin Login"): 
            st.session_state.page = "LOGIN"; st.rerun()

# 2. REGISTRATION PAGE
elif st.session_state.page == "REG":
    st.markdown(f'<div class="header-container"><div class="custom-header">Grievance Registration</div></div>', unsafe_allow_html=True)
    with st.container(key="reg_page_col"):
        if "last_ref" not in st.session_state:
            emp_df = load_sheet("EMPLOYEE_MAPPING")
            drop_df = load_sheet("DROPDOWN_MAPPINGS")
            
            hrms_id = st.text_input("HRMS ID दर्ज करें").upper().strip()
            match = emp_df[emp_df['HRMS_ID'].astype(str).str.upper() == hrms_id]
            
            emp_name = match.iloc[0]['EMPLOYEE_NAME'] if not match.empty else ""
            if emp_name: st.success(f"✅ User: {emp_name}")
            
            with st.form("reg_form"):
                st.text_input("Employee Name", value=emp_name, disabled=True)
                emp_no = st.text_input("Employee No.*")
                
                # Dynamic Dropdowns
                d_list = drop_df[drop_df['CATEGORY'] == 'DESIGNATION']['ITEM_VALUE'].tolist()
                t_list = drop_df[drop_df['CATEGORY'] == 'TRADE']['ITEM_VALUE'].tolist()
                g_list = drop_df[drop_df['CATEGORY'] == 'GRIEVANCE_TYPE']['ITEM_VALUE'].tolist()
                
                desig = st.selectbox("Designation*", ["--Select--"] + d_list)
                trade = st.selectbox("Trade*", ["--Select--"] + t_list)
                sect = st.text_input("Section (कार्यस्थल)*")
                g_type = st.selectbox("Grievance Type*", ["--Select--"] + g_list)
                desc = st.text_area("Brief Description (100 chars)*", max_chars=100)
                
                if st.form_submit_button("Submit Grievance"):
                    if not emp_name or not desc or g_type == "--Select--":
                        st.error("❌ कृपया सभी जानकारी भरें")
                    else:
                        prev_g = load_sheet("GRIEVANCE")
                        ref = f"G{datetime.now().strftime('%y%m%d%H%M')}"
                        new_data = pd.DataFrame([{
                            "REFERENCE_NO": ref, "DATE_TIME": datetime.now().strftime("%d-%m-%Y %H:%M"),
                            "HRMS_ID": hrms_id, "EMP_NAME": emp_name, "EMP_NO": emp_no,
                            "DESIGNATION": desig, "TRADE": trade, "SECTION": sect,
                            "GRIEVANCE_TYPE": g_type, "GRIEVANCE_TEXT": desc,
                            "STATUS": "NEW", "OFFICER_REMARK": "", "REMARK_BY": ""
                        }])
                        conn.update(worksheet="GRIEVANCE", data=pd.concat([prev_g, new_data], ignore_index=True))
                        st.session_state.last_ref = ref; st.rerun()
            if st.button("Back"): st.session_state.page = "LANDING"; st.rerun()
        else:
            st.markdown(f'<div class="success-card-refined"><h1>सफलतापूर्वक दर्ज!</h1><div class="ref-id-balanced">REF ID: {st.session_state.last_ref}</div></div>', unsafe_allow_html=True)
            if st.button("Home"): del st.session_state.last_ref; st.session_state.page = "LANDING"; st.rerun()

# 3. STATUS TRACKING
elif st.session_state.page == "STATUS":
    st.markdown(f'<div class="header-container"><div class="custom-header">Grievance Status</div></div>', unsafe_allow_html=True)
    with st.container(key="status_container"):
        search_id = st.text_input("Enter HRMS ID to track").upper().strip()
        if st.button("Search"):
            data = load_sheet("GRIEVANCE")
            user_recs = data[data['HRMS_ID'].astype(str).str.upper() == search_id]
            if not user_recs.empty:
                for _, row in user_recs[::-1].iterrows():
                    s = clean_val(row['STATUS'], 'NEW').lower()
                    st.markdown(f"""
                    <div class="status-card">
                        <span class="status-id">#{row['REFERENCE_NO']}</span> | 
                        <span class="badge status-{s}">{s.upper()}</span><br>
                        <b>Type:</b> {row['GRIEVANCE_TYPE']}<br>
                        <p style="margin-top:10px;">{row['GRIEVANCE_TEXT']}</p>
                        <hr style="opacity:0.2">
                        <small>Remark: {clean_val(row['OFFICER_REMARK'], 'Pending Review')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.warning("No records found for this ID.")
        if st.button("Back"): st.session_state.page = "LANDING"; st.rerun()

# 4. OFFICER/ADMIN DASHBOARDS
elif st.session_state.page in ["OFFICER_DASHBOARD", "ADMIN_DASHBOARD"]:
    st.markdown(f'<h2 style="text-align:center; color:#fca311;">{st.session_state.page.replace("_", " ")}</h2>', unsafe_allow_html=True)
    st.write(f"Welcome, **{st.session_state.user['NAME']}**")
    
    full_data = load_sheet("GRIEVANCE")
    
    # OFFICER SECTION: Update Grievances
    if st.session_state.page == "OFFICER_DASHBOARD":
        st.subheader("📝 Update Pending Grievances")
        pending = full_data[full_data['STATUS'] != 'RESOLVED']
        
        if not pending.empty:
            ref_list = pending['REFERENCE_NO'].tolist()
            selected_ref = st.selectbox("Select Reference No", ref_list)
            
            with st.form("update_form"):
                new_status = st.selectbox("Action", ["PENDING", "RESOLVED"])
                remark = st.text_area("Officer Remark")
                if st.form_submit_button("Save Update"):
                    # Find index and update
                    idx = full_data[full_data['REFERENCE_NO'] == selected_ref].index[0]
                    full_data.at[idx, 'STATUS'] = new_status
                    full_data.at[idx, 'OFFICER_REMARK'] = remark
                    full_data.at[idx, 'REMARK_BY'] = st.session_state.user['NAME']
                    
                    conn.update(worksheet="GRIEVANCE", data=full_data)
                    st.success(f"Grievance {selected_ref} updated!")
                    st.rerun()
        else:
            st.info("No pending grievances to process.")

    # ADMIN SECTION: Full Oversight
    if st.session_state.page == "ADMIN_DASHBOARD":
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(full_data))
        c2.metric("Resolved", len(full_data[full_data['STATUS'] == 'RESOLVED']))
        c3.metric("Pending", len(full_data[full_data['STATUS'] != 'RESOLVED']))
        st.dataframe(full_data, use_container_width=True)

    if st.button("Logout"): 
        st.session_state.user = None; st.session_state.page = "LANDING"; st.rerun()

# 5. LOGIN LOGIC (Included but unchanged for flow)
elif st.session_state.page == "LOGIN":
    # [Keep your existing login logic here]
    # Ensure it redirects to CHOOSER, OFFICER_DASHBOARD or ADMIN_DASHBOARD
    pass
