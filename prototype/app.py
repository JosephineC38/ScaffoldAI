# the main Streamlit application
from pydoc import text

import streamlit as st
import os
import json
import csv
from datetime import datetime

# Define file paths for logging within the /eval directory
LOG_DIR = "eval"
CSV_LOG_PATH = os.path.join(LOG_DIR, "activity_log.csv")
JSON_LOG_PATH = os.path.join(LOG_DIR, "activity_log.json")

# Ensure the eval directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# LOGGING FUNCTIONS
# -----------------------------------------------------------------------------
def log_to_csv(data_dict):
    """Appends data as a row in a local CSV file."""
    file_exists = os.path.isfile(CSV_LOG_PATH)
    with open(CSV_LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data_dict.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_dict)

def log_to_json(data_dict):
    """Appends data to a local JSON array."""
    logs = []
    if os.path.isfile(JSON_LOG_PATH):
        try:
            with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass  # Handle empty or corrupted file
           
    logs.append(data_dict)
   
    with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

# -----------------------------------------------------------------------------
# FRONT END FUNCTIONS
# -----------------------------------------------------------------------------
if "user_text" not in st.session_state:
    st.session_state.user_text = ""

# Clear the text input field and record the user_text   
def clear_text():
    st.session_state.user_text = st.session_state.clear_user_text
    st.session_state.student_history.append(st.session_state.user_text)
    st.session_state.ai_history.append("This is a test response")
    chat.write("This is a test response")

    st.session_state.clear_user_text = ""

    # st.session_state.uploaded_file = None 

def submit_text():
    clear_text()

# Clear the chat history
def new_chat():
    st.session_state.student_history = []
    st.session_state.ai_history = []
    st.session_state.clear_user_text = ""

    with open(CSV_LOG_PATH, "r+") as f:
        f.seek(0)
        f.truncate()

    with open(JSON_LOG_PATH, "r+") as f:
        f.seek(0)
        f.truncate()

# -----------------------------------------------------------------------------
# STREAMLIT UI SKELETON
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Foundational Architecture", layout="centered")

st.title("ScaffoldAI")

st.markdown("---")

# Input Section
st.header("User Inputs")

st.text_area(key="clear_user_text", label="Type something here...", placeholder="Type something here...", 
                         help="This is a text input field for user interaction.", height="content", on_change=clear_text)

# Chatbot Buttons
col1, col2, col3 = st.columns([2,1,1])

# Dropdown Selection
with col1:
    options = ["Concept Explanation", "Step-by-Step", "Hint Only", "Check-My-Plan"]
    selected_option = st.selectbox("Reasoning Model:", options)
    if selected_option == "Concept Explanation":
        pass
    elif selected_option == "Step-by-Step":
        pass
    elif selected_option == "Hint Only":
        pass
    elif selected_option == "Check-My-Plan":
        pass

# Image Upload
with col2:
    uploaded_file = st.file_uploader("Upload Image", accept_multiple_files=False)

# Enter Button
with col3:
    st.button(label="",shortcut="Enter", on_click=submit_text)

chat = st.container(border=True)

# Helpful Action Button
st.markdown("### Actions")
if st.button("🚀 Process & Log Data", help="Click to run calculations and log inputs locally."):
    # Package data to log
    log_payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_text": st.session_state.user_text,
        "selected_mode": selected_option
    }
   
    # Save to local storage
    log_to_csv(log_payload)
    log_to_json(log_payload)

    # Image to log if uploaded
    if uploaded_file is not None:
        image_path = os.path.join(LOG_DIR, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        log_payload["uploaded_image"] = image_path
   
    st.success("Data successfully processed and logged to `/eval` directory!")
   
    # Output Display Section
    st.markdown("---")
    st.header("Outputs & Results Preview")
    st.json(log_payload)
else:
    st.info("Fill out the inputs above and press the button to see the output structure.")

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
if "student_history" not in st.session_state:
    st.session_state.student_history = []

if "ai_history" not in st.session_state:
    st.session_state.ai_history = []

st.sidebar.title("Chatbot History")
st.sidebar.button("+ New Chat", on_click=new_chat)

for student_txt, ai_txt in zip(st.session_state.student_history, st.session_state.ai_history):
    st.sidebar.markdown(f"**Student:** {student_txt}", text_alignment="left")
    st.sidebar.markdown(f"**AI:** {ai_txt}", text_alignment="right")
