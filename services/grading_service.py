"""
Deterministic and Mathematical Grading Service.
Uses SymPy and regex normalizers to grade MCQs, True/False, Fill in Blank,
and Numerical answers with unit and equivalence awareness (e.g., '24 cm' == '24cm' == '24.0').
Provides rubric grading for descriptive answers.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import sympy as sp
from models.schemas import AnswerEvaluationResult, QuestionModel, QuestionType


class GradingService:
    """Evaluates student submissions with deterministic accuracy and math intelligence."""

    @staticmethod
    def clean_math_string(s: str) -> str:
        """Removes spaces, lowercase, strips units like cm, m, sq cm, m^2."""
        s = str(s).strip().lower()
        # Remove common units
        s = re.sub(r"\b(sq\s*cm|cm\^2|cm2|centimeters\s*squared|sq\s*m|m\^2|m2|meters\s*squared)\b", "", s)
        s = re.sub(r"\b(cm|centimeters|m|meters|km|kilometers|tiles|units)\b", "", s)
        s = s.replace(" ", "").replace("=", "")
        return s

    @classmethod
    def evaluate_numerical_equality(cls, student_ans: str, correct_ans: str, alternatives: List[str]) -> bool:
        """
        Tests whether the student's answer is mathematically equal to the correct answer
        or any of the accepted alternatives using SymPy.
        """
        all_targets = [correct_ans] + list(alternatives)
        clean_stud = cls.clean_math_string(student_ans)

        for target in all_targets:
            clean_tgt = cls.clean_math_string(target)
            if clean_stud == clean_tgt:
                return True

            # Try parsing both as SymPy expressions or numbers
            try:
                # Handle fractions like '11/15'
                val_stud = sp.sympify(clean_stud)
                val_tgt = sp.sympify(clean_tgt)
                diff = sp.simplify(val_stud - val_tgt)
                if diff == 0 or abs(float(diff)) < 1e-4:
                    return True
            except Exception:
                pass

        return False

    @classmethod
    def evaluate_answer(
        cls,
        question: Dict[str, Any],
        student_answer: str,
        llm_evaluator: Optional[Any] = None
    ) -> AnswerEvaluationResult:
        """
        Main grading dispatcher.
        Returns an AnswerEvaluationResult model.
        """
        q_id = question.get("question_id", "q")
        q_type = question.get("question_type", "MCQ")
        correct_ans = str(question.get("correct_answer", "")).strip()
        alternatives = question.get("accepted_alternatives", [])
        max_marks = float(question.get("marks", 1))
        solution_steps = question.get("solution_steps", [])
        detailed_solution = "\n".join(solution_steps) if solution_steps else question.get("explanation", "")
        source_pages = question.get("source_pages", [])

        # Normalize student answer
        stud_ans_str = str(student_answer).strip()

        # 1. MCQ
        if q_type == "MCQ":
            # Compare options directly or by letter
            is_correct = (
                stud_ans_str.lower() == correct_ans.lower() or
                cls.clean_math_string(stud_ans_str) == cls.clean_math_string(correct_ans)
            )
            marks_awarded = max_marks if is_correct else 0.0
            
            if is_correct:
                feedback = f"Excellent! {correct_ans} is the correct answer."
            else:
                feedback = (
                    f"Not quite. You selected '{stud_ans_str}', but the correct answer is '{correct_ans}'. "
                    f"{question.get('explanation', '')}"
                )

            return AnswerEvaluationResult(
                question_id=q_id,
                student_answer=stud_ans_str,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
                max_marks=max_marks,
                feedback=feedback,
                detailed_solution=detailed_solution,
                is_arithmetic_mistake=False,
                is_conceptual_misunderstanding=not is_correct,
                evaluator_confidence=1.0,
                source_pages=source_pages
            )

        # 2. True / False
        elif q_type == "True/False":
            norm_stud = "true" if stud_ans_str.lower().startswith("t") else "false"
            norm_corr = "true" if correct_ans.lower().startswith("t") else "false"
            is_correct = (norm_stud == norm_corr)
            marks_awarded = max_marks if is_correct else 0.0

            return AnswerEvaluationResult(
                question_id=q_id,
                student_answer=stud_ans_str,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
                max_marks=max_marks,
                feedback="Correct!" if is_correct else f"Incorrect. The statement is {correct_ans}. {question.get('explanation', '')}",
                detailed_solution=detailed_solution,
                evaluator_confidence=1.0,
                source_pages=source_pages
            )

        # 3. Fill in Blank & Numerical
        elif q_type in ["Fill Blank", "Numerical"]:
            is_correct = cls.evaluate_numerical_equality(stud_ans_str, correct_ans, alternatives)
            marks_awarded = max_marks if is_correct else 0.0

            # Check if student made an arithmetic slip vs conceptual error
            is_arithmetic = False
            is_conceptual = False
            if not is_correct:
                # If numbers are close or off by factor of 2 (e.g. forgot to double in perimeter)
                try:
                    s_val = float(cls.clean_math_string(stud_ans_str))
                    c_val = float(cls.clean_math_string(correct_ans))
                    if abs(s_val * 2 - c_val) < 0.1 or abs(s_val - c_val) <= 2:
                        is_arithmetic = True
                    else:
                        is_conceptual = True
                except Exception:
                    is_conceptual = True

            feedback = (
                f"Correct! Well done." if is_correct else
                f"Incorrect. Your answer was '{stud_ans_str}', but the expected answer is '{correct_ans}'. "
                f"{question.get('explanation', '')}"
            )

            return AnswerEvaluationResult(
                question_id=q_id,
                student_answer=stud_ans_str,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
                max_marks=max_marks,
                feedback=feedback,
                detailed_solution=detailed_solution,
                is_arithmetic_mistake=is_arithmetic,
                is_conceptual_misunderstanding=is_conceptual,
                evaluator_confidence=1.0,
                source_pages=source_pages
            )

        # 4. Assertion & Reason
        elif q_type == "Assertion and Reason":
            is_correct = (stud_ans_str.lower() == correct_ans.lower())
            marks_awarded = max_marks if is_correct else 0.0

            return AnswerEvaluationResult(
                question_id=q_id,
                student_answer=stud_ans_str,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
                max_marks=max_marks,
                feedback="Correct logical deduction!" if is_correct else f"Incorrect. Correct choice is: {correct_ans}",
                detailed_solution=detailed_solution,
                evaluator_confidence=1.0,
                source_pages=source_pages
            )

        # 5. Matching
        elif q_type == "Matching":
            matching_pairs = question.get("matching_pairs", {})
            # If student answer contains all mappings or correct keywords
            matches_found = sum(1 for k, v in matching_pairs.items() if (k.lower() in stud_ans_str.lower() and v.lower() in stud_ans_str.lower()))
            total_pairs = max(1, len(matching_pairs))
            fraction_correct = matches_found / total_pairs
            is_correct = fraction_correct >= 0.75
            marks_awarded = round(fraction_correct * max_marks, 1)

            return AnswerEvaluationResult(
                question_id=q_id,
                student_answer=stud_ans_str,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
                max_marks=max_marks,
                feedback=f"Matched {matches_found}/{total_pairs} pairs correctly.",
                detailed_solution=detailed_solution,
                evaluator_confidence=0.9,
                source_pages=source_pages
            )

        # 6. Short Answer, Long Answer & Subjective Evaluation
        else:
            if not stud_ans_str or len(stud_ans_str) < 2:
                return AnswerEvaluationResult(
                    question_id=q_id,
                    student_answer=stud_ans_str,
                    is_correct=False,
                    marks_awarded=0.0,
                    max_marks=max_marks,
                    feedback="No answer provided.",
                    detailed_solution=detailed_solution,
                    evaluator_confidence=1.0,
                    source_pages=source_pages
                )

            # Check if LLM evaluator is configured for intelligent rubric grading
            if llm_evaluator and hasattr(llm_evaluator, "is_configured") and llm_evaluator.is_configured():
                try:
                    eval_prompt = (
                        f"You are an expert CBSE examiner. Grade this student's response strictly.\n"
                        f"Question: {question.get('question_text')}\n"
                        f"Correct Answer / Solution: {correct_ans}\n"
                        f"Max Marks: {max_marks}\n"
                        f"Marking Rubric: {question.get('marking_rubric')}\n"
                        f"Student Answer: {stud_ans_str}\n\n"
                        f"CRITICAL: If the question requires a numerical answer (e.g. 48 tiles, 144 m^2, 11/15) "
                        f"and the student's number is wrong (e.g. 24 tiles instead of 48), they MUST NOT receive full marks! "
                        f"Award 0 or very small partial marks (max 1) only if valid intermediate formula steps are shown.\n"
                        f"Return JSON with: 'marks_awarded' (float between 0 and {max_marks}), 'is_correct' (boolean: true only if fully correct), "
                        f"'feedback' (string explaining what was right/wrong)."
                    )
                    resp = llm_evaluator.generate_completion(
                        messages=[
                            {"role": "system", "content": "You are a strict CBSE examiner. Return valid JSON only."},
                            {"role": "user", "content": eval_prompt}
                        ],
                        json_mode=True,
                        max_tokens=250,
                        temperature=0.1
                    )
                    if resp:
                        import json
                        p_data = json.loads(resp)
                        awarded = min(max_marks, max(0.0, float(p_data.get("marks_awarded", 0.0))))
                        is_corr = bool(p_data.get("is_correct", False)) and (awarded >= max_marks * 0.8)
                        return AnswerEvaluationResult(
                            question_id=q_id,
                            student_answer=stud_ans_str,
                            is_correct=is_corr,
                            marks_awarded=awarded,
                            max_marks=max_marks,
                            feedback=p_data.get("feedback", f"Score: {awarded}/{max_marks}"),
                            detailed_solution=detailed_solution,
                            evaluator_confidence=0.95,
                            source_pages=source_pages
                        )
                except Exception:
                    pass

            # Strict Deterministic Fallback:
            # Check numerical requirement: if correct_ans has numbers, student answer MUST contain them!
            expected_numbers = re.findall(r"\b\d+(?:\.\d+)?\b", correct_ans)
            student_numbers = re.findall(r"\b\d+(?:\.\d+)?\b", stud_ans_str)

            if expected_numbers:
                # Key numbers in correct answer must be matched
                matched_nums = sum(1 for en in expected_numbers if any(abs(float(en) - float(sn)) < 0.01 for sn in student_numbers))
                if matched_nums < len(expected_numbers):
                    # Numbers do not match! Final answer is wrong.
                    return AnswerEvaluationResult(
                        question_id=q_id,
                        student_answer=stud_ans_str,
                        is_correct=False,
                        marks_awarded=0.0,
                        max_marks=max_marks,
                        feedback=f"Incorrect numerical result. Expected: '{correct_ans}'. Your answer: '{stud_ans_str}'.",
                        detailed_solution=detailed_solution,
                        is_arithmetic_mistake=True,
                        evaluator_confidence=1.0,
                        source_pages=source_pages
                    )

            # Check keyword match
            keywords = [w for w in re.findall(r"\b\w{4,}\b", correct_ans.lower()) if w not in ["with", "that", "this", "from", "each", "were", "what", "find"]]
            matched_kw = sum(1 for kw in keywords if kw in stud_ans_str.lower())
            ratio = (matched_kw / max(1, len(keywords))) if keywords else 1.0

            if ratio >= 0.7:
                awarded = max_marks
                is_corr = True
                fb = f"Correct! Well articulated."
            elif ratio >= 0.4:
                awarded = round(max_marks * 0.5, 1)
                is_corr = False
                fb = f"Partially correct ({awarded}/{max_marks} Marks). Missing some key explanations."
            else:
                awarded = 0.0
                is_corr = False
                fb = f"Incorrect. Key concepts were missing."

            return AnswerEvaluationResult(
                question_id=q_id,
                student_answer=stud_ans_str,
                is_correct=is_corr,
                marks_awarded=awarded,
                max_marks=max_marks,
                feedback=fb,
                detailed_solution=detailed_solution,
                evaluator_confidence=0.9,
                source_pages=source_pages
            )
