# ==========================================
# PAGE 2: GRIEVANCE REGISTRATION
# ==========================================
elif st.session_state.page == 'new_form':
    st.markdown('<div class="hindi-heading">Grievance Registration</div>', unsafe_allow_html=True)
    st.markdown('<div class="english-heading">शिकायत पंजीकरण</div>', unsafe_allow_html=True)

    # Initialize session state for HRMS verification if not exists
    if 'hrms_verified' not in st.session_state:
        st.session_state.hrms_verified = False
    if 'found_emp_name' not in st.session_state:
        st.session_state.found_emp_name = ""

    # HRMS ID Input Box
    hrms_input = st.text_input(
        "Enter HRMS ID (अपनी HRMS ID दर्ज करें)", 
        max_chars=6, 
        help="Enter exactly 6 CAPITAL alphabets"
    ).upper() # Force uppercase

    # Enter/Verify Button
    if st.button("Verify ID / सत्यापित करें"):
        # Validation: Exact 6 Alphabets
        if len(hrms_input) == 6 and hrms_input.isalpha():
            
            # --- DATABASE LOOKUP LOGIC ---
            # Replace the following lines with your actual Sheet search logic
            # Example: df = get_sheet_data("EMPLOYEE_MAPPING")
            # match = df[df['HRMS_ID'] == hrms_input]
            
            # TEMPORARY MOCK LOGIC for demonstration:
            mock_database = {"ABCDEF": "Maitri Singh", "RWAILW": "Rajesh Kumar"}
            
            if hrms_input in mock_database:
                st.session_state.found_emp_name = mock_database[hrms_input]
                st.session_state.hrms_verified = True
                st.success(f"✅ Employee Found: {st.session_state.found_emp_name}")
            else:
                st.session_state.hrms_verified = False
                st.error("❌ HRMS ID not found in database.")
        else:
            st.error("⚠️ Invalid Format! Please enter exactly 6 CAPITAL alphabets.")

    # --- CONDITIONAL FORM DISPLAY ---
    if st.session_state.hrms_verified:
        st.markdown("---")
        st.info(f"Logging grievance for: **{st.session_state.found_emp_name}**")
        
        # This is where the rest of the form will appear
        st.write("Rest of the grievance form will appear here...")
        
        # Placeholder for final submit
        if st.button("Final Submit"):
            st.toast("Form Submitted!")

    # Navigation Back
    if st.button("⬅️ Back to Home"):
        # Reset verification state when leaving
        st.session_state.hrms_verified = False
        go_to('landing')
