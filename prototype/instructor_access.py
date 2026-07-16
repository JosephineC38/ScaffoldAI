import streamlit as st
import os

# 1. Setup Password Protection / Admin Access
def account_login():
    ADMIN_PASSWORD = os.getenv("SYLLABUS_ADMIN_PASSWORD")  

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    st.sidebar.title("🔐 Instructor Access")
    if not st.session_state["authenticated"]:
        pwd_input = st.sidebar.text_input("Enter Admin Password to Edit Fields", type="password")
        if st.sidebar.button("Login"):
            if pwd_input == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect password.")
    else:
        if st.sidebar.button("Log Out"):
            st.session_state["authenticated"] = False
            st.rerun()