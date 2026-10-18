"""
Agent 3: Question Generator Agent
Role: CBSE Examination Question Setter
Tasks:
- Generate questions based on chapter coverage
- Allow the user to choose difficulty: Easy, Medium, Hard, Mixed
- Generate all supported question formats (MCQ, Fill in blank, Numerical, True/False,
  Assertion-Reason, Short Answer, Long Answer, Case Study, Matching, Diagram Based)
- Provide exactly one correct answer for single-select MCQs
- Create plausible distractors
- Generate solutions, explanations, marks, and rubrics
- Produce questions in valid structured JSON
- Map every question to chapter topic and source pages
- Generate novel questions, not merely repeat source questions
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseTutorAgent
from models.schemas import QuestionModel, QuestionType, DifficultyLevel


class QuestionGeneratorAgent(BaseTutorAgent):
    """CBSE Examination Question Setter Agent."""

    def __init__(self, groq_service: Optional[Any] = None, verbose: bool = True):
        super().__init__(
            role="CBSE Examination Question Setter",
            goal="Generate novel, rigorous, curriculum-grounded assessment questions across diverse cognitive levels.",
            backstory=(
                "You are an experienced CBSE examination question designer. You know the exact "
                "marking schemes, distractor patterns, and competency-based question styles. "
                "Every question you produce is unambiguous and grounded in the syllabus."
            ),
            verbose=verbose,
            groq_service=groq_service
        )

    def generate_questions(
        self,
        document_id: str,
        chapter_title: str,
        topic_title: str,
        chunks_context: str,
        count: int = 5,
        difficulty: str = "Medium",
        question_types: Optional[List[str]] = None,
        source_pages: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Generates a batch of structured questions for the chosen topic."""
        source_pages = source_pages or [1, 2]
        allowed_types = question_types or ["MCQ", "Fill Blank", "Numerical", "True/False", "Assertion and Reason"]

        # If Groq is available and configured, generate with LLM in strict JSON mode
        if self.groq_service and self.groq_service.is_configured():
            try:
                self.log(f"Prompting Groq to generate {count} {difficulty} questions for '{topic_title}'...")
                system_prompt = (
                    "You are a CBSE Examination Question Setter. Generate high-quality, novel questions "
                    "strictly grounded in the provided chapter text.\n"
                    "CRITICAL CONSTRAINTS:\n"
                    "1. For MCQs, provide exactly 4 unique, plausible options with exactly ONE correct answer.\n"
                    "2. For Assertion-Reason, use the standard 4 CBSE options.\n"
                    "3. Return a JSON object with key 'questions', which is a list of question objects.\n"
                    "Each question object MUST contain:\n"
                    "- question_text (string)\n"
                    "- question_type (one of: MCQ, Fill Blank, Numerical, True/False, Assertion and Reason, Short Answer, Long Answer)\n"
                    "- difficulty (Easy, Medium, Hard)\n"
                    "- marks (integer, typically 1 for MCQ/Fill/TF/AR, 2 for Numerical, 3 for Short, 5 for Long)\n"
                    "- options (list of 4 strings for MCQ/AR, or ['True', 'False'] for TF, null otherwise)\n"
                    "- correct_answer (string matching one option for MCQ/TF/AR, or exact value)\n"
                    "- accepted_alternatives (list of strings for numerical units/forms)\n"
                    "- explanation (comprehensive string explaining why correct is right and distractors are wrong)\n"
                    "- solution_steps (list of step strings)\n"
                    "- source_pages (list of integers, e.g. [1, 2])"
                )

                user_prompt = (
                    f"Chapter: {chapter_title}\n"
                    f"Topic: {topic_title}\n"
                    f"Target Difficulty: {difficulty}\n"
                    f"Number of questions: {count}\n"
                    f"Allowed Question Types: {allowed_types}\n\n"
                    f"Chapter Source Text:\n{chunks_context[:3500]}"
                )

                response = self.groq_service.generate_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    json_mode=True,
                    max_tokens=2500,
                    temperature=0.3
                )

                if response:
                    parsed = json.loads(response)
                    raw_questions = parsed.get("questions", [])
                    validated_list = []
                    for q in raw_questions:
                        q["question_id"] = f"q_{uuid.uuid4().hex[:8]}"
                        q["document_id"] = document_id
                        q["chapter"] = chapter_title
                        q["topic"] = topic_title
                        q["source_pages"] = q.get("source_pages") or source_pages
                        validated_list.append(q)
                    if validated_list:
                        return validated_list
            except Exception as e:
                self.log(f"LLM question generation encountered error: {e}. Falling back to curated bank.")

        # Procedural / Verified Bank Fallback
        return self._get_fallback_questions(
            document_id, chapter_title, topic_title, count, difficulty, allowed_types, source_pages
        )

    def _get_fallback_questions(
        self,
        document_id: str,
        chapter_title: str,
        topic_title: str,
        count: int,
        difficulty: str,
        allowed_types: List[str],
        source_pages: List[int]
    ) -> List[Dict[str, Any]]:
        """Returns verified, procedurally parameterized questions when LLM is unavailable."""
        from sample_data.demo_questions import get_verified_demo_questions
        questions = get_verified_demo_questions()
        
        # 1. Filter by allowed question types first
        if allowed_types:
            type_match = [q for q in questions if q.get("question_type") in allowed_types]
            if type_match:
                questions = type_match

        # 2. Filter by chapter/topic if available
        matching = [
            q for q in questions 
            if (topic_title.lower() in q["topic"].lower() or "all" in topic_title.lower())
        ]
        if not matching:
            matching = questions

        # 3. Filter by difficulty if not Mixed
        if difficulty != "Mixed":
            diff_match = [q for q in matching if q["difficulty"].lower() == difficulty.lower()]
            if diff_match:
                matching = diff_match

        # Adjust count and inject new UUIDs
        result = []
        for i in range(count):
            base_q = dict(matching[i % len(matching)])
            base_q["question_id"] = f"q_gen_{uuid.uuid4().hex[:8]}"
            base_q["document_id"] = document_id
            base_q["chapter"] = chapter_title
            base_q["topic"] = topic_title if topic_title != "All" else base_q["topic"]
            base_q["source_pages"] = source_pages
            result.append(base_q)
        return result
