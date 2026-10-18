"""
Test Suite: Student Memory & Adaptive Progress.
Verifies profile isolation, mastery categorization, and history clearing.
"""

import database.db as db
from services.memory_service import MemoryService


def test_student_isolation_and_mastery():
    db.init_db()

    std_a = "std_alice_test"
    std_b = "std_bob_test"

    # Create students
    db.get_or_create_student(std_a, "Alice", "Class 6")
    db.get_or_create_student(std_b, "Bob", "Class 6")

    # Clear previous test data
    db.delete_student_history(std_a)
    db.delete_student_history(std_b)

    # Ingest dummy question
    db.save_questions([{
        "question_id": "q_mem_1",
        "document_id": "doc_mem",
        "chapter": "Perimeter",
        "topic": "Rectangles",
        "question_type": "MCQ",
        "question_text": "Sample perimeter question",
        "marks": 1,
        "options": ["10", "20", "30", "40"],
        "correct_answer": "20",
        "explanation": "Test explanation",
        "validation_status": "approved"
    }])

    # Alice answers correctly
    db.record_question_attempt({
        "session_id": "sess_alice",
        "student_id": std_a,
        "question_id": "q_mem_1",
        "student_answer": "20",
        "is_correct": 1,
        "marks_awarded": 1.0,
        "max_marks": 1.0
    })

    # Bob answers incorrectly
    db.record_question_attempt({
        "session_id": "sess_bob",
        "student_id": std_b,
        "question_id": "q_mem_1",
        "student_answer": "10",
        "is_correct": 0,
        "marks_awarded": 0.0,
        "max_marks": 1.0
    })

    # Verify Alice's metrics
    overview_a = MemoryService.get_mastery_overview(std_a)
    assert overview_a["overall_accuracy"] == 100.0
    assert overview_a["correct_count"] == 1

    # Verify Bob's metrics
    overview_b = MemoryService.get_mastery_overview(std_b)
    assert overview_b["overall_accuracy"] == 0.0
    assert overview_b["correct_count"] == 0

    # Verify Delete History for Alice does not affect Bob
    db.delete_student_history(std_a)
    overview_a_cleared = MemoryService.get_mastery_overview(std_a)
    assert overview_a_cleared["total_questions_answered"] == 0

    overview_b_recheck = MemoryService.get_mastery_overview(std_b)
    assert overview_b_recheck["total_questions_answered"] == 1
