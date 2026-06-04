# the main Streamlit application
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
# STREAMLIT UI SKELETON
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Foundational Architecture", layout="centered")

st.title("Week 1 Foundational Architecture")
st.subheader("Streamlit Prototype Skeleton")

st.markdown("---")

# Input Section
st.header("User Inputs")
user_text = st.text_input("Enter parameters or notes:", placeholder="Type something here...")
numeric_input = st.number_input("Numerical Value Input:", value=0.0, step=0.1)

# Dropdown Selection
options = ["Calculation Mode A", "Simulation Mode B", "Data Analysis Mode C"]
selected_option = st.selectbox("Select Analysis/Process Mode:", options)

# Helpful Action Button
st.markdown("### Actions")
if st.button("🚀 Process & Log Data", help="Click to run calculations and log inputs locally."):
    # Package data to log
    log_payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_text": user_text,
        "numeric_value": numeric_input,
        "selected_mode": selected_option
    }
   
    # Save to local storage
    log_to_csv(log_payload)
    log_to_json(log_payload)
   
    st.success("Data successfully processed and logged to `/eval` directory!")
   
    # Output Display Section
    st.markdown("---")
    st.header("Outputs & Results Preview")
    st.json(log_payload)
else:
    st.info("Fill out the inputs above and press the button to see the output structure.")