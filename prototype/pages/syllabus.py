import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ENGR 234 Syllabus & Dashboard",
    page_icon="🔥",
    layout="wide",
)

# --- PASSWORD / AUTHENTICATION SYSTEM ---
# Set your preferred admin password here
ADMIN_PASSWORD = "thermoadmin"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- INITIALIZE SESSION STATE WITH FULL SYLLABUS DATA ---
if "term_info" not in st.session_state:
    st.session_state["term_info"] = "Spring 2026"

if "lectures_df" not in st.session_state:
    st.session_state["lectures_df"] = pd.DataFrame(
        [
            {"Section": "A", "Days": "MW", "Time": "9:00 AM - 9:50 AM", "Room": "GN 103"},
            {"Section": "B", "Days": "MW", "Time": "10:00 AM - 10:50 AM", "Room": "GN 103"},
            {"Section": "C", "Days": "MW", "Time": "11:00 AM - 11:50 AM", "Room": "Babbio 203"},
        ]
    )

if "recitations_df" not in st.session_state:
    st.session_state["recitations_df"] = pd.DataFrame(
        [
            {"Section": "RA", "Days": "R", "Time": "1:00 PM - 1:50 PM", "Room": "Marth B 104"},
            {"Section": "RB", "Days": "F", "Time": "9:00 AM - 9:50 AM", "Room": "Burchard 102"},
            {"Section": "RC", "Days": "T", "Time": "2:00 PM - 2:50 PM", "Room": "EAS 330"},
            {"Section": "RD", "Days": "F", "Time": "10:00 AM - 10:50 AM", "Room": "Burchard 102"},
            {"Section": "RE", "Days": "T", "Time": "9:00 AM - 9:50 AM", "Room": "Babbio 321"},
            {"Section": "RF", "Days": "F", "Time": "11:00 AM - 11:50 AM", "Room": "Burchard 102"},
        ]
    )

if "instructors_df" not in st.session_state:
    st.session_state["instructors_df"] = pd.DataFrame(
        [
            {
                "Instructor": "Chang-Hwan Choi",
                "Section(s)": "C, RF",
                "Office": "C205",
                "Office Hours": "MW 1 PM-2 PM Or by appointment!",
                "Contact Info": "cchoi@stevens.edu | (201) 216-5579",
            },
            {
                "Instructor": "Zahra Pournorouz",
                "Section(s)": "A, B, RA, RB, RC, RD, RE",
                "Office": "EAS 307",
                "Office Hours": "MW 11 AM-12 PM Or by appointment!",
                "Contact Info": "zpournor@stevens.edu | (201) 216-8052",
            },
        ]
    )

