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
import time
import secrets
from datetime import datetime
from architecture.two_pass_engine import generate_response
import instructor_access
from pylatexenc.latex2text import LatexNodes2Text
from architecture.config.modes import MODES

# Define file paths for logging within the /eval directory & for symbols
LOG_DIR = "prototype/eval"
CSV_LOG_PATH = os.path.join(LOG_DIR, "activity_log.csv")
JSON_LOG_PATH = os.path.join(LOG_DIR, "activity_log.json")
SYMBOLS_PATH = os.path.join("thermo_pack", "symbols.json")

# Ensure the eval directory exists
os.makedirs(LOG_DIR, exist_ok=True)

AUTO_LOGOUT_SECONDS = 3600 #1 hour 

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

# Current Session Key
if "curr_chat_session" not in st.session_state:
    st.session_state.curr_chat_session = secrets.token_urlsafe(32)

if "last_activity" not in st.session_state:
    st.session_state.last_activity = int(time.time())

def session_expired():
    return int(time.time()) - st.session_state.last_activity > AUTO_LOGOUT_SECONDS

def submit_text():
    if session_expired():
        return  # session timed out; main flow will log out on this rerun
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
            "helpful": None,
            "current_chat_session": st.session_state.curr_chat_session
        }
        log_to_csv(log)
        log_to_json(log)
        st.session_state["last_log_timestamp"] = timestamp

        # Image to log if uploaded
        uploaded_file = st.session_state.get(str(st.session_state.upload_key))
        if uploaded_file is not None:
            image_path = os.path.join(LOG_DIR, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            log["uploaded_image"] = image_path

        st.session_state["prev_input"] = user_input

        # Reset user input field after submission
        st.session_state["user_text"] = ""

# Clear the chat history
def new_chat():
    if session_expired():
        return  
    st.session_state["user_text"] = ""
    st.session_state["conversation_history"] = []
    st.session_state["last_helpful"] = False
    st.session_state["output"] = ""

    if st.session_state.curr_chat_session and os.path.isfile(CSV_LOG_PATH):
        with open(CSV_LOG_PATH, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = [r for r in reader if r.get("current_chat_session") != st.session_state.curr_chat_session]
        if fieldnames:
            with open(CSV_LOG_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    if st.session_state.curr_chat_session and os.path.isfile(JSON_LOG_PATH):
        try:
            with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
        logs = [e for e in logs if e.get("current_chat_session") != st.session_state.curr_chat_session]
        with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)
    
    for file in os.listdir(LOG_DIR):
        if file.endswith((".png", ".jpg", ".jpeg")):
            os.remove(os.path.join(LOG_DIR, file))
            print(f"Deleted: {file}")
    

# Mark as helpful
def helpful():
    if session_expired():
        return 
    last_timestamp = st.session_state.get("last_log_timestamp")
    if last_timestamp:
        mark_helpful(last_timestamp)
        st.session_state["last_helpful"] = True

def add_latex(symbol):
    st.session_state["user_text"] = st.session_state.get("user_text", "") + symbol

def display_latex():
    st.session_state.show_latex = not st.session_state.show_latex

def load_symbols():
    if os.path.exists(SYMBOLS_PATH):
        with open(SYMBOLS_PATH, "r+") as f:
            data = json.load(f)
        symbols = {}
        for entry in data:
            symbols.setdefault(entry["type"], []).append(entry["symbol"])
        return symbols

def render_symbols(title, symbols, cols=4):
    with st.popover(title):
        colSym = st.columns(cols)
        for i, sym in enumerate(symbols):
            latex_symbol = f"${sym}$"
            colSym[i % cols].button(
                    latex_symbol,
                    key=f"{title}_{i}",     
                    on_click=add_latex,
                    args=(latex_symbol,),
                    width="stretch")

def check_inactivity():
    if st.session_state["user_authenticated"]:
        current_ts = int(time.time())
        elapsed_seconds = current_ts - st.session_state.last_activity
        if elapsed_seconds > AUTO_LOGOUT_SECONDS:
            st.session_state["user_authenticated"] = False
            st.session_state["authenticated"] = False
            st.warning("You have been logged out due to inactivity.")
            st.rerun()

def update_activity():
    if st.session_state["user_authenticated"]:
        st.session_state.last_activity = int(time.time())

# -----------------------------------------------------------------------------
# MAIN PAGE
# -----------------------------------------------------------------------------
def main_page():
# --- ScaffoldAI INTERFACE ---
    if st.session_state["user_authenticated"]:
        user_input = st.text_area(key="user_text", label="Type something here...", placeholder="Type something here...", 
                                    help="This is a text input field for user interaction.", height="content")

        latexCont = st.container()
        if st.session_state.show_latex:
            latex_text = st.session_state.get("user_text", "").strip()
            if latex_text:
                with latexCont:
                    st.markdown(latex_text)

        # Helping Mode Dropdown
        mode = st.selectbox("Helping Mode", MODES, key="mode")

        # Upload Image Section
        uploaded_file = st.file_uploader("Upload Image", accept_multiple_files=False, type=["png", "jpg", "jpeg"], key=f"{st.session_state.upload_key}")

        # Symbols Section
        symbols = load_symbols()
        colMathSym, colGreekSym, colPropSym, colSubScrSym, colUnitSym, colDisplaySym, _ = st.columns([3, 3, 4, 4, 4, 5, 20])

        with colMathSym:
            render_symbols("Math", symbols.get("math", []))

        with colGreekSym:
            render_symbols("Greek", symbols.get("greek", []))

        with colPropSym:
            render_symbols("Properties", symbols.get("properties", []), cols=5)

        with colSubScrSym:
            render_symbols("Subscripts", symbols.get("subscripts", []))

        with colUnitSym:
            render_symbols("Units", symbols.get("units", []))

        with colDisplaySym:
            st.button("Display Latex Format", on_click=display_latex) 

        # buttons
        col1, col2 = st.columns([1, 5])

        with col1:
            submit = st.button(label="Submit 🚀", use_container_width=True, on_click=submit_text)

        with col2:
            helpful_btn = st.button("Helpful?", disabled=not st.session_state.get("output"), on_click=helpful)

        # Output display
        chat = st.container(border=False)
        helpfulCont = st.container(border=False)
        display_converter = LatexNodes2Text()

        #Chat History
        for message in st.session_state["conversation_history"]:
            if message["role"] == "assistant":
                chat.info(display_converter.latex_to_text(message["content"]))
            else:
                chat.info(message["content"])
        
        if st.session_state.get("last_helpful"):
                helpfulCont.success("Logged as helpful.")

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
def sidebar():
        st.sidebar.button("➕ New Chat", use_container_width=True, on_click=new_chat)
        st.sidebar.write("---")
        st.sidebar.title("ScaffoldAI History")

        # Chat History 
        if os.path.isfile(JSON_LOG_PATH):
            with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                    for log in logs:
                        if log.get("current_chat_session") != st.session_state.curr_chat_session:
                            continue
                        st.sidebar.markdown(f"**Student:** {log['input']}", text_alignment="left")
                        st.sidebar.markdown(f"**ScaffoldAI:** {log['output']}", text_alignment="right")
                        st.sidebar.write("---")
                except json.JSONDecodeError:
                    st.sidebar.write("")

# -----------------------------------------------------------------------------
# AUTHENTICATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Homepage", layout="wide")
st.title("ScaffoldAI")
instructor_access.main_page_login()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"]:
    instructor_access.user_sidebar()
else:
    instructor_access.admin_sidebar()

if st.session_state["user_authenticated"]:
    check_inactivity()   
    update_activity()    
    main_page()
    sidebar()

