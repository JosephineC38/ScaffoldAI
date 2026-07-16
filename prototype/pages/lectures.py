import streamlit as st
from instructor_access import account_login

# -----------------------------------------------------------------------------
# VARIABLE SETUP
# -----------------------------------------------------------------------------
if 'chap1' not in st.session_state:
    st.session_state.chap1 = 'https://docs.google.com/presentation/d/1lMt_ClWRpOvYL8TwWzTrHzXQY7I8VRiH/edit?usp=sharing&ouid=103874424269682400963&rtpof=true&sd=true'

if 'chap2' not in st.session_state:
    st.session_state.chap2 = 'https://docs.google.com/presentation/d/1PYgohbTkSI-ZE9vooRSKzsgo8oIzDKE-/edit?slide=id.p1#slide=id.p1'

if 'chap3' not in st.session_state:
    st.session_state.chap3 = 'https://docs.google.com/presentation/d/18KWVzFAzHWMXW5-MvPdAm5t0lNOru0we/edit?slide=id.p1#slide=id.p1'

if 'chap4' not in st.session_state:
    st.session_state.chap4 = 'https://docs.google.com/presentation/d/1o2AX6vwP9byjz_kAZ6bn9nLtOCp6Hcft/edit?slide=id.p1#slide=id.p1'

if 'chap5' not in st.session_state:
    st.session_state.chap5 = 'https://docs.google.com/presentation/d/1x7eB4FewPvM7hCEw4gljSK1VTzcsqlNU/edit?slide=id.p1#slide=id.p1'

if 'chap6' not in st.session_state:
    st.session_state.chap6 = 'https://docs.google.com/presentation/d/15fWLF3GzU8tYSTyLi6T5dDm_NpD5Cm4u/edit?slide=id.p1#slide=id.p1'

if 'chap7' not in st.session_state:
    st.session_state.chap7 = 'https://docs.google.com/presentation/d/1991Z13sQGMea5WrXH2_BFWB4V0P3Oas8/edit?slide=id.p1#slide=id.p1'

if 'chap8' not in st.session_state:
    st.session_state.chap8 = 'https://docs.google.com/presentation/d/1IzhqDLa1wpXjDWzOHHvbyFaN0i9SWoFQ/edit?slide=id.p1#slide=id.p1'


def updateSlide(chapter_index):
    slide_key = f"chap{chapter_index + 1}Update"
    new_url = st.session_state.get(slide_key, "")
    if new_url:
        st.session_state[f"chap{chapter_index + 1}"] = new_url
        st.success(f"Chapter {chapter_index + 1} slides updated successfully!")
    else:
        st.warning(f"Please enter a valid URL for Chapter {chapter_index + 1} slides.")

updateSlides = [
    {"SlideNum": "1", "desc": "Review recent class slides & notes."},
    {"SlideNum": "2", "desc": "Review recent class slides & notes."},
    {"SlideNum": "3", "desc": "Review recent class slides & notes."},
    {"SlideNum": "4", "desc": "Review recent class slides & notes."},
    {"SlideNum": "5", "desc": "Review recent class slides & notes."},
    {"SlideNum": "6", "desc": "Review recent class slides & notes."},
    {"SlideNum": "7", "desc": "Review recent class slides & notes."},
    {"SlideNum": "8", "desc": "Review recent class slides & notes."}
]

# -----------------------------------------------------------------------------
# FRONT END FUNCTIONS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Lectures", layout="wide")
st.title("Lectures")
account_login()

def lec_update():
    st.info("🔓 Admin Mode Active.")
    with st.expander("Slides Update"):
        for i, col in enumerate(updateSlides):
            with st.container(border=True):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.text_input(label=f"Update Chapter {col['SlideNum']} Slides", key=f"chap{col['SlideNum']}Update", placeholder=f"Enter new URL for Chapter {col['SlideNum']} Slides")
                with col2:
                    st.button(f"Update Chapter {col['SlideNum']} Slides", key=f"chap{col['SlideNum']}UpdateButton", on_click=lambda i=i: updateSlide(i))

def lectures():
    with st.expander("Lecture Quick Views"):
        st.page_link(st.session_state.chap1, label="Chapter 1 - Introduction and Basic Concepts")
        st.page_link(st.session_state.chap2, label="Chapter 2 - Energy, Energy Transfer, and General Energy Analysis")
        st.page_link(st.session_state.chap3, label="Chapter 3 - Properties of Pure Substances")
        st.page_link(st.session_state.chap4, label="Chapter 4 - Energy Analysis of a Closed System")
        st.page_link(st.session_state.chap5, label="Chapter 5 - Mass and Energy Analysis of Control Volume")
        st.page_link(st.session_state.chap6, label="Chapter 6 - The Second Law of Thermodynamics")
        st.page_link(st.session_state.chap7, label="Chapter 7 - Entropy")
        st.page_link(st.session_state.chap8, label="Chapter 8 - Cycle")

    st.write("---")

    with st.expander("Chapter 1 - Introduction and Basic Concepts"):
        st.iframe(st.session_state.chap1, height=600)

    with st.expander("Chapter 2 - Energy, Energy Transfer, and General Energy Analysis"):
        st.iframe(st.session_state.chap2, height=600)

    with st.expander("Chapter 3 - Properties of Pure Substances"):
        st.iframe(st.session_state.chap3, height=600)

    with st.expander("Chapter 4 - Energy Analysis of a Closed System"):
        st.iframe(st.session_state.chap4, height=600)

    with st.expander("Chapter 5 - Mass and Energy Analysis of Control Volume"):
        st.iframe(st.session_state.chap5, height=600)

    with st.expander("Chapter 6 - The Second Law of Thermodynamics"):
        st.iframe(st.session_state.chap6, height=600)

    with st.expander("Chapter 7 - Entropy"):
        st.iframe(st.session_state.chap7, height=600)

    with st.expander("Chapter 8 - Cycle"):
        st.iframe(st.session_state.chap8, height=600)


# -----------------------------------------------------------------------------
# SIDEBAR & AUTHENTICATION
# -----------------------------------------------------------------------------
if st.session_state["authenticated"]:
    lec_update()
    lectures()
else:
    lectures()
