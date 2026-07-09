import os
import streamlit as st
import pandas as pd

# 1. Setup Password Protection / Admin Access
ADMIN_PASSWORD = os.getenv("SYLLABUS_ADMIN_PASSWORD")  

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

st.sidebar.title("🔐 Instructor Access")
if not st.session_state["authenticated"]:
    pwd_input = st.sidebar.text_input("Enter Admin Password to Edit Fields", type="password")
    if st.sidebar.button("Login"):
        if pwd_input == ADMIN_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.sidebar.error("Incorrect password.")
else:
    if st.sidebar.button("Log Out"):
        st.session_state["authenticated"] = False
        st.rerun()

# 2. Initialize Session State Variables for the 4 Fields
if "class_schedule" not in st.session_state:
    st.session_state["class_schedule"] = "Mon., Wed., and Fri., 11:00-11:50 PM"

if "location" not in st.session_state:
    st.session_state["location"] = "McLean 414"

if "office_hours" not in st.session_state:
    st.session_state["office_hours"] = "Mon., Wed., 12:00 PM-1:00 PM or with prior appointment by email"

if "ta_info" not in st.session_state:
    st.session_state["ta_info"] = "Tuesday 3:00-5:00 p.m. or with prior appointment by email jpatel104@stevens.edu"

st.title("📚 ME 234A Full Syllabus Portal")
st.write("Authorized users can modify administrative constraints. The official lecture layout remains fixed.")

st.markdown("---")

st.markdown(ADMIN_PASSWORD)

# 3. Dynamic Form Inputs (Admin Mode) vs Public View (Read-Only Mode)
if st.session_state["authenticated"]:
    st.info("🔓 Admin Mode Active. You can now modify the 4 fields below.")
    
    new_schedule = st.text_input("Class Schedule", st.session_state["class_schedule"])
    new_location = st.text_input("Location", st.session_state["location"])
    new_office_hours = st.text_area("Instructor Office Hours", st.session_state["office_hours"])
    new_ta_info = st.text_area("TA Office Hours and Location", st.session_state["ta_info"])
    
    if st.button("💾 Save Changes and Exit Admin Mode"):
        st.session_state["class_schedule"] = new_schedule
        st.session_state["location"] = new_location
        st.session_state["office_hours"] = new_office_hours
        st.session_state["ta_info"] = new_ta_info
        st.session_state["authenticated"] = False
        st.success("Changes saved successfully!")
        st.rerun()

else:
    st.warning("🔒 Read-Only Mode. Log in via the sidebar to update settings.")
    
    # --- FULL READ-ONLY SYLLABUS DISPLAY FOR STUDENTS ---
    st.subheader("ΜΕ 234A - MECHANICAL ENGINEERING THERMODYNAMICS")
    st.caption("Spring 2026 | Course Credits: 3 credits, 3 contact hours per week | Required course")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Instructor:** Prof. Shima Hajimirza (shima.hajimirza@stevens.edu)")
        st.markdown(f"**Class Schedule:** {st.session_state['class_schedule']}")
        st.markdown(f"**Location:** {st.session_state['location']}")
        st.markdown(f"**Instructor Office Hours:** {st.session_state['office_hours']}")
    with col2:
        st.markdown("**Teaching Assistant:** Jimmy Babubhai Patel")
        st.markdown(f"**TA Office Hours and Location:** {st.session_state['ta_info']}")
        st.markdown("**Zoom Link (Remote Class):** https://stevens.zoom.us/j/96072520626")

    st.markdown("#### Course Description")
    st.write("Concepts of energy, heat and work; thermodynamic properties of substances and property "
             "relationships, phase change; First and Second Laws for closed and open systems including "
             "steady and transient processes and cycles; using entropy; representative applications "
             "including vapor and gas power and refrigeration cycles.")

    st.markdown("#### Textbook")
    st.write("Fundamentals of Engineering Thermodynamics, 9th edition, Wiley, 2018 by M.J. Moran, H.N. Shapiro, D.D. Boettner, and M.B. Bailey\n"
             "* ISBN# 9781119503118: WileyPLUS access only\n"
             "* ISBN# 9781119503132: WileyPLUS access with print text")

    st.markdown("#### Grading Scheme")
    st.markdown("- **Homework:** 40%\n- **Quiz (3 @ 10%):** 30%\n- **Final Exam:** 30%")

    st.markdown("#### Homework, Quiz & Exam Policies")
    st.write("- Homework must be submitted online through Canvas or WileyPLUS. Late assignments are NOT accepted.\n"
             "- Quizzes/Exams are closed textbook. You may bring hand-written equation sheets (1 sheet front/back for quizzes, 2 for final).\n"
             "- NO SOLVED PROBLEMS allowed on equation sheets. Violations go directly to the Honor Board.\n"
             "- No phones, computers, or unapproved devices are allowed. No make-up assessments are offered without documented constraints.")

    st.markdown("#### Course Learning Outcomes")
    st.write("1. Demonstrate solid understanding of equations of state and evaluating thermodynamic properties.\n"
             "2. Apply steady-flow energy equations or the First Law to components (turbines, pumps, compressors, etc.).\n"
             "3. Identify and describe energy exchange processes (heat, work) in various thermodynamic systems.\n"
             "4. Explain reversibility/irreversibility concepts and determine performance impacts on thermal systems.\n"
             "5. Demonstrate a solid understanding of entropy and the increase of entropy principle.\n"
             "6. Apply conservation of mass, energy, and the second law to thermodynamic configurations.\n"
             "7. Apply ideal cycle analysis to simple power cycles (Rankine) and refrigeration loops.\n"
             "8. Analyze performance markers and compare loops against maximum theoretical performance constraints.\n"
             "9. Design operating conditions for a thermodynamic system based on specified requirements.")

    # --- ADDED: COURSE OBJECTIVES & RELATIONSHIP TO PROGRAM OUTCOMES ---
    st.markdown("#### Course Objectives and Relationship of Course to Program Outcomes")
    st.write("This course is aimed at developing the ability to analyze a problem logically for its thermodynamic content. "
             "The student should be able to clearly articulate, both verbally and mathematically, the laws of thermodynamics "
             "and some of their important applications and implications for engineering practice. "
             "The student should be able to select and evaluate appropriate parameters describing the thermodynamic performance "
             "of various devices and systems, and to determine the thermodynamic constraints on this performance. "
             "The student should also be able to describe cogently, both verbally and graphically (schematically), major energy "
             "conversion devices and systems. This fundamental course is a pillar of the scientific foundations and "
             "engineering foundations outcomes of our program.")

    st.markdown("#### Basic Topics Covered")
    st.write("- Properties of pure substances\n"
             "- 1st law for closed systems\n"
             "- 2nd law\n"
             "- Entropy\n"
             "- Deviations from ideal behavior\n"
             "- Control volumes\n"
             "- Power cycles\n"
             "- Energy conversion\n"
             "- Phase equilibria and chemical thermodynamics")

    st.markdown("#### Tentative Lecture Schedule Matrix")

