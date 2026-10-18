"""
Pydantic schemas and data models for Multi-Agent AI Tutor.
Strictly validated data structures for questions, chapters, evaluations, and student records.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class QuestionType(str, Enum):
    MCQ = "MCQ"
    FILL_BLANK = "Fill Blank"
    NUMERICAL = "Numerical"
    TRUE_FALSE = "True/False"
    SHORT_ANSWER = "Short Answer"
    LONG_ANSWER = "Long Answer"
    ASSERTION_REASON = "Assertion and Reason"
    CASE_STUDY = "Case Study"
    DIAGRAM_BASED = "Diagram Based"
    MATCHING = "Matching"


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    MIXED = "Mixed"


class QuizMode(str, Enum):
    PRACTICE = "Practice Mode"
    EXAM = "Exam Mode"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ChunkMetadata(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    chunk_type: str = "text"  # text, table, formula, diagram
    content: str
    bounding_box: Optional[List[float]] = None


class TopicConcept(BaseModel):
    topic_id: str
    document_id: str
    title: str
    description: str
    learning_objectives: List[str] = Field(default_factory=list)
    formulas: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    solved_example: Optional[str] = None
    source_pages: List[int] = Field(default_factory=list)


class ChapterAnalysisResult(BaseModel):
    document_id: str
    filename: str
    title: str
    subject: str = "Mathematics"
    grade: str = "Class 6"
    topics: List[TopicConcept] = Field(default_factory=list)
    total_pages: int
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    extraction_notes: Optional[str] = None
    diagram_references: List[str] = Field(default_factory=list)


class SubQuestion(BaseModel):
    sub_id: str
    question_text: str
    question_type: QuestionType = QuestionType.MCQ
    marks: int = 1
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str


class RubricCriterion(BaseModel):
    criterion: str
    points: float
    description: str


class QuestionModel(BaseModel):
    question_id: str
    document_id: str
    chapter: str
    topic: str
    question_type: QuestionType
    question_text: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    marks: int = Field(default=1, ge=1)
    
    # MCQ / TrueFalse / AssertionReason options
    options: Optional[List[str]] = None
    correct_answer: str
    accepted_alternatives: List[str] = Field(default_factory=list)
    
    explanation: str
    solution_steps: List[str] = Field(default_factory=list)
    marking_rubric: Optional[List[RubricCriterion]] = None
    
    diagram_reference: Optional[str] = None
    source_pages: List[int] = Field(default_factory=list)
    source_chunk_ids: List[str] = Field(default_factory=list)
    
    # Case study subquestions
    subquestions: Optional[List[SubQuestion]] = None
    
    # Matching pairs
    matching_pairs: Optional[Dict[str, str]] = None
    
    # Quality review status
    validation_status: ValidationStatus = ValidationStatus.APPROVED
    validation_notes: Optional[str] = None
    revision_count: int = 0

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, info):
        q_type = info.data.get("question_type")
        if q_type == QuestionType.MCQ:
            if not v or len(v) != 4:
                raise ValueError("Standard MCQ must contain exactly 4 options.")
            if len(set(v)) != 4:
                raise ValueError("MCQ options must be unique and distinct.")
        elif q_type == QuestionType.TRUE_FALSE:
            if not v:
                return ["True", "False"]
        elif q_type == QuestionType.ASSERTION_REASON:
            standard_ar = [
                "Both (A) and (R) are true and (R) is the correct explanation of (A).",
                "Both (A) and (R) are true but (R) is NOT the correct explanation of (A).",
                "(A) is true but (R) is false.",
                "(A) is false but (R) is true."
            ]
            if not v or len(v) != 4:
                return standard_ar
        return v

    @model_validator(mode="after")
    def validate_correct_answer(self):
        if self.question_type == QuestionType.MCQ and self.options:
            cleaned_ans = self.correct_answer.strip()
            # Match directly or by option letter e.g. "A", "B", "C", "D"
            if cleaned_ans not in self.options:
                letter_map = {"A": 0, "B": 1, "C": 2, "D": 3}
                if cleaned_ans in letter_map and letter_map[cleaned_ans] < len(self.options):
                    # Canonicalize correct answer to the full option text
                    self.correct_answer = self.options[letter_map[cleaned_ans]]
                else:
                    raise ValueError(
                        f"Correct answer '{cleaned_ans}' must be one of the 4 options: {self.options}"
                    )
        return self


class AnswerEvaluationResult(BaseModel):
    question_id: str
    student_answer: str
    is_correct: bool
    marks_awarded: float
    max_marks: float
    feedback: str
    detailed_solution: str
    is_arithmetic_mistake: bool = False
    is_conceptual_misunderstanding: bool = False
    evaluator_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_pages: List[int] = Field(default_factory=list)


class QuizSessionState(BaseModel):
    session_id: str
    student_id: str
    document_id: str
    chapter_title: str
    mode: QuizMode
    total_marks: int
    current_index: int = 0
    questions: List[QuestionModel] = Field(default_factory=list)
    answers: Dict[str, str] = Field(default_factory=dict)
    evaluations: Dict[str, AnswerEvaluationResult] = Field(default_factory=dict)
    flagged_questions: List[str] = Field(default_factory=list)
    is_completed: bool = False
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class StudentProfile(BaseModel):
    student_id: str
    name: str
    grade: str = "Class 6"
    created_at: str
    preferred_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class MasteryScore(BaseModel):
    topic_id: str
    topic_title: str
    score_percentage: float
    attempts_count: int
    correct_count: int
    level: str  # Foundation (<50%), Standard (50-79%), Mastery (>=80%)


class LearningRecommendation(BaseModel):
    topic_id: str
    topic_title: str
    recommendation: str
    priority: str  # High, Medium, Low
    suggested_action: str
