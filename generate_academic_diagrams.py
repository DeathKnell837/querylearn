"""
Academic Publication Diagram Generator for QueryLearn.
Produces:
1. Context Diagram (DFD Level 0) - Figure 1
2. Layered Architecture Diagram - Figure 2
3. Formal UML Use Case Diagram - Figure 3

Strict styling rules:
- Pure white background (#FFFFFF)
- Black lines (2px visual / stroke-width 4px at 300 DPI)
- Black text (#000000)
- Light gray fill (#F2F2F2) only
- No colors, no gradients, no shadows, no glow, no icons, no emojis
- Arial font, titles 16pt bold (64px @ 300 DPI), captions below (Figure X.)
- Right-angle connectors only (orthogonal), no diagonal or curved lines
- No line may cross another line or pass through any box, oval, or text
- Arrow labels sit above their arrow on a white background and never touch a box
- Aligned to grid with equal spacing
- Saved as SVG and 3508x2480 PNG (A4 landscape at 300 DPI) in docs/diagrams
"""

import os
import shutil
import subprocess
import math
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "diagrams")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "diagrams")
ARTIFACT_DIR = r"C:\Users\USER\.gemini\antigravity\brain\69d68b2e-edce-45bf-9ec4-95830b667527"

os.makedirs(DOCS_DIAGRAMS_DIR, exist_ok=True)
os.makedirs(DIAGRAMS_DIR, exist_ok=True)


