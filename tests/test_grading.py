"""
Test Suite: Deterministic Grading and SymPy Math Normalizer.
Verifies equivalence of numbers with units, fractions, and rubric evaluation.
"""

from services.grading_service import GradingService


def test_mcq_grading():
    q = {
        "question_id": "q1",
        "question_type": "MCQ",
        "correct_answer": "50 cm",
        "marks": 1,
        "explanation": "2*(15+10)=50"
    }

    # Exact match
    res1 = GradingService.evaluate_answer(q, "50 cm")
    assert res1.is_correct
    assert res1.marks_awarded == 1.0

    # Wrong answer
    res2 = GradingService.evaluate_answer(q, "25 cm")
    assert not res2.is_correct
    assert res2.marks_awarded == 0.0


def test_numerical_unit_normalization():
    q = {
        "question_id": "q2",
        "question_type": "Numerical",
        "correct_answer": "144",
        "accepted_alternatives": ["144 m^2", "144 sq m"],
        "marks": 2,
        "explanation": "12 * 12 = 144"
    }

    # Exact string
    assert GradingService.evaluate_answer(q, "144").is_correct
    # With unit
    assert GradingService.evaluate_answer(q, "144 m^2").is_correct
    # With decimal
    assert GradingService.evaluate_answer(q, "144.0").is_correct
    # With alternative format
    assert GradingService.evaluate_answer(q, "144 sq m").is_correct
    # Arithmetic equivalence
    assert GradingService.evaluate_answer(q, "288/2").is_correct
    # Incorrect
    assert not GradingService.evaluate_answer(q, "140").is_correct


def test_fraction_sum_normalization():
    q = {
        "question_id": "q3",
        "question_type": "Numerical",
        "correct_answer": "11/15",
        "accepted_alternatives": ["0.733", "0.73"],
        "marks": 2,
        "explanation": "2/5 + 1/3 = 11/15"
    }

    assert GradingService.evaluate_answer(q, "11/15").is_correct
    assert GradingService.evaluate_answer(q, " 11 / 15 ").is_correct
