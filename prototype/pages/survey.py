import sys
from pathlib import Path
import streamlit as st

# Force Python to find modules in the parent directory
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import the local file safely
from instructor_access import account_login

# Configure page settings
st.set_page_config(page_title="Survey", layout="wide")
st.title("Survey Dashboard")

# 1. Setup Password Protection / Admin Access
account_login()

st.divider()

# --- Survey Access Links ---
st.header("📋 Access Surveys")
st.write("Click the links below to access and manage the Microsoft Forms surveys:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("[**🔗 Survey Form 1**](https://forms.office.com/Pages/DesignPageV2.aspx?origin=NeoPortalPage&subpage=design&id=7GkajbUDRUOuIdrREvX7Tyr8Mfpamc1KgaQUPAGb7SJUQjFQWVJCT0c4VEZGVzZZUjQxUDRUNFBSUi4u)", unsafe_allow_html=True)

with col2:
    st.markdown("[**🔗 Survey Form 2**](https://forms.office.com/Pages/DesignPageV2.aspx?origin=NeoPortalPage&subpage=design&id=7GkajbUDRUOuIdrREvX7Tyr8Mfpamc1KgaQUPAGb7SJUQVgzVUJBNVE4QzMyR0FXRTFQRzMxRkowUC4u)", unsafe_allow_html=True)

with col3:
    st.markdown("[**🔗 Survey Form 3**](https://forms.office.com/Pages/DesignPageV2.aspx?origin=NeoPortalPage&subpage=design&id=7GkajbUDRUOuIdrREvX7Tyr8Mfpamc1KgaQUPAGb7SJURVU1REo1VEZJMUdQVUJZTzJBREM3OEI4WS4u)", unsafe_allow_html=True)

st.divider()

# --- Assignment & Due Date Panel ---
st.sidebar.header("📅 Assignment Planner")
st.sidebar.write("Configure the active assignment and its upcoming deadline here:")

assignment_name = st.sidebar.text_input("Assignment Name", placeholder="e.g., Homework 1")
due_date = st.sidebar.date_input("Due Date")
due_time = st.sidebar.time_input("Due Time")

st.header("🔔 Current Deadlines")
if assignment_name:
    st.info(f"The assignment **{assignment_name}** is due on **{due_date}** at **{due_time}**.")
else:
    st.info("No active assignment set. Use the sidebar panel on the left to set an assignment and due date.")
