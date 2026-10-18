"""
Student Memory and Adaptive Learning Service.
Tracks student performance, maintains concept mastery scores,
identifies weak and strong topics, and generates adaptive recommendations.
"""

from typing import List, Dict, Any, Optional
import database.db as db
from models.schemas import MasteryScore, LearningRecommendation, DifficultyLevel


class MemoryService:
    """Manages student memory, mastery progression, and adaptive difficulty recommendation."""

    @staticmethod
    def get_mastery_overview(student_id: str) -> Dict[str, Any]:
        """Calculates aggregate metrics, strong/weak concepts, and recommended next difficulty."""
        mastery_rows = db.get_student_mastery(student_id)
        attempts = db.get_student_attempts(student_id, limit=200)

        total_quizzes = len(db.get_student_sessions(student_id))
        total_questions = len(attempts)
        correct_count = sum(1 for a in attempts if a["is_correct"] == 1)
        overall_accuracy = round((correct_count / max(1, total_questions)) * 100.0, 1) if total_questions > 0 else 0.0

        weak_topics = []
        strong_topics = []
        mastery_levels = {}

        for row in mastery_rows:
            topic = row["topic_title"]
            pct = row["score_percentage"]
            mastery_levels[topic] = {
                "score": pct,
                "level": row["level"],
                "attempts": row["attempts_count"]
            }
            if pct < 50.0 and row["attempts_count"] >= 2:
                weak_topics.append({"topic": topic, "score": pct, "level": "Foundation"})
            elif pct >= 80.0 and row["attempts_count"] >= 3:
                strong_topics.append({"topic": topic, "score": pct, "level": "Mastery"})

        # Determine adaptive recommended difficulty
        if overall_accuracy >= 80.0 and len(strong_topics) >= 1:
            recommended_difficulty = DifficultyLevel.HARD
        elif overall_accuracy >= 50.0:
            recommended_difficulty = DifficultyLevel.MEDIUM
        else:
            recommended_difficulty = DifficultyLevel.EASY

        return {
            "student_id": student_id,
            "total_quizzes": total_quizzes,
            "total_questions_answered": total_questions,
            "correct_count": correct_count,
            "overall_accuracy": overall_accuracy,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "mastery_by_topic": mastery_levels,
            "recommended_difficulty": recommended_difficulty.value
        }

    @staticmethod
    def generate_recommendations(student_id: str) -> List[Dict[str, Any]]:
        """Retrieves or creates prioritized targeted recommendations for weak areas."""
        existing = db.get_student_recommendations(student_id)
        if existing:
            return existing

        overview = MemoryService.get_mastery_overview(student_id)
        weak = overview.get("weak_topics", [])
        recs = []

        if weak:
            for w in weak[:3]:
                recs.append({
                    "topic_title": w["topic"],
                    "recommendation": f"Focus revision on '{w['topic']}' (Current mastery: {w['score']}%).",
                    "priority": "High",
                    "suggested_action": "Review step-by-step solved examples and attempt 5 Foundation questions."
                })
        else:
            recs.append({
                "topic_title": "Continuous Learning",
                "recommendation": "Great consistency! Ready to tackle mixed higher-order thinking (HOTS) questions.",
                "priority": "Medium",
                "suggested_action": "Attempt an Exam Mode quiz with Section D & E questions."
            })

        return recs