# Static schedule layout matrix
schedule_data = [
    ("1-3", "1-2", "1/21 - 1/26", "Introduction, Concepts and Definitions", "Chapter 1 (HW 1 Out)"),
    ("4-8", "2-3", "1/28 - 2/6", "Energy and the First Law of Thermodynamics", "Chapter 2 (HW 2/3 Out)"),
    ("9-10", "4", "2/9 - 2/11", "Evaluating Properties", "Chapter 3"),
    ("11", "4", "2/13 - 2/16", "Quiz 1 (Chapters 1-2) / Presidents' Day Break", "No Class (HW 4 Out)"),
    ("12-17", "5-6", "2/17 - 2/27", "Evaluating Properties continuation", "Chapter 3 (HW 5 Out)"),
    ("18-19", "7", "3/2 - 3/4", "Property analysis structures", "Chapter 3 (HW 6 Out)"),
    ("20-21", "7-8", "3/6 - 3/9", "Control Volume Analysis Using Energy", "Chapter 4"),
    ("22", "8", "3/11", "Quiz 2 (Chapter 3)", "HW 7 Out"),
    ("23", "8", "3/13", "Control Volume Analysis Using Energy", "Chapter 4"),
    ("-", "9", "3/16 - 3/20", "Spring Break - No Class scheduled", "Vacation Matrix"),
    ("24-26", "10", "3/23 - 3/27", "Control Volume Analysis refinement", "Chapter 4 (HW 8 Out)"),
    ("27-28", "11", "3/30 - 4/1", "Control Volume / Second Law entry", "Chapter 4 & 5"),
    ("-", "11", "4/3", "Good Friday - No Class scheduled", "Break"),
    ("29-33", "12-13", "4/6 - 4/15", "The Second Law of Thermodynamics", "Chapter 5 (HW 9 Out)"),
    ("34", "13", "4/17", "Quiz 3 (Chapter 4)", "Assessment"),
    ("35-41", "14-16", "4/20 - 5/4", "Using Entropy formulation loops", "Chapter 6 (HW 10/11 Out)"),
    ("42", "16", "5/6", "Using Entropy (Last Day of Class)", "Chapter 6"),
    ("-", "TBD", "Finals Wk", "Final Exam Coverage (Chapters 1-6)", "Comprehensive Assessment")
]

if not st.session_state["authenticated"]:
    df_schedule = pd.DataFrame(schedule_data, columns=["Lecture", "Week", "Date", "Topic Coverage Overview", "Reading/Assignments"])
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)

st.markdown("---")