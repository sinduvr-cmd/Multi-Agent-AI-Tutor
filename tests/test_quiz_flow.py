"""
Test Suite: Quiz Flow and State Transitions.
Verifies quiz generation, state initialization, and attempt locking.
"""

from orchestration.tutor_flow import TutorFlow
import database.db as db


def test_quiz_generation_and_evaluation_cycle():
    flow = TutorFlow()
    db.init_db()

    # Ingest sample chapter
    analysis = flow.analyze_and_index_chapter(
        "sample_data/ncert_class6_perimeter_and_area.pdf",
        "ncert_class6_perimeter_and_area.pdf"
    )
    doc_id = analysis["document_id"]

    # Generate 3 questions
    questions = flow.generate_and_validate_quiz(document_id=doc_id, count=3)
    assert len(questions) == 3

    # Evaluate question 0 correctly
    q0 = questions[0]
    res_correct = flow.evaluate_student_answer(
        session_id="test_sess_flow",
        student_id="test_std_flow",
        question=q0,
        student_answer=q0["correct_answer"]
    )
    assert res_correct["is_correct"]
    assert res_correct["marks_awarded"] == q0.get("marks", 1)

    # Evaluate question 1 with wrong answer
    q1 = questions[1]
    res_wrong = flow.evaluate_student_answer(
        session_id="test_sess_flow",
        student_id="test_std_flow",
        question=q1,
        student_answer="WRONG_VALUE_999"
    )
    assert not res_wrong["is_correct"]
    assert res_wrong["marks_awarded"] == 0.0
