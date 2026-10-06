"""
Generates publication-quality formal software engineering diagrams for QueryLearn:
1. System Architecture Diagram (4-tier layered architecture)
2. System Context Diagram (DFD Level 0)
3. Formal UML Use Case Diagram
"""

import os
from PIL import Image, ImageDraw, ImageFont

DIAGRAMS_DIR = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

# Standard Fonts
FONT_TITLE = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 24)
FONT_HEADING = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 18)
FONT_BOLD = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 14)
FONT_REGULAR = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 13)
FONT_SMALL = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 11)
FONT_MONO = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 12)

# Color Palette
BG_COLOR = (13, 17, 28)          # Deep slate background #0d111c
CARD_BG = (22, 30, 49)           # Card fill #161e31
CARD_BORDER = (51, 65, 85)       # Slate border #334155
ACCENT_BLUE = (59, 130, 246)     # Primary blue #3b82f6
ACCENT_CYAN = (56, 189, 248)     # Cyan #38bdf8
ACCENT_GREEN = (16, 185, 129)    # Emerald #10b981
ACCENT_PURPLE = (168, 85, 247)   # Purple #a855f7
ACCENT_ORANGE = (249, 115, 22)   # Orange #f97316
TEXT_WHITE = (248, 250, 252)     # Off-white
TEXT_MUTED = (148, 163, 184)     # Muted slate
TEXT_DIM = (100, 116, 139)       # Dim slate
ARROW_COLOR = (96, 165, 250)     # Arrow blue #60a5fa


def draw_arrow(draw, start, end, color=ARROW_COLOR, width=2, arrow_size=8):
    """Draws a line with an arrowhead pointing at end."""
    x0, y0 = start
    x1, y1 = end
    draw.line([start, end], fill=color, width=width)
    import math
    angle = math.atan2(y1 - y0, x1 - x0)
    left_x = x1 - arrow_size * math.cos(angle - math.pi / 6)
    left_y = y1 - arrow_size * math.sin(angle - math.pi / 6)
    right_x = x1 - arrow_size * math.cos(angle + math.pi / 6)
    right_y = y1 - arrow_size * math.sin(angle + math.pi / 6)
    draw.polygon([(x1, y1), (left_x, left_y), (right_x, right_y)], fill=color)


