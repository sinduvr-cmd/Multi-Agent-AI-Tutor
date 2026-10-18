"""
Agent 5: Answer Evaluation Agent
Role: Student Assessment Specialist
Tasks:
- Evaluate submitted answers
- Grade MCQs, True/False, matching, and numeric answers deterministically
- Normalize equivalent numeric answers and units using SymPy
- Evaluate descriptive answers using a chapter-grounded marking rubric
- Give partial marks where appropriate
- Explain mistakes without discouraging the student
- Provide step-by-step solutions after submission
- Distinguish conceptual misunderstanding from arithmetic mistakes
- Record confidence or uncertainty for subjective grading
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseTutorAgent
from services.grading_service import GradingService
from models.schemas import AnswerEvaluationResult


class AnswerEvaluationAgent(BaseTutorAgent):
    """Student Assessment Specialist Agent."""

    def __init__(self, groq_service: Optional[Any] = None, verbose: bool = True):
        super().__init__(
            role="Student Assessment Specialist",
            goal="Provide fair, diagnostic, and encouraging assessment, rewarding partial steps and pinpointing misconceptions.",
            backstory=(
                "You are an empathetic, highly skilled CBSE exam examiner. You look beyond mere right or wrong: "
                "you identify whether an error was a slip in arithmetic or a gap in foundational understanding, "
                "giving students clear actionable guidance to improve."
            ),
            verbose=verbose,
            groq_service=groq_service
        )

    def evaluate(self, question: Dict[str, Any], student_answer: str) -> AnswerEvaluationResult:
        """Evaluates a student's answer deterministically, with diagnostic feedback."""
        self.log(f"Evaluating answer for question {question.get('question_id')}...")
        result = GradingService.evaluate_answer(question, student_answer, llm_evaluator=self.groq_service)
        return result
