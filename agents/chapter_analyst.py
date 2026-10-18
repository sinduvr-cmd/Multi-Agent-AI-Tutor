"""
Agent 1: Chapter Analysis Agent
Role: Educational Content Researcher
Tasks:
- Extract PDF text, layout, headings, tables, equations, and diagrams
- Detect chapter name, subject, grade, and topic hierarchy
- Identify formulas, definitions, worked examples, and exercises
- Summarize concepts with source page references
- Create structured learning objectives
- Detect incomplete or low-confidence extraction
- Retain page-level chunks and metadata for source-grounded generation
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseTutorAgent
from services.pdf_processor import PDFProcessor
from models.schemas import ChapterAnalysisResult, TopicConcept


class ChapterAnalysisAgent(BaseTutorAgent):
    """Educational Content Researcher Agent."""

    def __init__(self, groq_service: Optional[Any] = None, verbose: bool = True):
        super().__init__(
            role="Educational Content Researcher",
            goal="Thoroughly extract and structure textbook chapters, preserving exact formulas, concepts, and page grounding.",
            backstory=(
                "You are an expert CBSE curriculum specialist and educational researcher. "
                "You meticulously parse textbooks, extract learning objectives, formulas, "
                "and ensure no spurious content is invented."
            ),
            verbose=verbose,
            groq_service=groq_service
        )
        self.pdf_processor = PDFProcessor()

    def run_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        file_path_or_bytes = context.get("file_path_or_bytes")
        filename = context.get("filename", "chapter.pdf")

        if not file_path_or_bytes:
            raise ValueError("No file provided for Chapter Analysis Agent.")

        # Step 1: Deterministic PyMuPDF extraction
        self.log(f"Extracting layout and text from '{filename}'...")
        analysis_dict, chunks = self.pdf_processor.process_pdf(file_path_or_bytes, filename)

        # Step 2: If Groq is available and configured, optionally enrich topic objectives
        if self.groq_service and self.groq_service.is_configured():
            try:
                self.log("Enhancing concept objectives with Groq LLM...")
                sample_text = "\n".join([c["content"] for c in chunks[:15]])
                prompt = (
                    f"Analyze this textbook chapter content:\n{sample_text}\n\n"
                    "Identify key topics, formulas, and common student misconceptions. "
                    "Return a JSON object with key 'topics' containing a list of objects with fields: "
                    "'title', 'description', 'learning_objectives' (list of strings), 'formulas' (list of strings), 'common_mistakes' (list of strings)."
                )
                response = self.groq_service.generate_completion(
                    messages=[
                        {"role": "system", "content": "You are a CBSE Educational Researcher. Return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    json_mode=True,
                    max_tokens=1000
                )
                if response:
                    parsed = json.loads(response)
                    if "topics" in parsed and len(parsed["topics"]) > 0:
                        # Merge enriched topics while preserving page grounding
                        for idx, t in enumerate(parsed["topics"]):
                            if idx < len(analysis_dict["topics"]):
                                orig = analysis_dict["topics"][idx]
                                orig["learning_objectives"] = t.get("learning_objectives", orig["learning_objectives"])
                                orig["formulas"] = t.get("formulas", orig["formulas"])
                                orig["common_mistakes"] = t.get("common_mistakes", orig["common_mistakes"])
            except Exception as e:
                self.log(f"Optional LLM enrichment skipped: {e}")

        return {
            "analysis": analysis_dict,
            "chunks": chunks
        }
