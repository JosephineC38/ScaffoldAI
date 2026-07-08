import streamlit as st
import os
import json
import csv
from datetime import datetime
from architecture.two_pass_engine import generate_response

# file path
LOG_DIR = "eval"
CSV_LOG_PATH = os.path.join(LOG_DIR, "activity_log.csv")
JSON_LOG_PATH = os.path.join(LOG_DIR, "activity_log.json")
os.makedirs(LOG_DIR, exist_ok=True)

# CSV logging
def log_to_csv(data):
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

if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []


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

user_input = st.text_area("Input", placeholder="Type your question here...", height=100)

# buttons
col1, col2 = st.columns([1, 5])

with col1:
    submit = st.button("Submit")

with col2:
    helpful = st.button("Helpful?")

# submission logic
if submit and user_input.strip():
    response, topic, diagnostics = generate_response(user_input, st.session_state["conversation_history"])
    st.session_state["output"] = response
    st.session_state["conversation_history"].append({"role": "user", "content": user_input})
    st.session_state["conversation_history"].append({"role": "assistant", "content": response})

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = {
        "timestamp": timestamp,
        "mode": mode,
        "input": user_input,
        "output": response,
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
    st.rerun()

# helpful button logic
if helpful:
    last_timestamp = st.session_state.get("last_log_timestamp")
    if last_timestamp:
        mark_helpful(last_timestamp)
        st.session_state["last_helpful"] = True
        st.success("Logged as helpful.")
