import streamlit as st
import os
st.set_page_config(page_title="Recitation", layout="wide")
st.title("Recitations")

# Define file paths for recitation files
REC_DIR = "prototype/materials/recitations"

# -----------------------------------------------------------------------------
# VARIABLE SETUP
# -----------------------------------------------------------------------------
if 'rec1' not in st.session_state:
    st.session_state.rec1 = os.path.join(REC_DIR, "thermoChapter1Workshop.pdf")

if 'rec2' not in st.session_state:
    st.session_state.rec2 = os.path.join(REC_DIR, "thermoChapter2Workshop.pdf")

if 'rec3' not in st.session_state:
    st.session_state.rec3 = os.path.join(REC_DIR, "thermoChapter3Workshop.pdf")

if 'rec4' not in st.session_state:
    st.session_state.rec4 = os.path.join(REC_DIR, "thermoChapter4Workshop.pdf")

if 'rec5' not in st.session_state:
    st.session_state.rec5 = os.path.join(REC_DIR, "thermoChapter5Workshop.pdf")

if 'rec6' not in st.session_state:
    st.session_state.rec6 = os.path.join(REC_DIR, "thermoChapter6Workshop.pdf")

if 'rec7' not in st.session_state:
    st.session_state.rec7 = os.path.join(REC_DIR, "thermoChapter7Workshop.pdf")

if 'rec8' not in st.session_state:
    st.session_state.rec8 = os.path.join(REC_DIR, "thermoChapter8Workshop.pdf")

updateRecitations = [
    {"RecNum": "1"},
    {"RecNum": "2"},
    {"RecNum": "3"},
    {"RecNum": "4"},
    {"RecNum": "5"},
    {"RecNum": "6"},
    {"RecNum": "7"},
    {"RecNum": "8"}
]

# -----------------------------------------------------------------------------
# FRONT END FUNCTIONS
# -----------------------------------------------------------------------------
def updateRecitation(recIdx):
    chapter_num = int(recIdx)
    rec_key = f"rec{chapter_num}Update"
    uploaded_file = st.session_state.get(rec_key, None)
    if uploaded_file is not None:
        # Save the uploaded file to the recitation directory
        save_path = os.path.join(REC_DIR, f"thermoChapter{chapter_num}Workshop.pdf")
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state[f"rec{chapter_num}"] = save_path
        st.success(f"Chapter {chapter_num} recitation updated successfully!")
    else:
        st.warning(f"Please upload a valid PDF file for Chapter {chapter_num} recitation.")

# -----------------------------------------------------------------------------
# RECITATION PAGE
# -----------------------------------------------------------------------------
with st.expander("Recitations Update"):
    st.write("Only for Admin User, account creation will be later")

    for i in enumerate(updateRecitations):
        chapter_num = int(i[1]["RecNum"])
        with st.container(border=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.file_uploader(label=f"Update Recitation for Chapter {chapter_num}", key=f"rec{chapter_num}Update", accept_multiple_files=False)
            with col2:
                st.button("Upload Recitation", key=f"rec{chapter_num}UpdateButton", on_click=lambda i=i: updateRecitation(int(i[1]['RecNum'])))
               
             
st.write("---")

with st.expander("Chapter 1 - Introduction and Basic Concepts"):
    with open(st.session_state.rec1 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter1Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_1",
        )
    st.pdf(st.session_state.rec1, height=600, key="recitation_1")


with st.expander("Chapter 2 - Energy, Energy Transfer, and General Energy Analysis"):
    with open(st.session_state.rec1 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter2Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_2",
        )
    st.pdf(st.session_state.rec2, height=600, key="recitation_2")

with st.expander("Chapter 3 - Properties of Pure Substances"):
    with open(st.session_state.rec3 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter3Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_3",
        )
    st.pdf(st.session_state.rec3, height=600, key="recitation_3")

with st.expander("Chapter 4 - Energy Analysis of a Closed System"):
    with open(st.session_state.rec4 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter4Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_4",
        )
    st.pdf(st.session_state.rec4, height=600, key="recitation_4")

with st.expander("Chapter 5 - Mass and Energy Analysis of Control Volume"):
    with open(st.session_state.rec5 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter5Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_5",
        )
    st.pdf(st.session_state.rec5, height=600, key="recitation_5")

with st.expander("Chapter 6 - The Second Law of Thermodynamics"):
    with open(st.session_state.rec6 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter6Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_6",
        )
    st.pdf(st.session_state.rec6, height=600, key="recitation_6")

with st.expander("Chapter 7 - Entropy"):
    with open(st.session_state.rec7 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter7Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_7",
        )
    st.pdf(st.session_state.rec7, height=600, key="recitation_7")

with st.expander("Chapter 8 - Cycle"):
    with open(st.session_state.rec8 , "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="thermoChapter8Workshop.pdf",
            mime="application/pdf",
            key="download_recitation_8",
        )
    st.pdf(st.session_state.rec8, height=600, key="recitation_8")

