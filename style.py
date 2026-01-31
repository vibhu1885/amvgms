import streamlit as st

def add_bg(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{image_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* This makes the input boxes slightly transparent so the background shows through */
        .stTextInput, .stSelectbox, .stTextArea {{
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )