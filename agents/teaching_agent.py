"""
Agent 2: Personalized Teaching Agent
Role: Expert AI Tutor
Tasks:
- Create easy-to-understand explanations
- Adjust explanations to student grade and performance
- Generate worked examples
- Support Explain Like I'm 10, Standard, and Detailed modes
- Create personalized lesson plans
- Provide interactive tutoring through a chat interface
- Use only retrieved chapter context for claims about the uploaded material
- State clearly when a student asks something beyond the uploaded chapter
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseTutorAgent


class TeachingAgent(BaseTutorAgent):
    """Personalized AI Tutor for interactive learning and grounded explanations."""

    def __init__(self, groq_service: Optional[Any] = None, verbose: bool = True):
        super().__init__(
            role="Expert AI Tutor",
            goal="Provide engaging, grade-appropriate explanations and worked examples strictly grounded in chapter material.",
            backstory=(
                "You are an inspiring, patient CBSE master teacher. You break complex mathematical "
                "concepts into vivid real-world analogies. You never invent textbook facts, and you "
                "always celebrate student curiosity."
            ),
            verbose=verbose,
            groq_service=groq_service
        )

    def explain_concept(
        self,
        topic: Dict[str, Any],
        mode: str = "Standard",  # "Explain Like I'm 10", "Standard", "Detailed"
        grade: str = "Class 6"
    ) -> Dict[str, Any]:
        """Generates a structured lesson tailored to the requested explanation mode."""
        topic_title = topic.get("title", "Concept")
        formulas = topic.get("formulas", [])
        mistakes = topic.get("common_mistakes", [])
        base_example = topic.get("solved_example", "")

        # If Groq is available, generate dynamic personalized explanation
        if self.groq_service and self.groq_service.is_configured():
            prompt = (
                f"Topic: {topic_title}\n"
                f"Grade Level: {grade}\n"
                f"Explanation Mode: {mode}\n"
                f"Formulas: {formulas}\n"
                f"Description: {topic.get('description', '')}\n\n"
                f"Please explain this concept for a {grade} student in {mode} style. "
                "Include:\n"
                "1. Intuitive Explanation with an engaging analogy\n"
                "2. Step-by-step Solved Example\n"
                "3. Common Pitfalls / Tips to avoid errors\n"
                "4. A quick 1-sentence memory trick."
            )
            response = self.groq_service.generate_completion(
                messages=[
                    {"role": "system", "content": "You are a warm, crystal-clear CBSE Math Tutor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            if response:
                return {
                    "mode": mode,
                    "explanation_text": response,
                    "formulas": formulas,
                    "common_mistakes": mistakes,
                    "solved_example": base_example
                }

        # Deterministic rich fallback explanation
        if mode == "Explain Like I'm 10":
            explanation = (
                f"Imagine walking around the fence of your favorite playground! "
                f"Every step you take along the border is like measuring **{topic_title}**. "
                f"We just add up the boundary steps one by one. If it's a rectangle, the opposite sides "
                f"are twins, so you take double the length and double the width!"
            )
        elif mode == "Detailed":
            explanation = (
                f"### Formal Mathematical Analysis of {topic_title}\n\n"
                f"{topic.get('description', '')}\n\n"
                f"**Key Geometric Principles:**\n"
                f"1. Perimeter represents a one-dimensional linear measure ($cm$, $m$).\n"
                f"2. Area represents a two-dimensional surface measure ($cm^2$, $m^2$).\n"
                f"3. Dimensional homogeneity requires consistent units prior to algebraic substitution."
            )
        else:  # Standard
            explanation = (
                f"**{topic_title}** is an essential chapter concept in {grade}. "
                f"{topic.get('description', '')}\n\n"
                f"Always remember to inspect the units given in the problem statement before starting calculations."
            )

        return {
            "mode": mode,
            "explanation_text": explanation,
            "formulas": formulas,
            "common_mistakes": mistakes,
            "solved_example": base_example or "Refer to textbook worked examples."
        }

    def chat_response(
        self,
        student_query: str,
        chat_history: List[Dict[str, str]],
        chapter_context: str
    ) -> str:
        """Responds to student questions, strictly citing chapter context or flagging out-of-scope."""
        if self.groq_service and self.groq_service.is_configured():
            system_prompt = (
                "You are an AI Tutor for CBSE students. You MUST use only the provided chapter context "
                "for claims about the textbook material. If the student asks something completely outside "
                "the uploaded chapter (e.g. quantum physics or world history), state clearly and politely: "
                "'This topic is beyond our uploaded chapter, but here is a brief general note...'\n\n"
                f"Chapter Context:\n{chapter_context[:3000]}"
            )
            messages = [{"role": "system", "content": system_prompt}]
            for msg in chat_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": student_query})

            resp = self.groq_service.generate_completion(messages, max_tokens=500)
            if resp:
                return resp

        # Deterministic tutor fallback
        lower_q = student_query.lower()
        if "formula" in lower_q or "perimeter" in lower_q or "area" in lower_q:
            return (
                "Here are the core formulas from our uploaded chapter:\n"
                "• **Perimeter of Rectangle:** $2 \\times (\\text{Length} + \\text{Breadth})$\n"
                "• **Perimeter of Square:** $4 \\times \\text{Side}$\n"
                "• **Area of Rectangle:** $\\text{Length} \\times \\text{Breadth}$\n"
                "• **Area of Square:** $\\text{Side} \\times \\text{Side}$\n\n"
                "Remember: Always write perimeter in $cm$ or $m$, and area in $cm^2$ or $m^2$!"
            )
        elif "fraction" in lower_q:
            return (
                "In Fractions:\n"
                "• **Proper Fraction:** Numerator < Denominator (e.g. $3/8$)\n"
                "• **Improper Fraction:** Numerator $\\ge$ Denominator (e.g. $7/4$)\n"
                "• To add unlike fractions, always calculate the LCM of the denominators first!"
            )
        else:
            return (
                f"Great question! Based on our uploaded chapter: "
                f"Make sure to check the definitions and solved examples on source pages. "
                f"Is there a specific formula or worked example you would like me to break down step-by-step?"
            )
