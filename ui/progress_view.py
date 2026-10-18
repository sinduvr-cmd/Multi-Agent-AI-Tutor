"""
UI Module: Student Progress and Mastery Analytics
Displays interactive Plotly charts, mastery radar, score progression,
and weakness diagnostic recommendations.
"""

import streamlit as st
import database.db as db
from services.memory_service import MemoryService
from services.analytics_service import AnalyticsService
from services.export_service import ExportService


def render_progress_view(active_student_id: str):
    student = db.get_or_create_student(active_student_id)
    overview = MemoryService.get_mastery_overview(active_student_id)
    mastery_rows = db.get_student_mastery(active_student_id)
    attempts = db.get_student_attempts(active_student_id, limit=200)

    st.markdown(f"""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">📊 Learning Analytics & Mastery: {student['name']}</div>
        <div class="tutor-hero-subtitle">
            Agent 6 (Adaptive Learning Coach) tracks your long-term concept retention, 
            identifies weaknesses, and calibrates your learning trajectory.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Metric Banner
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quizzes Attempted", overview["total_quizzes"])
    c2.metric("Questions Solved", overview["total_questions_answered"])
    c3.metric("Overall Accuracy", f"{overview['overall_accuracy']}%")
    c4.metric("Adaptive Mastery Level", overview["recommended_difficulty"])

    st.write("")

    # Visual Charts
    col_chart1, col_chart2 = st.columns([1.2, 1])
    with col_chart1:
        st.subheader("🎯 Concept Mastery Radar")
        fig_radar = AnalyticsService.create_mastery_radar(mastery_rows)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_chart2:
        st.subheader("🍩 Overall Accuracy Breakdown")
        fig_donut = AnalyticsService.create_accuracy_donut(
            overview["correct_count"],
            overview["total_questions_answered"]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Score Progression Timeline
    st.subheader("📈 Performance Timeline")
    fig_line = AnalyticsService.create_attempts_timeline(attempts)
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # Diagnostic Weakness and Strength Breakdown
    col_weak, col_strong = st.columns(2)

    with col_weak:
        st.subheader("⚠️ Weak Concepts (< 50%)")
        if overview["weak_topics"]:
            for w in overview["weak_topics"]:
                st.markdown(f"""
                <div style="background: rgba(127, 29, 29, 0.35); border-left: 4px solid #EF4444; 
                            border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="font-weight: 700; color: #FEE2E2;">{w['topic']}</div>
                    <div style="color: #FCA5A5; font-size: 13px;">Mastery: <b>{w['score']}%</b> ({w['level']})</div>
                    <div style="color: #E2E8F0; font-size: 12px; margin-top: 4px;">Recommended: Review basic formulas and retake 5 Easy practice items.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No weak concepts detected! All attempted topics are above 50% mastery.")

    with col_strong:
        st.subheader("🌟 Mastered Concepts (≥ 80%)")
        if overview["strong_topics"]:
            for s in overview["strong_topics"]:
                st.markdown(f"""
                <div style="background: rgba(6, 78, 59, 0.35); border-left: 4px solid #10B981; 
                            border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="font-weight: 700; color: #D1FAE5;">{s['topic']}</div>
                    <div style="color: #6EE7B7; font-size: 13px;">Mastery: <b>{s['score']}%</b> ({s['level']})</div>
                    <div style="color: #E2E8F0; font-size: 12px; margin-top: 4px;">Excellent! Ready for higher-order Olympiad or HOTS challenges.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Keep practicing to unlock 80%+ mastery badges across topics!")

    st.divider()

    # Report Card PDF, CSV Export and History Reset
    col_exp1, col_exp2, col_exp3 = st.columns([1.5, 1.5, 1])
    with col_exp1:
        report_pdf = ExportService.generate_student_report_card_pdf(
            student_name=student["name"],
            grade=student["grade"],
            overview=overview,
            mastery_rows=mastery_rows,
            attempts=attempts
        )
        st.download_button(
            label="📄 Download Official Report Card (PDF)",
            data=report_pdf,
            file_name=f"Report_Card_{student['name'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_exp2:
        csv_data = ExportService.export_attempts_to_csv(attempts)
        st.download_button(
            label="📥 Download My Quiz History (CSV)",
            data=csv_data,
            file_name=f"quiz_history_{student['name'].replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_exp3:
        if st.button("🗑️ Reset My History", use_container_width=True):
            db.delete_student_history(active_student_id)
            st.success("Student quiz history and mastery cleared.")
            st.rerun()
