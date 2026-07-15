import streamlit as st
st.set_page_config(page_title="Survey", layout="wide")
st.title("Survey")

from instructor_access import account_login

# 1. Setup Password Protection / Admin Access
account_login()