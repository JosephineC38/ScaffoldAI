import streamlit as st

# Set page config must be the very first Streamlit command
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
