"""
Agent 6: Adaptive Learning and Memory Agent
Role: Personalized Learning Coach
Tasks:
- Track student performance across quiz sessions
- Maintain mastery scores by chapter and concept
- Identify strengths, weaknesses and repeated mistakes
- Recommend revision topics
- Generate targeted practice questions
- Gradually increase difficulty after demonstrated improvement
- Repeat poorly understood concepts with fresh questions
- Generate daily and weekly learning recommendations
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseTutorAgent
from services.memory_service import MemoryService


class AdaptiveCoachAgent(BaseTutorAgent):
    """Personalized Learning Coach Agent."""

    def __init__(self, groq_service: Optional[Any] = None, verbose: bool = True):
        super().__init__(
            role="Personalized Learning Coach",
            goal="Analyze long-term student memory, adapt question difficulty dynamically, and prescribe personalized revision pathways.",
            backstory=(
                "You are an encouraging cognitive learning coach. You celebrate student gains, "
                "detect recurring misconceptions early, and calibrate challenge levels so students "
                "stay in their optimal Zone of Proximal Development."
            ),
            verbose=verbose,
            groq_service=groq_service
        )

    def analyze_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Synthesizes memory data, weak areas, and coaching advice."""
        overview = MemoryService.get_mastery_overview(student_id)
        recommendations = MemoryService.generate_recommendations(student_id)
        
        advice = "Keep practicing regularly to build enduring mathematical fluency."
        if overview["weak_topics"]:
            weak_names = ", ".join([w["topic"] for w in overview["weak_topics"]])
            advice = f"Focus your next session on: {weak_names}. You are close to mastering these concepts!"
        elif overview["overall_accuracy"] >= 80.0:
            advice = "Outstanding performance! You are demonstrating mastery across your chapters. Try challenging HOTS problems next."

        return {
            "overview": overview,
            "recommendations": recommendations,
            "coach_advice": advice,
            "recommended_difficulty": overview["recommended_difficulty"]
        }