if "schedule_df" not in st.session_state:
    st.session_state["schedule_df"] = pd.DataFrame(
        [
            {"Week": "1", "Lecture Dates": "W-01/21", "Lecture Activities": "Syllabus and course objective overview / Introductions / meet and greet", "Recitation Activities": "No Tue recitation. Group formation and structure information on Thu and Fri."},
            {"Week": "2", "Lecture Dates": "M-01/26, W-01/28", "Lecture Activities": "Introduction to Thermo, Dimensions, and Units - Ch 1 / Basic Concepts, Definitions- Ch 1", "Recitation Activities": "Group formation and structure information on Tue. Chapter 1 Workshop on Thu and Fri."},
            {"Week": "3", "Lecture Dates": "M-02/02, W-02/04", "Lecture Activities": "The 1st law, Work & Heat - Ch 2 / Energy & Energy Transfer - Ch 2", "Recitation Activities": "Chapter 1 Workshop on Tue. Chapter 2 Workshop on Thu and Fri."},
            {"Week": "4", "Lecture Dates": "M-02/09, W-02/11", "Lecture Activities": "Properties of Pure Substances - Ch 3 / Properties Tables - Ch 3", "Recitation Activities": "Chapter 2 Workshop on Tue. Chapter 3 Workshop on Fri and Thu."},
            {"Week": "5", "Lecture Dates": "M-02/16, T-02/17, W-02/18", "Lecture Activities": "President's Day - No Classes / Monday Class Schedule / Properties Tables - Ch 3", "Recitation Activities": "No Tuesday Recitations! Chapter 3 workshop on Thu and Fri."},
            {"Week": "6", "Lecture Dates": "M-02/23, W-02/25", "Lecture Activities": "Review Session for Exam I / Exam 1 (chapters 1, 2, and 3)", "Recitation Activities": "Chapter 3 workshop on Tue. Group Q#1 on Thu and Fri."},
            {"Week": "7", "Lecture Dates": "M-03/02, W-03/04", "Lecture Activities": "Energy Analysis of Closed Systems - Ch 4 / Energy Analysis of Closed Systems - Ch 4", "Recitation Activities": "Group Q#1 on Tue. Chapter 4 Workshop on Thu and Fri."},
            {"Week": "8", "Lecture Dates": "M-03/09, W-03/11", "Lecture Activities": "Spring Recess (No Classes)", "Recitation Activities": "No Recitations (Spring Recess)"},
            {"Week": "9", "Lecture Dates": "M-03/23, W-03/25", "Lecture Activities": "Specific Heats and Ideal gases - Ch 4 / Energy Analysis of Control Volumes - Ch 5", "Recitation Activities": "Chapter 4 workshop"},
            {"Week": "10", "Lecture Dates": "M-03/30, W-04/01", "Lecture Activities": "Energy analysis of steady-flow devices - Ch 5 / Energy analysis of steady-flow devices - Ch 5", "Recitation Activities": "Chapter 5 workshop on Tue and Thu. No Friday recitations!"},
            {"Week": "11", "Lecture Dates": "M-04/06, W-04/08", "Lecture Activities": "Refrigerators and heat pumps - Ch 6 / Reversibility, Carnot efficiency - Ch 6", "Recitation Activities": "Chapter 5 workshop"},
            {"Week": "12", "Lecture Dates": "M-04/13, W-04/15", "Lecture Activities": "Review Session for Exam II / Exam II (chapters 4 and 5)", "Recitation Activities": "Group Q#2"},
            {"Week": "13", "Lecture Dates": "M-04/20, W-04/22", "Lecture Activities": "Reversibility, Carnot efficiency - Ch 6 / Entropy - Ch 7", "Recitation Activities": "Chapter 6 workshop"},
            {"Week": "14", "Lecture Dates": "M-04/27, W-04/29", "Lecture Activities": "Reversible & isentropic processes - Ch 7 / Reversible & isentropic processes - Ch 7", "Recitation Activities": "Chapter 7 workshop"},
            {"Week": "15", "Lecture Dates": "M-05/04, W-05/06", "Lecture Activities": "Rankine Cycles - Ch 8 / Rankine Cycles / Refrigeration Cycles - Ch 8", "Recitation Activities": "Chapter 8 workshop"},
            {"Week": "16", "Lecture Dates": "M-05/11, W-05/13", "Lecture Activities": "Project presentations / Friday Class Schedule", "Recitation Activities": "Project Presentations"},
        ]
    )

# Textual sections in session state for live editing
if "textbook_info" not in st.session_state:
    st.session_state["textbook_info"] = "Thermodynamics: An Engineering Approach, 10th Ed. Yunus A. Çengel & Michael A. Boles (ISBN-13: 978-1259822674)"

if "course_desc" not in st.session_state:
    st.session_state["course_desc"] = (
        "To gain an understanding of the basic concepts and laws of thermodynamics and the application of these laws "
        "or principles to simple engineering technology systems. Basic concepts and definitions of thermodynamics, "
        "properties of pure substance, work and heat, the first law of thermodynamics, the second law of thermodynamics, "
        "entropy, thermodynamics of gases, vapors, and liquids in various non-flow and flow processes."
    )

# --- SIDEBAR: AUTHENTICATION & CONTROLS ---
st.sidebar.title("🔒 Admin Control Panel")

if not st.session_state["authenticated"]:
    pwd_input = st.sidebar.text_input("Enter Admin Password", type="password")
    if st.sidebar.button("Login"):
        if pwd_input == ADMIN_PASSWORD:
            st.session_state["authenticated"] = True
            st.sidebar.success("Logged in as Admin!")
            st.rerun()
        else:
            st.sidebar.error("Incorrect Password")
