import streamlit as st
import os
import time
import datetime
from zoneinfo import ZoneInfo
from st_supabase_connection import SupabaseConnection

# Timezone 
SCHEDULE_TZ = ZoneInfo("America/New_York")

# Admin Account Login
def account_login():
    # Initialize connection.
    conn = st.connection("supabase",type=SupabaseConnection)
    rows = conn.table("admin_passwords").select("*").execute()

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

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

    if "user_authenticated" not in st.session_state:
        st.session_state["user_authenticated"] = False

    if not st.session_state["user_authenticated"]:
        pwd_input = st.text_input("Enter Password to Access ScaffoldAI", type="password")
        if st.button("Login"):
            now = datetime.datetime.now(SCHEDULE_TZ)
            matches = [row for row in rows.data if row["password"] == pwd_input]

            if not matches:
                st.error("Incorrect password.")
            elif any(
                datetime.datetime.strptime(row["start_time"], "%m-%d-%Y %H:%M").replace(tzinfo=SCHEDULE_TZ)
                <= now
                <= datetime.datetime.strptime(row["end_time"], "%m-%d-%Y %H:%M").replace(tzinfo=SCHEDULE_TZ)
                for row in matches
            ):
                st.session_state["user_authenticated"] = True
                st.session_state["last_activity"] = int(time.time())
                st.rerun()
            else:
                st.error("This password is not active at the current time.")

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
    

