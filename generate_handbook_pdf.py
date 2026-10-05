import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Draws running headers and dynamic 'Page X of Y' footers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, 755, "QueryLearn — Visual System Guide & Oral Defense Handbook")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 755, "Screen-by-Screen Walkthrough")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawRightString(558, 34, footer_text)
        self.drawString(54, 34, "QueryLearn Case Study — Prepared for Research Defense")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        
        self.restoreState()


def build_visual_guide_pdf(output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0F172A")
    c_blue = colors.HexColor("#2563EB")
    c_blue_bg = colors.HexColor("#EFF6FF")
    c_blue_border = colors.HexColor("#BFDBFE")
    c_slate = colors.HexColor("#334155")
    c_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")
    c_green_bg = colors.HexColor("#ECFDF5")
    c_green_border = colors.HexColor("#A7F3D0")
    c_green_text = colors.HexColor("#065F46")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'H1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_blue,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_slate,
        spaceAfter=3
    )

    say_style = ParagraphStyle(
        'SayStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_green_text
    )

    box_text_style = ParagraphStyle(
        'BoxText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E3A8A")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=c_slate
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    def teacher_box(text):
        content = f"<b>🗣️ What you say to your teacher:</b> \"{text}\""
        t = Table([[Paragraph(content, say_style)]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_green_bg),
            ('BOX', (0,0), (-1,-1), 1, c_green_border),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def screen_card(img_path, title, what_it_does, key_elements, teacher_say, img_height=150):
        items = []
        items.append(Paragraph(f"<b>{title}</b>", h1_style))
        items.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))
        
        # Screenshot image wrapped in a styled border table
        if os.path.exists(img_path):
            img = Image(img_path, width=496, height=img_height)
            t_img = Table([[img]], colWidths=[504])
            t_img.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#080C14")),
                ('BOX', (0,0), (-1,-1), 1, c_border),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
            ]))
            items.append(t_img)
            items.append(Spacer(1, 3))
        
        # Details table
        desc_content = f"<b>What this screen does:</b> {what_it_does}<br/><b>Key parts:</b> {key_elements}"
        t_desc = Table([[Paragraph(desc_content, box_text_style)]], colWidths=[504])
        t_desc.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_blue_bg),
            ('BOX', (0,0), (-1,-1), 1, c_blue_border),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        items.append(t_desc)
        items.append(Spacer(1, 3))
        items.append(teacher_box(teacher_say))
        items.append(Spacer(1, 6))
        return KeepTogether(items)

    story = []

    # ==========================================
    # PAGE 1: TITLE & EXECUTIVE SUMMARY
    # ==========================================
    story.append(Paragraph("QueryLearn: Visual System Guide &amp; Defense Handbook", title_style))
    story.append(Paragraph("A Complete Screen-by-Screen Walkthrough with Pictures, Explanations, and Spoken Defense Answers", subtitle_style))

    summary_table = [
        [Paragraph("<b>Project Overview:</b> QueryLearn is an online research lab comparing whether beginner students learn data querying faster and with less frustration using declarative SQL or procedural Python.", body_style),
         Paragraph("<b>Target Learners:</b> College freshmen and novice students with little or no formal database background.", body_style)],
        [Paragraph("<b>Fair Testing Plan:</b> A 2×2 Crossover Design where every student tries both languages in balanced orders to remove intelligence or practice bias.", body_style),
         Paragraph("<b>What Is Measured:</b> Reading comprehension (/18), writing success (%), time spent (s), attempt count, and mental effort ratings.", body_style)]
    ]
    t_sum = Table(summary_table, colWidths=[250, 254])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 8))

    story.append(Paragraph("The Core Comparison: Declarative SQL vs. Procedural Python", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))
    
    comp_data = [
        [Paragraph("<b>Feature</b>", table_header), Paragraph("<b>SQL (Declarative)</b>", table_header), Paragraph("<b>Python (Procedural / Loops)</b>", table_header)],
        [Paragraph("<b>How you think</b>", table_cell), Paragraph("You describe <b>WHAT</b> data you want. The database engine figures out how to fetch it.", table_cell), Paragraph("You describe <b>HOW</b> to get the data, writing every single loop and dictionary step.", table_cell)],
        [Paragraph("<b>Simple filter</b>", table_cell), Paragraph("<code>SELECT name FROM Students WHERE year = 1;</code>", table_cell), Paragraph("<code>for s in students:<br/>&nbsp;&nbsp;if s['year'] == 1: result.append(s['name'])</code>", table_cell)],
        [Paragraph("<b>Joining tables</b>", table_cell), Paragraph("<code>JOIN Courses ON Enrollments.course_id = ...</code>", table_cell), Paragraph("Must build a dictionary lookup or write nested loops by hand.", table_cell)],
        [Paragraph("<b>What we study</b>", table_cell), Paragraph("Do beginners find SQL natural, or do keywords feel like a foreign language?", table_cell), Paragraph("Do beginners prefer Python because they already know loops, or is it too tedious?", table_cell)]
    ]
    t_comp = Table(comp_data, colWidths=[80, 212, 212])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 6))

    story.append(Paragraph("The 6 Relational Task Challenges (T1 to T6)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=4))

    tasks_table = [
        [Paragraph("<b>Task</b>", table_header), Paragraph("<b>Concept</b>", table_header), Paragraph("<b>What the Student Solves</b>", table_header), Paragraph("<b>SQL vs. Python Mapping</b>", table_header)],
        [Paragraph("<b>T1</b>", table_cell), Paragraph("Selection &amp; Filtering", table_cell), Paragraph("Find all 2nd-year BSIT students.", table_cell), Paragraph("<code>WHERE program='BSIT' AND year=2</code> vs. loop filter", table_cell)],
        [Paragraph("<b>T2</b>", table_cell), Paragraph("Sorting &amp; Limiting", table_cell), Paragraph("Get top 3 scores in course C102 (ignore empty scores).", table_cell), Paragraph("<code>IS NOT NULL, ORDER BY DESC, LIMIT 3</code> vs. <code>[:3]</code> slice", table_cell)],
        [Paragraph("<b>T3</b>", table_cell), Paragraph("Grouping &amp; Counting", table_cell), Paragraph("Count total students enrolled in each program.", table_cell), Paragraph("<code>GROUP BY program, COUNT(*)</code> vs. dictionary counter", table_cell)],
        [Paragraph("<b>T4</b>", table_cell), Paragraph("Joining Tables", table_cell), Paragraph("Show student name and course name together.", table_cell), Paragraph("<code>INNER JOIN</code> across tables vs. dictionary index lookup", table_cell)],
        [Paragraph("<b>T5</b>", table_cell), Paragraph("Average per Group", table_cell), Paragraph("Find courses with average score 85.0 or higher.", table_cell), Paragraph("<code>GROUP BY ... HAVING AVG() &gt;= 85</code> vs. dict-of-lists mean", table_cell)],
        [Paragraph("<b>T6</b>", table_cell), Paragraph("Records With No Match", table_cell), Paragraph("Find students who have zero enrollments.", table_cell), Paragraph("<code>LEFT JOIN ... WHERE id IS NULL</code> vs. set difference", table_cell)]
    ]
    t_tasks = Table(tasks_table, colWidths=[30, 95, 175, 204])
    t_tasks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tasks)
    story.append(Spacer(1, 6))
    story.append(teacher_box("QueryLearn tests the core operations of relational databases: filtering, sorting, grouping, joining, aggregations, and anti-joins. Both languages solve the exact same tasks so the comparison is 100% fair."))

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: SCREENS 1 & 2
    # ==========================================
    story.append(screen_card(
        img_path="screenshots/01_homepage.png",
        title="Screen 1: Landing Page (The Welcome Screen)",
        what_it_does="Welcomes participants, explains the study overview, and provides clear buttons for students to start the test or researchers to sign in to the dashboard.",
        key_elements="Large 'Start Evaluation' button for students, 'Researcher Login' for administrators, and 3 feature summary cards explaining the timed tasks and automatic grading.",
        teacher_say="This is the entrance portal. Students click 'Start Evaluation' to register anonymously, while researchers use the login to access real-time analytics and CSV exports.",
        img_height=140
    ))

    story.append(screen_card(
        img_path="screenshots/02_register.png",
        title="Screen 2: Registration &amp; Ethics Consent Wizard",
        what_it_does="Collects student background (program, year level, prior SQL and Python experience) and presents official ethics consent before assigning an anonymous Study ID.",
        key_elements="Program dropdown (BSCS, BSIT, BSIS), experience selectors, ethics agreement checkbox, and automatic assignment to a balanced testing sequence (Sequences 1 to 4).",
        teacher_say="We protect student privacy by generating an anonymous Study ID (like P001 or P017). Students are automatically assigned to one of four balanced sequences so condition ordering is counterbalanced.",
        img_height=140
    ))

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: SCREENS 3 & 4
    # ==========================================
    story.append(screen_card(
        img_path="screenshots/03_instructions.png",
        title="Screen 3: Language Reference Guide (The Study Guide)",
        what_it_does="Teaches the 6 necessary coding patterns in both SQL and Python with plain-English summaries before the timed evaluation starts.",
        key_elements="Tab buttons to switch between SQL and Python, syntax-highlighted code blocks, and a one-sentence 'What it does' summary under every example.",
        teacher_say="To ensure complete fairness, the guide uses an isolated university catalog schema (Courses and Departments) that never appears in actual tasks, teaching the rules without giving away any answers.",
        img_height=145
    ))

    story.append(screen_card(
        img_path="screenshots/05_comprehension.png",
        title="Screen 4: Code Comprehension Assessment (Reading Test)",
        what_it_does="Tests reading comprehension before code writing. Students inspect 6 code snippets and answer: (1) what the code does (0-2 pts) and (2) what output it produces (0-1 pt).",
        key_elements="Read-only code window, multiple-choice explanation radio buttons, multiple-choice output prediction, 3-minute automatic countdown timer, and 18 points maximum score.",
        teacher_say="Reading code is a distinct skill from writing code. We test comprehension first so we can measure mental readability independently of typing speed or syntax typos.",
        img_height=145
    ))

    story.append(PageBreak())

    # ==========================================
    # PAGE 4: SCREENS 5 & 6
    # ==========================================
    story.append(screen_card(
        img_path="screenshots/06_task_sql.png",
        title="Screen 5: SQL Task Workspace (The Writing Test)",
        what_it_does="The live workspace where students write SQL queries for Tasks 1 to 6. Code runs against SQLite with instant output tables and automated test validation.",
        key_elements="8-minute countdown timer, attempt counter (1/5), task requirements, collapsible schema tree, collapsible 'Need Help?' quick reference, CodeMirror SQL editor, Run button, and Submit button.",
        teacher_say="The workspace provides real-time feedback. When students click Run, their query executes safely. When they click Submit, their code is validated against 3 hidden test databases with edge cases.",
        img_height=145
    ))

    story.append(screen_card(
        img_path="screenshots/07_task_python.png",
        title="Screen 6: Procedural Python Task Workspace",
        what_it_does="The counterpart workspace for Python tasks. Pre-injects in-memory data structures (students, courses, enrollments) so students can write pure data manipulation logic.",
        key_elements="Identical 8-minute timer, attempt counter, data structure reference, Python CodeMirror editor, starter template code, and console output panel.",
        teacher_say="The Python workspace uses the exact same layout, timer, and attempt limits as SQL. This ensures that the only variable being tested is the programming language itself.",
        img_height=145
    ))

    story.append(PageBreak())

    # ==========================================
    # PAGE 5: SCREENS 7 & 8
    # ==========================================
    story.append(screen_card(
        img_path="screenshots/08_survey.png",
        title="Screen 7: Post-Task Feedback Survey (Cognitive Ratings)",
        what_it_does="Measures student experience immediately after finishing each language: 5 agreement items on readability and debugging, mental effort, fatigue, and written comments.",
        key_elements="Symmetrical 5-column Likert scale (1=Strongly Disagree to 5=Strongly Agree), separated 'Not applicable' option, 1-5 mental effort rating, 1-5 fatigue rating, and qualitative textareas.",
        teacher_say="We capture subjective cognitive load right after the tasks while it is fresh in the student's mind. 'Not applicable' is stored as NULL so it does not distort statistical numerical averages.",
        img_height=145
    ))

    story.append(screen_card(
        img_path="screenshots/09_dashboard.png",
        title="Screen 8: Researcher Analytics Dashboard",
        what_it_does="The secure administrative portal showing live telemetry, comparative statistics between SQL and Python, completion rates, and raw CSV data downloads.",
        key_elements="Comparative Productivity Summary, Median Comprehension Score out of 18, Task Success Rate charts, participant registry, and one-click CSV export buttons for statistical packages.",
        teacher_say="The dashboard gives researchers complete visibility. It calculates medians, tracks time-on-task, and exports raw data for statistical analysis in SPSS or R.",
        img_height=145
    ))

    story.append(PageBreak())

    # ==========================================
    # PAGE 6: DEFENSE Q&A CHEAT SHEET
    # ==========================================
    story.append(Paragraph("Oral Defense Cheat Sheet: Top 10 Questions Your Teachers Will Ask", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))
    story.append(Paragraph("Study these 10 questions and speak the green answers clearly during your defense presentation:", body_style))
    story.append(Spacer(1, 3))

    qa_simple = [
        ("1. 'Why did you build a web app instead of just giving students Google Forms or paper?'",
         "Because a web app records exact millisecond typing time, tracks every failed attempt, executes code safely in a sandbox, and auto-grades solutions against edge cases without human bias."),

        ("2. 'How can freshmen or students with zero experience answer these tasks?'",
         "We provided three beginner scaffolds: (1) a Reference Guide with plain-English summaries, (2) an untimed practice sandbox with a readiness check, and (3) a collapsible 'Need Help?' quick reference box inside the task window. All references use fake course data so they don't give away task answers."),

        ("3. 'What if a student just guesses or hardcodes the answer like print([1, 2, 3])?'",
         "They cannot cheat! The system tests their code against hidden test datasets with edge cases (like tie scores, missing values, and empty rows). If their code does not genuinely calculate the right logic, it fails automatically."),

        ("4. 'What are the main metrics or numbers you are collecting?'",
         "We collect four primary numbers: (1) Reading score (out of 18), (2) Task success rate (percentage solved), (3) Time spent solving each task (seconds), and (4) Number of attempts (from 1 to 5). We also collect self-reported mental effort and fatigue ratings."),

        ("5. 'Why do you test code comprehension before task writing?'",
         "Because reading and writing are two different cognitive skills. Testing comprehension first lets us measure how easily a beginner understands the syntax before they have to worry about typing speed or syntax typos."),

        ("6. 'Why does each task have an 8-minute timer?'",
         "To keep the experiment controlled and standardized. If there were no timer, one student might spend 40 minutes on one task, which ruins the time comparison and exhausts the participant."),

        ("7. 'What happens if the timer runs out before they finish?'",
         "The app automatically saves whatever they did, marks the task as timed out, and smoothly moves them to the next task so they don't get stuck forever."),

        ("8. 'Why is Python longer than SQL for tasks 4, 5, and 6?'",
         "Because SQL has built-in database keywords like JOIN and GROUP BY, while in Python you have to manually build dictionaries, compute sums, and check set memberships. That difference in difficulty is exactly what this study is measuring!"),

        ("9. 'How do you keep participant identities anonymous?'",
         "Students never type their real name. The system assigns an anonymous Study ID (like P001, P002, P017). All research data and exports only use that ID, keeping participant privacy 100% protected."),

        ("10. 'What will you do with the final data collected in the dashboard?'",
         "We export the data as clean CSV files and run standard statistical tests (like Wilcoxon paired tests for ratings and paired t-tests for task times) to prove whether SQL or Python was statistically significantly better.")
    ]

    for q, a in qa_simple:
        story.append(KeepTogether([
            Paragraph(f"<b>{q}</b>", h2_style),
            teacher_box(a),
            Spacer(1, 2)
        ]))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Visual Guide PDF successfully created at: {output_filename}")


if __name__ == '__main__':
    target = os.path.join(r"C:\Users\USER\.gemini\antigravity\scratch\querylearn", "QueryLearn_System_Guide_and_Defense_Handbook.pdf")
    build_visual_guide_pdf(target)
