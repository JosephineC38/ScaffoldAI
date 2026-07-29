import streamlit as st
import datetime
from st_supabase_connection import SupabaseConnection
from instructor_access import account_login_homepage, account_logout_homepage, admin_sidebar, user_sidebar

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

st.set_page_config(page_title="Admin", layout="wide")
st.title("Admin Settings")
account_login_homepage()

# -----------------------------------------------------------------------------
# ADMIN PAGE
# -----------------------------------------------------------------------------
def admin_page():

    #Add a Password
    st.subheader("Add a new password")
    with st.container(border=True):
        with st.form("add_mytable_entry", clear_on_submit=True):
            password = st.text_input("Password", type="password")
            start_time = st.datetime_input("Start Time", format="MM/DD/YYYY")
            end_time = st.datetime_input("End Time", format="MM/DD/YYYY")
            submitted = st.form_submit_button("Add password", use_container_width=True, type="primary")
            if submitted:
                if start_time and end_time:
                    conn.table("passwords").insert({
                        "password": password,
                        "start_time": start_time.strftime("%m-%d-%Y %H:%M"),
                        "end_time": end_time.strftime("%m-%d-%Y %H:%M"),
                    }).execute()
                    st.success("Password added.")
                    st.rerun()

    #Password History
    with st.expander("Password History"):
        rows = conn.table("passwords").select("*").execute()

        if not rows.data:
            st.info("No passwords history.")

        for row in rows.data:
            with st.container(key=f"pwd_cont_{row['id']}", border=True):

                header_col, _, del_col = st.columns([1,1,1], vertical_alignment="center")
                with header_col:
                    st.write(f"{row['password']}")
                with del_col:
                    if st.button("Delete", key=f"delete_btn_{row['id']}", use_container_width=True):
                        conn.table("passwords").delete().eq("id", row['id']).execute()
                        st.rerun()

                info_start, info_end, _ = st.columns([1,1,3])
                with info_start:
                    st.write("Start Time: ", row['start_time'])
                with info_end:
                    st.write("End Time: ", row['end_time'])

                with st.expander("Edit Time"):
                    edit_start, edit_end = st.columns(2)

                    with edit_start:
                        new_start = st.datetime_input("New Start Time", format="MM/DD/YYYY", key=f"start_input_{row['id']}")
                        if st.button("Update", key=f"start_btn_{row['id']}", use_container_width=True):
                            if new_start:
                                conn.table("passwords").update({"start_time": new_start.strftime("%m-%d-%Y %H:%M")}).eq("id", row['id']).execute()
                                st.rerun()

                    with edit_end:
                        new_end = st.datetime_input("New End Time", format="MM/DD/YYYY", key=f"end_input_{row['id']}")
                        if st.button("Update", key=f"end_btn_{row['id']}", use_container_width=True):
                            if new_end:
                                conn.table("passwords").update({"end_time": new_end.strftime("%m-%d-%Y %H:%M")}).eq("id", row['id']).execute()
                                st.rerun()

    st.divider()
    account_logout_homepage()


# -----------------------------------------------------------------------------
# SIDEBAR & AUTHENTICATION
# -----------------------------------------------------------------------------
if st.session_state["authenticated"]:
    admin_page()
    admin_sidebar()
else:
    user_sidebar()