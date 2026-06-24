import streamlit as st
import os
import json
import csv
from datetime import datetime
from prototype.architecture.two_pass_engine import generate_response

# file path
LOG_DIR = "eval"
CSV_LOG_PATH = os.path.join(LOG_DIR, "activity_log.csv")
JSON_LOG_PATH = os.path.join(LOG_DIR, "activity_log.json")
os.makedirs(LOG_DIR, exist_ok=True)

# CSV logging
def log_to_csv(data):
    file_exists = os.path.isfile(CSV_LOG_PATH)
    with open(CSV_LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def log_to_json(data):
    logs = []
    if os.path.isfile(JSON_LOG_PATH):
        try:
            with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass
    logs.append(data)
    with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


st.title("ScaffoldAI")

# helping mode dropdown
mode = st.selectbox("Helping Mode", [
    "Concept Explanation",
    "Step-by-step",
    "Hint-only",
    "Check-my-plan"
])

# output/input boxes
st.text_area("Output", value=st.session_state.get("output", ""), height=200)

user_input = st.text_area("Input", placeholder="Ask a question...", height=100)

# buttons
col1, col2 = st.columns([1, 5])

with col1:
    submit = st.button("Submit")

with col2:
    helpful = st.button("Helpful?")

# submission logic 
if submit and user_input.strip():
    response = f"[ScaffoldAI - {mode}] Response will appear here once the AI is connected."
    st.session_state["output"] = response

    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "input": user_input,
        "output": response,
        "helpful": None
    }
    log_to_csv(log)
    log_to_json(log)
    st.rerun()

# helpful button logic
if helpful:
    st.session_state["last_helpful"] = True
    st.success("Logged as helpful.")

# conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if user_input:
    response = generate_response(user_input)

    st.session_state.conversation_history.append(
        {"role": "user", "content": user_input}
    )
    st.session_state.conversation_history.append(
        {"role": "assistant", "content": response}
    )
