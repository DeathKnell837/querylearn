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
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, 755, "QueryLearn — Beginner-Friendly Project & Defense Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Simple Defense Guide — Use this to answer your teachers")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def build_simple_pdf(output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Colors
    c_primary = colors.HexColor("#0F172A")
    c_blue = colors.HexColor("#2563EB")
    c_blue_bg = colors.HexColor("#EFF6FF")
    c_blue_border = colors.HexColor("#BFDBFE")
    c_slate = colors.HexColor("#334155")
    c_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")
    c_green = colors.HexColor("#059669")
    c_green_bg = colors.HexColor("#ECFDF5")
    c_green_border = colors.HexColor("#A7F3D0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=c_primary,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'H1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=c_blue,
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
        textColor=c_slate,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3
    )

    # Callout for "What to say to your teacher"
    say_style = ParagraphStyle(
        'SayStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#065F46")
    )

    # Callout for simple summary
    summary_box_style = ParagraphStyle(
        'SummaryBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E3A8A")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
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
        content = f"<b>🗣️ What you say to your teacher:</b><br/>\"{text}\""
        t = Table([[Paragraph(content, say_style)]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_green_bg),
            ('BOX', (0,0), (-1,-1), 1, c_green_border),
            ('TOPPADDING', (0,0), (-1,-1), 4.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    def blue_box(title, text):
        content = f"<b>💡 {title}</b><br/>{text}"
        t = Table([[Paragraph(content, summary_box_style)]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_blue_bg),
            ('BOX', (0,0), (-1,-1), 1, c_blue_border),
            ('TOPPADDING', (0,0), (-1,-1), 4.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    story = []

    # ==========================================
    # TITLE & OVERVIEW
    # ==========================================
    story.append(Paragraph("QueryLearn: Simple Project Guide &amp; Defense Cheat Sheet", title_style))
    story.append(Paragraph("Everything you need to easily understand your website and confidently answer your teachers.", subtitle_style))
    
    meta_box = [
        [Paragraph("<b>What is this?</b> A website that tests whether beginners learn databases better with SQL or Python.", body_style),
         Paragraph("<b>Who takes it?</b> College freshmen or beginners with no past database courses.", body_style)],
        [Paragraph("<b>How is it tested?</b> Each student tests BOTH languages under fair, timed conditions.", body_style),
         Paragraph("<b>What is measured?</b> Reading score, writing success, speed, and mental effort.", body_style)]
    ]
    t_meta = Table(meta_box, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # ==========================================
    # PART 1: THE BIG PICTURE
    # ==========================================
    story.append(Paragraph("Part 1: What is QueryLearn in Plain Words?", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))
    
    story.append(Paragraph(
        "Normally, universities teach database queries using <b>SQL</b>. But beginner students often struggle because SQL feels different from regular programming. Some teachers wonder: <i>Would beginners find it easier or harder if we taught data queries using normal Python code instead?</i>",
        body_style
    ))
    story.append(Paragraph(
        "<b>QueryLearn is the testing lab we built to find out the real answer.</b> It is an online testing system where real students try solving the same data tasks in SQL and in Python. The website records their scores, their time, their errors, and how tired they felt, so we have real proof of which language is better for beginners.",
        body_style
    ))
    story.append(Spacer(1, 3))
    story.append(teacher_box("Our project is an evaluation platform called QueryLearn. It compares SQL versus procedural Python for beginner students to see which language is easier to read, faster to write, and causes less mental frustration."))
    story.append(Spacer(1, 10))

    # ==========================================
    # PART 2: SQL VS PYTHON
    # ==========================================
    story.append(Paragraph("Part 2: SQL vs. Python — What is the Difference?", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))
    
    diff_data = [
        [Paragraph("<b>Feature</b>", table_header), Paragraph("<b>SQL (Declarative)</b>", table_header), Paragraph("<b>Python (Procedural / Step-by-Step)</b>", table_header)],
        [Paragraph("<b>How you write</b>", table_cell), Paragraph("You tell the computer <b>WHAT</b> data you want, and the database engine finds it for you.", table_cell), Paragraph("You tell the computer <b>HOW</b> to get the data, writing every single step yourself.", table_cell)],
        [Paragraph("<b>Simple example</b>", table_cell), Paragraph("<code>SELECT name FROM Students WHERE year = 1;</code>", table_cell), Paragraph("<code>for s in students:<br/>&nbsp;&nbsp;if s['year'] == 1: print(s['name'])</code>", table_cell)],
        [Paragraph("<b>Joining 2 tables</b>", table_cell), Paragraph("One simple word: <code>JOIN Courses ON ...</code>", table_cell), Paragraph("Must build a dictionary lookup or write nested loops.", table_cell)],
        [Paragraph("<b>What we test</b>", table_cell), Paragraph("Do beginners find SQL syntax natural, or does it feel confusing?", table_cell), Paragraph("Do beginners prefer Python loops because they already know them, or is it too tedious?", table_cell)]
    ]
    t_diff = Table(diff_data, colWidths=[90, 207, 207])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_diff)
    story.append(Spacer(1, 10))

    # ==========================================
    # PART 3: HOW WE MADE THE TEST FAIR
    # ==========================================
    story.append(Paragraph("Part 3: How We Made the Test Fair (The Swap Plan)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))
    
    story.append(Paragraph(
        "A common mistake in student research is testing Group 1 on SQL and Group 2 on Python. If Group 1 happens to have smarter students, the test is ruined! To prevent this, we used a <b>Crossover Design</b>: <i>every single student tests both languages</i>.",
        body_style
    ))
    story.append(Paragraph(
        "We also created <b>4 balanced sequences</b> so neither language gets an unfair advantage:",
        body_style
    ))

    fair_data = [
        [Paragraph("<b>Group</b>", table_header), Paragraph("<b>First Language</b>", table_header), Paragraph("<b>Second Language</b>", table_header), Paragraph("<b>Why this is fair</b>", table_header)],
        [Paragraph("Sequence 1", table_cell), Paragraph("SQL (Form A)", table_cell), Paragraph("Python (Form B)", table_cell), Paragraph("Starts with SQL", table_cell)],
        [Paragraph("Sequence 2", table_cell), Paragraph("Python (Form A)", table_cell), Paragraph("SQL (Form B)", table_cell), Paragraph("Starts with Python (balances practice)", table_cell)],
        [Paragraph("Sequence 3", table_cell), Paragraph("SQL (Form B)", table_cell), Paragraph("Python (Form A)", table_cell), Paragraph("Swaps the problem sets", table_cell)],
        [Paragraph("Sequence 4", table_cell), Paragraph("Python (Form B)", table_cell), Paragraph("SQL (Form A)", table_cell), Paragraph("Swaps the problem sets", table_cell)]
    ]
    t_fair = Table(fair_data, colWidths=[70, 140, 140, 154])
    t_fair.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_fair)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Notice Form A and Form B:</b> They test the exact same difficulty, but use different numbers and student names so nobody can memorize answers.", body_style))
    story.append(Spacer(1, 3))
    story.append(teacher_box("We used a counterbalanced crossover design. Every student does both SQL and Python in alternating orders, so differences in student intelligence or practice effects cancel out completely."))
    
    story.append(Spacer(1, 10))

    # ==========================================
    # PART 4: THE 8 STEPS ON THE WEBSITE
    # ==========================================
    story.append(Paragraph("Part 4: What a Student Experiences (The 8 Steps)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))
    story.append(Paragraph("Here is what happens when someone uses QueryLearn from start to finish:", body_style))

    flow_items = [
        ("Step 1: Registration &amp; Ethics Consent",
         "The student enters their college year level and programming background. They agree to the privacy consent. The system creates an anonymous Study ID (like P001 or P017) so their real identity is never shown in research."),
        
        ("Step 2: Language Reference Guide",
         "A study guide showing 6 short code examples in SQL and Python. <b>Important secret:</b> The guide uses made-up course and department data so it teaches the rules without giving away any task answers!"),
        
        ("Step 3: Practice Sandbox &amp; Quick Check",
         "Students test the buttons and editor on 2 simple practice tasks (not timed, not graded). Then they answer 2 quick readiness questions to make sure they didn't just rush through."),
        
        ("Step 4: Reading Test (Code Comprehension)",
         "Before writing code, students read 6 code snippets. For each snippet, they explain what the code does (2 pts) and predict the output (1 pt). Max score is 18 points. Has a 3-minute timer per question."),
        
        ("Step 5: Writing Test (The 6 Coding Tasks)",
         "Students write their own code for Tasks 1 to 6. Each task has an 8-minute countdown timer and allows up to 5 tries. A green Run button tests their code, and a blue Submit button grades it."),
        
        ("Step 6: Post-Task Survey",
         "Students rate how easy the language was to read, understand, and debug (1 to 5 stars), plus their mental effort and fatigue, with a couple of optional written comments."),
        
        ("Step 7: 5-Minute Break",
         "A screen telling them to rest their eyes and relax before moving on to the second language."),
        
        ("Step 8: Second Language &amp; Completion",
         "They repeat Steps 4, 5, and 6 with the second language. When done, they see a Thank You screen, and all their numbers are safely saved in the researcher dashboard.")
    ]

    for st_title, st_desc in flow_items:
        story.append(Paragraph(f"<b>{st_title}</b>", h2_style))
        story.append(Paragraph(st_desc, body_style))

    story.append(Spacer(1, 8))

    # ==========================================
    # PART 5: THE 6 TASKS EXPLAINED SIMPLY
    # ==========================================
    story.append(Paragraph("Part 5: The 6 Coding Tasks (What the Student Actually Solves)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))

    task_simple = [
        [Paragraph("<b>Task #</b>", table_header), Paragraph("<b>Goal in Plain English</b>", table_header), Paragraph("<b>In SQL</b>", table_header), Paragraph("<b>In Python</b>", table_header)],
        [Paragraph("<b>Task 1</b>", table_cell), Paragraph("Find all 2nd-year BSIT students.", table_cell), Paragraph("<code>WHERE program='BSIT' AND year=2</code>", table_cell), Paragraph("<code>if s['program']=='BSIT' and s['year']==2</code>", table_cell)],
        [Paragraph("<b>Task 2</b>", table_cell), Paragraph("Get the top 3 highest scores in a course.", table_cell), Paragraph("<code>ORDER BY score DESC LIMIT 3</code>", table_cell), Paragraph("Sort by score descending and take slice <code>[:3]</code>", table_cell)],
        [Paragraph("<b>Task 3</b>", table_cell), Paragraph("Count how many students in each program.", table_cell), Paragraph("<code>GROUP BY program, COUNT(*)</code>", table_cell), Paragraph("Use a dictionary to count frequencies", table_cell)],
        [Paragraph("<b>Task 4</b>", table_cell), Paragraph("Show student name and course name together.", table_cell), Paragraph("<code>JOIN Enrollments ... JOIN Courses</code>", table_cell), Paragraph("Lookup dictionary matching student and course IDs", table_cell)],
        [Paragraph("<b>Task 5</b>", table_cell), Paragraph("Find courses where average score is &gt;= 85.", table_cell), Paragraph("<code>GROUP BY ... HAVING AVG(score) &gt;= 85</code>", table_cell), Paragraph("Group scores in dictionary lists, compute average", table_cell)],
        [Paragraph("<b>Task 6</b>", table_cell), Paragraph("Find students who have zero enrolled courses.", table_cell), Paragraph("<code>LEFT JOIN ... WHERE course_id IS NULL</code>", table_cell), Paragraph("Set difference (find student IDs not in enrolled list)", table_cell)]
    ]
    t_ts = Table(task_simple, colWidths=[40, 164, 150, 150])
    t_ts.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_ts)
    story.append(Spacer(1, 12))

    # ==========================================
    # PART 6: ORAL DEFENSE CHEAT SHEET
    # ==========================================
    story.append(Paragraph("Part 6: Teacher Defense Questions &amp; Simple Answers", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_blue, spaceBefore=1, spaceAfter=5))
    story.append(Paragraph("Here are the top 10 questions your teachers or panelists will ask, with the simple answers you can say out loud:", body_style))
    story.append(Spacer(1, 4))

    qa_simple = [
        ("1. 'Why did you build a web app instead of just giving students Google Forms or paper?'",
         "Because a web app automatically records exact seconds spent, tracks every single failed attempt, runs their code in a secure sandbox, and grades their answers instantly without human grading errors."),

        ("2. 'How can freshmen or students with zero experience answer these tasks?'",
         "We provided three beginner helpers: (1) a Reference Guide with plain-English summaries, (2) an untimed practice sandbox with a readiness check, and (3) a collapsible 'Need Help?' quick reference box inside the task window. All references use fake course data so they don't give away task answers."),

        ("3. 'What if a student just guesses or hardcodes the answer like print([1, 2, 3])?'",
         "They cannot cheat! The system tests their code against hidden test datasets with edge cases (like tie scores, missing values, and empty rows). If their code does not genuinely calculate the right logic, it fails automatically."),

        ("4. 'What are the main metrics or numbers you are collecting?'",
         "We collect four main numbers: (1) Reading score (out of 18), (2) Task success rate (percentage solved), (3) Time spent solving each task (seconds), and (4) Number of attempts (from 1 to 5). We also collect self-reported mental effort and fatigue ratings."),

        ("5. 'Why do you test code comprehension before task writing?'",
         "Because reading and writing are two different cognitive skills. Testing comprehension first lets us measure how easily a beginner understands the syntax before they have to worry about typing speed or syntax typos."),

        ("6. 'Why did each task have an 8-minute timer?'",
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
            Spacer(1, 4)
        ]))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Simple Handbook PDF successfully created at: {output_filename}")


if __name__ == '__main__':
    target = os.path.join(r"C:\Users\USER\.gemini\antigravity\scratch\querylearn", "QueryLearn_System_Guide_and_Defense_Handbook.pdf")
    build_simple_pdf(target)
