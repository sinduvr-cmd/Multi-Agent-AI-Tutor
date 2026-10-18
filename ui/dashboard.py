"""
UI Module: Home Dashboard
Displays welcome greeting, active student metrics, quick launch actions,
and mastery progress summary.
"""

import streamlit as st
import database.db as db
from services.memory_service import MemoryService
from services.analytics_service import AnalyticsService


def render_dashboard(active_student_id: str, on_navigate_callback):
    student = db.get_or_create_student(active_student_id)
    overview = MemoryService.get_mastery_overview(active_student_id)
    documents = db.list_documents()

    # Hero Banner
    st.markdown(f"""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">Welcome back, {student['name']}! 👋</div>
        <div class="tutor-hero-subtitle">
            Your Multi-Agent AI Tutor is ready. All lessons and assessments are strictly grounded 
            in your verified CBSE textbooks and uploaded chapters.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Chapters Indexed</div>
            <div class="metric-val">{len(documents)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Quizzes Attempted</div>
            <div class="metric-val">{overview['total_quizzes']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Overall Accuracy</div>
            <div class="metric-val">{overview['overall_accuracy']}%</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Adaptive Level</div>
            <div class="metric-val" style="color: #38BDF8;">{overview['recommended_difficulty']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Quick Launch Buttons
    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
    with col_act1:
        if st.button("📖 Learn with AI", use_container_width=True, type="primary"):
            on_navigate_callback("Learn with AI")
    with col_act2:
        if st.button("📝 Start Adaptive Quiz", use_container_width=True):
            on_navigate_callback("Generate Quiz")
    with col_act3:
        if st.button("📄 Upload Chapter PDF", use_container_width=True):
            on_navigate_callback("Upload Chapter")
    with col_act4:
        if st.button("💬 AI Tutor Chat", use_container_width=True):
            on_navigate_callback("AI Tutor Chat")

    st.divider()

    # Visual Analytics Split: Mastery Radar + Quick Recommendations
    col_chart, col_recs = st.columns([1.2, 1])

    with col_chart:
        st.subheader("🎯 Topic Mastery Radar")
        mastery_data = db.get_student_mastery(active_student_id)
        fig_radar = AnalyticsService.create_mastery_radar(mastery_data)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_recs:
        st.subheader("💡 Learning Recommendations")
        recs = MemoryService.generate_recommendations(active_student_id)
        for r in recs[:3]:
            priority_color = "#EF4444" if r.get("priority") == "High" else "#F59E0B"
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.45); border-left: 4px solid {priority_color}; 
                        border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #F8FAFC; font-size: 14px;">{r.get('topic_title')}</div>
                <div style="color: #CBD5E1; font-size: 13px; margin-top: 4px;">{r.get('recommendation')}</div>
                <div style="color: #94A3B8; font-size: 12px; margin-top: 4px;"><b>Suggested:</b> {r.get('suggested_action')}</div>
            </div>
            """, unsafe_allow_html=True)

        if not recs:
            st.info("No revision flags! Complete a quiz to receive targeted suggestions.")

    # Recent Chapters Table
    st.subheader("📚 Available Textbook Chapters")
    if documents:
        for doc in documents[:5]:
            col_d1, col_d2, col_d3 = st.columns([3, 1, 1])
            with col_d1:
                st.markdown(f"**{doc['title']}** ({doc['subject']} — {doc['grade']})")
                st.caption(f"Filename: `{doc['filename']}` | Pages: {doc['page_count']} | Confidence: {int(doc['confidence_score']*100)}%")
            with col_d2:
                if st.button(f"Study", key=f"btn_study_{doc['document_id']}"):
                    st.session_state["selected_document_id"] = doc["document_id"]
                    on_navigate_callback("Learn with AI")
            with col_d3:
                if st.button(f"Quiz", key=f"btn_quiz_{doc['document_id']}"):
                    st.session_state["selected_document_id"] = doc["document_id"]
                    on_navigate_callback("Generate Quiz")
            st.write("---")
    else:
        st.info("No chapters indexed yet. Use the 'Upload Chapter' tab or load sample NCERT chapters!")
