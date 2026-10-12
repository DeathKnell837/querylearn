import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header line
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 755, letter[0] - 40, 755)
        self.drawString(40, 760, "QueryLearn — Presentation & Defense Cheat Sheet")
        
        # Footer
        self.line(40, 42, letter[0] - 40, 42)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 30, page_text)
        self.drawString(40, 30, "Notre Dame of Midsayap College • BSCS / BSIT Case Study")
        self.restoreState()

def build_defense_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#0f172a")
    )

    script_style = ParagraphStyle(
        'SayThis',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=2,
        spaceAfter=4
    )

    tag_style = ParagraphStyle(
        'Tag',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0284c7")
    )

    story = []

    # Title Banner
    story.append(Paragraph("QueryLearn: Defense & Presentation Guide", title_style))
    story.append(Paragraph("<b>Simple Student Edition</b> • Everything You Need to Know for Your Defense in Plain Words", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # SECTION 1: 2-MINUTE SYSTEM EXPLANATION
    story.append(Paragraph("1. System Overview: What is QueryLearn? (In Simple Words)", h1_style))
    
    desc_text = (
        "<b>What is it?</b> QueryLearn is an online web platform built for our case study. "
        "Its main job is to measure and compare how computer students write and read data queries using two different languages: "
        "<b>SQL</b> (database queries) vs. <b>Python</b> (step-by-step code loops)."
    )
    story.append(Paragraph(desc_text, body_style))

    why_text = (
        "<b>Why did we build this?</b> In college (BSCS and BSIT), students learn both SQL and Python. "
        "SQL tells the database <i>what</i> you want (e.g., <code>SELECT name WHERE score >= 80</code>), "
        "while Python requires you to write loops and check conditions line by line. "
        "We wanted to see which language is faster, easier to understand, and causes fewer headaches for student beginners."
    )
    story.append(Paragraph(why_text, body_style))

    # How it works table
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>How a Student Uses the System (Step-by-Step Flow):</b>", body_bold))
    
    flow_data = [
        [Paragraph("<b>Step</b>", body_bold), Paragraph("<b>What Happens</b>", body_bold), Paragraph("<b>Why It's There</b>", body_bold)],
        [
            Paragraph("1. Registration", body_style),
            Paragraph("Student registers with their Program (BSCS/BSIT) and Year Level (2nd, 3rd, 4th). They get a private Study ID (like P001, P002).", body_style),
            Paragraph("Keeps data anonymous and makes sure freshmen are excluded (because SQL starts in 2nd year).", body_style)
        ],
        [
            Paragraph("2. Language Guide", body_style),
            Paragraph("Shows a simple reference sheet for SQL commands and Python syntax with clear examples.", body_style),
            Paragraph("Makes sure every student has a fair refresher before they start.", body_style)
        ],
        [
            Paragraph("3. Readiness Quiz", body_style),
            Paragraph("A 2-question quick check to confirm they understand what SELECT and for-loops do.", body_style),
            Paragraph("Verifies that the student is ready to take the evaluation.", body_style)
        ],
        [
            Paragraph("4. Reading Test (Comprehension)", body_style),
            Paragraph("Students look at 6 short code snippets and predict what the output will be (scored 0 to 18 points).", body_style),
            Paragraph("Measures <b>code readability</b> — is SQL or Python easier to read without running it?", body_style)
        ],
        [
            Paragraph("5. The 6 Timed Coding Tasks", body_style),
            Paragraph("Students solve 6 data problems with an 8-minute countdown timer per task. An auto-grader checks their output.", body_style),
            Paragraph("Measures <b>productivity & accuracy</b> — how fast and correctly students write queries.", body_style)
        ],
        [
            Paragraph("6. Student Survey", body_style),
            Paragraph("Students rate their experience (1-5 scale) on ease of use, mental effort, and fatigue.", body_style),
            Paragraph("Captures student feedback and preferences.", body_style)
        ]
    ]

    t_flow = Table(flow_data, colWidths=[110, 260, 160])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_flow)

    story.append(Spacer(1, 10))

    # SECTION 2: THE 6 TASKS EXPLAINED
    story.append(Paragraph("2. The 6 Coding Tasks: What Did Students Solve?", h1_style))
    tasks_intro = (
        "Both SQL and Python used identical student database scenarios (Students, Courses, and Enrollments tables). "
        "The 6 tasks tested different levels of database skills from simple to complex:"
    )
    story.append(Paragraph(tasks_intro, body_style))

    task_table_data = [
        [Paragraph("<b>Task ID</b>", body_bold), Paragraph("<b>What the Student Had to Do</b>", body_bold), Paragraph("<b>Difficulty / Skill Tested</b>", body_bold)],
        [Paragraph("T1", body_bold), Paragraph("Find all 2nd-year BSCS students and sort them by student ID.", body_style), Paragraph("Basic filtering & sorting (WHERE & ORDER BY)", body_style)],
        [Paragraph("T2", body_bold), Paragraph("Find the top 3 highest scores in course C101 (skipping blank scores).", body_style), Paragraph("Ordering and picking top rows (LIMIT & NULL check)", body_style)],
        [Paragraph("T3", body_bold), Paragraph("Count how many students are in each academic program (BSCS, BSIT, etc.).", body_style), Paragraph("Group counting (GROUP BY & COUNT)", body_style)],
        [Paragraph("T4", body_bold), Paragraph("Combine 3 tables to show student names and the courses they are taking.", body_style), Paragraph("Connecting tables together (INNER JOIN)", body_style)],
        [Paragraph("T5", body_bold), Paragraph("Find courses with an average grade of 80 or higher.", body_style), Paragraph("Filtering grouped averages (HAVING clause)", body_style)],
        [Paragraph("T6", body_bold), Paragraph("Find students who have NEVER enrolled in any course.", body_style), Paragraph("Finding missing records (LEFT JOIN ... IS NULL)", body_style)]
    ]
    t_tasks = Table(task_table_data, colWidths=[60, 270, 200])
    t_tasks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_tasks)

    story.append(PageBreak())

    # SECTION 3: THE NUMBERS & RESULTS (MATCHING THE PAPER)
    story.append(Paragraph("3. Study Findings: What Did the Results Prove?", h1_style))
    story.append(Paragraph(
        "Our study evaluated <b>28 student participants ($n = 28$)</b> across 168 total task attempts per language. "
        "Here are the core findings and what each number means:", body_style
    ))

    res_table_data = [
        [Paragraph("<b>Key Metric</b>", body_bold), Paragraph("<b>SQL</b>", body_bold), Paragraph("<b>Python</b>", body_bold), Paragraph("<b>What This Means in Plain Words</b>", body_bold)],
        [
            Paragraph("<b>Speed (Time to Finish)</b>", body_style),
            Paragraph("<b>103.8 seconds</b>", body_bold),
            Paragraph("184.8 seconds", body_style),
            Paragraph("<b>SQL was ~81 seconds faster.</b> Writing a SQL query took nearly half the time of writing nested Python loops.", body_style)
        ],
        [
            Paragraph("<b>Tasks Done per Hour</b>", body_style),
            Paragraph("<b>28.2 tasks/hr</b>", body_bold),
            Paragraph("18.4 tasks/hr", body_style),
            Paragraph("<b>SQL has much higher productivity.</b> Students can solve roughly 10 more problems every hour using SQL.", body_style)
        ],
        [
            Paragraph("<b>Reading Test Score (Comprehension)</b>", body_style),
            Paragraph("<b>16.0 / 18 pts</b> (78.2%)", body_bold),
            Paragraph("11.0 / 18 pts (63.9%)", body_style),
            Paragraph("<b>SQL is significantly easier to read and predict.</b> Students immediately understood SQL clauses without needing mental simulation.", body_style)
        ],
        [
            Paragraph("<b>Task Success Rate (Correctness)</b>", body_style),
            Paragraph("83.3% (140/168)", body_style),
            Paragraph("<b>89.9% (151/168)</b>", body_bold),
            Paragraph("Python had slightly higher raw accuracy (+6.6%). Why? Because students took much longer writing and double-checking loops. The difference was not statistically significant.", body_style)
        ],
        [
            Paragraph("<b>T6 (Finding Missing Records)</b>", body_style),
            Paragraph("<b>100% correct</b>", body_bold),
            Paragraph("80% correct", body_style),
            Paragraph("Writing anti-joins in Python confused students (managing sets vs list of dicts), while SQL's <code>LEFT JOIN</code> was easy.", body_style)
        ]
    ]
    t_res = Table(res_table_data, colWidths=[120, 95, 95, 220])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_res)

    story.append(Spacer(1, 10))

    # SECTION 4: STEP-BY-STEP PRESENTATION SCRIPT
    story.append(Paragraph("4. Step-by-Step Defense Script (Word-for-Word Speaking Guide)", h1_style))
    story.append(Paragraph("Read these sections out loud when presenting to your teacher. Practice them once or twice:", body_style))

    # Script Step 1
    script_box_1 = [
        [Paragraph("<b>PART 1: GREETING & INTRODUCTION (30 SECONDS)</b>", tag_style)],
        [Paragraph(
            "\"Good morning/afternoon, Sir/Ma'am. Today, I am presenting our case study project called <b>QueryLearn</b>.<br/><br/>"
            "QueryLearn is an online evaluation platform that compares how student developers read and write database queries "
            "using two different approaches: <b>SQL</b> versus <b>procedural Python</b>.<br/><br/>"
            "As computing students, we are taught both languages for data handling. Our goal with QueryLearn was to conduct "
            "an objective case study to find out which language is faster, easier to understand, and more efficient for students "
            "solving everyday data retrieval tasks.\"",
            script_style
        )]
    ]
    t_sb1 = Table(script_box_1, colWidths=[530])
    t_sb1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#22c55e")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sb1)
    story.append(Spacer(1, 8))

    # Script Step 2
    script_box_2 = [
        [Paragraph("<b>PART 2: SYSTEM ARCHITECTURE & DEMO (1 MINUTE)</b>", tag_style)],
        [Paragraph(
            "\"Let me give you a quick walkthrough of how the system works:<br/><br/>"
            "1. <b>Registration:</b> Students sign up with their year level and course. First-year students are excluded because database instruction starts in 2nd year.<br/>"
            "2. <b>Fair Order (Counterbalancing):</b> To be fair, half of the students do SQL first, and the other half do Python first. This prevents any order bias.<br/>"
            "3. <b>Reading Comprehension Test:</b> Before coding, students predict the output of 6 code snippets. This measures code readability.<br/>"
            "4. <b>Coding Tasks:</b> In the workspace, students write queries for 6 standard tasks under an 8-minute timer. Our automated grading engine checks their output against hidden datasets in real time.<br/>"
            "5. <b>Cloud Database & Dashboard:</b> All attempts, execution times, and survey answers are stored in a cloud database (Supabase) and synced so the researcher dashboard can display live analytics.\"",
            script_style
        )]
    ]
    t_sb2 = Table(script_box_2, colWidths=[530])
    t_sb2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3b82f6")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sb2)

    story.append(PageBreak())

    # Script Step 3
    script_box_3 = [
        [Paragraph("<b>PART 3: EXPLAINING THE FINDINGS & CHARTS (1.5 MINUTES)</b>", tag_style)],
        [Paragraph(
            "\"Now, looking at our live dashboard and results from the 28 participants:<br/><br/>"
            "• <b>First, on Writing Speed:</b> SQL was clearly faster. The average time to reach a correct solution in SQL was <b>103.8 seconds</b>, compared to <b>184.8 seconds</b> in Python. That means SQL was about 81 seconds faster per task, giving SQL a <b>1.82x speed advantage</b>.<br/><br/>"
            "• <b>Second, on Productivity:</b> Students completed <b>28.2 tasks per hour in SQL</b> versus only <b>18.4 tasks per hour in Python</b>. SQL allowed students to get nearly 10 more tasks done per hour.<br/><br/>"
            "• <b>Third, on Readability:</b> In the comprehension test, SQL had an average score of <b>16.0 out of 18</b> (78.2%), while Python had <b>11.0 out of 18</b> (63.9%). Students found SQL significantly easier to read and predict without running the code.<br/><br/>"
            "• <b>Fourth, on Accuracy:</b> Python had a slightly higher raw success rate (89.9% vs 83.3%), but this was because students spent much more time carefully debugging their loops. However, on complex operations like Task 6 (anti-joins), all students got SQL right (100%), while only 80% succeeded in Python.\"",
            script_style
        )]
    ]
    t_sb3 = Table(script_box_3, colWidths=[530])
    t_sb3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#faf5ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#a855f7")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sb3)
    story.append(Spacer(1, 8))

    # Script Step 4
    script_box_4 = [
        [Paragraph("<b>PART 4: CONCLUSION & RECOMMENDATION (30 SECONDS)</b>", tag_style)],
        [Paragraph(
            "\"In conclusion, our case study proves that for relational data retrieval, <b>SQL offers superior productivity, faster completion times, and higher code readability</b> for student learners. While Python is powerful for general programming, having to write manual loops and dictionary lookups slows down query formulation.<br/><br/>"
            "We recommend that educational curricula introduce SQL early for database querying, while positioning Python as an analytical tool that processes data after it has been retrieved via SQL.<br/><br/>"
            "Thank you, Sir/Ma'am! I am now ready to answer any questions you may have.\"",
            script_style
        )]
    ]
    t_sb4 = Table(script_box_4, colWidths=[530])
    t_sb4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fffbeb")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#f59e0b")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sb4)

    story.append(Spacer(1, 12))

    # SECTION 5: ANTICIPATED TEACHER QUESTIONS (Q&A CHEAT SHEET)
    story.append(Paragraph("5. Anticipated Teacher Questions & Exact Answers (Q&A Cheat Sheet)", h1_style))
    story.append(Paragraph("Your teacher might ask these common questions during your defense. Here is exactly what to say:", body_style))

    qa_list = [
        (
            "Q1: Why did you compare SQL and Python? Aren't they used for different purposes?",
            "\"Sir/Ma'am, in modern data science and software development, developers often manipulate tabular data using both SQL queries and Python scripts (like list/dict operations or Pandas). We wanted to see whether students grasp declarative queries (SQL) faster than procedural logic (Python loops) when handling the exact same dataset.\""
        ),
        (
            "Q2: Why did Python have an 89.9% accuracy rate while SQL had 83.3%?",
            "\"That is a great observation, Sir/Ma'am. Students spent much longer in Python (averaging 184 seconds compared to 103 seconds in SQL). Because they spent more time writing and testing loops, slightly more students eventually solved the tasks. However, this difference of 6.6% was not statistically significant (p = 0.366), whereas SQL was statistically significantly faster in speed and tasks per hour.\""
        ),
        (
            "Q3: Why are freshmen (1st Year) excluded from the study?",
            "\"In our college curriculum, formal database management and SQL instruction begin in the second year. First-year students have not yet taken a database course, so including them would skew the results toward zero SQL familiarity.\""
        ),
        (
            "Q4: How does the system grade students automatically?",
            "\"When a student clicks 'Submit', the system runs their code in a sandboxed runner and compares their table output against expected test datasets. If their column names, rows, and values match the hidden test key, it automatically marks it correct; otherwise, it records the error message and lets them retry until the 8-minute timer expires.\""
        ),
        (
            "Q5: What technology stack does QueryLearn use?",
            "\"The frontend uses HTML, CSS, JavaScript, and Chart.js for interactive charts. The backend is built with Python Flask and hosted on Vercel. For database storage, we use SQLite for local execution and Supabase (PostgreSQL) in the cloud to sync participant results across different computers in real time.\""
        ),
        (
            "Q6: Why did you use counterbalancing (Sequence 1 to 4)?",
            "\"If all students did SQL first and then Python, they might do better in Python simply because they already saw the problem in SQL (called a 'learning effect'). By having half the students start with SQL and the other half start with Python, the study remains fair and unbiased.\""
        )
    ]

    for q, a in qa_list:
        qa_data = [
            [Paragraph(f"<b>{q}</b>", body_bold)],
            [Paragraph(f"<b>What to Answer:</b> {a}", script_style)]
        ]
        t_qa = Table(qa_data, colWidths=[530])
        t_qa.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_qa)
        story.append(Spacer(1, 4))

    doc.build(story, canvasmaker=NumberedCanvas)
    return True

if __name__ == '__main__':
    desktop = os.path.expanduser('~/Desktop')
    out_desktop = os.path.join(desktop, 'QueryLearn_Defense_Presentation_Script.pdf')
    out_local = os.path.join(os.getcwd(), 'QueryLearn_Defense_Presentation_Script.pdf')
    
    print(f"Generating PDF to Desktop: {out_desktop}")
    build_defense_pdf(out_desktop)
    
    print(f"Generating local copy: {out_local}")
    build_defense_pdf(out_local)
    
    print("SUCCESS!")
