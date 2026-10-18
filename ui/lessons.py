"""
UI Module: Learn with AI (Interactive Lessons)
Provides personalized, multi-mode concept explanations, solved examples,
formulas, and interactive tutoring buttons ("Explain Again", "Make It Simpler").
"""

import streamlit as st
import database.db as db
from orchestration.tutor_flow import TutorFlow


def render_lessons_view(flow: TutorFlow):
    st.markdown("""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">📖 Learn with AI: Interactive Lessons</div>
        <div class="tutor-hero-subtitle">
            Agent 2 (Expert AI Tutor) delivers engaging, step-by-step concept explanations 
            grounded directly in your uploaded textbook.
        </div>
    </div>
    """, unsafe_allow_html=True)

    documents = db.list_documents()
    if not documents:
        st.warning("No chapters uploaded yet. Please upload a chapter or load a sample from the 'Upload Chapter' page.")
        return

    # Document & Topic Selector
    doc_options = {d["document_id"]: f"{d['title']} ({d['grade']})" for d in documents}
    selected_doc_id = st.selectbox(
        "Select Chapter:",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x],
        index=0 if "selected_document_id" not in st.session_state or st.session_state["selected_document_id"] not in doc_options else list(doc_options.keys()).index(st.session_state["selected_document_id"])
    )
    st.session_state["selected_document_id"] = selected_doc_id

    topics = db.get_document_topics(selected_doc_id)
    if not topics:
        st.info("No topics extracted for this chapter.")
        return

    topic_titles = [t["title"] for t in topics]
    selected_topic_title = st.selectbox("Select Topic:", options=topic_titles)
    selected_topic = next((t for t in topics if t["title"] == selected_topic_title), topics[0])

    # Mode Selector
    st.write("")
    c_mode, c_btn1, c_btn2, c_btn3 = st.columns([2, 1, 1, 1])
    with c_mode:
        explanation_mode = st.radio(
            "Explanation Style:",
            options=["Explain Like I'm 10", "Standard", "Detailed"],
            horizontal=True
        )

    # Trigger action buttons
    extra_prompt = ""
    with c_btn1:
        if st.button("🔄 Explain Again", use_container_width=True):
            extra_prompt = "explain_again"
    with c_btn2:
        if st.button("💡 Another Example", use_container_width=True):
            extra_prompt = "another_example"
    with c_btn3:
        if st.button("🧸 Make It Simpler", use_container_width=True):
            explanation_mode = "Explain Like I'm 10"

    st.divider()

    # Generate or fetch lesson explanation
    lesson = flow.teaching_agent.explain_concept(selected_topic, mode=explanation_mode)

    # 1. Learning Objectives Card
    with st.container():
        st.markdown(f"### 🎯 Learning Objectives")
        for obj in selected_topic.get("learning_objectives", []):
            st.markdown(f"- **{obj}**")

    st.write("")

    # 2. Main Explanation
    st.markdown("### 💡 Concept Breakdown")
    st.markdown(f"""
    <div class="lesson-card">
        <div class="lesson-title">{selected_topic['title']} ({explanation_mode})</div>
        <div style="font-size: 15px; line-height: 1.7; color: #E2E8F0;">
            {lesson['explanation_text']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Important Formulas
    if lesson.get("formulas"):
        st.markdown("### 📐 Core Formulas")
        f_cols = st.columns(len(lesson["formulas"])) if len(lesson["formulas"]) <= 4 else st.columns(3)
        for idx, formula in enumerate(lesson["formulas"]):
            with f_cols[idx % len(f_cols)]:
                st.code(formula, language="latex")

    # 4. Solved Example
    if lesson.get("solved_example"):
        st.markdown("### 📝 Step-by-Step Solved Example")
        st.info(lesson["solved_example"])

    # 5. Common Pitfalls
    if lesson.get("common_mistakes"):
        st.markdown("### ⚠️ Common Mistakes to Avoid")
        for m in lesson["common_mistakes"]:
            st.warning(m)

    # 6. Quick Knowledge Check
    st.markdown("### ⚡ Quick Check")
    st.write(f"Test your understanding of **{selected_topic['title']}**:")
    
    # Simple interactive check
    qc_key = f"qc_{selected_topic['topic_id']}"
    if "Perimeter" in selected_topic['title']:
        q_ans = st.radio(
            "What is the perimeter of a rectangle with length 10 cm and breadth 4 cm?",
            options=["14 cm", "28 cm", "40 cm²", "20 cm"],
            key=qc_key
        )
        if st.button("Check Answer", key="btn_qc"):
            if q_ans == "28 cm":
                st.success("🎉 Correct! 2 × (10 + 4) = 28 cm.")
            else:
                st.error("Remember: Perimeter = 2 × (Length + Breadth). Try 2 × (10 + 4)!")
    elif "Area" in selected_topic['title']:
        q_ans = st.radio(
            "What is the area of a square with side 6 m?",
            options=["24 m", "36 m²", "12 m²", "36 m"],
            key=qc_key
        )
        if st.button("Check Answer", key="btn_qc"):
            if q_ans == "36 m²":
                st.success("🎉 Correct! Side × Side = 6 × 6 = 36 m².")
            else:
                st.error("Remember: Area of square = Side × Side. Unit must be m²!")
    else:
        st.info("Ready to practice? Navigate to 'Generate Quiz' for a comprehensive test!")