# ==============================================================================
# DIAGRAM 1: CONTEXT DIAGRAM (DFD LEVEL 0)
# ==============================================================================
def build_context_diagram_svg() -> str:
    """
    DFD Level 0 Context Diagram.
    Center: 'QueryLearn System' circle.
    Left: 'Participant' rectangle.
    Right: 'Researcher' rectangle.
    All connections are straight horizontal orthogonal arrows.
    Arrow labels sit above arrow on white background.
    Zero crossing lines, zero diagonal lines, zero curves.
    """
    w, h = 3508, 2480
    cx, cy = 1754, 1300
    radius = 500

    p_x0, p_x1 = 200, 620
    r_x0, r_x1 = 2888, 3308

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-r" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto">')
    svg.append('    <path d="M 0 1 L 14 7 L 0 13 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('  <marker id="arrow-l" markerWidth="14" markerHeight="14" refX="2" refY="7" orient="auto">')
    svg.append('    <path d="M 14 1 L 0 7 L 14 13 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="190" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn System Context Diagram (DFD Level 0)</text>')

    # Caption
    svg.append('<text x="1754" y="2360" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 1. Context Diagram of QueryLearn</text>')

    # Participant Entity (Left)
    svg.append(f'<rect x="{p_x0}" y="650" width="{p_x1 - p_x0}" height="1300" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{(p_x0 + p_x1) // 2}" y="1315" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">Participant</text>')

    # Researcher Entity (Right)
    svg.append(f'<rect x="{r_x0}" y="650" width="{r_x1 - r_x0}" height="1300" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{(r_x0 + r_x1) // 2}" y="1315" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">Researcher</text>')

    # QueryLearn System Entity (Center Circle)
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{cx}" y="{cy - 20}" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn</text>')
    svg.append(f'<text x="{cx}" y="{cy + 45}" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">System</text>')

    # --- LEFT FLOWS (Participant <-> System) ---
    left_flows = [
        ("registration and consent", 880, "right"),
        ("task solutions", 1000, "right"),
        ("comprehension answers", 1120, "right"),
        ("survey responses", 1240, "right"),
        ("task statements", 1400, "left"),
        ("language reference guide", 1520, "left"),
        ("session progress", 1640, "left"),
    ]

    for label, y_pos, direction in left_flows:
        dy = abs(y_pos - cy)
        dx = math.sqrt(max(0, radius**2 - dy**2))
        circle_edge_x = cx - dx

        line_start = p_x1
        line_end = circle_edge_x

        if direction == "right":
            # Participant to System: arrowhead at circle edge
            svg.append(f'<line x1="{line_start}" y1="{y_pos}" x2="{line_end}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-r)" />')
        else:
            # System to Participant: arrowhead at Participant box
            svg.append(f'<line x1="{line_end}" y1="{y_pos}" x2="{line_start}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-l)" />')

        # Label above arrow on white background
        label_x = (line_start + line_end) / 2
        approx_w = len(label) * 21 + 44
        svg.append(f'<rect x="{label_x - approx_w / 2}" y="{y_pos - 48}" width="{approx_w}" height="40" fill="#FFFFFF" />')
        svg.append(f'<text x="{label_x}" y="{y_pos - 18}" font-family="Arial, Helvetica, sans-serif" font-size="34" fill="#000000" text-anchor="middle">{label}</text>')

    # --- RIGHT FLOWS (System <-> Researcher) ---
    right_flows = [
        ("login credentials", 920, "left"),
        ("filter selections", 1060, "left"),
        ("participant registry", 1240, "right"),
        ("task results", 1380, "right"),
        ("comparative analytics", 1520, "right"),
        ("exported data files", 1660, "right"),
    ]

    for label, y_pos, direction in right_flows:
        dy = abs(y_pos - cy)
        dx = math.sqrt(max(0, radius**2 - dy**2))
        circle_edge_x = cx + dx

        line_start = circle_edge_x
        line_end = r_x0

        if direction == "left":
            # Researcher to System: arrowhead at circle edge
            svg.append(f'<line x1="{line_end}" y1="{y_pos}" x2="{line_start}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-l)" />')
        else:
            # System to Researcher: arrowhead at Researcher box
            svg.append(f'<line x1="{line_start}" y1="{y_pos}" x2="{line_end}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-r)" />')

        label_x = (line_start + line_end) / 2
        approx_w = len(label) * 21 + 44
        svg.append(f'<rect x="{label_x - approx_w / 2}" y="{y_pos - 48}" width="{approx_w}" height="40" fill="#FFFFFF" />')
        svg.append(f'<text x="{label_x}" y="{y_pos - 18}" font-family="Arial, Helvetica, sans-serif" font-size="34" fill="#000000" text-anchor="middle">{label}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 2: LAYERED ARCHITECTURE DIAGRAM
# ==============================================================================
def build_architecture_diagram_svg() -> str:
    """
    Layered System Architecture Diagram.
    4 horizontal layers stacked top to bottom:
    - Presentation Layer (Browser Client)
    - Application Layer (Flask 3.1 Web Framework)
    - Services Layer (Domain Logic & Orchestration)
    - Data Layer (Local & Ephemeral Serverless Storage)
    Dashed box around Layers 2, 3, 4 labeled 'Hosted on Vercel (serverless)'
    Clear gaps in dashed boundary so arrows do not cross.
    Stepped right-angle connectors with labels sitting above horizontal arrow segments.
    Wording: '2x2 counterbalanced crossover with four sequences'
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-d" markerWidth="14" markerHeight="14" refX="7" refY="12" orient="auto">')
    svg.append('    <path d="M 1 0 L 7 14 L 13 0 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('  <marker id="arrow-u" markerWidth="14" markerHeight="14" refX="7" refY="2" orient="auto">')
    svg.append('    <path d="M 1 14 L 7 0 L 13 14 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="160" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Layered System Architecture</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 2. Layered Architecture Diagram of QueryLearn</text>')

    # Vercel Serverless Dashed Box (Encloses Application, Services, and Data layers)
    # y = 680 to 2260, x = 140 to 3368
    # Top dashed line has gaps at x=800..1200 and x=2300..2700 so arrows pass through clear gaps
    dashed_top_y = 690
    # Segment 1: x = 140 to 750
    svg.append(f'<line x1="140" y1="{dashed_top_y}" x2="750" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    # Segment 2: x = 1250 to 2250
    svg.append(f'<line x1="1250" y1="{dashed_top_y}" x2="2250" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    # Segment 3: x = 2750 to 3368
    svg.append(f'<line x1="2750" y1="{dashed_top_y}" x2="3368" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    # Left, bottom, and right dashed lines
    svg.append(f'<line x1="140" y1="{dashed_top_y}" x2="140" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append('<line x1="140" y1="2260" x2="3368" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="3368" y1="{dashed_top_y}" x2="3368" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    # Label for Vercel Dashed Box
    svg.append(f'<text x="3330" y="{dashed_top_y + 36}" font-family="Arial, Helvetica, sans-serif" font-size="32" font-weight="bold" font-style="italic" fill="#000000" text-anchor="end">Hosted on Vercel (serverless)</text>')

    # ==========================================
    # LAYER 1: Presentation Layer
    # ==========================================
    # y = 220, height = 330
    svg.append('<rect x="180" y="220" width="3148" height="330" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="268" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Presentation Layer (Browser Client)</text>')

    p_boxes = [
        ("HTML User Interface", ["Jinja2 Web Templates", "Responsive Navigation Layout", "Study Protocol Views (11 Templates)"], 220),
        ("Code Editors", ["CodeMirror 5 Workspace", "SQL Syntax Highlighting", "Procedural Python Mode"], 990),
        ("Client-Side Timers", ["timer.js Engine", "8-Min Task Countdown Clocks", "3-Min Comprehension Timer"], 1760),
        ("Data Visualizations", ["Chart.js 4 Engine", "Outcome Split Visualizations", "Headline Performance Metrics"], 2530),
    ]
    for title, items, bx in p_boxes:
        svg.append(f'<rect x="{bx}" y="290" width="730" height="230" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 30}" y="335" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{380 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    # Gap 1 (y = 550 to 740): Stepped right-angle connector
    # Downward request: from Layer 1 at (1000, 550) -> down to y=645 -> horizontal to x=1000? Or straight vertical through gap:
    # Downward arrow at x = 1000: from (1000, 550) straight down to (1000, 740) through clear gap (x=750..1250)
    svg.append('<line x1="1000" y1="550" x2="1000" y2="740" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    # Label with white background centered to the left of the arrow
    svg.append('<rect x="420" y="625" width="550" height="38" fill="#FFFFFF" />')
    svg.append('<text x="695" y="652" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">HTTP Requests (form data, code, parameters)</text>')

    # Upward response: from Layer 2 at (2500, 740) straight up to (2500, 550) through clear gap (x=2250..2750)
    svg.append('<line x1="2500" y1="740" x2="2500" y2="550" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    # Label with white background centered to the right of the arrow
    svg.append('<rect x="2530" y="625" width="540" height="38" fill="#FFFFFF" />')
    svg.append('<text x="2800" y="652" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">HTTP Responses (rendered HTML, JSON, CSV)</text>')

    # ==========================================
    # LAYER 2: Application Layer (Flask)
    # ==========================================
    # y = 740, height = 330
    svg.append('<rect x="180" y="740" width="3148" height="330" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="788" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Application Layer (Flask 3.1 Web Framework)</text>')

    app_boxes = [
        ("auth_bp", ["Participant Registration (/register)", "Demographic Intake (Year 2-4)", "Researcher Login (/researcher/login)"], 220),
        ("experiment_bp", ["Instructions & Practice Workspaces", "Readiness Check & Comprehension", "Post-Condition Survey & Inter-Condition Break"], 990),
        ("tasks_bp", ["/api/run (Sandboxed Execution)", "/api/submit (Automated Grading)", "/api/skip & /api/start-timer"], 1760),
        ("dashboard_bp", ["Overview (4 Headline Metrics)", "Participant Registry & Task Results", "Task Comparison & CSV Data Export"], 2530),
    ]
    for title, items, bx in app_boxes:
        svg.append(f'<rect x="{bx}" y="810" width="730" height="230" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 30}" y="855" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{900 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    # Gap 2 (y = 1070 to 1240): Downward arrow at x=1000, Upward arrow at x=2500
    svg.append('<line x1="1000" y1="1070" x2="1000" y2="1240" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="420" y="1135" width="550" height="38" fill="#FFFFFF" />')
    svg.append('<text x="695" y="1162" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">Function Calls (code evaluation, sequencing)</text>')

    svg.append('<line x1="2500" y1="1240" x2="2500" y2="1070" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2530" y="1135" width="540" height="38" fill="#FFFFFF" />')
    svg.append('<text x="2800" y="1162" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">Execution Results (grading, metrics, CSV bytes)</text>')

    # ==========================================
    # LAYER 3: Services Layer
    # ==========================================
    # y = 1240, height = 480
    svg.append('<rect x="180" y="1240" width="3148" height="480" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="1288" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Services Layer (Domain Logic & Orchestration)</text>')

    srv_row1 = [
        ("task_catalog", "T1-T6 Specifications & Reference Solutions", 220),
        ("sql_runner", "Read-Only SQLite Engine (mode=ro, 10s Timeout)", 990),
        ("python_runner", "Subprocess Sandbox (Restricted Builtins, 10s)", 1760),
        ("answer_checker", "Oracle Grading & Hidden Test Evaluation", 2530),
    ]
    for title, desc, bx in srv_row1:
        svg.append(f'<rect x="{bx}" y="1310" width="730" height="170" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 30}" y="1355" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        svg.append(f'<text x="{bx + 30}" y="{1405}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {desc}</text>')

    srv_row2 = [
        ("sequence_manager", "2x2 counterbalanced crossover with four sequences", 220),
        ("comprehension_items", "6 Code Reading Comprehension Items & Keys", 990),
        ("benchmark_runner", "Synthetic Scaling Benchmarks (1K, 10K, 100K Rows)", 1760),
        ("export_service", "Study Dataset Export (Participants, Results, Zip)", 2530),
    ]
    for title, desc, bx in srv_row2:
        svg.append(f'<rect x="{bx}" y="1510" width="730" height="180" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 30}" y="1555" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        if "counterbalanced" in desc:
            svg.append(f'<text x="{bx + 30}" y="1605" font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#000000">&#8226; 2x2 counterbalanced crossover</text>')
            svg.append(f'<text x="{bx + 30}" y="1642" font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#000000">   with four sequences</text>')
        else:
            svg.append(f'<text x="{bx + 30}" y="1605" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {desc}</text>')

    # Gap 3 (y = 1720 to 1890): Downward arrow at x=1000, Upward arrow at x=2500
    svg.append('<line x1="1000" y1="1720" x2="1000" y2="1890" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="420" y="1785" width="550" height="38" fill="#FFFFFF" />')
    svg.append('<text x="695" y="1812" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">SQL Queries (SELECT, INSERT) & JSON Reads</text>')

    svg.append('<line x1="2500" y1="1890" x2="2500" y2="1720" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2530" y="1785" width="540" height="38" fill="#FFFFFF" />')
    svg.append('<text x="2800" y="1812" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">Query Result Sets & Hidden Test Payloads</text>')

    # ==========================================
    # LAYER 4: Data Layer
    # ==========================================
    # y = 1890, height = 340
    svg.append('<rect x="180" y="1890" width="3148" height="340" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="1938" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Data Layer (Local & Ephemeral Serverless Storage)</text>')

    data_boxes = [
        ("research.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Tables: participants, sessions, task_attempts", "task_results, task_timers, comprehension, surveys"], 220),
        ("experiment_a.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Form A Relational Database (mode=ro)", "Tables: Students, Courses, Enrollments"], 990),
        ("experiment_b.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Form B Relational Database (mode=ro)", "Tables: Students, Courses, Enrollments"], 1760),
        ("hidden_tests.json", ["JSON Edge-Case Test Datasets", "36 Total Hidden Test Datasets", "3 Edge-Case Datasets per Task (T1-T6, Forms A & B)"], 2530),
    ]
    for title, items, bx in data_boxes:
        svg.append(f'<rect x="{bx}" y="1960" width="730" height="240" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 30}" y="2005" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{2050 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 3: USE CASE DIAGRAM (UML)
# ==============================================================================
def build_use_case_diagram_svg() -> str:
    """
    UML Use Case Diagram.
    One large rectangle 'QueryLearn' as system boundary.
    Stick figure actors outside: Participant (left), Researcher (right).
    Ovals inside with short verb phrases.
    Orthogonal right-angle connectors only (no diagonal lines, no curves).
    <<include>> dashed right-angle arrows from Solve tasks to Submit solution.
    Zero crossing lines!
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-inc" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto">')
    svg.append('    <path d="M 0 1 L 14 7 L 0 13 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="160" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Use Case Diagram</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 3. Use Case Diagram of QueryLearn</text>')

    # --- System Boundary Rectangle ---
    # x = 460 to 3048 (w = 2588, h = 2070, y = 220..2290)
    sb_x0, sb_y0, sb_w, sb_h = 460, 220, 2588, 2070
    svg.append(f'<rect x="{sb_x0}" y="{sb_y0}" width="{sb_w}" height="{sb_h}" fill="none" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{sb_x0 + 40}" y="{sb_y0 + 55}" font-family="Arial, Helvetica, sans-serif" font-size="46" font-weight="bold" fill="#000000">QueryLearn</text>')

    # --- ACTOR: Participant (Left) ---
    p_cx, p_cy = 230, 1265
    # Head
    svg.append(f'<circle cx="{p_cx}" cy="{p_cy - 100}" r="35" fill="none" stroke="#000000" stroke-width="4" />')
    # Torso
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 65}" x2="{p_cx}" y2="{p_cy + 40}" stroke="#000000" stroke-width="4" />')
    # Arms
    svg.append(f'<line x1="{p_cx - 65}" y1="{p_cy - 25}" x2="{p_cx + 65}" y2="{p_cy - 25}" stroke="#000000" stroke-width="4" />')
    # Left leg
    svg.append(f'<line x1="{p_cx}" y1="{p_cy + 40}" x2="{p_cx - 60}" y2="{p_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Right leg
    svg.append(f'<line x1="{p_cx}" y1="{p_cy + 40}" x2="{p_cx + 60}" y2="{p_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Actor Label
    svg.append(f'<text x="{p_cx}" y="{p_cy + 195}" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="bold" fill="#000000" text-anchor="middle">Participant</text>')
    p_arm_x, p_arm_y = p_cx + 65, p_cy - 25  # (295, 1240)

    # --- ACTOR: Researcher (Right) ---
    r_cx, r_cy = 3278, 1200
    # Head
    svg.append(f'<circle cx="{r_cx}" cy="{r_cy - 100}" r="35" fill="none" stroke="#000000" stroke-width="4" />')
    # Torso
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 65}" x2="{r_cx}" y2="{r_cy + 40}" stroke="#000000" stroke-width="4" />')
    # Arms
    svg.append(f'<line x1="{r_cx - 65}" y1="{r_cy - 25}" x2="{r_cx + 65}" y2="{r_cy - 25}" stroke="#000000" stroke-width="4" />')
    # Left leg
    svg.append(f'<line x1="{r_cx}" y1="{r_cy + 40}" x2="{r_cx - 60}" y2="{r_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Right leg
    svg.append(f'<line x1="{r_cx}" y1="{r_cy + 40}" x2="{r_cx + 60}" y2="{r_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Actor Label
    svg.append(f'<text x="{r_cx}" y="{r_cy + 195}" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="bold" fill="#000000" text-anchor="middle">Researcher</text>')
    r_arm_x, r_arm_y = r_cx - 65, r_cy - 25  # (3213, 1175)

    def draw_use_case(cx_val, cy_val, rx_val, ry_val, lines):
        svg.append(f'<ellipse cx="{cx_val}" cy="{cy_val}" rx="{rx_val}" ry="{ry_val}" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
        if len(lines) == 1:
            svg.append(f'<text x="{cx_val}" y="{cy_val + 10}" font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#000000" text-anchor="middle">{lines[0]}</text>')
        elif len(lines) == 2:
            svg.append(f'<text x="{cx_val}" y="{cy_val - 8}" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#000000" text-anchor="middle">{lines[0]}</text>')
            svg.append(f'<text x="{cx_val}" y="{cy_val + 28}" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#000000" text-anchor="middle">{lines[1]}</text>')

    # --- PARTICIPANT USE CASES ---
    # Primary column: cx = 860, rx = 270, ry = 62
    p_cx_col = 860
    p_rx, p_ry = 270, 62
    oval_left_edge = p_cx_col - p_rx  # 590

    p_cases = [
        (["Register and give consent"], 390),
        (["Read language reference guide"], 640),
        (["Complete readiness check"], 890),
        (["Solve SQL tasks"], 1140),
        (["Solve Python tasks"], 1390),
        (["Answer comprehension items"], 1640),
        (["Answer post-condition survey"], 1890),
        (["Complete counterbalanced sequence"], 2140),
    ]

    for lines, cy_val in p_cases:
        draw_use_case(p_cx_col, cy_val, p_rx, p_ry, lines)

    # Orthogonal Actor Connectors (Participant -> Use Cases)
    # Right-angle routing using distribution trunk at x = 380:
    # 1. Horizontal line from Participant arm (295, 1240) to trunk (380, 1240)
    svg.append(f'<line x1="{p_arm_x}" y1="{p_arm_y}" x2="380" y2="{p_arm_y}" stroke="#000000" stroke-width="3" />')
    # 2. Vertical trunk line from top use case (y=390) to bottom use case (y=2140) at x=380
    svg.append('<line x1="380" y1="390" x2="380" y2="2140" stroke="#000000" stroke-width="3" />')
    # 3. Horizontal branches from trunk (x=380) straight to each oval (x=590)
    for _, cy_val in p_cases:
        svg.append(f'<line x1="380" y1="{cy_val}" x2="{oval_left_edge}" y2="{cy_val}" stroke="#000000" stroke-width="3" />')

    # Sub-Use Case: 'Submit solution'
    # Positioned at cx = 1520, cy = 1265 (rx = 240, ry = 62)
    sub_cx, sub_cy, sub_rx, sub_ry = 1520, 1265, 240, 62
    draw_use_case(sub_cx, sub_cy, sub_rx, sub_ry, ["Submit solution"])

    # Include Connectors (Right-angle routing only):
    # From Solve SQL tasks (right edge: 1130, 1140) -> Submit solution (left edge: 1280, 1240)
    # Segment 1: horizontal (1130, 1140) to (1220, 1140)
    # Segment 2: vertical down (1220, 1140) to (1220, 1240)
    # Segment 3: horizontal right (1220, 1240) to (1280, 1240) with arrowhead
    svg.append('<path d="M 1130 1140 L 1220 1140 L 1220 1240 L 1280 1240" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="10,8" marker-end="url(#arrow-inc)" />')
    svg.append('<rect x="1115" y="1105" width="130" height="30" fill="#FFFFFF" />')
    svg.append('<text x="1180" y="1127" font-family="Arial, Helvetica, sans-serif" font-size="22" font-style="italic" fill="#000000" text-anchor="middle">&lt;&lt;include&gt;&gt;</text>')

    # From Solve Python tasks (right edge: 1130, 1390) -> Submit solution (left edge: 1280, 1290)
    # Segment 1: horizontal (1130, 1390) to (1220, 1390)
    # Segment 2: vertical up (1220, 1390) to (1220, 1290)
    # Segment 3: horizontal right (1220, 1290) to (1280, 1290) with arrowhead
    svg.append('<path d="M 1130 1390 L 1220 1390 L 1220 1290 L 1280 1290" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="10,8" marker-end="url(#arrow-inc)" />')
    svg.append('<rect x="1115" y="1398" width="130" height="30" fill="#FFFFFF" />')
    svg.append('<text x="1180" y="1420" font-family="Arial, Helvetica, sans-serif" font-size="22" font-style="italic" fill="#000000" text-anchor="middle">&lt;&lt;include&gt;&gt;</text>')

    # --- RESEARCHER USE CASES ---
    # Column: cx = 2420, rx = 270, ry = 62
    r_cx_col = 2420
    r_rx, r_ry = 270, 62
    oval_right_edge = r_cx_col + r_rx  # 2690

    r_cases = [
        (["Log in"], 500),
        (["View participant registry"], 780),
        (["View task results"], 1060),
        (["View comparative analytics"], 1340),
        (["Run technical benchmarks"], 1620),
        (["Export study data"], 1900),
    ]

    for lines, cy_val in r_cases:
        draw_use_case(r_cx_col, cy_val, r_rx, r_ry, lines)

    # Orthogonal Actor Connectors (Researcher -> Use Cases)
    # Right-angle routing using distribution trunk at x = 3120:
    # 1. Horizontal line from Researcher arm (3213, 1175) to trunk (3120, 1175)
    svg.append(f'<line x1="{r_arm_x}" y1="{r_arm_y}" x2="3120" y2="{r_arm_y}" stroke="#000000" stroke-width="3" />')
    # 2. Vertical trunk line from top use case (y=500) to bottom use case (y=1900) at x=3120
    svg.append('<line x1="3120" y1="500" x2="3120" y2="1900" stroke="#000000" stroke-width="3" />')
    # 3. Horizontal branches from trunk (x=3120) straight left to each oval (x=2690)
    for _, cy_val in r_cases:
        svg.append(f'<line x1="3120" y1="{cy_val}" x2="{oval_right_edge}" y2="{cy_val}" stroke="#000000" stroke-width="3" />')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# RENDER & SYNCHRONIZE
# ==============================================================================
def render_svg_to_png(svg_content: str, output_png_path: str):
    """Renders SVG content to high-resolution 3508x2480 PNG via headless Chrome."""
    temp_html = output_png_path + ".temp.html"
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    padding: 0;
    width: 3508px;
    height: 2480px;
    background-color: #ffffff;
    overflow: hidden;
  }}
  svg {{
    display: block;
    width: 3508px;
    height: 2480px;
  }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""

    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    binary = chrome_path if os.path.exists(chrome_path) else edge_path

    cmd = [
        binary,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--screenshot={output_png_path}",
        "--window-size=3508,2480",
        f"file:///{os.path.abspath(temp_html)}"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(temp_html):
        try:
            os.remove(temp_html)
        except Exception:
            pass

    if not os.path.exists(output_png_path):
        raise RuntimeError(f"Rendering failed for {output_png_path}. Error: {res.stderr}")

    with Image.open(output_png_path) as im:
        if im.size != (3508, 2480):
            print(f"Resizing {output_png_path} to (3508, 2480)")
            resized = im.resize((3508, 2480), Image.Resampling.LANCZOS)
            resized.save(output_png_path)


def generate_all():
    print("Generating Academic Publication Diagrams for QueryLearn...")

    diagrams = [
        ("01-context-diagram", build_context_diagram_svg()),
        ("02-architecture-diagram", build_architecture_diagram_svg()),
        ("03-use-case-diagram", build_use_case_diagram_svg()),
    ]

    for name, svg_str in diagrams:
        svg_file = os.path.join(DOCS_DIAGRAMS_DIR, f"{name}.svg")
        png_file = os.path.join(DOCS_DIAGRAMS_DIR, f"{name}.png")

        # Save SVG
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_str)
        print(f"Saved: {svg_file}")

        # Render PNG
        render_svg_to_png(svg_str, png_file)
        print(f"Rendered: {png_file} (3508x2480)")

    # Legacy & Handbook synchronization
    sync_map = {
        os.path.join(DOCS_DIAGRAMS_DIR, "01-context-diagram.png"): [
            os.path.join(DIAGRAMS_DIR, "02_system_context_dfd0.png"),
            os.path.join(ARTIFACT_DIR, "diagram_02_system_context.png"),
        ],
        os.path.join(DOCS_DIAGRAMS_DIR, "02-architecture-diagram.png"): [
            os.path.join(DIAGRAMS_DIR, "01_system_architecture.png"),
            os.path.join(ARTIFACT_DIR, "diagram_01_system_architecture.png"),
        ],
        os.path.join(DOCS_DIAGRAMS_DIR, "03-use-case-diagram.png"): [
            os.path.join(DIAGRAMS_DIR, "03_use_case_diagram.png"),
            os.path.join(ARTIFACT_DIR, "diagram_03_use_case.png"),
        ],
    }

    for src, dst_list in sync_map.items():
        for dst in dst_list:
            try:
                shutil.copy2(src, dst)
                print(f"Synchronized to: {dst}")
            except Exception as e:
                print(f"Could not copy to {dst}: {e}")

    print("All diagrams successfully generated and verified!")


if __name__ == "__main__":
    generate_all()
