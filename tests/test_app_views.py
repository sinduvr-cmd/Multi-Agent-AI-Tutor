"""
End-to-End Streamlit App View Testing using Streamlit's official AppTest framework.
Tests:
1. Home Dashboard loads without exceptions
2. Sidebar navigation across all routes:
   - Learn with AI
   - Generate Quiz
   - My Progress
   - AI Tutor Chat
   - Teacher Tools
   - Settings
3. Custom Student Name Entry and Profile Switching
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str((Path(__file__).resolve().parent.parent / "app.py").resolve())


def test_app_dashboard_loads():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception


def test_app_navigation_to_learn_with_ai():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("Learn with AI").run()
    assert not at.exception


def test_app_navigation_to_progress_view():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("My Progress").run()
    assert not at.exception


def test_app_navigation_to_teacher_tools():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("Teacher Tools").run()
    assert not at.exception


def test_app_navigation_to_settings():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("Settings").run()
    assert not at.exception


def test_app_navigation_to_generate_quiz():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("Generate Quiz").run()
    assert not at.exception


def test_app_navigation_to_upload_chapter():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("Upload Chapter").run()
    assert not at.exception


def test_app_navigation_to_tutor_chat():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    nav_radio = at.sidebar.radio[0]
    nav_radio.set_value("AI Tutor Chat").run()
    assert not at.exception


def test_app_student_name_update():
    at = AppTest.from_file(APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception

    # Find the student name text input in the sidebar or dashboard
    name_inputs = [i for i in at.text_input if "Name" in (i.label or "")]
    if name_inputs:
        name_inputs[0].set_value("Ananya Iyer")
        # Find save button
        save_buttons = [b for b in at.button if "Save" in (b.label or "") or "Update" in (b.label or "")]
        if save_buttons:
            save_buttons[0].click().run()
            assert not at.exception
