import streamlit as st
try:
    from ScaffoldAI.prototype.account_access import account_login, admin_sidebar, user_sidebar, ta_sidebar
except:
    from prototype.account_access import account_login, admin_sidebar, user_sidebar, ta_sidebar

# -----------------------------------------------------------------------------
# QUIZZES PAGE
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Quizzes", layout="wide")
st.title("Quizzes")

# Create the visual card layout block
with st.container(border=True):
    st.markdown("### 📝 Quizzes")
    st.write("Practice sets and mock exams.")
    
    # Your verified Google Drive hyperlink button
    st.link_button(
        "Open 🔗", 
        "https://drive.google.com/drive/folders/1-g4g52EsMeh2iBPmzFJsXMD05IThsuz2?usp=drive_link", 
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# SIDEBAR & AUTHENTICATION
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "ta_authenticated" not in st.session_state:
        st.session_state["ta_authenticated"] = False
    
if st.session_state["authenticated"]:
    admin_sidebar()
elif st.session_state["ta_authenticated"]:
    ta_sidebar()
else:
    user_sidebar()
account_login()