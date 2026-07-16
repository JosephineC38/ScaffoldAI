# the main Streamlit application
from pydoc import text
from datetime import datetime
from time import sleep, time
from pathlib import Path
import streamlit as st
import sys
import os
import json
import csv
from datetime import datetime
from architecture.two_pass_engine import generate_response
from pylatexenc.latex2text import LatexNodes2Text
from architecture.config.modes import MODES

# Define file paths for logging within the /eval directory
LOG_DIR = "prototype/eval"
CSV_LOG_PATH = os.path.join(LOG_DIR, "activity_log.csv")
JSON_LOG_PATH = os.path.join(LOG_DIR, "activity_log.json")

# Ensure the eval directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# LOGGING FUNCTIONS
# -----------------------------------------------------------------------------
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []
    
def log_to_csv(data):
    """Appends data as a row in a local CSV file."""
    file_exists = os.path.isfile(CSV_LOG_PATH)
    existing_rows = []
    existing_fieldnames = []
    if file_exists:
        with open(CSV_LOG_PATH, "r", newline="", encoding="utf-8") as f:
            existing_rows = list(csv.DictReader(f))
        if existing_rows:
            existing_fieldnames = list(existing_rows[0].keys())

    fieldnames = list(dict.fromkeys(existing_fieldnames + list(data.keys())))

    if existing_fieldnames and set(fieldnames) != set(existing_fieldnames):
        # Log schema grew (e.g. new diagnostic fields) — rewrite with the
        # unioned header so old and new rows stay aligned, backfilling
        # missing values on historical rows as empty rather than corrupting
        # the file by appending rows with a different column count.
        with open(CSV_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows)
            writer.writerow(data)
    else:
        with open(CSV_LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

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

# updates the "helpful" field of the log entry matching timestamp, in both logs
def mark_helpful(timestamp):
    if os.path.isfile(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
        for entry in reversed(logs):
            if entry["timestamp"] == timestamp:
                entry["helpful"] = True
                break
        with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

    if os.path.isfile(CSV_LOG_PATH):
        with open(CSV_LOG_PATH, "r", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in reversed(rows):
            if row["timestamp"] == timestamp:
                row["helpful"] = True
                break
        with open(CSV_LOG_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

# -----------------------------------------------------------------------------
# FRONTEND FUNCTIONS & VARIABLES
# -----------------------------------------------------------------------------
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

if "prev_input" not in st.session_state:
    st.session_state.prev_input = ""

if "show_latex" not in st.session_state:
    st.session_state.show_latex = False

# what does d/dx do in thermo?
def submit_text():
    converter = LatexNodes2Text()
    user_input = converter.latex_to_text(st.session_state.get("user_text", "").strip())
    if user_input:
        response, topic, diagnostics = generate_response(user_input, st.session_state["conversation_history"], st.session_state["mode"])
        st.session_state["output"] = response
        st.session_state["conversation_history"].append({"role": "user", "content": user_input})
        st.session_state["conversation_history"].append({"role": "assistant", "content": response})

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = {
            "timestamp": timestamp,
            "mode": st.session_state.get("mode", ""),
            "input": user_input,
            "output": converter.latex_to_text(response),
            "topic": topic,
            "classification": diagnostics.get("classification"),
            "reasoning_gap": diagnostics.get("reasoning_gap"),
            "misconception": diagnostics.get("misconception"),
            "verification_verdict": diagnostics.get("verification_verdict"),
            "verification_tier": diagnostics.get("verification_tier"),
            "helpful": None
        }
        log_to_csv(log)
        log_to_json(log)
        st.session_state["last_log_timestamp"] = timestamp

        # Image to log if uploaded
        if uploaded_file is not None:
            image_path = os.path.join(LOG_DIR, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            log["uploaded_image"] = image_path

        # Display the conversation history in the chat container
        chat.info(user_input)
        chat.info(converter.latex_to_text(response))
        st.session_state["prev_input"] = user_input

        # Reset user input field after submission
        st.session_state["user_text"] = ""

# Clear the chat history
def new_chat():
    st.session_state["user_text"] = ""
    st.session_state["conversation_history"] = []

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

# Mark as helpful
def helpful():
    last_timestamp = st.session_state.get("last_log_timestamp")
    if last_timestamp:
        mark_helpful(last_timestamp)
        st.session_state["last_helpful"] = True
        helpfulCont.success("Logged as helpful.")

        chat.info(st.session_state["prev_input"])
        chat.info(st.session_state.get("output", ""))

def add_latex(symbol):
    st.session_state["user_text"] = st.session_state.get("user_text", "") + symbol

def display_latex():
    st.session_state.show_latex = not st.session_state.show_latex
    latex_text = st.session_state.get("user_text", "").strip()
    if latex_text:
        if st.session_state.show_latex:
            with latexCont:
                st.write(latex_text)
        else:
            latexCont.empty()

# -----------------------------------------------------------------------------
# MAIN PAGE
# -----------------------------------------------------------------------------

# --- ScaffoldAI INTERFACE ---
st.set_page_config(page_title="Homepage", layout="wide")
st.title("ScaffoldAI")

user_input = st.text_area(key="user_text", label="Type something here...", placeholder="Type something here...", 
                            help="This is a text input field for user interaction.", height="content")

latexCont = st.container()

# Helping Mode Dropdown
mode = st.selectbox("Helping Mode", MODES, key="mode")

# Upload Image Section
uploaded_file = st.file_uploader("Upload Image", accept_multiple_files=False, type=["png", "jpg", "jpeg"], key=f"{st.session_state.upload_key}")

# Symbols Section
colSym1, colSym2, colSym3 = st.columns([1, 1, 14])

with colSym1:
    with st.popover("Math"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.button(r"$\times$", on_click=add_latex, args=(r"$\times$",), width="stretch") # *
            st.button(r"$x^2$", on_click=add_latex, args=(r"$x^2$",), width="stretch") # x^2
            st.button("{", on_click=add_latex, args=("{",), width="stretch") # {
            st.button(r"$\frac{d}{dx}$", on_click=add_latex, args=(r"$\frac{d}{dx}$",), width="stretch") # d/dx

        with col2:
            st.button(r"$\div$", on_click=add_latex, args=(r"$\div$",), width="stretch")
            st.button(r"$\frac{a}{b}$", on_click=add_latex, args=(r"$\frac{a}{b}$",), width="stretch") # a/b
            st.button("}", on_click=add_latex, args=("}",), width="stretch") # }
            st.button(r"$e^x$", on_click=add_latex, args=(r"$e^x$",), width="stretch") # e^x

        with col3:
            st.button(r"$-$", on_click=add_latex, args=(r"-",), width="stretch")
            st.button(r"$\sqrt{x}$", on_click=add_latex, args=(r"$\sqrt{x}$",), width="stretch") # √
            st.button(r"$($", on_click=add_latex, args=(r"(",), width="stretch") # (
            st.button(r"$\Sigma$", on_click=add_latex, args=(r"$\Sigma$",), width="stretch") # Σ
        
        with col4:
            st.button(r"$+$", on_click=add_latex, args=(r"+",), width="stretch") # +
            st.button(r"$x_{n}$", on_click=add_latex, args=(r"x_{n}",), width="stretch") 
            st.button(r"$)$", on_click=add_latex, args=(r")",), width="stretch") # )
            st.button(r"$\Delta$", on_click=add_latex, args=(r"$\Delta$",), width="stretch") # Delta


with colSym2:
    with st.popover("Units"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.button(r"$\frac{m}{s^2}$", on_click=add_latex, args=(r"$\frac{m}{s^2}$",), width="stretch")
            st.button(r"${\degree}C$", on_click=add_latex, args=(r"${\degree}C$",), width="stretch")
            st.button(r"$\frac{g}{cm^3}$", on_click=add_latex, args=(r"$\frac{g}{cm^3}$",), width="stretch")

        with col2:
            st.button(r"$m^2$", on_click=add_latex, args=(r"$m^2$",), width="stretch")
            st.button(r"${\degree}F$", on_click=add_latex, args=(r"${\degree}F$",), width="stretch")
            st.button(r"$\frac{m^3}{kg}$", on_click=add_latex, args=(r"$\frac{m^3}{kg}$",), width="stretch")

        with col3:
            st.button(r"$\frac{kJ}{kg}$", on_click=add_latex, args=(r"$\frac{kJ}{kg}$",), width="stretch")
            st.button(r"$K$", on_click=add_latex, args=(r"$K$",), width="stretch")
            st.button(r"$kPa$", on_click=add_latex, args=(r"$kPa$",), width="stretch")

        with col4:
            st.button(r"$\frac{kJ}{kg·K}$", on_click=add_latex, args=(r"$\frac{kJ}{kg·K}$",), width="stretch")
            st.button(r"$kJ$", on_click=add_latex, args=(r"$kJ$",), width="stretch")
            st.button(r"$N·m$", on_click=add_latex, args=(r"$N·m$",), width="stretch")


with colSym3:
    st.button("Display Latex Format", on_click=display_latex) 

# buttons
col1, col2 = st.columns([1, 5])

with col1:
    submit = st.button(label="Submit 🚀", use_container_width=True, on_click=submit_text)

with col2:
    helpful = st.button("Helpful?", disabled=not st.session_state.get("output"), on_click=helpful)

# Output display
chat = st.container(border=False)
helpfulCont = st.container(border=False)

# --- COURSE MATERIALS SECTION ---
st.markdown("<p style='text-align: center; color: gray;'>Access different course materials</p>", unsafe_allow_html=True)
material_cols = st.columns(5)

materials = [
    {"title": "📚 Lectures", "desc": "Review recent class slides & notes."},
    {"title": "📝 Quizzes", "desc": "Practice sets and mock exams."},
    {"title": "🔬 Recitations", "desc": "Lab manuals and safety guidelines."},
    {"title": "📖 Syllabus", "desc": "Review the class syllabus."},
    {"title": "📖 Survey", "desc": "Course schedule and grading criteria."}
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
                    st.switch_page("pages/quizzes.py")
                elif i == 2:
                    st.switch_page("pages/recitations.py")
                elif i == 3:
                    st.switch_page("pages/syllabus.py")
                elif i == 4:
                    st.switch_page("pages/survey.py")

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.button("➕ New Chat", use_container_width=True, on_click=new_chat)
st.sidebar.write("---")
st.sidebar.title("ScaffoldAI History")

# Chat History 
if os.path.isfile(JSON_LOG_PATH):
    with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
        try:
            logs = json.load(f)
            for log in logs:
                st.sidebar.markdown(f"**Student:** {log['input']}", text_alignment="left")
                st.sidebar.markdown(f"**ScaffoldAI:** {log['output']}", text_alignment="right")
                st.sidebar.write("---")
        except json.JSONDecodeError:
            st.sidebar.write("")
