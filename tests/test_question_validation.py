"""
Test Suite: Question Schema & Academic Quality Reviewer.
Verifies Pydantic model validation and SymPy mathematical checks in Quality Reviewer.
"""

import pytest
from models.schemas import QuestionModel, QuestionType, DifficultyLevel
from agents.quality_reviewer import QualityReviewerAgent


def test_mcq_requires_four_distinct_options():
    # Valid MCQ
    valid_q = QuestionModel(
        question_id="q_test_1",
        document_id="doc_1",
        chapter="Perimeter and Area",
        topic="Perimeter",
        question_type=QuestionType.MCQ,
        question_text="What is the perimeter of a rectangle with length 5 cm and width 3 cm?",
        marks=1,
        options=["16 cm", "15 cm", "8 cm", "20 cm"],
        correct_answer="16 cm",
        explanation="2 * (5 + 3) = 16 cm."
    )
    assert valid_q.correct_answer == "16 cm"

    # Invalid MCQ with 3 options should fail validation
    with pytest.raises(ValueError):
        QuestionModel(
            question_id="q_test_2",
            document_id="doc_1",
            chapter="Perimeter and Area",
            topic="Perimeter",
            question_type=QuestionType.MCQ,
            question_text="Invalid question?",
            marks=1,
            options=["16 cm", "15 cm", "8 cm"],
            correct_answer="16 cm",
            explanation="Invalid"
        )


def test_reviewer_rejects_arithmetic_error():
    reviewer = QualityReviewerAgent(verbose=False)
    
    # Intentionally incorrect arithmetic in question stem:
    # "length is 15 cm and breadth is 10 cm", correct perimeter is 50, but we state 60
    flawed_q = {
        "question_id": "q_flawed",
        "question_type": "MCQ",
        "question_text": "Find the perimeter of a rectangle whose length is 15 cm and breadth is 10 cm.",
        "options": ["60 cm", "40 cm", "30 cm", "25 cm"],
        "correct_answer": "60 cm",
        "explanation": "Calculated incorrectly as 60 cm."
    }

    passed, notes = reviewer.review_question(flawed_q)
    assert not passed
    assert "Verification Failed" in notes or "Calculated perimeter" in notes