else:
    st.sidebar.success("🔑 Admin Mode Active")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Edit Syllabus Data")

    st.session_state["term_info"] = st.sidebar.text_input(
        "Semester / Term", st.session_state["term_info"]
    )

    st.session_state["textbook_info"] = st.sidebar.text_area(
        "Textbook Info", st.session_state["textbook_info"]
    )

    st.session_state["course_desc"] = st.sidebar.text_area(
        "Course Description", st.session_state["course_desc"]
    )

    st.sidebar.subheader("Instructors & TAs")
    st.session_state["instructors_df"] = st.sidebar.data_editor(
        st.session_state["instructors_df"], num_rows="dynamic", key="edit_instructors"
    )

    st.sidebar.subheader("Lecture Hours & Rooms")
    st.session_state["lectures_df"] = st.sidebar.data_editor(
        st.session_state["lectures_df"], num_rows="dynamic", key="edit_lectures"
    )

    st.sidebar.subheader("Recitation Hours & Rooms")
    st.session_state["recitations_df"] = st.sidebar.data_editor(
        st.session_state["recitations_df"], num_rows="dynamic", key="edit_recitations"
    )

    st.sidebar.subheader("Tentative Schedule & Dates")
    st.session_state["schedule_df"] = st.sidebar.data_editor(
        st.session_state["schedule_df"], num_rows="dynamic", key="edit_schedule"
    )

# --- MAIN DASHBOARD DISPLAY ---
st.title(f"Thermodynamics (ENGR 234) — {st.session_state['term_info']}")
st.caption("Charles V. Schaefer, Jr. School of Engineering & Science | Stevens Institute of Technology")

# 1. Instructor & Contact Info
st.header("👨‍🏫 Instructors & Teaching Assistants")
st.dataframe(st.session_state["instructors_df"], use_container_width=True, hide_index=True)

# 2. Meeting Hours & Rooms
st.header("⏰ Class Meeting Times & Rooms")
c_col1, c_col2 = st.columns(2)
with c_col1:
    st.subheader("📖 Lecture Sections")
    st.dataframe(st.session_state["lectures_df"], use_container_width=True, hide_index=True)
with c_col2:
    st.subheader("✏️ Recitation Sections")
    st.dataframe(st.session_state["recitations_df"], use_container_width=True, hide_index=True)

# 3. Course Description & Textbook
st.header("📚 Course Overview & Textbooks")
st.markdown(f"**Recommended Textbook:** {st.session_state['textbook_info']}")
st.markdown(f"**Course Description:** {st.session_state['course_desc']}")

# 4. Objectives & ABET Outcomes
with st.expander("🎯 Course Objectives & ABET Outcomes", expanded=False):
    st.markdown("""
    **Course Objectives:** Upon completion of the course, students are expected to:
    1. Determine the thermodynamic properties of solids, liquids and ideal gases and their changes in isothermal, isobaric, isochoric or isentropic processes.
    2. Transform problem statements into their graphical and mathematical representations and use a methodical approach to problem-solving.
    3. Utilize mass and energy balances to determine the characteristics of steady-flow devices undergoing simple processes and cycles.
    4. Describe in words and by using sketches of major thermodynamic devices and systems such as nozzles, diffusers, pumps, compressors, turbines, and throttling valves.
    5. Apply the second law of thermodynamics to cycles and cyclic devices and determine the efficiencies of reversible heat engines, refrigerators, and heat pumps.
    6. Calculate entropy changes that take place during processes for pure substances and apply the entropy balance to various systems.

    **ABET ETAC Learning Objectives:**
    * **SO #B:** Ability to select and apply a knowledge of mathematics, science, engineering, and technology to engineering technology problems that require the application of principles and applied procedures or methodologies;
    * **SO #C:** Ability to conduct standard tests and measurements; to conduct, analyze, and interpret experiments; and to apply experimental results to improve processes;
    * **SO #F:** Ability to identify, analyze, and solve broadly-defined engineering technology problems.
    """)

# 5. Grading Policy & Scale
st.header("📊 Grading Policy & Scale")
g_col1, g_col2 = st.columns(2)
with g_col1:
    st.markdown("""
    | Assessment | Weight |
    | :--- | :--- |
    | **Midterm Tests (2)** | 30% (15% each) |
    | **Final Test** | 20% |
    | **Group Questions (2)** | 20% (10% each) |
    | **Quiz** | 10% |
    | **Project or Homework** | 15% |
    | **Attendance** | 5% |
    """)
