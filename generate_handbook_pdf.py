import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute total page count."""
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
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "QueryLearn — System Architecture & Oral Defense Handbook")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential — Prepared for Academic Research Defense")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def create_handbook(output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom color palette
    primary_color = colors.HexColor("#0F172A")
    brand_blue = colors.HexColor("#1D4ED8")
    slate_dark = colors.HexColor("#334155")
    slate_light = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#475569")
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13.5,
        leading=17.5,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=brand_blue,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=slate_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=2.5
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )

    qa_q_style = ParagraphStyle(
        'QA_Q',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QA_A',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=slate_dark,
        spaceAfter=6
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=slate_dark
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ==========================
    # HEADER / METADATA
    # ==========================
    story.append(Paragraph("QueryLearn: System Architecture &amp; Defense Handbook", title_style))
    story.append(Paragraph("A Complete Guide to Experimental Design, System Workflow, Methodology, and Defense Q&amp;A", subtitle_style))
    
    meta_box = [
        [Paragraph("<b>Target Domain:</b> Novice Database Querying (SQL vs. Procedural Python)", meta_style),
         Paragraph("<b>Study Design:</b> 2×2 Crossover Counterbalanced Latin Square", meta_style)],
        [Paragraph("<b>Primary Metrics:</b> Comprehension (/18), Success (%), Time (s), Attempts", meta_style),
         Paragraph("<b>Architecture:</b> Flask / SQLite / CodeMirror / Serverless Vercel", meta_style)]
    ]
    t_meta = Table(meta_box, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), slate_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 1: RESEARCH BACKGROUND
    # ==========================
    story.append(Paragraph("1. Research Background &amp; Core Problem", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_blue, spaceBefore=1, spaceAfter=6))
    
    story.append(Paragraph(
        "<b>The Core Research Question:</b> In computer science education, what is the more effective cognitive and practical pathway for novice students to manipulate structured data: <b>declarative SQL</b> or <b>procedural Python</b>?",
        body_style
    ))
    story.append(Paragraph(
        "Novice students often encounter a steep cognitive barrier when learning relational databases. While SQL requires learners to express <i>what</i> data they need declaratively without specifying algorithmic steps, general-purpose procedural languages like Python require specifying <i>how</i> step-by-step (loops, conditionals, hash maps).",
        body_style
    ))
    story.append(Paragraph(
        "<b>QueryLearn</b> was developed as a standardized, automated, and empirically rigorous research instrument to test this comparison under controlled conditions with novice and beginner learners.",
        body_style
    ))
    
    # RQs Callout
    rq_text = """
    <b>Key Research Questions (RQs):</b><br/>
    • <b>RQ1 (Comprehension &amp; Readability):</b> Do novices demonstrate higher accuracy in interpreting query logic and predicting output values when reading SQL compared to procedural Python?<br/>
    • <b>RQ2 (Task Productivity &amp; Writing):</b> Which paradigm yields higher task completion rates, shorter problem-solving time, and fewer error-correction attempts?<br/>
    • <b>RQ3 (Subjective Cognitive Load):</b> Which paradigm generates lower self-reported mental effort, lower task fatigue, and higher perceived confidence among beginners?
    """
    t_rq = Table([[Paragraph(rq_text, callout_style)]], colWidths=[504])
    t_rq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_rq)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 2: EXPERIMENTAL DESIGN
    # ==========================
    story.append(Paragraph("2. Experimental Methodology &amp; Counterbalancing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_blue, spaceBefore=1, spaceAfter=6))
    
    story.append(Paragraph(
        "To ensure unbiased results, the experiment uses a <b>2×2 Crossover (Counterbalanced Latin Square) within-subjects design</b>. Every participant experiences both language conditions, but in balanced sequences to cancel out order and learning bias:",
        body_style
    ))

    seq_data = [
        [Paragraph("<b>Sequence</b>", table_header), Paragraph("<b>First Condition (Step 1)</b>", table_header), Paragraph("<b>Second Condition (Step 2)</b>", table_header), Paragraph("<b>Purpose / Balance</b>", table_header)],
        [Paragraph("Sequence 1", table_cell), Paragraph("SQL (Form A)", table_cell), Paragraph("Python (Form B)", table_cell), Paragraph("SQL-first baseline", table_cell)],
        [Paragraph("Sequence 2", table_cell), Paragraph("Python (Form A)", table_cell), Paragraph("SQL (Form B)", table_cell), Paragraph("Python-first baseline", table_cell)],
        [Paragraph("Sequence 3", table_cell), Paragraph("SQL (Form B)", table_cell), Paragraph("Python (Form A)", table_cell), Paragraph("Controls form ordering", table_cell)],
        [Paragraph("Sequence 4", table_cell), Paragraph("Python (Form B)", table_cell), Paragraph("SQL (Form A)", table_cell), Paragraph("Controls form ordering", table_cell)]
    ]
    t_seq = Table(seq_data, colWidths=[70, 140, 140, 154])
    t_seq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), brand_blue),
        ('BACKGROUND', (0,1), (-1,-1), slate_light),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_seq)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Why Is This Design Essential for Your Research?</b>", h2_style))
    story.append(Paragraph("• <b>Elimination of Order Effects:</b> If everyone did SQL first and then Python, Python might look artificially easier simply because students had already seen the task logic.", bullet_style))
    story.append(Paragraph("• <b>Form Isomorphism (Form A vs Form B):</b> Form A and Form B test identical relational concepts with identical structural complexity, but use different student records, course names, and threshold boundaries (Form A uses BSCS / threshold 80.0; Form B uses BSIT / threshold 85.0).", bullet_style))
    story.append(Paragraph("• <b>Round-Robin Assignment:</b> Participants are sequentially assigned to sequences 1–4 so group sizes remain balanced.", bullet_style))
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 3: THE 6 TASK FAMILIES
    # ==========================
    story.append(Paragraph("3. The 6 Task Families (T1 to T6)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_blue, spaceBefore=1, spaceAfter=6))
    
    story.append(Paragraph(
        "Each condition tests 6 representative query challenges spanning standard relational algebra operations:",
        body_style
    ))

    task_data = [
        [Paragraph("<b>Task</b>", table_header), Paragraph("<b>Relational Concept</b>", table_header), Paragraph("<b>SQL Construct</b>", table_header), Paragraph("<b>Python Procedural Construct</b>", table_header)],
        [Paragraph("<b>T1</b>", table_cell), Paragraph("Selection &amp; Filtering", table_cell), Paragraph("SELECT ... WHERE with AND, ORDER BY", table_cell), Paragraph("for loop / comprehension filtering on dict keys", table_cell)],
        [Paragraph("<b>T2</b>", table_cell), Paragraph("Sort, Limit &amp; Nulls", table_cell), Paragraph("WHERE score IS NOT NULL, ORDER BY composite, LIMIT 3", table_cell), Paragraph("None checks, tuple sort key <code>(-score, id)</code>, slice <code>[:3]</code>", table_cell)],
        [Paragraph("<b>T3</b>", table_cell), Paragraph("Grouping &amp; Counting", table_cell), Paragraph("GROUP BY program, COUNT(*)", table_cell), Paragraph("Dictionary frequency count accumulator", table_cell)],
        [Paragraph("<b>T4</b>", table_cell), Paragraph("Relational Joins", table_cell), Paragraph("INNER JOIN across Students, Enrollments, Courses", table_cell), Paragraph("Nested loop or dictionary lookup index", table_cell)],
        [Paragraph("<b>T5</b>", table_cell), Paragraph("Group Aggregation", table_cell), Paragraph("GROUP BY ... HAVING AVG(score) >= threshold", table_cell), Paragraph("Dict-of-lists accumulator, round(sum/len), threshold filter", table_cell)],
        [Paragraph("<b>T6</b>", table_cell), Paragraph("Records With No Match", table_cell), Paragraph("LEFT JOIN ... WHERE Enrollments.student_id IS NULL", table_cell), Paragraph("Set difference / membership: <code>id not in active_ids</code>", table_cell)]
    ]
    t_task = Table(task_data, colWidths=[34, 110, 180, 180])
    t_task.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, slate_light]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_task)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # ==========================
    # SECTION 4: SYSTEM WORKFLOW
    # ==========================
    story.append(Paragraph("4. Complete Participant Workflow (Step-by-Step)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_blue, spaceBefore=1, spaceAfter=6))

    story.append(Paragraph("When a participant enters QueryLearn, they progress through 8 controlled stages:", body_style))

    steps = [
        ("Step 1: Registration &amp; Ethics Consent",
         "Captures academic program (BSCS/BSIT/BSIS), year level, programming background, prior database courses. Displays research protocol and obtains informed consent. Generates an <b>anonymous Study ID</b> (e.g. P001) and round-robin sequence assignment."),
        
        ("Step 2: Language Reference Guide",
         "Presents equivalent SQL and Python constructs side-by-side. <b>Crucial Control:</b> To prevent learning task answers in advance, the guide uses an isolated university catalog schema (<code>Departments</code> and <code>Courses</code>) that never appears in actual tasks."),
        
        ("Step 3: Practice Sandbox &amp; Gatekeeper Check",
         "Includes 2 un-timed, un-scored practice exercises so participants familiarize themselves with the editor. A 2-question <b>Readiness Verification</b> ensures participants actually understand basic syntax before the timed evaluation begins."),
        
        ("Step 4: Code Comprehension Assessment (Reading Phase)",
         "Assesses code interpretation <i>before</i> code generation. 6 multiple-choice items per condition (C1–C6 matching T1–T6). Each item has 2 parts: <b>Explanation</b> (0, 1, or 2 points) and <b>Output Prediction</b> (0 or 1 point) for a max score of 18 points. Enforces a <b>3-minute per-item timer</b> that automatically submits on timeout."),
        
        ("Step 5: Timed Task Workspace (Writing Phase)",
         "Participants write code for T1 to T6. Features an <b>8-minute timer per task</b>, max 5 submission attempts, real-time error execution feedback, and automated validation against hidden edge-case test datasets. Includes a collapsible schema and beginner reference panel."),
        
        ("Step 6: Post-Task Survey",
         "Administered immediately after completing the language condition. 5 agreement items on code clarity and confidence (1–5 Likert + Not Applicable), mental effort (1–5), fatigue level (1–5), and 3–4 open-ended feedback prompts."),
        
        ("Step 7: Break &amp; Condition 2 Crossover",
         "Provides an optional 5-minute cognitive rest period before crossing over to the second language condition, which repeats Steps 4, 5, and 6 with the alternate language and form."),
        
        ("Step 8: Completion &amp; Researcher Dashboard",
         "Displays study completion receipt. Behind researcher login, the dashboard displays real-time telemetry, median comprehension scores out of 18, comparative productivity charts, and full CSV exports.")
    ]

    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 5: TECHNICAL ARCHITECTURE
    # ==========================
    story.append(Paragraph("5. Technical Architecture &amp; Security Measures", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_blue, spaceBefore=1, spaceAfter=6))

    tech_box = """
    • <b>Backend Framework:</b> Python Flask with modular Blueprints (<code>auth</code>, <code>experiment</code>, <code>tasks</code>, <code>dashboard</code>).<br/>
    • <b>Code Editors:</b> Integrated CodeMirror with SQL and Python syntax highlighting, matching brackets, and keyboard shortcuts (Ctrl+Enter).<br/>
    • <b>Database Storage:</b> SQLite relational architecture. Separates research telemetry (<code>research.db</code>) from experiment databases (<code>experiment_a.db</code>, <code>experiment_b.db</code>).<br/>
    • <b>SQL Security:</b> Queries execute in read-only mode (<code>uri=file:...mode=ro</code>) with strict DDL/DML blocking (prevents CREATE, DROP, INSERT, UPDATE, DELETE).<br/>
    • <b>Python Sandboxing:</b> Restricted execution environment blocking unauthorized system calls (no <code>os</code>, <code>sys</code>, <code>exec</code>, or file I/O).<br/>
    • <b>Automated Grading Engine:</b> Answers are parsed and graded against hidden datasets containing edge cases: tie-breaking, NULL values, and empty result sets.
    """
    t_tech = Table([[Paragraph(tech_box, callout_style)]], colWidths=[504])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # ==========================
    # SECTION 6: DEFENSE Q&A CHEAT SHEET
    # ==========================
    story.append(Paragraph("6. Oral Defense Cheat Sheet: Questions Teachers Will Ask", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=brand_blue, spaceBefore=1, spaceAfter=6))
    story.append(Paragraph("Study these questions and answers carefully before presenting to your committee:", body_style))
    story.append(Spacer(1, 4))

    qa_list = [
        ("Q1: Why did you use a Crossover (within-subjects) design instead of testing SQL on Group A and Python on Group B?",
         "A: A within-subjects crossover design eliminates inter-individual variation (such as student general intelligence, typing speed, or baseline aptitude) because every participant serves as their own baseline control. Counterbalancing (Sequences 1–4) completely neutralizes learning order effects. It also effectively doubles the statistical power of the dataset without requiring twice as many participants."),

        ("Q2: How did you ensure that novices with zero background could realistically answer these questions?",
         "A: We implemented three deliberate scaffolding layers: (1) an isolated Language Reference Guide with plain-English summaries, (2) an untimed practice playground with gatekeeper readiness questions, and (3) a non-intrusive collapsible Quick Reference inside the task workspace. Crucially, all reference materials use an entirely separate Courses/Departments schema so they teach the syntax without giving away task answers."),

        ("Q3: Why is the Comprehension Assessment separated from the Task Writing Workspace?",
         "A: In educational psychology (e.g. Bloom's taxonomy and cognitive load theory), code reading/comprehension is distinct from code generation. Measuring comprehension first provides an unadulterated metric of syntactic and mental readability before measuring writing productivity (speed, attempts, syntax errors)."),

        ("Q4: How does the scoring for the Comprehension test work?",
         "A: Each of the 6 items has two parts: an Explanation question (0 = incorrect, 1 = partially correct, 2 = fully correct) and an Output Prediction question (0 or 1 point). This yields a maximum of 3 points per item, or 18 points maximum per condition. It is timed at 3 minutes per item to measure fluent comprehension."),

        ("Q5: What prevents students from hardcoding answers or cheating?",
         "A: QueryLearn uses hidden automated test datasets (`hidden_tests.json`). When a student submits code, the grading engine executes their query against 3 separate synthetic databases with diverse edge cases (ties, NULL scores, empty matches). A solution only passes if it produces the mathematically correct result across all edge cases."),

        ("Q6: How do you measure 'Productivity'?",
         "A: Productivity is quantified by four objective dependent variables: (1) Task Success Rate (% of tasks solved within 8 minutes), (2) Time-to-Solve (elapsed seconds per task), (3) Number of Attempts required before success, and (4) Error Frequency."),

        ("Q7: Isn't Python naturally harder than SQL for databases? Doesn't that bias the study?",
         "A: That difference in paradigm is precisely what the study investigates. SQL was purpose-built for declarative set operations, whereas procedural Python represents how general programmers write data manipulation. By measuring where novice difficulties occur (e.g. joins, aggregations, nulls), the study generates empirical evidence for curriculum designers."),

        ("Q8: How did you handle participants who did not finish within the time limit?",
         "A: When the 8-minute task timer or 3-minute comprehension countdown expires, the system records a timeout flag (`timed_out = 1`), logs the current attempt count, and transitions automatically to the next item so the evaluation stays on schedule."),

        ("Q9: What happens if a participant answers 'Not applicable' on the survey?",
         "A: The survey cleanly separates 'Not applicable' from the 1–5 agreement scale and stores it as database `NULL`. When computing statistical means or medians, NULL values are excluded so they do not distort the numerical results."),

        ("Q10: Why did you build an automated web app instead of giving students pen-and-paper or Google Forms?",
         "A: QueryLearn provides millisecond-level telemetry (exact typing time, attempt counts, execution error logs), strictly enforces countdown timers, prevents lookahead bias, automatically randomizes answer choices, and eliminates human grading errors through server-side test oracles."),

        ("Q11: How do you know the data isn't biased by student fatigue?",
         "A: The Latin square crossover balances condition order across participants. Also, an optional 5-minute cognitive rest break is provided between conditions, and fatigue is explicitly quantified on a 1–5 scale after each condition to test for fatigue effects as a covariate in statistical analysis."),

        ("Q12: What statistical tests will you use to analyze the final data?",
         "A: For Comprehension and Survey ordinal data: Wilcoxon signed-rank test (non-parametric paired test). For Task Success Rates: McNemar's test for paired binary proportions. For Task Duration and Attempt Counts: Paired t-test or Wilcoxon test, along with Repeated Measures ANOVA (RM-ANOVA) or Mixed Effects Models to control for sequence, form, and prior programming experience."),

        ("Q13: How is data exported for statistical analysis (SPSS / R / Python)?",
         "A: The system generates RFC 4180-compliant CSV exports across 4 granularities: participants registry, task telemetry results, comprehension responses (item-level), and survey responses, as well as a consolidated ZIP archive.")
    ]

    for q, a in qa_list:
        story.append(KeepTogether([
            Paragraph(q, qa_q_style),
            Paragraph(a, qa_a_style),
            Spacer(1, 2.5)
        ]))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Handbook PDF successfully created at: {output_filename}")


if __name__ == '__main__':
    target = os.path.join(r"C:\Users\USER\.gemini\antigravity\scratch\querylearn", "QueryLearn_System_Guide_and_Defense_Handbook.pdf")
    create_handbook(target)
