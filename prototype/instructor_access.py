import streamlit as st
import os
import time
import datetime
from zoneinfo import ZoneInfo
from st_supabase_connection import SupabaseConnection

# Timezone that the start_time / end_time values in the DB are expressed in.
SCHEDULE_TZ = ZoneInfo("America/New_York")

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
            else:
                st.sidebar.error("Incorrect password.")
    else:
        if st.sidebar.button("Log Out"):
            st.session_state["authenticated"] = False
            st.rerun()

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

def log_out():
    st.session_state["authenticated"] = False
    st.rerun()
        
def account_logout_homepage():
    st.button("Log Out", on_click=log_out)

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


    

