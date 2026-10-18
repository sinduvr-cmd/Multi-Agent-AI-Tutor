"""
UI Module: Settings and Profile Management
Allows switching and creating student profiles, deleting history,
configuring Groq API credentials, model selection, and verifying connections.
"""

import os
import uuid
import streamlit as st
import database.db as db
from orchestration.tutor_flow import TutorFlow


def render_settings_view(flow: TutorFlow, active_student_id: str):
    st.markdown("""
    <div class="tutor-hero-card">
        <div class="tutor-hero-title">⚙️ System & Profile Settings</div>
        <div class="tutor-hero-subtitle">
            Manage student profiles, configure your Groq API credentials, or toggle 
            the verified offline demo mode.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_profile, tab_api = st.tabs(["👤 Student Profiles", "🔑 Groq API & LLM Models"])

    with tab_profile:
        st.subheader("Manage Active Student Profile")
        students = db.list_students()

        current_student = db.get_or_create_student(active_student_id)
        st.info(f"Currently Active: **{current_student['name']}** ({current_student['grade']}) — ID: `{active_student_id}`")

        # Edit Current Profile Name
        st.markdown("##### ✏️ Edit Current Student Name & Grade:")
        with st.form("form_edit_active_student"):
            edit_name = st.text_input("Student Name:", value=current_student["name"])
            grade_list = [f"Class {i}" for i in range(6, 13)]
            curr_g_idx = grade_list.index(current_student["grade"]) if current_student["grade"] in grade_list else 0
            edit_grade = st.selectbox("Grade / Class:", options=grade_list, index=curr_g_idx)
            save_clicked = st.form_submit_button("💾 Save Profile Updates", type="primary")
            if save_clicked:
                if edit_name.strip():
                    db.update_student_profile(active_student_id, edit_name.strip(), edit_grade)
                    st.success(f"Profile updated! Active student is now {edit_name.strip()}.")
                    st.rerun()
                else:
                    st.error("Please enter a valid student name.")

        st.divider()

        # Switch Profile
        if len(students) > 1:
            st.markdown("##### Switch Student Profile:")
            student_map = {s["student_id"]: f"{s['name']} ({s['grade']})" for s in students}
            new_selected_id = st.selectbox(
                "Select Profile:",
                options=list(student_map.keys()),
                format_func=lambda x: student_map[x],
                index=list(student_map.keys()).index(active_student_id)
            )
            if new_selected_id != active_student_id:
                if st.button("Switch to this profile"):
                    st.session_state["active_student_id"] = new_selected_id
                    st.rerun()

        st.divider()

        # Create New Profile
        st.markdown("##### Create New Student Profile:")
        with st.form("form_create_student"):
            new_name = st.text_input("Student Name:", placeholder="e.g. Priya Patel")
            new_grade = st.selectbox("Grade / Class:", options=["Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12"])
            submitted = st.form_submit_button("Create Profile")
            if submitted:
                if new_name.strip():
                    new_id = f"std_{uuid.uuid4().hex[:6]}"
                    db.get_or_create_student(new_id, new_name.strip(), new_grade)
                    st.session_state["active_student_id"] = new_id
                    st.success(f"Profile created for {new_name}! Switched to new profile.")
                    st.rerun()
                else:
                    st.error("Please enter a valid student name.")

        st.divider()

        # Delete History
        st.markdown("##### Danger Zone")
        st.caption("Clearing history removes quiz sessions, question attempts, and mastery scores for this profile.")
        if st.button("🗑️ Delete My Progress History", type="secondary"):
            db.delete_student_history(active_student_id)
            st.success(f"Progress history cleared for {current_student['name']}.")
            st.rerun()

    with tab_api:
        st.subheader("Groq API Configuration")
        st.caption("The system connects to Groq's high-speed inference engine for real-time agent generation and tutoring.")

        is_configured = flow.groq_service.is_configured()
        if is_configured:
            st.success("🟢 Groq API is configured and active.")
        else:
            st.warning("🟡 Groq API Key is not configured. Running in **Verified Demo Mode** using local CBSE question bank.")

        with st.form("form_groq_settings"):
            entered_key = st.text_input(
                "Groq API Key:",
                value=flow.groq_service.api_key or "",
                type="password",
                help="Enter your gsk_... key from console.groq.com. Keys are never logged."
            )
            selected_model = st.selectbox(
                "Inference Model:",
                options=["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"],
                index=0
            )
            save_api = st.form_submit_button("Save & Test Connection")
            
            if save_api:
                flow.groq_service.api_key = entered_key.strip()
                flow.groq_service.model = selected_model
                os.environ["GROQ_API_KEY"] = entered_key.strip()

                test_res = flow.groq_service.test_connection()
                if test_res["success"]:
                    st.success(f"✅ {test_res['message']}")
                else:
                    st.error(f"❌ {test_res['message']}")
