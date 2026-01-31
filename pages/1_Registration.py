import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# ==========================================
# 🎨 PAGE-SPECIFIC STYLE (Mobile & PC Friendly)
# ==========================================
st.set_page_config(layout="wide", page_title="Registration | AMV GMS", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Hide Sidebar & Header */
    [data-testid="stSidebar"], [data-testid="stHeader"] { display: none; }
    
    /* Global Centering for PC, Responsive for Mobile */
    [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* Form Container: 480px on PC, 95% on Mobile */
    .reg-container {
        width: 480px;
        max-width: 95%;
        margin: 0 auto;
        padding: 10px;
    }

    /* 🛡️ LABEL LOCK - 16px Bold White */
    [data-testid="stWidgetLabel"] p { 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        color: white !important; 
        text-align: left !important;
        margin-bottom: 8px !important;
    }

    /* Mobile Button Scaling */
    @media (max-width: 600px) {
        div.stButton > button { height: 70px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 DATA CONNECTION
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(name):
    return conn.read(worksheet=name, ttl="0")

# ==========================================
# 📝 REGISTRATION FORM
# ==========================================
st.markdown('<h2 style="color:white; text-align:center;">Grievance Registration</h2>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="reg-container">', unsafe_allow_html=True)
    
    try:
        emp_df = load_sheet("EMPLOYEE_MAPPING")
        drop_df = load_sheet("DROPDOWN_MAPPINGS")
        drop_df['CATEGORY'] = drop_df['CATEGORY'].astype(str).str.strip().str.upper()

        hrms_id = st.text_input("अपनी HRMS ID दर्ज करें।").upper().strip()
        
        match = emp_df[emp_df['HRMS_ID'].astype(str).str.strip().str.upper() == hrms_id]
        emp_name = match.iloc[0]['EMPLOYEE_NAME'] if not match.empty else ""
        
        if emp_name: 
            st.success(f"✅ User Verified: {emp_name}")

        with st.form("reg_form"):
            st.text_input("Employee Name (कर्मचारी का नाम)", value=emp_name, disabled=True)
            emp_no = st.text_input("Employee No. (कर्मचारी संख्या)*")
            
            # Fetching Dropdowns
            d_list = drop_df[drop_df['CATEGORY'] == 'DESIGNATION']['ITEM_VALUE'].dropna().unique().tolist()
            t_list = drop_df[drop_df['CATEGORY'] == 'TRADE']['ITEM_VALUE'].dropna().unique().tolist()
            g_list = drop_df[drop_df['CATEGORY'] == 'GRIEVANCE_TYPE']['ITEM_VALUE'].dropna().unique().tolist()
            
            st.selectbox("Designation (पद)*", ["--Select--"] + d_list, key="d_val")
            st.selectbox("Trade (ट्रेड)*", ["--Select--"] + t_list, key="t_val")
            st.text_input("Section (कार्यस्थल)*", key="s_val")
            # ✅ Label: समस्या का प्रकार
            st.selectbox("Grievance Type (समस्या का प्रकार)*", ["--Select--"] + g_list, key="g_type_val")
            st.text_area("Brief of Grievance (समस्या का संक्षिपत्त विवरण)*", max_chars=100, key="desc")
            
            submit = st.form_submit_button("Submit (दर्ज करें)")
            
            if submit:
                if not emp_name or not st.session_state.desc.strip() or st.session_state.g_type_val == "--Select--":
                    st.error("❌ सभी अनिवार्य क्षेत्र भरें")
                else:
                    prev_g = load_sheet("GRIEVANCE")
                    ref = f"{datetime.now().strftime('%Y%m%d')}{hrms_id}{str(len(prev_g[prev_g['HRMS_ID']==hrms_id])+1).zfill(3)}"
                    
                    new_entry = pd.DataFrame([{
                        "REFERENCE_NO": ref, 
                        "DATE_TIME": datetime.now().strftime("%d-%m-%Y %H:%M"), 
                        "HRMS_ID": hrms_id, 
                        "EMP_NAME": emp_name, 
                        "EMP_NO": emp_no, 
                        "DESIGNATION": st.session_state.d_val, 
                        "TRADE": st.session_state.t_val, 
                        "SECTION": st.session_state.s_val, 
                        "GRIEVANCE_TYPE": st.session_state.g_type_val, 
                        "GRIEVANCE_TEXT": st.session_state.desc, 
                        "STATUS": "NEW"
                    }])
                    
                    conn.update(worksheet="GRIEVANCE", data=pd.concat([prev_g, new_entry], ignore_index=True))
                    st.session_state.last_ref = ref
                    st.switch_page("pages/2_Success.py")

    except Exception as e:
        st.error(f"Error loading data: {e}")

    # Back button outside the form for better navigation
    if st.button("⬅️ Back to Home"):
        st.switch_page("streamlit_app.py")

    st.markdown('</div>', unsafe_allow_html=True)
