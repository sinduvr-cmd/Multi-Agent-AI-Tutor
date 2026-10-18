"""
Multi-Agent AI Tutor: Main Streamlit Application Entrypoint.
Orchestrates educational workflows for CBSE Classes 6-12 across 6 specialized agents.
"""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Streamlit Page Setup
st.set_page_config(
    page_title="Multi-Agent AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Styling
from ui.styles import apply_custom_styles
apply_custom_styles()

import database.db as db
from orchestration.tutor_flow import TutorFlow
from ui.dashboard import render_dashboard
from ui.upload import render_upload_view
from ui.lessons import render_lessons_view
from ui.quiz import render_quiz_view
from ui.progress_view import render_progress_view
from ui.tutor_chat import render_tutor_chat
from ui.teacher import render_teacher_view
from ui.settings_view import render_settings_view

# Initialize Database
db.init_db()

# Initialize Flow Orchestrator in Session State
if "tutor_flow" not in st.session_state:
    st.session_state["tutor_flow"] = TutorFlow()

flow: TutorFlow = st.session_state["tutor_flow"]

# Active Student Management
if "active_student_id" not in st.session_state:
    st.session_state["active_student_id"] = "std_default"

active_student_id = st.session_state["active_student_id"]
current_student = db.get_or_create_student(active_student_id)

# Auto-seed Sample Chapters if DB is empty so the app has instant content
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
if not db.list_documents():
    perimeter_pdf = SAMPLE_DIR / "ncert_class6_perimeter_and_area.pdf"
    if perimeter_pdf.exists():
        try:
            flow.analyze_and_index_chapter(str(perimeter_pdf), "ncert_class6_perimeter_and_area.pdf")
        except Exception:
            pass

# Sidebar Branding & Navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 20px 0;">
        <div style="font-size: 22px; font-weight: 800; color: #38BDF8; letter-spacing: -0.02em;">
            🎓 AI Tutor
        </div>
        <div style="font-size: 12px; color: #94A3B8; font-weight: 500;">
            Multi-Agent CBSE Learning Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Student Badge Card & Interactive Profile Manager
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); 
                border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;">
        <div style="font-size: 11px; text-transform: uppercase; color: #818CF8; font-weight: 700;">Student Profile</div>
        <div style="font-size: 16px; font-weight: 800; color: #F8FAFC; margin-top: 2px;">{current_student['name']}</div>
        <div style="font-size: 12px; color: #94A3B8;">{current_student['grade']} • Mathematics</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("👤 Enter Name / Switch Student", expanded=False):
        all_students = db.list_students()
        student_names = {s["student_id"]: f"{s['name']} ({s['grade']})" for s in all_students}

        if len(all_students) > 1:
            switch_id = st.selectbox(
                "Switch Profile:",
                options=list(student_names.keys()),
                format_func=lambda x: student_names[x],
                index=list(student_names.keys()).index(active_student_id) if active_student_id in student_names else 0,
                key="sb_switch_sel"
            )
            if switch_id != active_student_id:
                if st.button("🔄 Switch to Selected Student", use_container_width=True, key="btn_sb_switch"):
                    st.session_state["active_student_id"] = switch_id
                    st.rerun()

        st.caption("Change name or class for this session:")
        edit_name_val = st.text_input("Student Name:", value=current_student["name"], key="sb_name_input")
        grade_list = [f"Class {i}" for i in range(6, 13)]
        curr_g_idx = grade_list.index(current_student["grade"]) if current_student["grade"] in grade_list else 0
        edit_grade_val = st.selectbox("Grade / Class:", options=grade_list, index=curr_g_idx, key="sb_grade_select")

        c_sb1, c_sb2 = st.columns(2)
        with c_sb1:
            if st.button("💾 Save Name", use_container_width=True, type="primary", key="btn_sb_save"):
                if edit_name_val.strip():
                    db.update_student_profile(active_student_id, edit_name_val.strip(), edit_grade_val)
                    st.success("Updated!")
                    st.rerun()
        with c_sb2:
            if st.button("➕ New Student", use_container_width=True, key="btn_sb_create"):
                if edit_name_val.strip():
                    created = db.create_student_profile(edit_name_val.strip(), edit_grade_val)
                    st.session_state["active_student_id"] = created["student_id"]
                    st.success(f"Welcome, {edit_name_val.strip()}!")
                    st.rerun()

    st.write("")

    # Navigation Menu
    nav_options = [
        "Home Dashboard",
        "Upload Chapter",
        "Learn with AI",
        "Generate Quiz",
        "Take Quiz",
        "My Progress",
        "AI Tutor Chat",
        "Teacher Tools",
        "Settings"
    ]

    # Handle internal redirection
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "Home Dashboard"

    def set_view(view_name: str):
        st.session_state["current_view"] = view_name
        st.rerun()

    # Radio Navigation
    nav_idx = nav_options.index(st.session_state["current_view"]) if st.session_state["current_view"] in nav_options else 0
    selected_view = st.radio(
        "Navigation",
        options=nav_options,
        index=nav_idx,
        label_visibility="collapsed"
    )
    if selected_view != st.session_state["current_view"]:
        st.session_state["current_view"] = selected_view
        st.rerun()

    st.write("")
    st.divider()

    # Agent Health Monitor
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;'>Agent Crew Status</div>", unsafe_allow_html=True)
    agents_status = [
        ("A1: Chapter Analyst", "Active"),
        ("A2: Teaching Agent", "Active"),
        ("A3: Question Setter", "Active"),
        ("A4: QA Reviewer (SymPy)", "Active"),
        ("A5: Answer Evaluator", "Active"),
        ("A6: Adaptive Coach", "Active")
    ]
    for agent_name, status in agents_status:
        st.caption(f"🟢 **{agent_name}**: `{status}`")

    # Groq API Banner
    if flow.groq_service.is_configured():
        st.caption(f"⚡ Model: `{flow.groq_service.model}`")
    else:
        st.caption("📦 Engine: `Verified CBSE Offline Mode`")


# Router
current_view = st.session_state["current_view"]

if current_view == "Home Dashboard":
    render_dashboard(active_student_id, set_view)
elif current_view == "Upload Chapter":
    render_upload_view(flow)
elif current_view == "Learn with AI":
    render_lessons_view(flow)
elif current_view in ["Generate Quiz", "Take Quiz"]:
    render_quiz_view(flow, active_student_id)
elif current_view == "My Progress":
    render_progress_view(active_student_id)
elif current_view == "AI Tutor Chat":
    render_tutor_chat(flow)
elif current_view == "Teacher Tools":
    render_teacher_view(flow)
elif current_view == "Settings":
    render_settings_view(flow, active_student_id)