def draw_card(draw, box, title, items, color=ACCENT_BLUE, border=CARD_BORDER):
    """Draws a styled container card with a colored title header and bulleted items."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=CARD_BG, outline=border, width=2)
    # Header bar
    draw.rounded_rectangle([x0, y0, x1, y0 + 34], radius=10, fill=(30, 41, 59))
    draw.rectangle([x0, y0 + 20, x1, y0 + 34], fill=(30, 41, 59))
    draw.line([(x0, y0 + 34), (x1, y0 + 34)], fill=color, width=2)
    draw.text((x0 + 14, y0 + 7), title, fill=color, font=FONT_BOLD)

    # Content
    y = y0 + 44
    for item in items:
        draw.text((x0 + 14, y), f"• {item}", fill=TEXT_MUTED, font=FONT_REGULAR)
        y += 22


def generate_architecture_diagram():
    """Generates the formal 4-Layer System Architecture Diagram."""
    img = Image.new("RGB", (1400, 920), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Diagram Title Header
    draw.text((40, 24), "QueryLearn System Architecture Diagram", fill=TEXT_WHITE, font=FONT_TITLE)
    draw.text((40, 60), "Four-Tier Decoupled Architecture: Client, Application, Sandboxed Execution, and Distributed Persistence", fill=TEXT_MUTED, font=FONT_REGULAR)

    # 4 Tier Boundaries
    tiers = [
        ("Presentation Layer (Browser Client)", (40, 100, 1360, 250), ACCENT_CYAN),
        ("Application & Routing Layer (Flask Engine)", (40, 280, 1360, 450), ACCENT_BLUE),
        ("Execution & Grading Layer (Sandboxes & Oracle)", (40, 480, 1360, 660), ACCENT_ORANGE),
        ("Persistence & Telemetry Layer (Supabase Cloud + Local Cache)", (40, 690, 1360, 880), ACCENT_GREEN),
    ]

    for title, (x0, y0, x1, y1), col in tiers:
        draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=(18, 24, 38), outline=CARD_BORDER, width=1)
        draw.text((x0 + 16, y0 + 12), title.upper(), fill=col, font=FONT_BOLD)

    # Layer 1 Components (Presentation)
    draw_card(draw, (60, 140, 360, 235), "Web UI Components", ["Inter & JetBrains Mono Fonts", "Full-Screen Dark Mode Themes", "Responsive Flex/Grid Layout"], ACCENT_CYAN)
    draw_card(draw, (380, 140, 680, 235), "CodeMirror 5 Editors", ["SQL Mode Highlighting", "Python Procedural Indentation", "Real-Time Syntax Validation"], ACCENT_CYAN)
    draw_card(draw, (700, 140, 1000, 235), "Timer & State Watcher", ["8-Min Countdown Timers", "3-Min Comprehension Clock", "Auto-Save on Timeout Expiry"], ACCENT_CYAN)
    draw_card(draw, (1020, 140, 1340, 235), "Visualization UI", ["Chart.js Comparative Graphs", "Pass vs. Fail Metric Badges", "Real-time Telemetry Grid"], ACCENT_CYAN)

    # Layer 2 Components (Application Blueprints)
    draw_card(draw, (60, 320, 360, 435), "Auth Blueprint", ["Latin Square Crossover Assigner", "Study ID Generator (P017+)", "Enforced Year Level (2-4)"], ACCENT_BLUE)
    draw_card(draw, (380, 320, 680, 435), "Experiment Blueprint", ["Interactive Practice & Sandbox", "6-Item Code Comprehension", "Post-Condition Likert Survey"], ACCENT_BLUE)
    draw_card(draw, (700, 320, 1000, 435), "Tasks Blueprint", ["/api/run Code Dispatcher", "/api/submit Answer Broker", "Duplicate Submission Guard"], ACCENT_BLUE)
    draw_card(draw, (1020, 320, 1340, 435), "Dashboard Blueprint", ["Pass/Fail Split Calculations", "Paired Median Time Ratios", "CSV & ZIP Telemetry Streamer"], ACCENT_BLUE)

    # Layer 3 Components (Execution Sandbox)
    draw_card(draw, (60, 520, 460, 645), "SQLite Execution Engine", ["Read-Only URI (mode=ro)", "Regex Destructive DDL Filter", "10-Second Strict Timeout"], ACCENT_ORANGE)
    draw_card(draw, (490, 520, 890, 645), "Restricted Python Subprocess", ["AST ASTValidator Parsing", "Restricted In-Memory Dictionaries", "Traceback & Exception Sanitizer"], ACCENT_ORANGE)
    draw_card(draw, (920, 520, 1340, 645), "Automated Grading Oracle", ["3 Hidden Test Datasets / Task", "Permutation-Invariant Result Matcher", "Floating Point Epsilon (1e-6)"], ACCENT_ORANGE)

    # Layer 4 Components (Data & Persistence)
    draw_card(draw, (60, 730, 460, 865), "Supabase Cloud Database", ["PostgreSQL 17.6 Managed Engine", "Cross-Machine Unique Study IDs", "Live Real-Time Telemetry Sync"], ACCENT_GREEN)
    draw_card(draw, (490, 730, 890, 865), "Local SQLite Cache", ["/tmp/research.db Fallback", "Offline Resilience Buffer", "Bidirectional Sync Engine"], ACCENT_GREEN)
    draw_card(draw, (920, 730, 1340, 865), "Experiment Databases", ["experiment_a.db / experiment_b.db", "Synthetic University Records", "Export Service (CSV / ZIP)"], ACCENT_GREEN)

    # Inter-layer Connection Arrows
    draw_arrow(draw, (210, 235), (210, 320))
    draw_arrow(draw, (530, 235), (530, 320))
    draw_arrow(draw, (850, 235), (850, 320))
    draw_arrow(draw, (1180, 235), (1180, 320))

    draw_arrow(draw, (850, 435), (260, 520))
    draw_arrow(draw, (850, 435), (690, 520))
    draw_arrow(draw, (690, 580), (920, 580))
    draw_arrow(draw, (260, 580), (920, 580))

    draw_arrow(draw, (260, 645), (260, 730))
    draw_arrow(draw, (690, 645), (690, 730))
    draw_arrow(draw, (1130, 645), (1130, 730))
    draw_arrow(draw, (460, 795), (490, 795))  # Supabase <-> Local

    out_path = os.path.join(DIAGRAMS_DIR, "01_system_architecture.png")
    img.save(out_path, quality=95)
    print(f"Generated Architecture Diagram: {out_path}")


def generate_context_diagram():
    """Generates the formal System Context Diagram (DFD Level 0)."""
    img = Image.new("RGB", (1400, 860), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.text((40, 24), "QueryLearn System Context Diagram (DFD Level 0)", fill=TEXT_WHITE, font=FONT_TITLE)
    draw.text((40, 60), "External Entities, Boundary Scope, and Information Flows with the QueryLearn Evaluation System", fill=TEXT_MUTED, font=FONT_REGULAR)

    # External Entity 1: Participant (Left)
    p_box = (50, 260, 350, 640)
    draw.rounded_rectangle(p_box, radius=12, fill=CARD_BG, outline=ACCENT_CYAN, width=3)
    draw.text((70, 280), "EXTERNAL ENTITY", fill=ACCENT_CYAN, font=FONT_SMALL)
    draw.text((70, 305), "Student Participant", fill=TEXT_WHITE, font=FONT_HEADING)
    draw.text((70, 335), "2nd to 4th Year BSCS/BSIT/BSIS", fill=TEXT_MUTED, font=FONT_REGULAR)
    draw.line([(50, 365), (350, 365)], fill=CARD_BORDER, width=1)
    
    p_roles = [
        "Completes Registration Form",
        "Reviews Language Syntax Guides",
        "Performs Interactive Practice",
        "Executes & Tests Code Queries",
        "Submits Coded Tasks (T1-T6)",
        "Completes Comprehension Test",
        "Fills Post-Condition Surveys"
    ]
    y = 380
    for r in p_roles:
        draw.text((70, y), f"• {r}", fill=TEXT_WHITE, font=FONT_REGULAR)
        y += 32

    # Central Process: 0.0 QueryLearn (Center Circle/Rounded)
    c_box = (490, 240, 910, 660)
    draw.rounded_rectangle(c_box, radius=24, fill=(20, 27, 45), outline=ACCENT_BLUE, width=4)
    draw.text((540, 275), "PROCESS 0.0 (SYSTEM BOUNDARY)", fill=ACCENT_BLUE, font=FONT_SMALL)
    draw.text((540, 305), "QueryLearn Evaluation Platform", fill=TEXT_WHITE, font=FONT_TITLE)
    draw.line([(490, 345), (910, 345)], fill=CARD_BORDER, width=2)

    sys_tasks = [
        "1. Latin Square Counterbalanced Sequence Assignment",
        "2. Multi-Language Sandboxed Execution (SQL / Py)",
        "3. Dual-Dataset Oracle Automated Correctness Checker",
        "4. Server-Authoritative Task & Response Time Tracker",
        "5. Cross-Computer Shared Cloud Persistence (Supabase)",
        "6. Cognitive Workload & Likert Survey Processing",
        "7. Real-Time Researcher Pass/Fail Telemetry Generation"
    ]
    y = 370
    for st in sys_tasks:
        draw.text((515, y), st, fill=TEXT_MUTED, font=FONT_REGULAR)
        y += 36

    # External Entity 2: Researcher (Right)
    r_box = (1050, 260, 1350, 640)
    draw.rounded_rectangle(r_box, radius=12, fill=CARD_BG, outline=ACCENT_GREEN, width=3)
    draw.text((1070, 280), "EXTERNAL ENTITY", fill=ACCENT_GREEN, font=FONT_SMALL)
    draw.text((1070, 305), "Thesis Panel / Researcher", fill=TEXT_WHITE, font=FONT_HEADING)
    draw.text((1070, 335), "Teacher / Thesis Evaluator", fill=TEXT_MUTED, font=FONT_REGULAR)
    draw.line([(1050, 365), (1350, 365)], fill=CARD_BORDER, width=1)

    r_roles = [
        "Authenticates via Admin Portal",
        "Monitors Live Participant Progress",
        "Inspects Right vs. Wrong Analytics",
        "Observes Paired Time Ratios",
        "Triggers Synthetic Benchmarks",
        "Filters Telemetry by Condition",
        "Exports Research Datasets (CSV/ZIP)"
    ]
    y = 380
    for r in r_roles:
        draw.text((1070, y), f"• {r}", fill=TEXT_WHITE, font=FONT_REGULAR)
        y += 32

    # Flow Arrows: Student -> System
    draw_arrow(draw, (350, 330), (490, 330), color=ACCENT_CYAN, width=3)
    draw.text((362, 308), "1. Registration & Consent", fill=ACCENT_CYAN, font=FONT_SMALL)

    draw_arrow(draw, (350, 420), (490, 420), color=ACCENT_CYAN, width=3)
    draw.text((362, 398), "2. SQL/Python Code Submissions", fill=ACCENT_CYAN, font=FONT_SMALL)

    draw_arrow(draw, (350, 510), (490, 510), color=ACCENT_CYAN, width=3)
    draw.text((362, 488), "3. Comprehension & Survey Data", fill=ACCENT_CYAN, font=FONT_SMALL)

    # Flow Arrows: System -> Student
    draw_arrow(draw, (490, 580), (350, 580), color=ARROW_COLOR, width=3)
    draw.text((362, 558), "A. Instructions & Task Schema", fill=ARROW_COLOR, font=FONT_SMALL)

    draw_arrow(draw, (490, 620), (350, 620), color=ARROW_COLOR, width=3)
    draw.text((362, 626), "B. Immediate Oracle Feedback", fill=ARROW_COLOR, font=FONT_SMALL)

    # Flow Arrows: System -> Researcher
    draw_arrow(draw, (910, 350), (1050, 350), color=ACCENT_GREEN, width=3)
    draw.text((920, 328), "A. Real-Time Pass/Fail Telemetry", fill=ACCENT_GREEN, font=FONT_SMALL)

    draw_arrow(draw, (910, 440), (1050, 440), color=ACCENT_GREEN, width=3)
    draw.text((920, 418), "B. Median Ratios & Survey Charts", fill=ACCENT_GREEN, font=FONT_SMALL)

    draw_arrow(draw, (910, 530), (1050, 530), color=ACCENT_GREEN, width=3)
    draw.text((920, 508), "C. Clean Research Datasets (ZIP)", fill=ACCENT_GREEN, font=FONT_SMALL)

    # Flow Arrows: Researcher -> System
    draw_arrow(draw, (1050, 600), (910, 600), color=ARROW_COLOR, width=3)
    draw.text((920, 606), "1. Benchmark Triggers & Auth", fill=ARROW_COLOR, font=FONT_SMALL)

    out_path = os.path.join(DIAGRAMS_DIR, "02_system_context_dfd0.png")
    img.save(out_path, quality=95)
    print(f"Generated Context Diagram: {out_path}")


def generate_use_case_diagram():
    """Generates the formal UML Use Case Diagram."""
    img = Image.new("RGB", (1400, 920), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.text((40, 24), "QueryLearn Formal UML Use Case Diagram", fill=TEXT_WHITE, font=FONT_TITLE)
    draw.text((40, 60), "Actors, System Boundary, and Goal-Oriented Interactions across Experimental Conditions", fill=TEXT_MUTED, font=FONT_REGULAR)

    # System Boundary Box
    sb = (300, 110, 1100, 880)
    draw.rounded_rectangle(sb, radius=16, fill=(18, 25, 42), outline=CARD_BORDER, width=2)
    draw.text((320, 125), "SYSTEM BOUNDARY: QUERYLEARN PLATFORM", fill=ACCENT_BLUE, font=FONT_BOLD)

    # Left Actor: Student Participant
    draw.ellipse([100, 300, 160, 360], outline=ACCENT_CYAN, width=3, fill=(24, 32, 54))  # Head
    draw.line([(130, 360), (130, 450)], fill=ACCENT_CYAN, width=3)                       # Body
    draw.line([(130, 390), (80, 420)], fill=ACCENT_CYAN, width=3)                        # Left arm
    draw.line([(130, 390), (180, 420)], fill=ACCENT_CYAN, width=3)                       # Right arm
    draw.line([(130, 450), (90, 530)], fill=ACCENT_CYAN, width=3)                        # Left leg
    draw.line([(130, 450), (170, 530)], fill=ACCENT_CYAN, width=3)                       # Right leg
    draw.text((85, 550), "Participant", fill=TEXT_WHITE, font=FONT_HEADING)
    draw.text((65, 575), "(2nd-4th Year Student)", fill=TEXT_MUTED, font=FONT_SMALL)

    # Right Actor: Researcher / Evaluator
    draw.ellipse([1240, 300, 1300, 360], outline=ACCENT_GREEN, width=3, fill=(24, 32, 54))
    draw.line([(1270, 360), (1270, 450)], fill=ACCENT_GREEN, width=3)
    draw.line([(1270, 390), (1220, 420)], fill=ACCENT_GREEN, width=3)
    draw.line([(1270, 390), (1320, 420)], fill=ACCENT_GREEN, width=3)
    draw.line([(1270, 450), (1230, 530)], fill=ACCENT_GREEN, width=3)
    draw.line([(1270, 450), (1310, 530)], fill=ACCENT_GREEN, width=3)
    draw.text((1220, 550), "Researcher", fill=TEXT_WHITE, font=FONT_HEADING)
    draw.text((1205, 575), "(Teacher / Evaluator)", fill=TEXT_MUTED, font=FONT_SMALL)

    # Use Cases (Ovals)
    student_cases = [
        ("UC-01: Register & Consent (Year 2+)", (340, 170, 680, 225)),
        ("UC-02: Review Language Reference Guides", (340, 245, 680, 300)),
        ("UC-03: Complete Untimed Practice & Readiness", (340, 320, 680, 375)),
        ("UC-04: Execute & Debug Query in Sandbox", (340, 395, 680, 450)),
        ("UC-05: Submit Coded Task for Oracle Grading", (340, 470, 680, 525)),
        ("UC-06: Complete 6-Item Comprehension Test", (340, 545, 680, 600)),
        ("UC-07: Submit Post-Condition Likert Survey", (340, 620, 680, 675)),
        ("UC-08: Complete Counterbalanced Sequence", (340, 695, 680, 750)),
    ]

    researcher_cases = [
        ("UC-09: Authenticate via Researcher Portal", (720, 245, 1060, 300)),
        ("UC-10: Monitor Live Participant Registry", (720, 335, 1060, 390)),
        ("UC-11: Inspect Pass vs. Fail Breakdown Analytics", (720, 425, 1060, 480)),
        ("UC-12: Compare Paired Task Median Ratios", (720, 515, 1060, 570)),
        ("UC-13: Execute Scalability Benchmarks (1K-100K)", (720, 605, 1060, 660)),
        ("UC-14: Export Raw Research Datasets (CSV/ZIP)", (720, 695, 1060, 750)),
    ]

    for label, (x0, y0, x1, y1) in student_cases:
        draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(27, 38, 62), outline=ACCENT_CYAN, width=2)
        draw.text((x0 + 20, y0 + 17), label, fill=TEXT_WHITE, font=FONT_REGULAR)
        # Connect student actor to use case
        draw.line([(180, 420), (x0, (y0 + y1) // 2)], fill=(51, 65, 85), width=2)

    for label, (x0, y0, x1, y1) in researcher_cases:
        draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(24, 40, 54), outline=ACCENT_GREEN, width=2)
        draw.text((x0 + 20, y0 + 17), label, fill=TEXT_WHITE, font=FONT_REGULAR)
        # Connect researcher actor to use case
        draw.line([(1220, 420), (x1, (y0 + y1) // 2)], fill=(51, 65, 85), width=2)

    # Cross-relations: UC-05 (Submit) includes Oracle Verification
    draw.rounded_rectangle([530, 785, 870, 840], radius=24, fill=(35, 27, 45), outline=ACCENT_PURPLE, width=2)
    draw.text((550, 802), "«include» Real-Time Cloud Sync (Supabase)", fill=ACCENT_PURPLE, font=FONT_REGULAR)
    draw.line([(510, 525), (600, 785)], fill=ACCENT_PURPLE, width=1)
    draw.line([(890, 480), (800, 785)], fill=ACCENT_PURPLE, width=1)

    out_path = os.path.join(DIAGRAMS_DIR, "03_use_case_diagram.png")
    img.save(out_path, quality=95)
    print(f"Generated Use Case Diagram: {out_path}")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_context_diagram()
    generate_use_case_diagram()
    print("All formal diagrams generated successfully.")
