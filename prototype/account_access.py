import streamlit as st
import os
import time
import datetime
from zoneinfo import ZoneInfo
from st_supabase_connection import SupabaseConnection

# Timezone
SCHEDULE_TZ = ZoneInfo("America/New_York")

# -----------------------------------------------------------------------------
# SHARED AUTH HELPERS
# -----------------------------------------------------------------------------
def init_auth_state():
    """Make sure every auth flag exists before any page reads it."""
    for key in ("authenticated", "ta_authenticated", "user_authenticated"):
        if key not in st.session_state:
            st.session_state[key] = False
    if "login_mode" not in st.session_state:
        st.session_state["login_mode"] = "admin"

def password_active(row, now):
    """True when `now` falls inside the row's start_time/end_time window."""
    start = datetime.datetime.strptime(row["start_time"], "%m-%d-%Y %H:%M").replace(tzinfo=SCHEDULE_TZ)
    end = datetime.datetime.strptime(row["end_time"], "%m-%d-%Y %H:%M").replace(tzinfo=SCHEDULE_TZ)
    return start <= now <= end

# Admin Account Login
def account_login():
    init_auth_state()

    # Show the TA login form instead when the user has switched over to it
    if st.session_state["login_mode"] == "ta":
        ta_account_login()
        return

    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)
    rows = conn.table("admin_passwords").select("*").execute()

    st.sidebar.title("🔐 Instructor Access")
    if not st.session_state["authenticated"]:
        pwd_input = st.sidebar.text_input("Enter Admin Password to Edit Fields", type="password")

        if st.sidebar.button("Login"):
            matches = [row for row in rows.data if row["password"] == pwd_input]
            if matches:
                st.session_state["authenticated"] = True
                st.rerun()
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
    init_auth_state()

    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)

    rows = conn.table("ta_passwords").select("*").execute()

    st.sidebar.title("🔐 TA Access")
    if not st.session_state["ta_authenticated"]:
        pwd_input = st.sidebar.text_input("Enter TA Password to Edit Fields", type="password")
        if st.sidebar.button("Login"):
            now = datetime.datetime.now(SCHEDULE_TZ)
            matches = [row for row in rows.data if row["password"] == pwd_input]

            if not matches:
                st.sidebar.error("Incorrect password.")
            elif any(password_active(row, now) for row in matches):
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
    init_auth_state()
    ADMIN_PASSWORD = os.getenv("SYLLABUS_ADMIN_PASSWORD")

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
    """Student gate for the main page: sets `user_authenticated`."""
    init_auth_state()

    if st.session_state["user_authenticated"]:
        return

    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)
    rows = conn.table("passwords").select("*").execute()

    st.subheader("Student Access")
    pwd_input = st.text_input("Enter the class password to continue", type="password")

    if st.button("Login", type="primary"):
        now = datetime.datetime.now(SCHEDULE_TZ)
        matches = [row for row in rows.data if row["password"] == pwd_input]

        if not matches:
            st.error("Incorrect password.")
        elif any(password_active(row, now) for row in matches):
            st.session_state["user_authenticated"] = True
            st.session_state["last_activity"] = int(time.time())
            st.rerun()
        else:
            st.error("This password is not active at the current time.")

# -----------------------------------------------------------------------------
# SURVEY DESTINATION CONTROL
# -----------------------------------------------------------------------------
# Target File Mapping
FILE_MAPPING = {
    "Beginning of Semester": "survey_responses_beginning.xlsx",
    "Middle of Semester": "survey_responses_middle.xlsx",
    "End of Semester": "survey_responses_end.xlsx",
}

def survey_target_settings():
    init_auth_state()

    if not st.session_state["authenticated"]:
        account_login_homepage()
        return

    st.success("You are logged in as Admin.")
    st.divider()

    # --- SURVEY DESTINATION CONTROL ---
    st.subheader("📊 Active Survey Target File")
    st.write("Select which Excel file will receive incoming survey submissions:")

    if "target_file" not in st.session_state:
        st.session_state["target_file"] = FILE_MAPPING["Beginning of Semester"]

    # Fall back to the first phase if target_file holds a value we don't know
    labels = [k for k, v in FILE_MAPPING.items() if v == st.session_state["target_file"]]
    current_index = list(FILE_MAPPING.keys()).index(labels[0]) if labels else 0

    selected_phase = st.radio(
        "Active Phase:",
        options=list(FILE_MAPPING.keys()),
        index=current_index,
    )

    st.session_state["target_file"] = FILE_MAPPING[selected_phase]

    st.info(f"📁 Current Output Destination: **{st.session_state['target_file']}**")

    st.divider()
    account_logout_homepage()

# -----------------------------------------------------------------------------
# SIDEBAR HELPERS
# -----------------------------------------------------------------------------
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
