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

    @staticmethod
    def generate_student_report_card_pdf(
        student_name: str,
        grade: str,
        overview: Dict[str, Any],
        mastery_rows: List[Dict[str, Any]],
        attempts: List[Dict[str, Any]]
    ) -> bytes:
        """Generates an official CBSE Student Assessment & Mastery Report Card PDF."""
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
            'RepTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            alignment=1,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=4
        )
        sub_style = ParagraphStyle(
            'RepSub',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=1,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12
        )
        sec_title = ParagraphStyle(
            'RepSec',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1E3A8A'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'RepBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#1E293B')
        )
        badge_style = ParagraphStyle(
            'RepBadge',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#0F172A'),
            alignment=1
        )

        story = []

        # 1. Header
        story.append(Paragraph("<b>CBSE STUDENT ASSESSMENT & MASTERY REPORT</b>", title_style))
        story.append(Paragraph(f"Student: <b>{student_name}</b> &nbsp;|&nbsp; {grade} &nbsp;|&nbsp; Subject: Mathematics", sub_style))
        story.append(Spacer(1, 8))

        # 2. Executive Metrics Summary Table
        summary_data = [
            [
                Paragraph("<b>Quizzes Completed</b>", badge_style),
                Paragraph("<b>Questions Solved</b>", badge_style),
                Paragraph("<b>Overall Accuracy</b>", badge_style),
                Paragraph("<b>Adaptive Level</b>", badge_style)
            ],
            [
                Paragraph(f"<b>{overview.get('total_quizzes', 0)}</b>", badge_style),
                Paragraph(f"<b>{overview.get('total_questions_answered', 0)}</b>", badge_style),
                Paragraph(f"<b>{overview.get('overall_accuracy', 0.0)}%</b>", badge_style),
                Paragraph(f"<b>{overview.get('recommended_difficulty', 'Medium')}</b>", badge_style)
            ]
        ]
        sum_table = Table(summary_data, colWidths=[130, 130, 130, 140])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E0F2FE')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 14))

        # 3. Topic Mastery Table
        story.append(Paragraph("<b>1. Topic-Wise Concept Mastery Breakdown</b>", sec_title))
        if mastery_rows:
            table_rows = [[
                Paragraph("<b>Topic Concept</b>", body_style),
                Paragraph("<b>Mastery %</b>", body_style),
                Paragraph("<b>Attempts</b>", body_style),
                Paragraph("<b>Correct</b>", body_style),
                Paragraph("<b>Status Level</b>", body_style)
            ]]
            for m in mastery_rows:
                pct = m.get("score_percentage", 0.0)
                level = m.get("level", "Foundation")
                color_hex = "#059669" if pct >= 80 else ("#D97706" if pct >= 50 else "#DC2626")
                table_rows.append([
                    Paragraph(f"<b>{m.get('topic_title', 'General')}</b>", body_style),
                    Paragraph(f"<font color='{color_hex}'><b>{pct:.1f}%</b></font>", body_style),
                    Paragraph(str(m.get("attempts_count", 0)), body_style),
                    Paragraph(str(m.get("correct_count", 0)), body_style),
                    Paragraph(f"<b>{level}</b>", body_style)
                ])

            m_table = Table(table_rows, colWidths=[200, 75, 75, 75, 105])
            m_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(m_table)
        else:
            story.append(Paragraph("<i>No topic attempts recorded yet. Start a quiz to populate mastery breakdown.</i>", body_style))

        story.append(Spacer(1, 14))

        # 4. Diagnostic Feedback & Coach Recommendations
        story.append(Paragraph("<b>2. Adaptive AI Coach Diagnostic Notes</b>", sec_title))
        weak = overview.get("weak_topics", [])
        strong = overview.get("strong_topics", [])

        if strong:
            strong_str = ", ".join([f"<b>{s['topic']}</b> ({s['score']}%)" for s in strong])
            story.append(Paragraph(f"• <b>Mastered Areas (≥80%):</b> {strong_str}. High conceptual retention.", body_style))
        if weak:
            weak_str = ", ".join([f"<b>{w['topic']}</b> ({w['score']}%)" for w in weak])
            story.append(Paragraph(f"• <b>Areas Needing Reinforcement (<50%):</b> {weak_str}. Recommend reviewing foundational formulas and worked examples.", body_style))
        if not weak and not strong:
            story.append(Paragraph("• Student is progressing through foundational concepts consistently.", body_style))

        story.append(Spacer(1, 14))

        # 5. Recent Attempts Log
        if attempts:
            story.append(Paragraph("<b>3. Recent Assessment Log (Latest 8 Questions)</b>", sec_title))
            att_data = [[
                Paragraph("<b>Chapter / Topic</b>", body_style),
                Paragraph("<b>Type</b>", body_style),
                Paragraph("<b>Student Ans</b>", body_style),
                Paragraph("<b>Result</b>", body_style),
                Paragraph("<b>Score</b>", body_style)
            ]]
            for a in attempts[:8]:
                is_c = a.get("is_correct")
                res_str = "<font color='#059669'><b>CORRECT</b></font>" if is_c else "<font color='#DC2626'><b>INCORRECT</b></font>"
                ans_snippet = (str(a.get("student_answer", ""))[:20] + "...") if len(str(a.get("student_answer", ""))) > 20 else str(a.get("student_answer", ""))
                att_data.append([
                    Paragraph(f"{a.get('chapter', 'Math')}: {a.get('topic', 'General')}", body_style),
                    Paragraph(a.get("question_type", "MCQ"), body_style),
                    Paragraph(ans_snippet or "—", body_style),
                    Paragraph(res_str, body_style),
                    Paragraph(f"{a.get('marks_awarded', 0):.1f}/{a.get('max_marks', 1):.0f}", body_style)
                ])

            att_table = Table(att_data, colWidths=[180, 80, 110, 90, 70])
            att_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(att_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
