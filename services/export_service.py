"""
Export Service for Teachers and Students.
Generates CBSE Section A-E Examination Question Paper PDFs,
separate Answer Key & Explanations PDFs with ReportLab,
and exports student quiz results to CSV.
"""

import io
from typing import List, Dict, Any, Optional
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ExportService:
    """Handles PDF compilation and CSV generation."""

    @staticmethod
    def generate_question_paper_pdf(
        chapter_title: str,
        grade: str,
        subject: str,
        total_marks: int,
        questions: List[Dict[str, Any]],
        include_answers: bool = False
    ) -> bytes:
        """
        Builds a CBSE-format Examination Question Paper.
        If include_answers is False, renders the student test paper.
        If include_answers is True, renders the official Teacher Answer Key & Marking Scheme.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'PaperTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            alignment=1,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        sub_style = ParagraphStyle(
            'PaperSub',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13,
            alignment=1,
            textColor=colors.HexColor('#475569'),
            spaceAfter=8
        )
        sec_header = ParagraphStyle(
            'SecHeader',
            parent=styles['Heading2'],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#1E3A8A'),
            spaceBefore=10,
            spaceAfter=4
        )
        q_style = ParagraphStyle(
            'QText',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=4
        )
        ans_box = ParagraphStyle(
            'AnsBox',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#065F46'),
            backColor=colors.HexColor('#ECFDF5'),
            borderColor=colors.HexColor('#A7F3D0'),
            borderWidth=0.5,
            borderPadding=4,
            spaceAfter=6
        )

        story = []

        doc_type_header = "TEACHER ANSWER KEY & MARKING SCHEME" if include_answers else "EXAMINATION QUESTION PAPER"
        story.append(Paragraph(f"<b>CBSE {grade.upper()} {subject.upper()}</b>", title_style))
        story.append(Paragraph(f"<b>{doc_type_header}</b> — {chapter_title}", title_style))
        story.append(Paragraph(f"Time Allowed: 90 Minutes &nbsp;|&nbsp; Maximum Marks: {total_marks}", sub_style))
        story.append(Spacer(1, 4))

        if not include_answers:
            # Instructions Box
            inst_text = (
                "<b>General Instructions:</b><br/>"
                "1. All questions are compulsory.<br/>"
                "2. Section A contains 1-mark MCQs/Fill-in/True-False.<br/>"
                "3. Section B contains 2-mark Very Short Answer questions.<br/>"
                "4. Section C contains 3-mark Short Answer questions.<br/>"
                "5. Section D contains 5-mark Long Answer questions.<br/>"
                "6. Section E contains 4-mark Case-study questions."
            )
            story.append(Paragraph(inst_text, ParagraphStyle('Inst', parent=styles['Normal'], fontSize=8.5, leading=12, backColor=colors.HexColor('#F8FAFC'), borderPadding=6, borderWidth=0.5, borderColor=colors.HexColor('#CBD5E1'), spaceAfter=8)))

        # Group questions into CBSE Sections: A, B, C, D, E
        sec_a = [q for q in questions if q.get("marks", 1) == 1]
        sec_b = [q for q in questions if q.get("marks", 1) == 2]
        sec_c = [q for q in questions if q.get("marks", 1) == 3]
        sec_d = [q for q in questions if q.get("marks", 1) >= 5]
        sec_e = [q for q in questions if q.get("question_type") == "Case Study"]

        # Catch remaining
        allocated_ids = {q.get("question_id") for sec in [sec_a, sec_b, sec_c, sec_d, sec_e] for q in sec}
        leftover = [q for q in questions if q.get("question_id") not in allocated_ids]
        if leftover:
            sec_b.extend(leftover)

        sections = [
            ("SECTION A (1 Mark Questions)", sec_a),
            ("SECTION B (2 Mark Questions)", sec_b),
            ("SECTION C (3 Mark Questions)", sec_c),
            ("SECTION D (5 Mark Questions)", sec_d),
            ("SECTION E (Case Study Competency Questions)", sec_e)
        ]

        q_counter = 1
        for sec_title, sec_questions in sections:
            if not sec_questions:
                continue
            story.append(Paragraph(f"<b>{sec_title}</b>", sec_header))
            for q in sec_questions:
                q_text = f"<b>Q{q_counter}.</b> {q.get('question_text')} &nbsp;&nbsp;<b>[{q.get('marks', 1)} Mark]</b>"
                story.append(Paragraph(q_text, q_style))

                # Render options for MCQ
                if q.get("options") and q.get("question_type") in ["MCQ", "Assertion and Reason"]:
                    opts = q.get("options")
                    letters = ["(A)", "(B)", "(C)", "(D)"]
                    opt_line = " &nbsp;&nbsp;&nbsp;&nbsp; ".join([f"{letters[i]} {opts[i]}" for i in range(min(len(opts), 4))])
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt_line}", q_style))

                if include_answers:
                    ans_text = (
                        f"<b>Correct Answer:</b> {q.get('correct_answer')}<br/>"
                        f"<b>Explanation / Rubric:</b> {q.get('explanation')}<br/>"
                        f"<b>Source Page:</b> Page(s) {q.get('source_pages', [1])}"
                    )
                    story.append(Paragraph(ans_text, ans_box))

                story.append(Spacer(1, 4))
                q_counter += 1

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def export_attempts_to_csv(attempts: List[Dict[str, Any]]) -> str:
        """Converts attempts list to CSV string."""
        if not attempts:
            return "No quiz attempt records available."
        df = pd.DataFrame(attempts)
        cols_to_export = [
            "session_id", "student_id", "question_id", "chapter", "topic",
            "question_type", "difficulty", "student_answer", "is_correct",
            "marks_awarded", "max_marks", "attempt_time"
        ]
        available_cols = [c for c in cols_to_export if c in df.columns]
        return df[available_cols].to_csv(index=False)
