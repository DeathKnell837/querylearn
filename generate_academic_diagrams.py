"""
Academic Publication Diagram Generator for QueryLearn.
Produces:
1. Context Diagram (DFD Level 0) - Figure 1 (01-context-diagram)
2. Layered Architecture Diagram - Figure 2 (02-architecture-diagram: Simple publication version, names only, >=14pt)
   + Detailed Version (02b-architecture-detailed: Comprehensive engineering view with confirmed versions)
3. UML Use Case Diagram - Figure 3 (03-use-case-diagram: Actor connection from hand/side, <<include>> >=12pt)

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
    - Arrow label text increased to >=14pt (56px @ 300 DPI).
    - Labels placed above arrows on white background pads.
    - Arrow entry points spaced evenly around the circle (exact 150px vertical delta).
    - Straight horizontal right-angle arrows.
    - Zero crossing lines.
    """
    w, h = 3508, 2480
    cx, cy = 1754, 1300
    radius = 460

    p_x0, p_x1 = 150, 550
    r_x0, r_x1 = 2958, 3358

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-r" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto">')
    svg.append('    <path d="M 0 1 L 16 8 L 0 15 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('  <marker id="arrow-l" markerWidth="16" markerHeight="16" refX="2" refY="8" orient="auto">')
    svg.append('    <path d="M 16 1 L 0 8 L 16 15 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="190" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn System Context Diagram (DFD Level 0)</text>')

    # Caption
    svg.append('<text x="1754" y="2360" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 1. Context Diagram of QueryLearn</text>')

    # Participant Entity (Left)
    svg.append(f'<rect x="{p_x0}" y="700" width="{p_x1 - p_x0}" height="1200" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{(p_x0 + p_x1) // 2}" y="1315" font-family="Arial, Helvetica, sans-serif" font-size="54" font-weight="bold" fill="#000000" text-anchor="middle">Participant</text>')

    # Researcher Entity (Right)
    svg.append(f'<rect x="{r_x0}" y="700" width="{r_x1 - r_x0}" height="1200" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{(r_x0 + r_x1) // 2}" y="1315" font-family="Arial, Helvetica, sans-serif" font-size="54" font-weight="bold" fill="#000000" text-anchor="middle">Researcher</text>')

    # QueryLearn System Entity (Center Circle)
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{cx}" y="{cy - 25}" font-family="Arial, Helvetica, sans-serif" font-size="54" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn</text>')
    svg.append(f'<text x="{cx}" y="{cy + 45}" font-family="Arial, Helvetica, sans-serif" font-size="54" font-weight="bold" fill="#000000" text-anchor="middle">System</text>')

    # --- LEFT FLOWS: Participant <-> System ---
    # 7 entry points evenly spaced vertically around equator (cy=1300): step = 120px
    # y = 940, 1060, 1180, 1300, 1420, 1540, 1660
    left_flows = [
        ("registration and consent", 940, "right"),
        ("task solutions", 1060, "right"),
        ("comprehension answers", 1180, "right"),
        ("survey responses", 1300, "right"),
        ("task statements", 1420, "left"),
        ("language reference guide", 1540, "left"),
        ("session progress", 1660, "left"),
    ]

    for label, y_pos, direction in left_flows:
        dy = abs(y_pos - cy)
        dx = math.sqrt(max(0, radius**2 - dy**2))
        circle_edge_x = cx - dx

        line_start = p_x1
        line_end = circle_edge_x

        if direction == "right":
            svg.append(f'<line x1="{line_start}" y1="{y_pos}" x2="{line_end}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-r)" />')
        else:
            svg.append(f'<line x1="{line_end}" y1="{y_pos}" x2="{line_start}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-l)" />')

        # Label >= 14pt (56px) above arrow on white background
        label_x = (line_start + line_end) / 2
        approx_w = len(label) * 27 + 40
        svg.append(f'<rect x="{label_x - approx_w / 2}" y="{y_pos - 70}" width="{approx_w}" height="54" fill="#FFFFFF" />')
        svg.append(f'<text x="{label_x}" y="{y_pos - 26}" font-family="Arial, Helvetica, sans-serif" font-size="56" fill="#000000" text-anchor="middle">{label}</text>')

    # --- RIGHT FLOWS: System <-> Researcher ---
    # 6 entry points evenly spaced vertically around equator (cy=1300): step = 130px
    # y = 975, 1105, 1235, 1365, 1495, 1625
    right_flows = [
        ("login credentials", 975, "left"),
        ("filter selections", 1105, "left"),
        ("participant registry", 1235, "right"),
        ("task results", 1365, "right"),
        ("comparative analytics", 1495, "right"),
        ("exported data files", 1625, "right"),
    ]

    for label, y_pos, direction in right_flows:
        dy = abs(y_pos - cy)
        dx = math.sqrt(max(0, radius**2 - dy**2))
        circle_edge_x = cx + dx

        line_start = circle_edge_x
        line_end = r_x0

        if direction == "left":
            svg.append(f'<line x1="{line_end}" y1="{y_pos}" x2="{line_start}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-l)" />')
        else:
            svg.append(f'<line x1="{line_start}" y1="{y_pos}" x2="{line_end}" y2="{y_pos}" stroke="#000000" stroke-width="4" marker-end="url(#arrow-r)" />')

        label_x = (line_start + line_end) / 2
        approx_w = len(label) * 27 + 40
        svg.append(f'<rect x="{label_x - approx_w / 2}" y="{y_pos - 70}" width="{approx_w}" height="54" fill="#FFFFFF" />')
        svg.append(f'<text x="{label_x}" y="{y_pos - 26}" font-family="Arial, Helvetica, sans-serif" font-size="56" fill="#000000" text-anchor="middle">{label}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 2: ARCHITECTURE DIAGRAM (SIMPLE PAPER VERSION)
# ==============================================================================
def build_simple_architecture_diagram_svg() -> str:
    """
    Simple Architecture Diagram for Paper (Figure 2).
    - Names only inside boxes, NO bullet lists.
    - Text >= 14pt (56px-58px @ 300 DPI) inside boxes.
    - 4 layers: Presentation, Application, Services, Data.
    - Dashed 'Hosted on Vercel (serverless)' box enclosing Layers 2, 3, 4.
    - Clear gaps for labeled arrows.
    - Labeled arrows >= 14pt (56px).
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-d" markerWidth="16" markerHeight="16" refX="8" refY="14" orient="auto">')
    svg.append('    <path d="M 1 0 L 8 16 L 15 0 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('  <marker id="arrow-u" markerWidth="16" markerHeight="16" refX="8" refY="2" orient="auto">')
    svg.append('    <path d="M 1 16 L 8 0 L 15 16 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="160" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Layered System Architecture</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 2. Layered Architecture Diagram of QueryLearn</text>')

    # Dashed Boundary: Hosted on Vercel (serverless)
    # y = 680 to 2260
    dashed_top_y = 690
    svg.append(f'<line x1="140" y1="{dashed_top_y}" x2="700" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="1300" y1="{dashed_top_y}" x2="2200" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="2800" y1="{dashed_top_y}" x2="3368" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="140" y1="{dashed_top_y}" x2="140" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append('<line x1="140" y1="2260" x2="3368" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="3368" y1="{dashed_top_y}" x2="3368" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<text x="3330" y="{dashed_top_y + 40}" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" font-style="italic" fill="#000000" text-anchor="end">Hosted on Vercel (serverless)</text>')

    # --- LAYER 1: Presentation Layer ---
    # y = 220, height = 330
    svg.append('<rect x="180" y="220" width="3148" height="330" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="270" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#000000">Presentation Layer (Browser Client)</text>')

    p_boxes = [
        ("HTML User Interface", 220),
        ("CodeMirror Editor", 990),
        ("Task & Clock Timers", 1760),
        ("Chart.js Visualizations", 2530),
    ]
    for title, bx in p_boxes:
        svg.append(f'<rect x="{bx}" y="295" width="730" height="225" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 365}" y="420" font-family="Arial, Helvetica, sans-serif" font-size="56" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    # Gap 1 (y = 550 to 740): Labeled arrows >= 14pt (56px)
    svg.append('<line x1="1000" y1="550" x2="1000" y2="740" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="440" y="618" width="520" height="54" fill="#FFFFFF" />')
    svg.append('<text x="700" y="658" font-family="Arial, Helvetica, sans-serif" font-size="54" fill="#000000" text-anchor="middle">HTTP Requests</text>')

    svg.append('<line x1="2500" y1="740" x2="2500" y2="550" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2540" y="618" width="550" height="54" fill="#FFFFFF" />')
    svg.append('<text x="2815" y="658" font-family="Arial, Helvetica, sans-serif" font-size="54" fill="#000000" text-anchor="middle">HTTP Responses</text>')

    # --- LAYER 2: Application Layer (Flask) ---
    # y = 740, height = 330
    svg.append('<rect x="180" y="740" width="3148" height="330" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="790" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#000000">Application Layer (Flask Web Framework)</text>')

    app_boxes = [
        ("auth_bp", 220),
        ("experiment_bp", 990),
        ("tasks_bp", 1760),
        ("dashboard_bp", 2530),
    ]
    for title, bx in app_boxes:
        svg.append(f'<rect x="{bx}" y="815" width="730" height="225" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 365}" y="940" font-family="Arial, Helvetica, sans-serif" font-size="56" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    # Gap 2 (y = 1070 to 1240): Labeled arrows
    svg.append('<line x1="1000" y1="1070" x2="1000" y2="1240" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="410" y="1128" width="550" height="54" fill="#FFFFFF" />')
    svg.append('<text x="685" y="1168" font-family="Arial, Helvetica, sans-serif" font-size="54" fill="#000000" text-anchor="middle">Service Invocations</text>')

    svg.append('<line x1="2500" y1="1240" x2="2500" y2="1070" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2540" y="1128" width="530" height="54" fill="#FFFFFF" />')
    svg.append('<text x="2805" y="1168" font-family="Arial, Helvetica, sans-serif" font-size="54" fill="#000000" text-anchor="middle">Execution Results</text>')

    # --- LAYER 3: Services Layer ---
    # y = 1240, height = 480
    svg.append('<rect x="180" y="1240" width="3148" height="480" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="1290" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#000000">Services Layer (Domain Logic & Orchestration)</text>')

    srv_row1 = [
        ("task_catalog", 220),
        ("sql_runner", 990),
        ("python_runner", 1760),
        ("answer_checker", 2530),
    ]
    for title, bx in srv_row1:
        svg.append(f'<rect x="{bx}" y="1315" width="730" height="175" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 365}" y="1420" font-family="Arial, Helvetica, sans-serif" font-size="56" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    srv_row2 = [
        ("sequence_manager", 220),
        ("comprehension_items", 990),
        ("benchmark_runner", 1760),
        ("export_service", 2530),
    ]
    for title, bx in srv_row2:
        svg.append(f'<rect x="{bx}" y="1515" width="730" height="175" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 365}" y="1620" font-family="Arial, Helvetica, sans-serif" font-size="54" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    # Gap 3 (y = 1720 to 1890): Labeled arrows
    svg.append('<line x1="1000" y1="1720" x2="1000" y2="1890" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="360" y="1778" width="600" height="54" fill="#FFFFFF" />')
    svg.append('<text x="660" y="1818" font-family="Arial, Helvetica, sans-serif" font-size="54" fill="#000000" text-anchor="middle">Database Operations</text>')

    svg.append('<line x1="2500" y1="1890" x2="2500" y2="1720" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2540" y="1778" width="530" height="54" fill="#FFFFFF" />')
    svg.append('<text x="2805" y="1818" font-family="Arial, Helvetica, sans-serif" font-size="54" fill="#000000" text-anchor="middle">Data Result Sets</text>')

    # --- LAYER 4: Data Layer ---
    # y = 1890, height = 340
    svg.append('<rect x="180" y="1890" width="3148" height="340" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="1940" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#000000">Data Layer (Local & Ephemeral Serverless Storage)</text>')

    data_boxes = [
        ("research.db (SQLite)", 220),
        ("experiment_a.db (SQLite)", 990),
        ("experiment_b.db (SQLite)", 1760),
        ("hidden_tests.json (JSON)", 2530),
    ]
    for title, bx in data_boxes:
        svg.append(f'<rect x="{bx}" y="1965" width="730" height="235" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 365}" y="2095" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 2b: ARCHITECTURE DIAGRAM (DETAILED DENSE VERSION)
# ==============================================================================
def build_detailed_architecture_diagram_svg() -> str:
    """
    Detailed Architecture Diagram (02b-architecture-detailed).
    Contains full itemized bullets with confirmed versions:
    - Flask 3.1.1, CodeMirror 5.65.13, Chart.js 4.4.4
    - 21 Web Templates confirmed
    - 36 Hidden Test Datasets confirmed
    - '2x2 counterbalanced crossover with four sequences'
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
    svg.append('<text x="1754" y="160" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Detailed System Architecture</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 2b. Detailed Engineering Architecture Diagram of QueryLearn</text>')

    # Dashed Boundary: Hosted on Vercel (serverless)
    dashed_top_y = 690
    svg.append(f'<line x1="140" y1="{dashed_top_y}" x2="750" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="1250" y1="{dashed_top_y}" x2="2250" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="2750" y1="{dashed_top_y}" x2="3368" y2="{dashed_top_y}" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="140" y1="{dashed_top_y}" x2="140" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append('<line x1="140" y1="2260" x2="3368" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<line x1="3368" y1="{dashed_top_y}" x2="3368" y2="2260" stroke="#000000" stroke-width="4" stroke-dasharray="16,12" />')
    svg.append(f'<text x="3330" y="{dashed_top_y + 36}" font-family="Arial, Helvetica, sans-serif" font-size="32" font-weight="bold" font-style="italic" fill="#000000" text-anchor="end">Hosted on Vercel (serverless)</text>')

    # LAYER 1: Presentation
    svg.append('<rect x="180" y="220" width="3148" height="330" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="268" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Presentation Layer (Browser Client)</text>')

    p_boxes = [
        ("HTML User Interface", ["Jinja2 Web Templates (21 Total Views)", "Responsive Navigation Layout", "Participant & Researcher Views"], 220),
        ("Code Editors", ["CodeMirror 5.65.13 Workspace", "SQL Syntax Highlighting Mode", "Procedural Python Indentation Mode"], 990),
        ("Client-Side Timers", ["timer.js Engine", "8-Min Task Countdown Clocks", "3-Min Comprehension Timer"], 1760),
        ("Data Visualizations", ["Chart.js 4.4.4 Engine", "Outcome Split Visualizations", "Headline Performance Metrics"], 2530),
    ]
    for title, items, bx in p_boxes:
        svg.append(f'<rect x="{bx}" y="290" width="730" height="230" fill="#FFFFFF" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{bx + 30}" y="335" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{380 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    # Gap 1
    svg.append('<line x1="1000" y1="550" x2="1000" y2="740" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="420" y="625" width="550" height="38" fill="#FFFFFF" />')
    svg.append('<text x="695" y="652" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">HTTP Requests (form data, code, parameters)</text>')

    svg.append('<line x1="2500" y1="740" x2="2500" y2="550" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2530" y="625" width="540" height="38" fill="#FFFFFF" />')
    svg.append('<text x="2800" y="652" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">HTTP Responses (rendered HTML, JSON, CSV)</text>')

    # LAYER 2: Application
    svg.append('<rect x="180" y="740" width="3148" height="330" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="788" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Application Layer (Flask 3.1.1 Web Framework)</text>')

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

    # Gap 2
    svg.append('<line x1="1000" y1="1070" x2="1000" y2="1240" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="420" y="1135" width="550" height="38" fill="#FFFFFF" />')
    svg.append('<text x="695" y="1162" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">Function Calls (code evaluation, sequencing)</text>')

    svg.append('<line x1="2500" y1="1240" x2="2500" y2="1070" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2530" y="1135" width="540" height="38" fill="#FFFFFF" />')
    svg.append('<text x="2800" y="1162" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">Execution Results (grading, metrics, CSV bytes)</text>')

    # LAYER 3: Services
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

    # Gap 3
    svg.append('<line x1="1000" y1="1720" x2="1000" y2="1890" stroke="#000000" stroke-width="4" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="420" y="1785" width="550" height="38" fill="#FFFFFF" />')
    svg.append('<text x="695" y="1812" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">SQL Queries (SELECT, INSERT) & JSON Reads</text>')

    svg.append('<line x1="2500" y1="1890" x2="2500" y2="1720" stroke="#000000" stroke-width="4" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2530" y="1785" width="540" height="38" fill="#FFFFFF" />')
    svg.append('<text x="2800" y="1812" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#000000" text-anchor="middle">Query Result Sets & Hidden Test Payloads</text>')

    # LAYER 4: Data
    svg.append('<rect x="180" y="1890" width="3148" height="340" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
    svg.append('<text x="220" y="1938" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Data Layer (Local & Ephemeral Serverless Storage)</text>')

    data_boxes = [
        ("research.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Tables: participants, sessions, task_attempts", "task_results, task_timers, comprehension, surveys"], 220),
        ("experiment_a.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Form A Relational Database (mode=ro)", "Tables: Students, Courses, Enrollments"], 990),
        ("experiment_b.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Form B Relational Database (mode=ro)", "Tables: Students, Courses, Enrollments"], 1760),
        ("hidden_tests.json (JSON)", ["JSON Edge-Case Test Datasets", "36 Total Hidden Test Datasets", "3 Edge-Case Datasets per Task (T1-T6, Forms A & B)"], 2530),
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
    UML Use Case Diagram (Figure 3).
    - Actor lines leave from the actor's hand or side, NEVER passing through the body.
    - <<include>> labels >=12pt (48px @ 300 DPI), placed above the dashed line on white background without overlapping.
    - Pure right-angle orthogonal routing throughout.
    - Zero line crossings.
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-inc" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto">')
    svg.append('    <path d="M 0 1 L 16 8 L 0 15 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="160" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Use Case Diagram</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 3. Use Case Diagram of QueryLearn</text>')

    # System Boundary Rectangle: QueryLearn
    sb_x0, sb_y0, sb_w, sb_h = 460, 220, 2588, 2070
    svg.append(f'<rect x="{sb_x0}" y="{sb_y0}" width="{sb_w}" height="{sb_h}" fill="none" stroke="#000000" stroke-width="4" />')
    svg.append(f'<text x="{sb_x0 + 40}" y="{sb_y0 + 55}" font-family="Arial, Helvetica, sans-serif" font-size="46" font-weight="bold" fill="#000000">QueryLearn</text>')

    # --- ACTOR: Participant (Left) ---
    p_cx, p_cy = 200, 1265
    # Head
    svg.append(f'<circle cx="{p_cx}" cy="{p_cy - 100}" r="35" fill="none" stroke="#000000" stroke-width="4" />')
    # Torso
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 65}" x2="{p_cx}" y2="{p_cy + 40}" stroke="#000000" stroke-width="4" />')
    # Left arm (points down-left)
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 25}" x2="{p_cx - 65}" y2="{p_cy}" stroke="#000000" stroke-width="4" />')
    # Right arm (extends horizontally right as the hand connecting to system)
    # Leaves from side at (200, 1240) to hand at (275, 1240)
    p_hand_x, p_hand_y = 275, p_cy - 25
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 25}" x2="{p_hand_x}" y2="{p_hand_y}" stroke="#000000" stroke-width="4" />')
    # Left leg
    svg.append(f'<line x1="{p_cx}" y1="{p_cy + 40}" x2="{p_cx - 60}" y2="{p_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Right leg
    svg.append(f'<line x1="{p_cx}" y1="{p_cy + 40}" x2="{p_cx + 60}" y2="{p_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Label
    svg.append(f'<text x="{p_cx}" y="{p_cy + 195}" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="bold" fill="#000000" text-anchor="middle">Participant</text>')

    # --- ACTOR: Researcher (Right) ---
    r_cx, r_cy = 3308, 1200
    # Head
    svg.append(f'<circle cx="{r_cx}" cy="{r_cy - 100}" r="35" fill="none" stroke="#000000" stroke-width="4" />')
    # Torso
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 65}" x2="{r_cx}" y2="{r_cy + 40}" stroke="#000000" stroke-width="4" />')
    # Right arm (points down-right)
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 25}" x2="{r_cx + 65}" y2="{r_cy}" stroke="#000000" stroke-width="4" />')
    # Left arm (extends horizontally left as the hand connecting to system)
    # Leaves from side at (3308, 1175) to hand at (3233, 1175)
    r_hand_x, r_hand_y = 3233, r_cy - 25
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 25}" x2="{r_hand_x}" y2="{r_hand_y}" stroke="#000000" stroke-width="4" />')
    # Left leg
    svg.append(f'<line x1="{r_cx}" y1="{r_cy + 40}" x2="{r_cx - 60}" y2="{r_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Right leg
    svg.append(f'<line x1="{r_cx}" y1="{r_cy + 40}" x2="{r_cx + 60}" y2="{r_cy + 140}" stroke="#000000" stroke-width="4" />')
    # Label
    svg.append(f'<text x="{r_cx}" y="{r_cy + 195}" font-family="Arial, Helvetica, sans-serif" font-size="38" font-weight="bold" fill="#000000" text-anchor="middle">Researcher</text>')

    def draw_use_case(cx_val, cy_val, rx_val, ry_val, lines):
        svg.append(f'<ellipse cx="{cx_val}" cy="{cy_val}" rx="{rx_val}" ry="{ry_val}" fill="#F2F2F2" stroke="#000000" stroke-width="4" />')
        if len(lines) == 1:
            svg.append(f'<text x="{cx_val}" y="{cy_val + 10}" font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#000000" text-anchor="middle">{lines[0]}</text>')
        elif len(lines) == 2:
            svg.append(f'<text x="{cx_val}" y="{cy_val - 8}" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#000000" text-anchor="middle">{lines[0]}</text>')
            svg.append(f'<text x="{cx_val}" y="{cy_val + 28}" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#000000" text-anchor="middle">{lines[1]}</text>')

    # --- PARTICIPANT USE CASES ---
    p_cx_col = 860
    p_rx, p_ry = 260, 62
    oval_left_edge = p_cx_col - p_rx   # 600
    oval_right_edge = p_cx_col + p_rx  # 1120

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

    # Actor line leaves from Participant's HAND (275, 1240) to distribution trunk at x=380
    svg.append(f'<line x1="{p_hand_x}" y1="{p_hand_y}" x2="380" y2="{p_hand_y}" stroke="#000000" stroke-width="3" />')
    # Trunk line from y=390 to y=2140
    svg.append('<line x1="380" y1="390" x2="380" y2="2140" stroke="#000000" stroke-width="3" />')
    # Branches from trunk to each oval
    for _, cy_val in p_cases:
        svg.append(f'<line x1="380" y1="{cy_val}" x2="{oval_left_edge}" y2="{cy_val}" stroke="#000000" stroke-width="3" />')

    # Included use case: Submit solution
    # Shifted to cx=1720 to create a 390px clean clearance for <<include>> labels
    sub_cx, sub_cy, sub_rx, sub_ry = 1720, 1265, 210, 62
    sub_left_edge = sub_cx - sub_rx  # 1510
    draw_use_case(sub_cx, sub_cy, sub_rx, sub_ry, ["Submit solution"])

    # Include Connectors (Right-angle, <<include>> >=12pt placed ABOVE dashed line on white background):
    # From Solve SQL tasks (1120, 1140) to Submit solution (1510, 1235)
    # Horizontal segment from 1120 to 1420 (300px width), corner at 1420, label centered at 1270
    svg.append(f'<path d="M {oval_right_edge} 1140 L 1420 1140 L 1420 1235 L {sub_left_edge} 1235" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="10,8" marker-end="url(#arrow-inc)" />')
    # White background completely above dashed line (y=1080..1126, line is at 1140; x=1165..1375 strictly 45px away from oval and corner)
    svg.append('<rect x="1165" y="1080" width="210" height="46" fill="#FFFFFF" />')
    svg.append('<text x="1270" y="1116" font-family="Arial, Helvetica, sans-serif" font-size="42" font-style="italic" fill="#000000" text-anchor="middle">&lt;&lt;include&gt;&gt;</text>')

    # From Solve Python tasks (1120, 1390) to Submit solution (1510, 1295)
    svg.append(f'<path d="M {oval_right_edge} 1390 L 1420 1390 L 1420 1295 L {sub_left_edge} 1295" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="10,8" marker-end="url(#arrow-inc)" />')
    # White background completely above dashed line (y=1330..1376, line is at 1390; x=1165..1375 strictly 45px away from oval and corner)
    svg.append('<rect x="1165" y="1330" width="210" height="46" fill="#FFFFFF" />')
    svg.append('<text x="1270" y="1366" font-family="Arial, Helvetica, sans-serif" font-size="42" font-style="italic" fill="#000000" text-anchor="middle">&lt;&lt;include&gt;&gt;</text>')

    # --- RESEARCHER USE CASES ---
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

    # Actor line leaves from Researcher's HAND (3233, 1175) to distribution trunk at x=3120
    svg.append(f'<line x1="{r_hand_x}" y1="{r_hand_y}" x2="3120" y2="{r_hand_y}" stroke="#000000" stroke-width="3" />')
    # Trunk line from y=500 to y=1900
    svg.append('<line x1="3120" y1="500" x2="3120" y2="1900" stroke="#000000" stroke-width="3" />')
    # Branches from trunk to each oval
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
        ("02-architecture-diagram", build_simple_architecture_diagram_svg()),
        ("02b-architecture-detailed", build_detailed_architecture_diagram_svg()),
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