with g_col2:
    st.markdown("""
    | Grade | Range | Grade | Range |
    | :--- | :--- | :--- | :--- |
    | **A** | 93% | **C+** | 77% |
    | **A-** | 90% | **C** | 73% |
    | **B+** | 87% | **C-** | 70% |
    | **B** | 83% | **D+** | 67% |
    | **B-** | 80% | **D** | 60% |
    """)

# 6. Tentative Weekly Schedule
st.header("📅 Tentative Course Schedule & Dates")
st.dataframe(
    st.session_state["schedule_df"],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Week": st.column_config.TextColumn("Week", width="small"),
        "Lecture Dates": st.column_config.TextColumn("Lecture Dates", width="medium"),
        "Lecture Activities": st.column_config.TextColumn("Lecture Activities", width="large"),
        "Recitation Activities": st.column_config.TextColumn("Recitation Activities", width="large"),
    },
)

# 7. Policies, Procedures & Resources
st.header("📑 Course Policies & Campus Resources")

p_tab1, p_tab2, p_tab3, p_tab4, p_tab5 = st.tabs([
    "Format & Attendance", 
    "Exams & Quizzes", 
    "Academic Integrity", 
    "Accommodations & Inclusivity", 
    "Mental Health & Emergency"
])

with p_tab1:
    st.markdown("""
    **Format and Structure:**
    * **Lectures:** Active lectures where instructor delivers material and students ask questions/complete activities.
    * **Recitations:** Workshop format featuring group problem-solving under instructor & TA guidance.
    * **Office Hours:** Used to supplement student learning and discuss course material with instructors/TAs.

    **Classroom Procedures:**
    * No food allowed.
    * Laptops/cellphones are strictly restricted to book access, note-taking, or calculations. Cell phones must be on silent.

    **Attendance Policy:**
    * Mandatory and recorded via Canvas rolling code system. Late arrivals count as 1/2 absence (2 late marks = 1 absence).
    * Up to 3 excused absences allowed for lectures with advance notice. **Recitation absences cannot be excused.**
    * Attendance counts for 5% overall (2.5% Lecture / 2.5% Recitation across 26 lectures and 13 recitations).
    * Code sharing is a strict violation of the Stevens Honor System.
    """)

with p_tab2:
    st.markdown("""
    **Exams:**
    * Exams are comprehensive up through material covered prior to test day. Formula pages and tables are provided.
    * Prior notification and arrangements with the instructor are required if unable to attend.
    
    **Quizzes:**
    * Quizzes are purely conceptual/theoretical and administered online via Canvas.
    * Open for 3 days after publication with 2 attempts permitted. No extensions or makeups allowed unless due to documented illness, conference, or official athletic duty.
    """)

with p_tab3:
    st.markdown("""
    **Undergraduate Honor System:**
    * All undergraduate students are bound by the provisions of the Stevens Honor System.
    * **Honor Pledge:** Every submitted assignment/exam must contain the signed pledge:  
      > *"I pledge my honor that I have abided by the Stevens Honor System."*
    * **Reporting Violations:** Violations should be reported within 10 business days at [www.stevens.edu/honor](http://www.stevens.edu/honor).
    """)

with p_tab4:
    st.markdown("""
    **Learning Accommodations (ODS):**
    * Office of Disability Services coordinates accommodations for eligible students.
    * Contact: Phillip Gehman, Director of Disability Services Coordinator (`pgehman@stevens.edu` | 201-216-3748).
    * Files are strictly confidential under FERPA regulations.

    **Inclusivity & Diversity:**
    * Affirmation of chosen names and gender pronouns is fully supported.
    * Respect for all races, ethnicities, gender expressions, religions, sexual orientations, disabilities, and socioeconomic backgrounds is strictly enforced.
    """)

with p_tab5:
    st.markdown("""
    **Counseling and Psychological Services (CAPS):**
    * Free and confidential mental health support daily 9:00 AM – 5:00 PM (M–F).
    * Phone: 201-216-5177 | Web: [www.stevens.edu/CAPS](http://www.stevens.edu/CAPS)
    
    **Emergency Information (24/7):**
    * **Stevens Campus Police:** 201-216-5105 | Emergency: 201-216-3911
    * **National Suicide Prevention Lifeline:** 1-800-273-8255
    * **Crisis Text Line:** Text "HOME" to 741-741
    * **CARE Team (Non-urgent):** `care@stevens.edu`
    """)
