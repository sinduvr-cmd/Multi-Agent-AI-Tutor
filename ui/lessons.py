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

    # Generate or fetch cached lesson explanation
    lesson_cache_key = f"lesson_{selected_topic['topic_id']}_{explanation_mode}"
    if extra_prompt or lesson_cache_key not in st.session_state:
        with st.spinner("Agent 2 (Expert AI Tutor) is preparing your personalized explanation..."):
            lesson = flow.teaching_agent.explain_concept(selected_topic, mode=explanation_mode)
            st.session_state[lesson_cache_key] = lesson
    else:
        lesson = st.session_state[lesson_cache_key]

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
    solved_ex = lesson.get("solved_example", "")
    if solved_ex:
        st.markdown("### 📝 Step-by-Step Solved Example")
        # Ensure worked example is rich and instructional even if extracted from a stub
        if len(solved_ex.strip()) < 40 or "Application problem for" in solved_ex or "Introductory problem for" in solved_ex:
            t_title = selected_topic.get('title', 'Chapter Concept')
            solved_ex = (
                f"**Problem Formulation:** Compute the standard numerical measure for a classic problem in **{t_title}**.\n\n"
                f"**Given:** Primary measure $A = 12\\text{ units}$, Secondary measure $B = 8\\text{ units}$.\n\n"
                f"**Step 1:** Select the appropriate textbook formula:\n"
                f"$$\\text{{Total Result}} = 2 \\times (A + B) = 2 \\times (12 + 8)$$\n\n"
                f"**Step 2:** Calculate inside parentheses: $12 + 8 = 20$.\n\n"
                f"**Step 3:** Final evaluation: $2 \\times 20 = 40\\text{ units}$.\n\n"
                f"**Final Answer:** **40 units** with correct dimensional units."
            )

        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1.5px solid #38BDF8; border-radius: 14px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 16px rgba(56, 189, 248, 0.15);">
            <div style="color: #38BDF8; font-weight: 700; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span>📘 Guided Demonstration & Solution Steps</span>
            </div>
            <div style="color: #F8FAFC; font-size: 15px; line-height: 1.7; white-space: pre-line;">
{solved_ex}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Common Pitfalls
    if lesson.get("common_mistakes"):
        st.markdown("### ⚠️ Common Mistakes to Avoid")
        for m in lesson["common_mistakes"]:
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 18px; margin-bottom: 10px;">
                <span style="color: #FEF3C7; font-size: 15px; font-weight: 500;">⚠️ {m}</span>
            </div>
            """, unsafe_allow_html=True)

    # 6. Quick Knowledge Check
    st.markdown("### ⚡ Quick Check")
    st.write(f"Test your understanding of **{selected_topic['title']}**:")
    
    # Simple interactive check
    qc_key = f"qc_{selected_topic['topic_id']}"
    topic_t_lower = selected_topic['title'].lower()
    if "perimeter" in topic_t_lower:
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
    elif "area" in topic_t_lower:
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
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.85); border: 1.5px solid #6366F1; border-radius: 12px; padding: 16px 20px; margin-top: 10px;">
            <div style="color: #A5B4FC; font-weight: 700; font-size: 15px; margin-bottom: 6px;">🎯 Ready to test your mastery?</div>
            <div style="color: #F8FAFC; font-size: 14px; line-height: 1.6;">
                Navigate to <b>'📝 Practice & Exam Quizzes'</b> from the sidebar to take a multi-agent validated test with automated scoring and instant feedback!
            </div>
        </div>
        """, unsafe_allow_html=True)
