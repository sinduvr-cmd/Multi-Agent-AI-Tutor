"""
Sample PDF Generator for Multi-Agent AI Tutor.
Generates NCERT-style CBSE sample textbooks and question papers:
1. NCERT Class 6 Chapter 6: Perimeter and Area
2. NCERT Class 6 Chapter 7: Fractions
3. Class 6 Perimeter and Area Worksheet
4. Class 6 Mathematics Practice Paper (Sections A-E)
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

SAMPLE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def build_perimeter_area_pdf():
    pdf_path = SAMPLE_DIR / "ncert_class6_perimeter_and_area.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )
    box_style = ParagraphStyle(
        'DocBox',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=1,
        borderPadding=8,
        spaceAfter=8
    )

    story = []
    
    # Header
    story.append(Paragraph("NCERT Mathematics — Class 6", ParagraphStyle('Sub', fontSize=11, textColor=colors.HexColor('#64748B'))))
    story.append(Paragraph("Chapter 6: Perimeter and Area", title_style))
    story.append(Spacer(1, 10))

    # Section 6.1
    story.append(Paragraph("6.1 Introduction to Perimeter", h2_style))
    story.append(Paragraph(
        "Look at the figures around you: a picture frame, a rectangular table-top, or a football ground. "
        "When we walk around the boundary of a playground, the total distance covered is called its <b>perimeter</b>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Definition:</b> Perimeter is the total distance covered along the boundary forming a closed figure when you go around the figure once.",
        box_style
    ))
    
    # Diagram: Rectangle
    d = Drawing(400, 70)
    d.add(Rect(50, 10, 140, 50, fillColor=colors.HexColor('#E0E7FF'), strokeColor=colors.HexColor('#4338CA'), strokeWidth=1.5))
    d.add(String(100, 65, "Length = 15 cm", fontSize=9, fillColor=colors.HexColor('#1E1B4B')))
    d.add(String(195, 30, "Breadth = 10 cm", fontSize=9, fillColor=colors.HexColor('#1E1B4B')))
    story.append(d)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Perimeter of a Rectangle:</b><br/>Perimeter = Length + Breadth + Length + Breadth = 2 × (Length + Breadth)", body_style))
    story.append(Paragraph("<b>Perimeter of a Square:</b><br/>Perimeter = 4 × Side", body_style))
    story.append(Paragraph("<b>Perimeter of an Equilateral Triangle:</b><br/>Perimeter = 3 × Side", body_style))
    story.append(Spacer(1, 8))

    # Solved Example 1
    story.append(Paragraph("<b>Example 1:</b> Shabana wants to put a lace border all around a rectangular table cover 3 m long and 2 m wide. Find the length of the lace required by Shabana.", body_style))
    story.append(Paragraph(
        "<b>Solution:</b><br/>"
        "Length of rectangular table cover (l) = 3 m<br/>"
        "Breadth of table cover (b) = 2 m<br/>"
        "Length of lace required = Perimeter of table cover<br/>"
        "= 2 × (l + b) = 2 × (3 m + 2 m) = 2 × 5 m = 10 m.<br/>"
        "Therefore, 10 meters of lace is required.",
        box_style
    ))
    
    story.append(PageBreak())

    # Section 6.2
    story.append(Paragraph("6.2 Concept of Area", h2_style))
    story.append(Paragraph(
        "Look at closed figures like squares, triangles and rectangles drawn on paper. "
        "The amount of surface enclosed by a closed figure is called its <b>area</b>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Formulas:</b><br/>"
        "• Area of a Rectangle = Length × Breadth (sq units)<br/>"
        "• Area of a Square = Side × Side (sq units)",
        box_style
    ))
    
    # Diagram: Square
    d2 = Drawing(400, 70)
    d2.add(Rect(50, 10, 50, 50, fillColor=colors.HexColor('#DCFCE7'), strokeColor=colors.HexColor('#15803D'), strokeWidth=1.5))
    d2.add(String(60, 65, "Side = 8 m", fontSize=9, fillColor=colors.HexColor('#14532D')))
    story.append(d2)
    story.append(Spacer(1, 8))

    # Solved Example 2
    story.append(Paragraph("<b>Example 2:</b> Find the area of a square plot of side 8 m.", body_style))
    story.append(Paragraph(
        "<b>Solution:</b><br/>"
        "Side of the square plot = 8 m<br/>"
        "Area of the square = Side × Side = 8 m × 8 m = 64 sq m (or 64 m²).",
        box_style
    ))

    # Solved Example 3
    story.append(Paragraph("<b>Example 3 (Tiling Word Problem):</b> The floor of a room is 4 m long and 3 m wide. How many square tiles of side 50 cm are required to cover the floor?", body_style))
    story.append(Paragraph(
        "<b>Solution:</b><br/>"
        "Length of floor = 4 m = 400 cm<br/>"
        "Breadth of floor = 3 m = 300 cm<br/>"
        "Area of floor = 400 cm × 300 cm = 1,20,000 cm².<br/>"
        "Side of one tile = 50 cm<br/>"
        "Area of one tile = 50 cm × 50 cm = 2,500 cm².<br/>"
        "Number of tiles = (Area of floor) ÷ (Area of one tile) = 1,20,000 ÷ 2,500 = 48 tiles.",
        box_style
    ))

    story.append(Paragraph("6.3 Exercise Questions (Practice)", h2_style))
    exercise_data = [
        ["Q.No", "Question Description", "Marks"],
        ["1", "Find the perimeter of a rectangle whose length is 40 cm and breadth is 10 cm.", "1"],
        ["2", "A square piece of land has side 250 m. Find the cost of fencing it at Rs 20 per meter.", "2"],
        ["3", "The area of a rectangular garden 50 m long is 300 sq m. Find its width.", "2"],
        ["4", "Which has greater area: a square of side 10 cm or a rectangle of 12 cm by 8 cm?", "3"]
    ]
    t = Table(exercise_data, colWidths=[40, 420, 50])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
    ]))
    story.append(t)

    doc.build(story)
    print(f"Created: {pdf_path}")


def build_fractions_pdf():
    pdf_path = SAMPLE_DIR / "ncert_class6_fractions.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0F172A'), spaceAfter=12)
    h2_style = ParagraphStyle('DocH2', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#0284C7'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=6)
    box_style = ParagraphStyle('DocBox', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#0F172A'), backColor=colors.HexColor('#F0F9FF'), borderColor=colors.HexColor('#BAE6FD'), borderWidth=1, borderPadding=8, spaceAfter=8)

    story = []
    story.append(Paragraph("NCERT Mathematics — Class 6", ParagraphStyle('Sub', fontSize=11, textColor=colors.HexColor('#64748B'))))
    story.append(Paragraph("Chapter 7: Fractions", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7.1 What is a Fraction?", h2_style))
    story.append(Paragraph(
        "A fraction means a part of a whole or collection. A whole can be a single object or a group of objects. "
        "The whole must be divided into equal parts. In a fraction <b>a/b</b>, <b>a</b> is the <b>numerator</b> and <b>b</b> is the <b>denominator</b>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Types of Fractions:</b><br/>"
        "• <b>Proper Fraction:</b> Numerator is strictly less than denominator (e.g. 2/3, 5/8). Always &lt; 1.<br/>"
        "• <b>Improper Fraction:</b> Numerator is greater than or equal to denominator (e.g. 7/4, 9/5). Always ≥ 1.<br/>"
        "• <b>Mixed Fraction:</b> A combination of a whole number and a proper fraction (e.g. 1 3/4).",
        box_style
    ))

    story.append(Paragraph("7.2 Equivalent Fractions and Simplest Form", h2_style))
    story.append(Paragraph(
        "To find an equivalent fraction, we may multiply or divide both the numerator and the denominator of a given fraction by the same non-zero number.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Simplest Form:</b> A fraction is said to be in simplest (or lowest) form if its numerator and denominator have no common factor except 1 (i.e. HCF is 1).<br/>"
        "<i>Example:</i> 36/48 = (36 ÷ 12) / (48 ÷ 12) = 3/4.",
        box_style
    ))

    story.append(PageBreak())

    story.append(Paragraph("7.3 Addition and Subtraction of Fractions", h2_style))
    story.append(Paragraph(
        "<b>Like Fractions:</b> Fractions with the same denominator. To add like fractions, add the numerators and keep the common denominator: <b>a/d + b/d = (a + b)/d</b>.<br/>"
        "<b>Unlike Fractions:</b> Fractions with different denominators. Convert them to equivalent fractions with common denominator using LCM, then add or subtract.",
        body_style
    ))

    # Example
    story.append(Paragraph("<b>Example:</b> Sarita bought 2/5 metre of ribbon and Lalita 3/4 metre of ribbon. What was the total length of ribbon they bought?", body_style))
    story.append(Paragraph(
        "<b>Solution:</b><br/>"
        "Length bought by Sarita = 2/5 m<br/>"
        "Length bought by Lalita = 3/4 m<br/>"
        "Total length = 2/5 + 3/4.<br/>"
        "LCM of 5 and 4 is 20.<br/>"
        "2/5 = (2 × 4)/20 = 8/20.<br/>"
        "3/4 = (3 × 5)/20 = 15/20.<br/>"
        "Total = 8/20 + 15/20 = 23/20 = 1 3/20 metres.",
        box_style
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")


def build_worksheet_pdf():
    pdf_path = SAMPLE_DIR / "class6_perimeter_area_worksheet.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1E293B'), spaceAfter=8)
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=6)

    story = [
        Paragraph("Class 6 Mathematics — Practice Worksheet", title_style),
        Paragraph("Topic: Perimeter, Area and Word Applications | Total Marks: 20", body_style),
        Spacer(1, 10)
    ]

    questions = [
        "1. Multiple Choice: The perimeter of a regular pentagon of side 6 cm is: (A) 30 cm (B) 25 cm (C) 36 cm (D) 20 cm [1 Mark]",
        "2. Fill in the Blank: The area of a rectangle is equal to __________ × Breadth. [1 Mark]",
        "3. True/False: If the side of a square is doubled, its perimeter also doubles. [1 Mark]",
        "4. Assertion (A): The perimeter of a square with side 5 cm is 20 cm.<br/>Reason (R): Perimeter of a square is 4 × side. [1 Mark]",
        "5. Numerical: A rectangular piece of land measures 0.7 km by 0.5 km. Each side is to be fenced with 4 rows of wires. What is the length of wire needed? [2 Marks]",
        "6. Short Answer: Find the cost of leveling a square park of side 60 m at the rate of Rs 4 per square meter. [3 Marks]",
        "7. Case Study: An architect is designing a hall of length 15 m and width 10 m.<br/>(i) Find total floor area. [1 Mark]<br/>(ii) If tiles of 1 m × 1 m cost Rs 50 each, find the total cost of tiling. [2 Marks]",
        "8. HOTS: Two sides of a triangle are 12 cm and 14 cm. The perimeter of the triangle is 36 cm. What is its third side? [2 Marks]"
    ]

    for q in questions:
        story.append(Paragraph(q, body_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    print(f"Created: {pdf_path}")


def build_practice_paper_pdf():
    pdf_path = SAMPLE_DIR / "class6_math_practice_paper_sections_a_e.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, alignment=1, textColor=colors.HexColor('#0F172A'), spaceAfter=6)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, leading=14, alignment=1, textColor=colors.HexColor('#475569'), spaceAfter=10)
    sec_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1E3A8A'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=4)

    story = [
        Paragraph("CBSE Class 6 Mathematics — Examination Paper", title_style),
        Paragraph("Time: 2 Hours | Maximum Marks: 40 | Blueprint: Sections A to E", sub_style),
        Spacer(1, 6)
    ]

    # Section A
    story.append(Paragraph("SECTION A (Multiple Choice Questions - 1 Mark Each)", sec_style))
    sec_a = [
        "1. The perimeter of an equilateral triangle of side 9 cm is:<br/>(A) 18 cm &nbsp;&nbsp;&nbsp;&nbsp; (B) 27 cm &nbsp;&nbsp;&nbsp;&nbsp; (C) 36 cm &nbsp;&nbsp;&nbsp;&nbsp; (D) 81 cm",
        "2. Which of the following is a proper fraction?<br/>(A) 7/5 &nbsp;&nbsp;&nbsp;&nbsp; (B) 3/8 &nbsp;&nbsp;&nbsp;&nbsp; (C) 9/4 &nbsp;&nbsp;&nbsp;&nbsp; (D) 11/3",
        "3. The area of a rectangle of length 12 cm and breadth 5 cm is:<br/>(A) 34 cm² &nbsp;&nbsp;&nbsp;&nbsp; (B) 60 cm² &nbsp;&nbsp;&nbsp;&nbsp; (C) 17 cm² &nbsp;&nbsp;&nbsp;&nbsp; (D) 72 cm²",
        "4. Assertion (A): 2/3 and 6/9 are equivalent fractions.<br/>Reason (R): Multiplying numerator and denominator of 2/3 by 3 gives 6/9.<br/>(A) Both A and R are true and R is correct explanation of A.<br/>(B) Both A and R are true but R is not correct explanation.<br/>(C) A is true, R is false.<br/>(D) A is false, R is true."
    ]
    for q in sec_a:
        story.append(Paragraph(q, body_style))
        story.append(Spacer(1, 3))

    # Section B
    story.append(Paragraph("SECTION B (Very Short Answer Questions - 2 Marks Each)", sec_style))
    story.append(Paragraph("5. Find the side of the square whose perimeter is 64 cm.", body_style))
    story.append(Paragraph("6. Reduce 45/60 to its simplest form.", body_style))

    # Section C
    story.append(Paragraph("SECTION C (Short Answer Questions - 3 Marks Each)", sec_style))
    story.append(Paragraph("7. A rectangular park is 20 m long and 15 m wide. A path 2 m wide is constructed all around inside the park. Find the area of the path.", body_style))
    story.append(Paragraph("8. Ramesh had 20 pencils, Sheelu had 50 pencils and Jamaal had 80 pencils. After 4 months, Ramesh used up 10 pencils, Sheelu used up 25 pencils and Jamaal used up 40 pencils. What fraction of pencils did each use up? Check if each has used up an equal fraction.", body_style))

    # Section D
    story.append(Paragraph("SECTION D (Long Answer Questions - 5 Marks Each)", sec_style))
    story.append(Paragraph("9. Five square flower beds each of side 1.2 m are dug on a piece of land 4.8 m long and 4 m wide. What is the area of the remaining part of the land? Also find the cost of turfing the remaining land at Rs 25 per sq meter.", body_style))

    # Section E
    story.append(Paragraph("SECTION E (Case Study Based Problem - 4 Marks)", sec_style))
    story.append(Paragraph(
        "10. <b>Case Study:</b> Priya's school has an athletic ground. The ground consists of a central rectangular field of length 80 m and breadth 50 m, surrounded by a running track.<br/>"
        "Sub-question (i): What is the perimeter of the central rectangular field? [1 Mark]<br/>"
        "Sub-question (ii): What is the area of the central field? [1 Mark]<br/>"
        "Sub-question (iii): If grass is to be planted in the field at Rs 15 per sq m, find the total cost of planting grass. [2 Marks]",
        body_style
    ))

    doc.build(story)
    print(f"Created: {pdf_path}")


if __name__ == "__main__":
    build_perimeter_area_pdf()
    build_fractions_pdf()
    build_worksheet_pdf()
    build_practice_paper_pdf()
