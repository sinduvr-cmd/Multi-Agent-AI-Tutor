"""
UI Module: Upload and Analyze Chapter
Handles drag-and-drop PDF upload, PyMuPDF extraction, topic hierarchy preview,
formula and diagram inspection, and sample NCERT one-click ingestion.
"""

import os
from pathlib import Path
import streamlit as st
import database.db as db
from orchestration.tutor_flow import TutorFlow

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def render_upload_view(flow: TutorFlow):
    st.markdown("""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">📄 Upload & Analyze Textbook Chapters</div>
        <div class="tutor-hero-subtitle">
            Upload any CBSE or state textbook PDF. Agent 1 (Educational Content Researcher) 
            extracts topics, learning objectives, formulas, and diagrams with page grounding.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_samples = st.tabs(["📤 Upload PDF File", "📚 Built-in NCERT Sample Chapters"])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose a chapter PDF file (Max 50MB)",
            type=["pdf"],
            help="Supports standard NCERT, CBSE, and scanned chapter PDFs."
        )

        if uploaded_file:
            st.info(f"Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
            if st.button("🚀 Analyze Chapter with Agent 1", type="primary"):
                with st.spinner("Agent 1 is extracting layout, formulas, and diagrams..."):
                    progress_bar = st.progress(20)
                    try:
                        analysis = flow.analyze_and_index_chapter(uploaded_file, uploaded_file.name)
                        progress_bar.progress(100)
                        st.success(f"Successfully analyzed '{analysis['title']}'! Extracted {len(analysis['topics'])} topics.")
                        st.session_state["selected_document_id"] = analysis["document_id"]
                    except Exception as e:
                        st.error(f"Extraction error: {str(e)}")

    with tab_samples:
        st.markdown("##### Load Pre-configured Sample Reference Chapters")
        st.write("Click below to index the built-in NCERT sample chapters:")

        samples = [
            ("ncert_class6_perimeter_and_area.pdf", "NCERT Class 6: Perimeter and Area"),
            ("ncert_class6_fractions.pdf", "NCERT Class 6: Fractions"),
            ("class6_perimeter_area_worksheet.pdf", "Class 6 Perimeter & Area Worksheet"),
            ("class6_math_practice_paper_sections_a_e.pdf", "Class 6 Math Practice Paper (Sections A-E)")
        ]

        for filename, label in samples:
            sample_path = SAMPLE_DIR / filename
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                st.write(f"📖 **{label}**")
                st.caption(f"Path: `sample_data/{filename}`")
            with col_s2:
                if st.button(f"Load Chapter", key=f"btn_load_{filename}"):
                    if sample_path.exists():
                        with st.spinner(f"Ingesting {label}..."):
                            analysis = flow.analyze_and_index_chapter(str(sample_path), filename)
                            st.success(f"Indexed '{analysis['title']}'!")
                            st.session_state["selected_document_id"] = analysis["document_id"]
                            st.rerun()
                    else:
                        st.error("Sample PDF not found on disk.")

    st.divider()

    # Document Inspection & Preview
    documents = db.list_documents()
    if documents:
        st.subheader("🔍 Inspect Analyzed Chapter")
        doc_options = {d["document_id"]: f"{d['title']} ({d['filename']})" for d in documents}
        selected_doc_id = st.selectbox(
            "Select Chapter to Preview:",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
            index=0 if "selected_document_id" not in st.session_state or st.session_state["selected_document_id"] not in doc_options else list(doc_options.keys()).index(st.session_state["selected_document_id"])
        )
        st.session_state["selected_document_id"] = selected_doc_id

        doc_data = db.get_document(selected_doc_id)
        topics = db.get_document_topics(selected_doc_id)

        # Overview Metadata
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Subject", doc_data.get("subject", "Mathematics"))
        c2.metric("Grade", doc_data.get("grade", "Class 6"))
        c3.metric("Pages", doc_data.get("page_count", 1))
        c4.metric("Extraction Confidence", f"{int(doc_data.get('confidence_score', 1.0)*100)}%")

        if doc_data.get("extraction_notes"):
            st.caption(f"ℹ️ {doc_data['extraction_notes']}")

        # Topics & Formulas Accordion
        st.markdown("#### Detected Concept Hierarchy & Formulas")
        for idx, t in enumerate(topics):
            with st.expander(f"Topic {idx+1}: {t['title']} (Pages: {t['source_pages']})"):
                st.write(f"**Description:** {t['description']}")
                
                if t.get("learning_objectives"):
                    st.write("**Learning Objectives:**")
                    for obj in t["learning_objectives"]:
                        st.write(f"• {obj}")

                if t.get("formulas"):
                    st.write("**Key Formulas:**")
                    for f in t["formulas"]:
                        st.code(f, language="latex")

                if t.get("common_mistakes"):
                    st.write("**Common Student Mistakes:**")
                    for m in t["common_mistakes"]:
                        st.markdown(f"⚠️ {m}")

                if t.get("solved_example"):
                    st.write("**Worked Example:**")
                    st.info(t["solved_example"])
