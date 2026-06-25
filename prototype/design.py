import streamlit as st

# Configure the page to use a wider layout
st.set_page_config(layout="wide")

# --- SIDEBAR: Chat History Section ---
with st.sidebar:
    st.button("➕ New Chat", use_container_width=True)
    st.write("---")
    st.subheader("Chat History")
    
    # Placeholder for chat history items
    st.caption("📝 How to build a Streamlit app...")
    st.caption("📝 Calculus 3 Homework Help")
    st.caption("📝 Physics Lab Prep")

# --- MAIN PAGE ---
# Center the welcome header
st.markdown("<h1 style='text-align: center;'>Welcome</h1>", unsafe_allow_html=True)
st.write("")

# Create a container to group the input elements together like a unified box
input_container = st.container(border=True)

with input_container:
    # Text input for the question
    user_question = st.text_input("Type question here...", label_visibility="collapsed", placeholder="Type question here...")
    
    # Columns for the action row inside the input area
    col_upload, col_model, col_submit = st.columns([1, 3, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader("Upload Image", label_visibility="collapsed", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.toast("Image uploaded successfully!")
            
    with col_model:
        reasoning_model = st.selectbox(
            "Reasoning Model",
            options=["Concept Explanation", "Step-by-Step", "Hint Only", "Check-My-Plan"],
            label_visibility="collapsed",
            index=0
        )
        
    with col_submit:
        submit_pressed = st.button("Submit 🚀", use_container_width=True)

st.write("")
st.write("")

# --- COURSE MATERIALS SECTION (4 Cards/Buttons) ---
st.markdown("<p style='text-align: center; color: gray;'>Access different course materials</p>", unsafe_allow_html=True)

# Create 4 equal-width columns for the quick access cards
card_cols = st.columns(4)

materials = [
    {"title": "📚 Lectures", "desc": "Review recent class slides & notes."},
    {"title": "📝 Quizzes", "desc": "Practice sets and mock exams."},
    {"title": "🔬 Labs", "desc": "Lab manuals and safety guidelines."},
    {"title": "📖 Syllabus", "desc": "Course schedule and grading criteria."}
]

for i, col in enumerate(card_cols):
    with col:
        with st.container(border=True):
            st.markdown(f"### {materials[i]['title']}")
            st.write(materials[i]['desc'])
            if st.button("Open", key=f"mat_btn_{i}", use_container_width=True):
                st.info(f"Opening {materials[i]['title']}...")

# --- APP LOGIC PLACEHOLDER ---
if submit_pressed and user_question:
    st.write("---")
    st.subheader("AI Response")
    st.info(f"**Selected Mode:** {reasoning_model}\n\n**Your Question:** {user_question}")