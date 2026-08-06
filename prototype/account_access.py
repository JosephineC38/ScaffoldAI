import streamlit as st
import os
import time
import datetime
from zoneinfo import ZoneInfo
from st_supabase_connection import SupabaseConnection

<<<<<<< HEAD:prototype/account_access.py
# Timezone 
SCHEDULE_TZ = ZoneInfo("America/New_York")

# Admin Account Login
def account_login():
    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)
    rows = conn.table("admin_passwords").select("*").execute()
=======
# Timezone setup
SCHEDULE_TZ = ZoneInfo("America/New_York")

# Target File Mapping
FILE_MAPPING = {
    "Beginning of Semester": "survey_responses_beginning.xlsx",
    "Middle of Semester": "survey_responses_middle.xlsx",
    "End of Semester": "survey_responses_end.xlsx",
}
>>>>>>> 9ac763251d5a56994dbcb3875f047422b32aeee3:prototype/instructor_access.py

# -----------------------------------------------------------------------------
# MAIN INSTRUCTOR ACCESS PAGE CONTENT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Instructor Access", layout="wide")

<<<<<<< HEAD:prototype/account_access.py
    # Show the TA login form instead when the user has switched over to it
    if "login_mode" not in st.session_state:
        st.session_state["login_mode"] = "admin"

    if st.session_state["login_mode"] == "ta":
        ta_account_login()
        return

    st.sidebar.title("🔐 Instructor Access")
    if not st.session_state["authenticated"]:
        pwd_input = st.sidebar.text_input("Enter Admin Password to Edit Fields", type="password")

        if st.sidebar.button("Login"):
            matches = [row for row in rows.data if row["password"] == pwd_input]
            if matches:
                st.session_state["authenticated"] = True
            else:
                st.sidebar.error("Incorrect password.")

        if st.sidebar.button("Switch"):
            st.session_state["login_mode"] = "ta"
            st.rerun()
    else:
        if st.sidebar.button("Log Out"):
            st.session_state["authenticated"] = False
            st.rerun()

def ta_account_login():
    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)

    rows = conn.table("ta_passwords").select("*").execute() 

    if "ta_authenticated" not in st.session_state:
        st.session_state["ta_authenticated"] = False

    st.sidebar.title("🔐 TA Access")
    if not st.session_state["ta_authenticated"]:
        pwd_input = st.sidebar.text_input("Enter TA Password to Edit Fields", type="password")
        if st.sidebar.button("Login"):
            now = datetime.datetime.now(SCHEDULE_TZ)
            matches = [row for row in rows.data if row["password"] == pwd_input]

            if not matches:
                st.sidebar.error("Incorrect password.")
            elif any(
                datetime.datetime.strptime(row["start_time"], "%m-%d-%Y %H:%M").replace(tzinfo=SCHEDULE_TZ)
                <= now
                <= datetime.datetime.strptime(row["end_time"], "%m-%d-%Y %H:%M").replace(tzinfo=SCHEDULE_TZ)
                for row in matches
            ):
                st.session_state["ta_authenticated"] = True
                st.rerun()
            else:
                st.sidebar.error("This password is not active at the current time.")

        if st.sidebar.button("Switch"):
            st.session_state["login_mode"] = "admin"
            st.rerun()
    else:
        if st.sidebar.button("Log Out"):
            st.session_state["ta_authenticated"] = False
            st.rerun()

# Admin Page Login 
def account_login_homepage():
    ADMIN_PASSWORD = os.getenv("SYLLABUS_ADMIN_PASSWORD")  

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Instructor Access")
        pwd_input = st.text_input("Enter Admin Password to Edit Fields", type="password")
        if st.button("Login"):
            if pwd_input == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")

# Admin Page Logout Helper Function
def log_out():
    st.session_state["authenticated"] = False
    st.rerun()

# Admin Page Logout     
def account_logout_homepage():
    st.button("Log Out", on_click=log_out)

# ScaffoldAI Main Page login
def main_page_login():
    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)
    rows = conn.table("passwords").select("*").execute()
=======
st.title("🔐 Instructor Access & Settings")

ADMIN_PASSWORD = os.getenv("SYLLABUS_ADMIN_PASSWORD")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "target_file" not in st.session_state:
    st.session_state["target_file"] = "survey_responses_beginning.xlsx"
>>>>>>> 9ac763251d5a56994dbcb3875f047422b32aeee3:prototype/instructor_access.py

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

def admin_sidebar():
    st.sidebar.page_link('app.py', label='Home')
    st.sidebar.page_link('pages/admin.py', label='Admin Settings')
    st.sidebar.page_link('pages/ta.py', label='TA Account')
    st.sidebar.page_link('pages/lectures.py', label='Lectures')
    st.sidebar.page_link('pages/quizzes.py', label='Quizzes')
    st.sidebar.page_link('pages/recitations.py', label='Recitations')
    st.sidebar.page_link('pages/survey.py', label='Survey')
    st.sidebar.page_link('pages/syllabus.py', label='Syllabus')

def ta_sidebar():
    st.sidebar.page_link('app.py', label='Home')
    st.sidebar.page_link('pages/ta.py', label='TA Settings')
    st.sidebar.page_link('pages/lectures.py', label='Lectures')
    st.sidebar.page_link('pages/quizzes.py', label='Quizzes')
    st.sidebar.page_link('pages/recitations.py', label='Recitations')
    st.sidebar.page_link('pages/survey.py', label='Survey')
    st.sidebar.page_link('pages/syllabus.py', label='Syllabus')

def user_sidebar():
    st.sidebar.page_link('app.py', label='Home')
    st.sidebar.page_link('pages/lectures.py', label='Lectures')
    st.sidebar.page_link('pages/quizzes.py', label='Quizzes')
    st.sidebar.page_link('pages/recitations.py', label='Recitations')
    st.sidebar.page_link('pages/survey.py', label='Survey')
    st.sidebar.page_link('pages/syllabus.py', label='Syllabus')
<<<<<<< HEAD:prototype/account_access.py
    

=======

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
>>>>>>> 9ac763251d5a56994dbcb3875f047422b32aeee3:prototype/instructor_access.py
