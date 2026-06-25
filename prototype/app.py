# the main Streamlit application
from pydoc import text

import streamlit as st
import os
import json
import csv
from datetime import datetime
from time import sleep

# Define file paths for logging within the /eval directory
LOG_DIR = "prototype/eval"
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

if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

# Clear the text input field and record the user_text   
def clear_text():
    st.session_state.user_text = st.session_state.clear_user_text
    st.session_state.student_history.append(st.session_state.user_text)
    st.session_state.ai_history.append("This is a test response")

    chat.border = True
    chat.info("This is a test response")

    st.session_state.clear_user_text = ""

def submit_text():
    clear_text()

# Clear the chat history
def new_chat():
    st.session_state.student_history = []
    st.session_state.ai_history = []
    st.session_state.clear_user_text = ""

    if os.path.exists(CSV_LOG_PATH):
        with open(CSV_LOG_PATH, "r+") as f:
            f.seek(0)
            f.truncate()

    if os.path.exists(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r+") as f:
            f.seek(0)
            f.truncate()
    
    for file in os.listdir(LOG_DIR):
        if file.endswith((".png", ".jpg", ".jpeg")):
            os.remove(os.path.join(LOG_DIR, file))
            print(f"Deleted: {file}")
    
    #st.session_state.uploaded_file = None 


# -----------------------------------------------------------------------------
# HOME PAGE
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Homepage", layout="wide")

st.markdown("<h1 style='text-align: center;'>Welcome</h1>", unsafe_allow_html=True)
st.write("")

input_container = st.container(key="image_upload_form", border=True)

with input_container:
    # Input Section
    st.text_area(key="clear_user_text", label="Type something here...", placeholder="Type something here...", 
                            help="This is a text input field for user interaction.", height="content", on_change=clear_text)

    # Chatbot Buttons
    col1, col2, col3 = st.columns([2,1,1])

    # Image Upload
    with col1:
        uploaded_file = st.file_uploader("Upload Image", accept_multiple_files=False, type=["png", "jpg", "jpeg"], key=f"{st.session_state.upload_key}")

    # Dropdown Selection
    with col2:
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

    # Enter Button
    with col3:
        st.button("Submit 🚀", use_container_width=True,on_click=submit_text)

chat = st.container(border=False)

# --- COURSE MATERIALS SECTION ---
st.markdown("<p style='text-align: center; color: gray;'>Access different course materials</p>", unsafe_allow_html=True)
material_cols = st.columns(4)

materials = [
    {"title": "📚 Lectures", "desc": "Review recent class slides & notes."},
    {"title": "📝 Quizzes", "desc": "Practice sets and mock exams."},
    {"title": "🔬 Labs", "desc": "Lab manuals and safety guidelines."},
    {"title": "📖 Syllabus", "desc": "Course schedule and grading criteria."}
]

for i, col in enumerate(material_cols):
    with col:
        with st.container(border=True):
            st.markdown(f"### {materials[i]['title']}")
            st.write(materials[i]['desc'])
            if st.button("Open", key=f"mat_btn_{i}", use_container_width=True):
                openPage = st.empty()
                openPage.info(f"Opening {materials[i]['title']}...")
                sleep(1) #Update later to sync with actual page load
                openPage.empty()
                
                # Rewrite Later
                if i == 0:
                    st.switch_page("pages/lectures.py")
                elif i == 1:
                    st.switch_page("pages/labs.py")
                elif i == 2:
                    st.switch_page("pages/quizzes.py")
                elif i == 3:
                    st.switch_page("pages/syllabus.py")

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

st.sidebar.button("➕ New Chat", use_container_width=True, on_click=new_chat)
st.sidebar.write("---")
st.sidebar.title("Chatbot History")

for student_txt, ai_txt in zip(st.session_state.student_history, st.session_state.ai_history):
    st.sidebar.markdown(f"**Student:** {student_txt}", text_alignment="left")
    st.sidebar.markdown(f"**AI:** {ai_txt}", text_alignment="right")
    st.sidebar.write("---")
