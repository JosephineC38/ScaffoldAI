import streamlit as st
import os
import time
import datetime
from zoneinfo import ZoneInfo
from st_supabase_connection import SupabaseConnection

# Timezone setup
SCHEDULE_TZ = ZoneInfo("America/New_York")

# Target File Mapping
FILE_MAPPING = {
    "Beginning of Semester": "survey_responses_beginning.xlsx",
    "Middle of Semester": "survey_responses_middle.xlsx",
    "End of Semester": "survey_responses_end.xlsx",
}

# -----------------------------------------------------------------------------
# MAIN INSTRUCTOR ACCESS PAGE CONTENT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Instructor Access", layout="wide")

st.title("🔐 Instructor Access & Settings")

ADMIN_PASSWORD = os.getenv("SYLLABUS_ADMIN_PASSWORD")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "target_file" not in st.session_state:
    st.session_state["target_file"] = "survey_responses_beginning.xlsx"

if not st.session_state["authenticated"]:
    st.subheader("Admin Login")
    pwd_input = st.text_input("Enter Admin Password to Edit Fields", type="password")
    
    if st.button("Login", type="primary"):
        if pwd_input == ADMIN_PASSWORD:
            st.session_state["authenticated"] = True
            st.success("Successfully authenticated!")
            st.rerun()
        else:
            st.error("Incorrect password.")
else:
    st.success("You are logged in as Admin.")
    st.divider()

    # --- SURVEY DESTINATION CONTROL ---
    st.subheader("📊 Active Survey Target File")
    st.write("Select which Excel file will receive incoming survey submissions:")

    # Fixed: Split list comprehension and index calculation into two lines
    current_label = [k for k, v in FILE_MAPPING.items() if v == st.session_state["target_file"]][0]
    current_index = list(FILE_MAPPING.keys()).index(current_label)

    selected_phase = st.radio(
        "Active Phase:",
        options=list(FILE_MAPPING.keys()),
        index=current_index,
    )

    st.session_state["target_file"] = FILE_MAPPING[selected_phase]

    st.info(f"📁 Current Output Destination: **{st.session_state['target_file']}**")

    st.divider()
    if st.button("Log Out"):
        st.session_state["authenticated"] = False
        st.rerun()

# -----------------------------------------------------------------------------
# AUTHENTICATION & SIDEBAR HELPERS
# -----------------------------------------------------------------------------
def account_login():
    pass  # Auth state is managed via st.session_state

def user_sidebar():
    st.sidebar.page_link('app.py', label='Home')
    st.sidebar.page_link('pages/lectures.py', label='Lectures')
    st.sidebar.page_link('pages/quizzes.py', label='Quizzes')
    st.sidebar.page_link('pages/recitations.py', label='Recitations')
    st.sidebar.page_link('pages/survey.py', label='Survey')
    st.sidebar.page_link('pages/syllabus.py', label='Syllabus')

def admin_sidebar():
    st.sidebar.page_link('app.py', label='Home')
    st.sidebar.page_link('pages/admin.py', label='Admin')
    st.sidebar.page_link('pages/lectures.py', label='Lectures')
    st.sidebar.page_link('pages/quizzes.py', label='Quizzes')
    st.sidebar.page_link('pages/recitations.py', label='Recitations')
    st.sidebar.page_link('pages/survey.py', label='Survey')
    st.sidebar.page_link('pages/syllabus.py', label='Syllabus')

# Sidebar render based on status
if st.session_state["authenticated"]:
    admin_sidebar()
else:
    user_sidebar()
