"""
UI Module: Teacher Tools
Empowers educators to generate official CBSE examination question papers,
review and edit generated items, inspect source groundings, and export
high-resolution PDFs (Question Paper and Answer Key separately) and CSVs.
"""

import streamlit as st
import database.db as db
from orchestration.tutor_flow import TutorFlow
from services.export_service import ExportService


def render_teacher_view(flow: TutorFlow):
    st.markdown("""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">🎓 Teacher Examination Workshop</div>
        <div class="tutor-hero-subtitle">
            Generate customized CBSE Section A-E question papers, audit question quality, 
            and export printable Question Papers and Answer Keys to PDF.
        </div>
    </div>
    """, unsafe_allow_html=True)

    documents = db.list_documents()
    if not documents:
        st.warning("No chapters uploaded yet. Please upload a chapter or load a sample from 'Upload Chapter'.")
        return

    tab_paper, tab_review = st.tabs(["📝 Generate CBSE Examination Paper", "🔍 Question Bank & Quality Review"])

    with tab_paper:
        st.markdown("#### Examination Blueprint Settings")
        c1, c2, c3 = st.columns(3)
        with c1:
            doc_options = {d["document_id"]: f"{d['title']} ({d['grade']})" for d in documents}
            selected_doc_id = st.selectbox(
                "Target Chapter:",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                key="teacher_doc_sel"
            )
        with c2:
            total_target_marks = st.selectbox("Total Marks:", options=[20, 40, 80], index=1)
        with c3:
            include_hots = st.checkbox("Include Case Study & HOTS (Section E)", value=True)

        doc = db.get_document(selected_doc_id)
        st.caption(f"Blueprint layout: Section A (1M) | Section B (2M) | Section C (3M) | Section D (5M) | Section E (4M Case Study)")

        if st.button("🔨 Build Section A-E Examination Paper", type="primary", use_container_width=True):
            with st.spinner("Multi-Agent Crew is composing and vetting examination paper questions..."):
                # Calculate question counts based on total marks
                q_count = 10 if total_target_marks == 20 else (18 if total_target_marks == 40 else 30)
                paper_questions = flow.generate_and_validate_quiz(
                    document_id=selected_doc_id,
                    topic="All",
                    count=q_count,
                    difficulty="Mixed",
                    question_types=["MCQ", "Fill Blank", "Numerical", "True/False", "Assertion and Reason", "Short Answer", "Long Answer", "Case Study"]
                )
                st.session_state["teacher_paper_questions"] = paper_questions
                st.success(f"Generated and approved {len(paper_questions)} examination questions!")

        # If paper has been generated, offer preview and PDF exports
        if "teacher_paper_questions" in st.session_state and st.session_state["teacher_paper_questions"]:
            questions = st.session_state["teacher_paper_questions"]
            st.divider()
            st.subheader(f"📄 Generated Paper: {doc['title']} ({total_target_marks} Marks)")

            # Export Buttons
            col_pdf1, col_pdf2 = st.columns(2)
            with col_pdf1:
                pdf_paper = ExportService.generate_question_paper_pdf(
                    chapter_title=doc["title"],
                    grade=doc.get("grade", "Class 6"),
                    subject=doc.get("subject", "Mathematics"),
                    total_marks=total_target_marks,
                    questions=questions,
                    include_answers=False
                )
                st.download_button(
                    label="📥 Download Student Question Paper (PDF)",
                    data=pdf_paper,
                    file_name=f"CBSE_{doc['title'].replace(' ', '_')}_Question_Paper.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with col_pdf2:
                pdf_solutions = ExportService.generate_question_paper_pdf(
                    chapter_title=doc["title"],
                    grade=doc.get("grade", "Class 6"),
                    subject=doc.get("subject", "Mathematics"),
                    total_marks=total_target_marks,
                    questions=questions,
                    include_answers=True
                )
                st.download_button(
                    label="📥 Download Teacher Answer Key & Rubric (PDF)",
                    data=pdf_solutions,
                    file_name=f"CBSE_{doc['title'].replace(' ', '_')}_Answer_Key.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            st.write("")
            st.markdown("##### Paper Preview:")
            for idx, q in enumerate(questions):
                st.markdown(f"**Q{idx+1}. [{q.get('marks', 1)}M]** {q['question_text']}")
                if q.get("options"):
                    st.caption("Options: " + " | ".join(q["options"]))

    with tab_review:
        st.subheader("🔍 Review and Audit Question Bank")
        questions_in_db = db.get_questions_by_filter(limit=50)
        st.write(f"Total approved questions stored in database: **{len(questions_in_db)}**")

        for q in questions_in_db[:15]:
            with st.expander(f"[{q['question_type']}] {q['question_text'][:60]}... ({q['difficulty']} - {q['marks']}M)"):
                st.write(f"**Question:** {q['question_text']}")
                if q.get("options"):
                    st.write(f"**Options:** {q['options']}")
                st.write(f"**Correct Answer:** `{q['correct_answer']}`")
                st.write(f"**Explanation:** {q['explanation']}")
                st.write(f"**Source Pages:** Page(s) {q.get('source_pages')}")
                st.write(f"**Status:** `{q.get('validation_status')}` — {q.get('validation_notes')}")
