"""
CrewAI Flow and Multi-Agent Orchestration Controller for Multi-Agent AI Tutor.
Coordinates deterministic state transitions between:
1. Chapter Analysis Agent
2. Personalized Teaching Agent
3. Question Generator Agent
4. Question Quality Reviewer Agent
5. Answer Evaluation Agent
6. Adaptive Learning and Memory Agent
"""

from typing import Dict, Any, List, Optional
import database.db as db
from services.groq_client import GroqService
from agents.chapter_analyst import ChapterAnalysisAgent
from agents.teaching_agent import TeachingAgent
from agents.question_generator import QuestionGeneratorAgent
from agents.quality_reviewer import QualityReviewerAgent
from agents.answer_evaluator import AnswerEvaluationAgent
from agents.adaptive_coach import AdaptiveCoachAgent


class TutorFlow:
    """Master Multi-Agent Orchestrator controlling state transitions and agent handoffs."""

    def __init__(self, groq_api_key: Optional[str] = None, model: Optional[str] = None):
        self.groq_service = GroqService(api_key=groq_api_key, model=model)
        
        # Instantiate the 6 Crew Agents
        self.chapter_analyst = ChapterAnalysisAgent(self.groq_service)
        self.teaching_agent = TeachingAgent(self.groq_service)
        self.question_generator = QuestionGeneratorAgent(self.groq_service)
        self.quality_reviewer = QualityReviewerAgent(self.groq_service)
        self.answer_evaluator = AnswerEvaluationAgent(self.groq_service)
        self.adaptive_coach = AdaptiveCoachAgent(self.groq_service)

    def analyze_and_index_chapter(self, file_path_or_bytes: Any, filename: str) -> Dict[str, Any]:
        """Flow Step 1: Document validation, extraction, and topic persistence."""
        res = self.chapter_analyst.run_task(
            "Extract and structure textbook chapter",
            {"file_path_or_bytes": file_path_or_bytes, "filename": filename}
        )
        analysis = res["analysis"]
        chunks = res["chunks"]
        # Persist analysis and chunks in SQLite
        db.save_document_analysis(analysis, chunks)
        return analysis

    def generate_and_validate_quiz(
        self,
        document_id: str,
        topic: str = "All",
        count: int = 5,
        difficulty: str = "Medium",
        question_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Flow Step 2: Question Generation and Quality Review audit loop."""
        doc = db.get_document(document_id)
        chapter_title = doc["title"] if doc else "Chapter"
        
        # Retrieve chunks for grounded generation
        chunks = db.get_document_chunks(document_id)
        chunks_context = "\n\n".join([c["content"] for c in chunks[:12]])

        # 1. Question Generator Agent generates candidate questions
        candidates = self.question_generator.generate_questions(
            document_id=document_id,
            chapter_title=chapter_title,
            topic_title=topic,
            chunks_context=chunks_context,
            count=count,
            difficulty=difficulty,
            question_types=question_types
        )

        # 2. Quality Reviewer Agent audits and refines questions (max 3 revision attempts)
        approved_questions = self.quality_reviewer.audit_and_refine_batch(
            questions=candidates,
            generator_agent=self.question_generator,
            context={"chunks_context": chunks_context},
            max_revisions=3
        )

        # 3. Persist approved questions in database
        if approved_questions:
            db.save_questions(approved_questions)

        return approved_questions

    def evaluate_student_answer(
        self,
        session_id: str,
        student_id: str,
        question: Dict[str, Any],
        student_answer: str
    ) -> Dict[str, Any]:
        """Flow Step 3: Deterministic/Diagnostic Evaluation and Memory Update."""
        eval_result = self.answer_evaluator.evaluate(question, student_answer)
        
        attempt_record = {
            "session_id": session_id,
            "student_id": student_id,
            "question_id": question.get("question_id"),
            "student_answer": student_answer,
            "is_correct": eval_result.is_correct,
            "marks_awarded": eval_result.marks_awarded,
            "max_marks": eval_result.max_marks,
            "feedback": eval_result.feedback,
            "detailed_solution": eval_result.detailed_solution,
            "is_arithmetic_mistake": eval_result.is_arithmetic_mistake,
            "is_conceptual_misunderstanding": eval_result.is_conceptual_misunderstanding
        }
        db.record_question_attempt(attempt_record)
        return eval_result.model_dump()
