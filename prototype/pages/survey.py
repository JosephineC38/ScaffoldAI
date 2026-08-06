import os
import pandas as pd
import streamlit as st
from instructor_access import account_login, admin_sidebar, user_sidebar

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Survey", layout="wide")

# Ensure target_file is initialized
if "target_file" not in st.session_state:
    st.session_state["target_file"] = "survey_responses_beginning.xlsx"

# Standard Likert Scale Options
options = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]

# Store all responses (Likert + Text)
all_responses = {}

# Continuous question counter for Likert sections
q_counter = 1

# --- LIKERT SECTIONS (Questions 1 - 15) ---
integrity_questions = [
    "The prototype guides me through problem-solving steps rather than providing immediate answers.",
    "The prototype requires me to complete necessary conceptual steps before moving forward.",
    "Using the prototype focuses my efforts on understanding core solution steps.",
    "The prototype encourages me to identify and correct any errors that I make.",
    "The prototype requires me to demonstrate understanding of my errors to reach a correct result.",
]

usability_questions = [
    "The prototype is effective for studying course concepts outside of class.",
    "The specific features of the prototype facilitate learning thermodynamics concepts.",
    "Navigating through the prototype's interface is intuitive and straightforward.",
    "The prototype provides clear feedback when an error is made.",
    "Finding specific tools and features within the interface is easy.",
]

self_efficacy_questions = [
    "I feel confident solving thermodynamics problems after using this prototype.",
    "I feel capable of approaching unfamiliar thermodynamics problems on my own after using this prototype.",
    "I can independently identify calculation errors when working through problems.",
    "I feel prepared for exam problems after using this prototype.",
    "I am able to explain core thermodynamics concepts to peers after using this prototype.",
]

# -----------------------------------------------------------------------------
# FRONTEND FUNCTIONS 
# -----------------------------------------------------------------------------
def render_section(section_title, questions):
    """Helper function to display a section with horizontal radio scales."""
    global q_counter
    st.subheader(section_title)

    for q_text in questions:
        st.markdown(f"**{q_counter}. {q_text}**")
        field_key = f"{section_title.lower()}_q{q_counter}"

        all_responses[f"Q{q_counter}_{section_title}"] = st.radio(
            label=q_text,
            options=options,
            horizontal=True,
            key=field_key,
            label_visibility="collapsed",
            index=None,  # Default to unselected
        )
        q_counter += 1
        st.write("")

# -----------------------------------------------------------------------------
# SURVEY PAGE
# -----------------------------------------------------------------------------
st.title("Survey")
st.write("Please evaluate your experience using the prototype below.")

render_section("Integrity", integrity_questions)
st.divider()

render_section("Usability", usability_questions)
st.divider()

render_section("Self-Efficacy", self_efficacy_questions)
st.divider()

# --- OPEN-ENDED TEXT SECTIONS (Questions 16 - 24) ---
st.subheader("Open-Ended Feedback & Reflection")

all_responses["Q16_Frustrating_Part"] = st.text_input(
    "16. What was the most frustrating or confusing part of using this prototype? *"
)

all_responses["Q17_Hallucinations"] = st.text_area(
    "17. Did you notice any moments where the prototype was 'hallucinating' and giving wrong information? *"
)

all_responses["Q18_Improvements"] = st.text_area(
    "18. What improvements would you like to see implemented into the prototype? *"
)

all_responses["Q19_General_Experience"] = st.text_area(
    "19. Can you describe your experience using the prototype? What stood out to you the most? *"
)

all_responses["Q20_Accuracy_Confidence"] = st.text_area(
    "20. How confident do you feel about the accuracy of the prototype's responses? Were there any specific moments where you didn't fully trust the information you were given? *"
)

all_responses["Q21_Refusal_vs_Hallucination"] = st.text_area(
    "21. Did you notice any moments where the prototype started to 'hallucinate' and gave a wrong answer instead of refusing to answer and explaining why? *"
)

all_responses["Q22_Correction_Ease"] = st.text_area(
    "22. If the prototype made an error or gave an unexpected response, how easy or difficult was it to correct or get the right information? *"
)

all_responses["Q23_Comparison"] = st.text_area(
    "23. How does using the prototype compare to using other means of getting information on the topic? *"
)

all_responses["Q24_Reliability_Feature"] = st.text_area(
    "24. If you could change or add one specific feature to make this prototype more reliable for someone's use, what would it be? *"
)

# --- SESSION DETAILS (Individual Fields) ---
st.subheader("Session Details")

col1, col2 = st.columns(2)

with col1:
    all_responses["Observer_Name"] = st.text_input("Observer Name *")
    all_responses["Date_Time"] = st.text_input("Date/Time *")

with col2:
    all_responses["Participant_Name"] = st.text_input("Participant Name *")
    all_responses["Session_Length"] = st.text_input("Session Length with Prototype *")

st.divider()

# -----------------------------------------------------------------------------
# SUBMISSION HANDLER (DYNAMIC EXCEL STORAGE)
# -----------------------------------------------------------------------------
if st.button("Submit Survey", type="primary"):
    # Check if any Likert questions (1-15) were left unselected
    likert_keys = [f"Q{i}_" for i in range(1, 16)]
    missing_likert = any(
        all_responses[k] is None
        for k in all_responses
        if any(k.startswith(prefix) for prefix in likert_keys)
    )

    if missing_likert:
        st.warning("Please select a rating for all 15 Likert scale questions before submitting.")
    else:
        # Convert all survey responses into a DataFrame row
        df_responses = pd.DataFrame([all_responses])

        # Get active file path directly from session state
        excel_path = st.session_state.get("target_file", "survey_responses_beginning.xlsx")

        # Save or append directly to whichever file is currently selected
        if os.path.exists(excel_path):
            existing_df = pd.read_excel(excel_path)
            updated_df = pd.concat([existing_df, df_responses], ignore_index=True)
            updated_df.to_excel(excel_path, index=False)
        else:
            df_responses.to_excel(excel_path, index=False)

        st.success(f"Thank you! Your responses have been saved to **{excel_path}**.")
        st.write("### Submitted Response Summary")
        st.dataframe(df_responses)

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"]:
    admin_sidebar()
else:
    user_sidebar()

account_login()
