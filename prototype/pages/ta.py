import os
import json
import pandas as pd
import streamlit as st
try:
    from ScaffoldAI.prototype.account_access import account_login, admin_sidebar, ta_sidebar, account_login, user_sidebar
except:
    from prototype.account_access import account_login, admin_sidebar, ta_sidebar, account_login, user_sidebar

# Define file paths for activity logs
REC_DIR = "prototype/materials/recitations"
LOG_DIR = "prototype/eval"
CSV_LOG_PATH = os.path.join(LOG_DIR, "activity_log.csv")
JSON_LOG_PATH = os.path.join(LOG_DIR, "activity_log.json")

st.set_page_config(page_title="TA", layout="wide")
st.title("TA Settings")

# -----------------------------------------------------------------------------
# FRONTEND FUNCTIONS
# -----------------------------------------------------------------------------
def activity_log_viewer():
    if not os.path.isfile(JSON_LOG_PATH):
        st.info("No JSON activity log has been recorded yet.")
        return

    with open(JSON_LOG_PATH, "r", encoding="utf-8") as file:
        try:
            log = json.load(file)
        except json.JSONDecodeError:
            st.error("activity_log.json exists but could not be parsed.")
            return

    if not log:
        st.info("The activity log is empty.")
        return

    with st.expander(f"Activity Log — {len(log)} Entries"):
        table_tab, entry_tab, raw_tab = st.tabs(["Table", "Entry", "Raw JSON"])

        with table_tab:
            st.dataframe(
                pd.DataFrame(log),
                height=600,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.TextColumn("Timestamp", width="small"),
                    "input": st.column_config.TextColumn("Question", width="medium"),
                    "output": st.column_config.TextColumn("Response", width="large"),
                },
            )

        with entry_tab:
            labels = [f"{i + 1}. {row['timestamp']} — {row['input']}" for i, row in enumerate(log)]
            choice = st.selectbox("Select an entry", labels, key="activity_log_entry")
            entry = log[labels.index(choice)]

            st.markdown(f"**Question:** {entry['input']}")
            st.markdown(f"**Response:** {entry['output']}")
            st.write("---")
            st.json(entry, expanded=False)

        with raw_tab:
            st.json(log, expanded=False)

# -----------------------------------------------------------------------------
# TA PAGE
# -----------------------------------------------------------------------------
def ta_page():
    st.subheader("Download Chat History Logs")
    csv_col, json_col, _ = st.columns([1, 1, 6], gap="small")

    with csv_col:
        if os.path.isfile(CSV_LOG_PATH):
            with open(CSV_LOG_PATH, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f.read(),
                    file_name="activity_log.csv",
                    mime="text/csv",
                )
        else:
            st.info("No CSV activity log has been recorded yet.")

    with json_col:
        if os.path.isfile(JSON_LOG_PATH):
            with open(JSON_LOG_PATH, "rb") as f:
                st.download_button(
                    label="Download JSON",
                    data=f.read(),
                    file_name="activity_log.json",
                    mime="application/json",
                )
        else:
            st.info("No JSON activity log has been recorded yet.")

    st.subheader("Chat History")
    activity_log_viewer()

def no_ta_access():
    st.warning("You do not have access to this page. Please log in with a TA account.")

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
if "ta_authenticated" not in st.session_state:
    st.session_state["ta_authenticated"] = False

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"]:
    admin_sidebar()
    ta_page()
elif st.session_state["ta_authenticated"]:
    ta_sidebar()
    ta_page()
else:
    user_sidebar()
    no_ta_access()
account_login()

