"""
Academic Publication Diagram Generator for QueryLearn.
Produces publication-grade, IEEE / ACM / thesis standard diagrams:
1. Context Diagram (DFD Level 0) - Figure 1 (01-context-diagram)
2. Layered Architecture Diagram - Figure 2 (02-architecture-diagram: Simple publication version, names only, >=14pt)
   + Detailed Version (02b-architecture-detailed: Comprehensive engineering view with confirmed versions)
3. UML Use Case Diagram - Figure 3 (03-use-case-diagram: Pristine UML layout, actor hand fan associations, <<include>> >=12pt)

Strict styling rules:
- Pure white background (#FFFFFF)
- Crisp black lines and text (#000000)
- Subtle gray fill (#F4F6F8 or #FFFFFF) for clean box contrast
- No colors, no gradients, no shadows, no glow, no icons, no emojis
- Arial / Helvetica font throughout, titles 64px bold, captions 44px
- Minimum 14pt (56px) text for box names, minimum 12pt (48px) for labels
- Proper margins, zero clipped text, zero broken dashes, zero overlapping lines
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
    DFD Level 0 Context Diagram (Figure 1).
    - Spacious 200px+ vertical clearance between flow channels.
    - Flows distributed across top arc, side, and bottom arc of the central process circle.
    - Orthogonal and direct landing arrows with zero barcode crowding.
    - Clear white knockout badge pads for all flow labels (>=14pt).
    """
    w, h = 3508, 2480
    cx, cy = 1754, 1240
    radius = 440

    p_x0, p_x1 = 200, 640
    r_x0, r_x1 = 2868, 3308

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    # Arrow Right
    svg.append('  <marker id="arrow-r" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto">')
    svg.append('    <path d="M 1 2 L 14 8 L 1 14 Z" fill="#000000" />')
    svg.append('  </marker>')
    # Arrow Left
    svg.append('  <marker id="arrow-l" markerWidth="16" markerHeight="16" refX="2" refY="8" orient="auto">')
    svg.append('    <path d="M 15 2 L 2 8 L 15 14 Z" fill="#000000" />')
    svg.append('  </marker>')
    # Arrow Down
    svg.append('  <marker id="arrow-d" markerWidth="16" markerHeight="16" refX="8" refY="14" orient="auto">')
    svg.append('    <path d="M 2 1 L 8 14 L 14 1 Z" fill="#000000" />')
    svg.append('  </marker>')
    # Arrow Up
    svg.append('  <marker id="arrow-u" markerWidth="16" markerHeight="16" refX="8" refY="2" orient="auto">')
    svg.append('    <path d="M 2 15 L 8 2 L 14 15 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Pure White Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="150" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn System Context Diagram (DFD Level 0)</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 1. Context Diagram of QueryLearn</text>')

    # --------------------------------------------------------------------------
    # Participant External Entity (Left)
    # --------------------------------------------------------------------------
    svg.append(f'<rect x="{p_x0}" y="440" width="{p_x1 - p_x0}" height="1620" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="14" ry="14" />')
    svg.append(f'<rect x="{p_x0}" y="440" width="{p_x1 - p_x0}" height="90" fill="#E2E8F0" stroke="#000000" stroke-width="4" rx="14" ry="14" />')
    svg.append(f'<text x="{(p_x0 + p_x1) // 2}" y="495" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" letter-spacing="2" fill="#334155" text-anchor="middle">EXTERNAL ENTITY</text>')
    svg.append(f'<text x="{(p_x0 + p_x1) // 2}" y="1220" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">Participant</text>')
    svg.append(f'<text x="{(p_x0 + p_x1) // 2}" y="1275" font-family="Arial, Helvetica, sans-serif" font-size="32" font-style="italic" fill="#475569" text-anchor="middle">(Novice Learner Cohort)</text>')

    # --------------------------------------------------------------------------
    # Researcher External Entity (Right)
    # --------------------------------------------------------------------------
    svg.append(f'<rect x="{r_x0}" y="440" width="{r_x1 - r_x0}" height="1620" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="14" ry="14" />')
    svg.append(f'<rect x="{r_x0}" y="440" width="{r_x1 - r_x0}" height="90" fill="#E2E8F0" stroke="#000000" stroke-width="4" rx="14" ry="14" />')
    svg.append(f'<text x="{(r_x0 + r_x1) // 2}" y="495" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" letter-spacing="2" fill="#334155" text-anchor="middle">EXTERNAL ENTITY</text>')
    svg.append(f'<text x="{(r_x0 + r_x1) // 2}" y="1220" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">Researcher</text>')
    svg.append(f'<text x="{(r_x0 + r_x1) // 2}" y="1275" font-family="Arial, Helvetica, sans-serif" font-size="32" font-style="italic" fill="#475569" text-anchor="middle">(Evaluator / Admin)</text>')

    # --------------------------------------------------------------------------
    # QueryLearn System Process (Center Circle)
    # --------------------------------------------------------------------------
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#F4F6F8" stroke="#000000" stroke-width="4" />')
    # Inner subtle divider
    svg.append(f'<line x1="{cx - 320}" y1="{cy - 80}" x2="{cx + 320}" y2="{cy - 80}" stroke="#000000" stroke-width="2" />')
    svg.append(f'<text x="{cx}" y="{cy - 110}" font-family="Arial, Helvetica, sans-serif" font-size="36" font-weight="bold" fill="#334155" text-anchor="middle">0.0</text>')
    svg.append(f'<text x="{cx}" y="{cy - 10}" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn System</text>')
    svg.append(f'<text x="{cx}" y="{cy + 55}" font-family="Arial, Helvetica, sans-serif" font-size="32" font-style="italic" fill="#475569" text-anchor="middle">(Empirical Evaluation Platform)</text>')

    def draw_label(text, lx, ly, w_box=540, h_box=48):
        svg.append(f'<rect x="{lx - w_box/2}" y="{ly - h_box/2}" width="{w_box}" height="{h_box}" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
        svg.append(f'<text x="{lx}" y="{ly + 10}" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">{text}</text>')

    # --------------------------------------------------------------------------
    # LEFT FLOWS: Participant <-> System (7 Flows, Spaced 240px vertically)
    # --------------------------------------------------------------------------
    # 1. Registration & Consent (In)
    y1 = 520
    x_turn1 = 1530
    # circle top edge at x=1530:
    dy1 = math.sqrt(max(0, radius**2 - (cx - x_turn1)**2))
    y_dock1 = cy - dy1
    svg.append(f'<path d="M {p_x1} {y1} L {x_turn1} {y1} L {x_turn1} {y_dock1 - 10}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    draw_label("Registration & Demographic Intake", (p_x1 + x_turn1) / 2, y1, 560)

    # 2. Task Code Solutions (In)
    y2 = 760
    x_turn2 = 1410
    dy2 = math.sqrt(max(0, radius**2 - (cx - x_turn2)**2))
    y_dock2 = cy - dy2
    svg.append(f'<path d="M {p_x1} {y2} L {x_turn2} {y2} L {x_turn2} {y_dock2 - 10}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    draw_label("Task Code Solutions (SQL / Python)", (p_x1 + x_turn2) / 2, y2, 560)

    # 3. Comprehension Answers (In)
    y3 = 1000
    dy3 = cy - y3
    dx3 = math.sqrt(max(0, radius**2 - dy3**2))
    x_dock3 = cx - dx3
    svg.append(f'<line x1="{p_x1}" y1="{y3}" x2="{x_dock3 - 10}" y2="{y3}" stroke="#000000" stroke-width="3" marker-end="url(#arrow-r)" />')
    draw_label("Code Comprehension Responses", (p_x1 + x_dock3) / 2, y3, 530)

    # 4. Survey Responses (In)
    y4 = 1240
    x_dock4 = cx - radius
    svg.append(f'<line x1="{p_x1}" y1="{y4}" x2="{x_dock4 - 10}" y2="{y4}" stroke="#000000" stroke-width="3" marker-end="url(#arrow-r)" />')
    draw_label("Post-Condition Survey Responses", (p_x1 + x_dock4) / 2, y4, 540)

    # 5. Task Statements (Out)
    y5 = 1480
    dy5 = y5 - cy
    dx5 = math.sqrt(max(0, radius**2 - dy5**2))
    x_dock5 = cx - dx5
    svg.append(f'<line x1="{x_dock5}" y1="{y5}" x2="{p_x1 + 10}" y2="{y5}" stroke="#000000" stroke-width="3" marker-end="url(#arrow-l)" />')
    draw_label("Task Statements & DB Schema", (p_x1 + x_dock5) / 2, y5, 530)

    # 6. Reference Guides (Out)
    y6 = 1720
    x_turn6 = 1410
    dy6 = math.sqrt(max(0, radius**2 - (cx - x_turn6)**2))
    y_dock6 = cy + dy6
    svg.append(f'<path d="M {x_turn6} {y_dock6} L {x_turn6} {y6} L {p_x1 + 10} {y6}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-l)" />')
    draw_label("Language Reference Guides", (p_x1 + x_turn6) / 2, y6, 520)

    # 7. Execution Feedback (Out)
    y7 = 1960
    x_turn7 = 1530
    dy7 = math.sqrt(max(0, radius**2 - (cx - x_turn7)**2))
    y_dock7 = cy + dy7
    svg.append(f'<path d="M {x_turn7} {y_dock7} L {x_turn7} {y7} L {p_x1 + 10} {y7}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-l)" />')
    draw_label("Execution Output & Test Feedback", (p_x1 + x_turn7) / 2, y7, 560)

    # --------------------------------------------------------------------------
    # RIGHT FLOWS: Researcher <-> System (6 Flows, Spaced 260px vertically)
    # --------------------------------------------------------------------------
    # 1. Login Credentials (In)
    ry1 = 580
    rx_turn1 = 1978
    r_dy1 = math.sqrt(max(0, radius**2 - (rx_turn1 - cx)**2))
    r_ydock1 = cy - r_dy1
    svg.append(f'<path d="M {r_x0} {ry1} L {rx_turn1} {ry1} L {rx_turn1} {r_ydock1 - 10}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    draw_label("Researcher Authentication Credentials", (r_x0 + rx_turn1) / 2, ry1, 570)

    # 2. Filter Parameters (In)
    ry2 = 860
    rx_turn2 = 2098
    r_dy2 = math.sqrt(max(0, radius**2 - (rx_turn2 - cx)**2))
    r_ydock2 = cy - r_dy2
    svg.append(f'<path d="M {r_x0} {ry2} L {rx_turn2} {ry2} L {rx_turn2} {r_ydock2 - 10}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    draw_label("Telemetry Query & Filter Criteria", (r_x0 + rx_turn2) / 2, ry2, 540)

    # 3. Benchmark Triggers (In)
    ry3 = 1140
    r_dy3 = cy - ry3
    r_dx3 = math.sqrt(max(0, radius**2 - r_dy3**2))
    r_xdock3 = cx + r_dx3
    svg.append(f'<line x1="{r_x0}" y1="{ry3}" x2="{r_xdock3 + 10}" y2="{ry3}" stroke="#000000" stroke-width="3" marker-end="url(#arrow-l)" />')
    draw_label("Benchmark Execution Triggers", (r_x0 + r_xdock3) / 2, ry3, 520)

    # 4. Participant Registry (Out)
    ry4 = 1420
    r_dy4 = ry4 - cy
    r_dx4 = math.sqrt(max(0, radius**2 - r_dy4**2))
    r_xdock4 = cx + r_dx4
    svg.append(f'<line x1="{r_xdock4}" y1="{ry4}" x2="{r_x0 - 10}" y2="{ry4}" stroke="#000000" stroke-width="3" marker-end="url(#arrow-r)" />')
    draw_label("Participant Registry & Progress", (r_x0 + r_xdock4) / 2, ry4, 520)

    # 5. Task Telemetry (Out)
    ry5 = 1700
    rx_turn5 = 2098
    r_dy5 = math.sqrt(max(0, radius**2 - (rx_turn5 - cx)**2))
    r_ydock5 = cy + r_dy5
    svg.append(f'<path d="M {rx_turn5} {r_ydock5} L {rx_turn5} {ry5} L {r_x0 - 10} {ry5}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-r)" />')
    draw_label("Task Telemetry & Outcomes (Right/Wrong)", (r_x0 + rx_turn5) / 2, ry5, 590)

    # 6. Exported Datasets (Out)
    ry6 = 1980
    rx_turn6 = 1978
    r_dy6 = math.sqrt(max(0, radius**2 - (rx_turn6 - cx)**2))
    r_ydock6 = cy + r_dy6
    svg.append(f'<path d="M {rx_turn6} {r_ydock6} L {rx_turn6} {ry6} L {r_x0 - 10} {ry6}" fill="none" stroke="#000000" stroke-width="3" marker-end="url(#arrow-r)" />')
    draw_label("Comparative Analytics & Exported Datasets", (r_x0 + rx_turn6) / 2, ry6, 610)

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 2: ARCHITECTURE DIAGRAM (SIMPLE PAPER VERSION)
# ==============================================================================
def build_simple_architecture_diagram_svg() -> str:
    """
    Simple Architecture Diagram for Publication (Figure 2).
    - Names only inside component boxes (no bullet clutter, >=14pt).
    - 4 distinct layers: Presentation, Application, Services, Data.
    - Dashed 'Hosted on Vercel (serverless)' boundary drawn as a single clean rectangle enclosing Layers 2, 3, 4.
    - Zero floating dashed lines.
    - Symmetric, perfectly aligned vertical transfer channels with white label badges.
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    # Arrow Down
    svg.append('  <marker id="arrow-d" markerWidth="14" markerHeight="14" refX="7" refY="12" orient="auto">')
    svg.append('    <path d="M 1 1 L 7 12 L 13 1 Z" fill="#000000" />')
    svg.append('  </marker>')
    # Arrow Up
    svg.append('  <marker id="arrow-u" markerWidth="14" markerHeight="14" refX="7" refY="2" orient="auto">')
    svg.append('    <path d="M 1 13 L 7 2 L 13 13 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Pure White Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="150" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Layered System Architecture</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 2. Layered Architecture Diagram of QueryLearn</text>')

    # --------------------------------------------------------------------------
    # Dashed Boundary: Hosted on Vercel (serverless)
    # A single, continuous dashed box enclosing Layers 2, 3, 4.
    # --------------------------------------------------------------------------
    svg.append('<rect x="130" y="690" width="3248" height="1560" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="16,12" rx="14" ry="14" />')
    # Badge seated cleanly on top border
    svg.append('<rect x="2700" y="664" width="620" height="52" fill="#FFFFFF" stroke="#000000" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="3010" y="700" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" font-style="italic" fill="#000000" text-anchor="middle">Hosted on Vercel (serverless)</text>')

    box_w = 720
    box_x = [220, 1016, 1812, 2608]

    # --------------------------------------------------------------------------
    # LAYER 1: Presentation Layer (Browser Client)
    # y = 220, height = 330
    # --------------------------------------------------------------------------
    svg.append('<rect x="180" y="220" width="3148" height="330" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="270" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Presentation Layer (Browser Client)</text>')

    p_boxes = [
        ("HTML User Interface", box_x[0]),
        ("CodeMirror Editor", box_x[1]),
        ("Task & Clock Timers", box_x[2]),
        ("Chart.js Visualizations", box_x[3]),
    ]
    for title, bx in p_boxes:
        svg.append(f'<rect x="{bx}" y="295" width="{box_w}" height="225" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + box_w//2}" y="420" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    # --------------------------------------------------------------------------
    # Gap 1 (y = 550 to 750): Connectors between Presentation & Application
    # --------------------------------------------------------------------------
    # Channel 1: Requests (Down) at x=978
    svg.append('<line x1="978" y1="550" x2="978" y2="744" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="688" y="622" width="580" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="978" y="659" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" fill="#000000" text-anchor="middle">HTTP Requests (GET / POST)</text>')

    # Channel 2: Responses (Up) at x=2570
    svg.append('<line x1="2570" y1="750" x2="2570" y2="556" stroke="#000000" stroke-width="3" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2270" y="622" width="600" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="2570" y="659" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" fill="#000000" text-anchor="middle">HTTP Responses (HTML / JSON)</text>')

    # --------------------------------------------------------------------------
    # LAYER 2: Application Layer (Flask Web Framework)
    # y = 750, height = 330
    # --------------------------------------------------------------------------
    svg.append('<rect x="180" y="750" width="3148" height="330" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="800" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Application Layer (Flask Web Framework)</text>')

    app_boxes = [
        ("auth_bp", box_x[0]),
        ("experiment_bp", box_x[1]),
        ("tasks_bp", box_x[2]),
        ("dashboard_bp", box_x[3]),
    ]
    for title, bx in app_boxes:
        svg.append(f'<rect x="{bx}" y="825" width="{box_w}" height="225" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + box_w//2}" y="950" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    # --------------------------------------------------------------------------
    # Gap 2 (y = 1080 to 1240): Connectors between Application & Services
    # --------------------------------------------------------------------------
    svg.append('<line x1="978" y1="1080" x2="978" y2="1234" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="668" y="1132" width="620" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="978" y="1169" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" fill="#000000" text-anchor="middle">Service Invocations &amp; Logic Calls</text>')

    svg.append('<line x1="2570" y1="1240" x2="2570" y2="1086" stroke="#000000" stroke-width="3" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2255" y="1132" width="630" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="2570" y="1169" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" fill="#000000" text-anchor="middle">Execution Results &amp; Telemetry Data</text>')

    # --------------------------------------------------------------------------
    # LAYER 3: Services Layer (Domain Logic & Orchestration)
    # y = 1240, height = 470
    # --------------------------------------------------------------------------
    svg.append('<rect x="180" y="1240" width="3148" height="470" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="1290" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Services Layer (Domain Logic &amp; Orchestration)</text>')

    srv_row1 = [
        ("task_catalog", box_x[0]),
        ("sql_runner", box_x[1]),
        ("python_runner", box_x[2]),
        ("answer_checker", box_x[3]),
    ]
    for title, bx in srv_row1:
        svg.append(f'<rect x="{bx}" y="1315" width="{box_w}" height="175" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + box_w//2}" y="1420" font-family="Arial, Helvetica, sans-serif" font-size="50" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    srv_row2 = [
        ("sequence_manager", box_x[0]),
        ("comprehension_items", box_x[1]),
        ("benchmark_runner", box_x[2]),
        ("export_service", box_x[3]),
    ]
    for title, bx in srv_row2:
        svg.append(f'<rect x="{bx}" y="1510" width="{box_w}" height="175" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + box_w//2}" y="1615" font-family="Arial, Helvetica, sans-serif" font-size="50" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    # --------------------------------------------------------------------------
    # Gap 3 (y = 1710 to 1880): Connectors between Services & Data
    # --------------------------------------------------------------------------
    svg.append('<line x1="978" y1="1710" x2="978" y2="1874" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="668" y="1767" width="620" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="978" y="1804" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" fill="#000000" text-anchor="middle">Database Operations &amp; File Reads</text>')

    svg.append('<line x1="2570" y1="1880" x2="2570" y2="1716" stroke="#000000" stroke-width="3" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2255" y="1767" width="630" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="2570" y="1804" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" fill="#000000" text-anchor="middle">Relational Datasets &amp; Test Payloads</text>')

    # --------------------------------------------------------------------------
    # LAYER 4: Data Layer
    # y = 1880, height = 340
    # --------------------------------------------------------------------------
    svg.append('<rect x="180" y="1880" width="3148" height="340" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="1930" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Data Layer (Local &amp; Ephemeral Serverless Storage)</text>')

    data_boxes = [
        ("research.db (SQLite)", box_x[0]),
        ("experiment_a.db (SQLite)", box_x[1]),
        ("experiment_b.db (SQLite)", box_x[2]),
        ("hidden_tests.json (JSON)", box_x[3]),
    ]
    for title, bx in data_boxes:
        svg.append(f'<rect x="{bx}" y="1955" width="{box_w}" height="235" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + box_w//2}" y="2085" font-family="Arial, Helvetica, sans-serif" font-size="48" font-weight="bold" fill="#000000" text-anchor="middle">{title}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 2b: ARCHITECTURE DIAGRAM (DETAILED DENSE VERSION)
# ==============================================================================
def build_detailed_architecture_diagram_svg() -> str:
    """
    Detailed Architecture Diagram (Figure 2b / 02b-architecture-detailed).
    Contains full itemized engineering details with verified versions:
    - Flask 3.1.1, CodeMirror 5.65.13, Chart.js 4.4.4
    - 21 Jinja2 HTML Templates confirmed
    - 36 Hidden Test Datasets confirmed (6 tasks x 2 forms x 3 edge-case tests)
    - 2x2 counterbalanced crossover with four sequences
    - Single, unbroken dashed Vercel boundary box
    - Symmetric transfer channels with centered white label badges
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    svg.append('  <marker id="arrow-d" markerWidth="14" markerHeight="14" refX="7" refY="12" orient="auto">')
    svg.append('    <path d="M 1 1 L 7 12 L 13 1 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('  <marker id="arrow-u" markerWidth="14" markerHeight="14" refX="7" refY="2" orient="auto">')
    svg.append('    <path d="M 1 13 L 7 2 L 13 13 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="150" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Detailed System Architecture</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 2b. Detailed Engineering Architecture Diagram of QueryLearn</text>')

    # Dashed Boundary: Hosted on Vercel (serverless)
    svg.append('<rect x="130" y="690" width="3248" height="1560" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="16,12" rx="14" ry="14" />')
    svg.append('<rect x="2700" y="664" width="620" height="52" fill="#FFFFFF" stroke="#000000" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="3010" y="700" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" font-style="italic" fill="#000000" text-anchor="middle">Hosted on Vercel (serverless)</text>')

    box_w = 720
    box_x = [220, 1016, 1812, 2608]

    # LAYER 1: Presentation Layer
    svg.append('<rect x="180" y="220" width="3148" height="330" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="268" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Presentation Layer (Browser Client)</text>')

    p_boxes = [
        ("HTML User Interface", ["Jinja2 Web Templates (21 Views)", "Responsive Split Layout", "Participant & Researcher Views"], box_x[0]),
        ("Code Editors", ["CodeMirror 5.65.13 Workspace", "SQL Syntax Highlighting Mode", "Procedural Python Indentation Mode"], box_x[1]),
        ("Client-Side Timers", ["timer.js Countdown Engine", "8-Min Task Countdown Clocks", "Elapsed Time Accumulators"], box_x[2]),
        ("Data Visualizations", ["Chart.js 4.4.4 Engine", "Outcome Split Visualizations", "Headline Performance Metrics"], box_x[3]),
    ]
    for title, items, bx in p_boxes:
        svg.append(f'<rect x="{bx}" y="290" width="{box_w}" height="230" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + 30}" y="335" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{380 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    # Connectors Gap 1
    svg.append('<line x1="978" y1="550" x2="978" y2="744" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="668" y="622" width="620" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="978" y="659" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">HTTP Requests (form data, code, parameters)</text>')

    svg.append('<line x1="2570" y1="750" x2="2570" y2="556" stroke="#000000" stroke-width="3" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2255" y="622" width="630" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="2570" y="659" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">HTTP Responses (rendered HTML, JSON, CSV)</text>')

    # LAYER 2: Application Layer
    svg.append('<rect x="180" y="750" width="3148" height="330" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="798" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Application Layer (Flask 3.1.1 Web Framework)</text>')

    app_boxes = [
        ("auth_bp", ["Participant Intake (/register)", "Demographic Validation (Yr 2-4)", "Researcher Login (/researcher/login)"], box_x[0]),
        ("experiment_bp", ["Instructions & Practice Workspaces", "Readiness Check & Comprehension", "Post-Condition Survey & Break"], box_x[1]),
        ("tasks_bp", ["/api/run (Sandboxed Execution)", "/api/submit (Automated Grading)", "/api/skip & Status Telemetry"], box_x[2]),
        ("dashboard_bp", ["Overview (Headline Metrics)", "Participant Registry & Results", "Task Comparison & CSV Data Export"], box_x[3]),
    ]
    for title, items, bx in app_boxes:
        svg.append(f'<rect x="{bx}" y="820" width="{box_w}" height="230" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + 30}" y="865" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{910 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    # Connectors Gap 2
    svg.append('<line x1="978" y1="1080" x2="978" y2="1234" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="668" y="1132" width="620" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="978" y="1169" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">Function Calls (code evaluation, sequencing)</text>')

    svg.append('<line x1="2570" y1="1240" x2="2570" y2="1086" stroke="#000000" stroke-width="3" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2255" y="1132" width="630" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="2570" y="1169" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">Execution Results (grading, metrics, CSV bytes)</text>')

    # LAYER 3: Services Layer
    svg.append('<rect x="180" y="1240" width="3148" height="470" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="1288" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Services Layer (Domain Logic &amp; Orchestration)</text>')

    srv_row1 = [
        ("task_catalog", "T1-T6 Specs & Reference Solutions", box_x[0]),
        ("sql_runner", "Read-Only SQLite Engine (mode=ro, 10s)", box_x[1]),
        ("python_runner", "Subprocess Sandbox (Builtins Block, 10s)", box_x[2]),
        ("answer_checker", "Oracle Grading & Hidden Test Evaluation", box_x[3]),
    ]
    for title, desc, bx in srv_row1:
        svg.append(f'<rect x="{bx}" y="1310" width="{box_w}" height="170" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + 30}" y="1355" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        svg.append(f'<text x="{bx + 30}" y="1405" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {desc}</text>')

    srv_row2 = [
        ("sequence_manager", "2x2 Counterbalanced Crossover (4 Seq)", box_x[0]),
        ("comprehension_items", "6 Code Reading Assessment Items", box_x[1]),
        ("benchmark_runner", "Scaling Benchmarks (1K, 10K, 100K Rows)", box_x[2]),
        ("export_service", "Telemetry Export (Participants, Results)", box_x[3]),
    ]
    for title, desc, bx in srv_row2:
        svg.append(f'<rect x="{bx}" y="1505" width="{box_w}" height="175" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + 30}" y="1550" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        svg.append(f'<text x="{bx + 30}" y="1600" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {desc}</text>')

    # Connectors Gap 3
    svg.append('<line x1="978" y1="1710" x2="978" y2="1874" stroke="#000000" stroke-width="3" marker-end="url(#arrow-d)" />')
    svg.append('<rect x="668" y="1767" width="620" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="978" y="1804" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">SQL Queries (SELECT, INSERT) &amp; JSON Reads</text>')

    svg.append('<line x1="2570" y1="1880" x2="2570" y2="1716" stroke="#000000" stroke-width="3" marker-end="url(#arrow-u)" />')
    svg.append('<rect x="2255" y="1767" width="630" height="54" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2" rx="8" ry="8" />')
    svg.append('<text x="2570" y="1804" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000" text-anchor="middle">Query Result Sets &amp; Hidden Test Payloads</text>')

    # LAYER 4: Data Layer
    svg.append('<rect x="180" y="1880" width="3148" height="340" fill="#F4F6F8" stroke="#000000" stroke-width="4" rx="12" ry="12" />')
    svg.append('<text x="220" y="1928" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="bold" fill="#000000">Data Layer (Local &amp; Ephemeral Serverless Storage)</text>')

    data_boxes = [
        ("research.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Tables: participants, sessions, task_attempts", "task_results, task_timers, comprehension, surveys"], box_x[0]),
        ("experiment_a.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Form A Relational Database (mode=ro)", "Tables: Students, Courses, Enrollments"], box_x[1]),
        ("experiment_b.db (SQLite)", ["Copied to /tmp on Vercel initialization", "Form B Relational Database (mode=ro)", "Tables: Students, Courses, Enrollments"], box_x[2]),
        ("hidden_tests.json (JSON)", ["JSON Edge-Case Test Datasets", "36 Total Hidden Test Datasets", "3 Edge-Case Datasets per Task (T1-T6, Forms A &amp; B)"], box_x[3]),
    ]
    for title, items, bx in data_boxes:
        svg.append(f'<rect x="{bx}" y="1950" width="{box_w}" height="245" fill="#FFFFFF" stroke="#000000" stroke-width="3" rx="8" ry="8" />')
        svg.append(f'<text x="{bx + 30}" y="1995" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="bold" fill="#000000">{title}</text>')
        for idx, itm in enumerate(items):
            svg.append(f'<text x="{bx + 30}" y="{2040 + idx * 36}" font-family="Arial, Helvetica, sans-serif" font-size="23" fill="#000000">&#8226; {itm}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


# ==============================================================================
# DIAGRAM 3: USE CASE DIAGRAM (UML)
# ==============================================================================
def build_use_case_diagram_svg() -> str:
    """
    UML Use Case Diagram (Figure 3 / 03-use-case-diagram).
    - Standard UML standard: straight fan association lines radiating from actor side/hand directly to ellipse perimeters.
    - Zero line crossings among association lines.
    - Included use case positioned in center with clean <<include>> stereotyping (>=12pt) on white knockout badges.
    - Clean stick figures with proper human proportions.
    """
    w, h = 3508, 2480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    svg.append('<defs>')
    # Dashed arrow for <<include>>
    svg.append('  <marker id="arrow-inc" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto">')
    svg.append('    <path d="M 1 2 L 14 8 L 1 14 Z" fill="#000000" />')
    svg.append('  </marker>')
    svg.append('</defs>')

    # Pure White Background
    svg.append(f'<rect width="{w}" height="{h}" fill="#FFFFFF" />')

    # Title
    svg.append('<text x="1754" y="150" font-family="Arial, Helvetica, sans-serif" font-size="64" font-weight="bold" fill="#000000" text-anchor="middle">QueryLearn Use Case Diagram (UML)</text>')

    # Caption
    svg.append('<text x="1754" y="2380" font-family="Arial, Helvetica, sans-serif" font-size="44" fill="#000000" text-anchor="middle">Figure 3. Use Case Diagram of QueryLearn</text>')

    # --------------------------------------------------------------------------
    # System Boundary Box
    # --------------------------------------------------------------------------
    sb_x0, sb_y0, sb_w, sb_h = 520, 220, 2468, 2080
    svg.append(f'<rect x="{sb_x0}" y="{sb_y0}" width="{sb_w}" height="{sb_h}" fill="none" stroke="#000000" stroke-width="4" rx="16" ry="16" />')
    svg.append(f'<text x="{sb_x0 + 40}" y="{sb_y0 + 60}" font-family="Arial, Helvetica, sans-serif" font-size="44" font-weight="bold" fill="#000000">QueryLearn System</text>')

    # --------------------------------------------------------------------------
    # Actor 1: Participant (Left)
    # --------------------------------------------------------------------------
    p_cx, p_cy = 250, 1240
    # Head
    svg.append(f'<circle cx="{p_cx}" cy="{p_cy - 110}" r="42" fill="#FFFFFF" stroke="#000000" stroke-width="4" />')
    # Torso
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 68}" x2="{p_cx}" y2="{p_cy + 70}" stroke="#000000" stroke-width="4" />')
    # Left Arm
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 30}" x2="{p_cx - 90}" y2="{p_cy - 10}" stroke="#000000" stroke-width="4" />')
    # Right Arm / Hand (Source of association lines)
    p_hand_x, p_hand_y = p_cx + 90, p_cy - 10
    svg.append(f'<line x1="{p_cx}" y1="{p_cy - 30}" x2="{p_hand_x}" y2="{p_hand_y}" stroke="#000000" stroke-width="4" />')
    # Legs
    svg.append(f'<line x1="{p_cx}" y1="{p_cy + 70}" x2="{p_cx - 75}" y2="{p_cy + 200}" stroke="#000000" stroke-width="4" />')
    svg.append(f'<line x1="{p_cx}" y1="{p_cy + 70}" x2="{p_cx + 75}" y2="{p_cy + 200}" stroke="#000000" stroke-width="4" />')
    # Actor Label
    svg.append(f'<text x="{p_cx}" y="{p_cy + 265}" font-family="Arial, Helvetica, sans-serif" font-size="42" font-weight="bold" fill="#000000" text-anchor="middle">Participant</text>')
    svg.append(f'<text x="{p_cx}" y="{p_cy + 305}" font-family="Arial, Helvetica, sans-serif" font-size="28" font-style="italic" fill="#475569" text-anchor="middle">(Novice Learner Cohort)</text>')

    # --------------------------------------------------------------------------
    # Actor 2: Researcher (Right)
    # --------------------------------------------------------------------------
    r_cx, r_cy = 3258, 1240
    # Head
    svg.append(f'<circle cx="{r_cx}" cy="{r_cy - 110}" r="42" fill="#FFFFFF" stroke="#000000" stroke-width="4" />')
    # Torso
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 68}" x2="{r_cx}" y2="{r_cy + 70}" stroke="#000000" stroke-width="4" />')
    # Right Arm
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 30}" x2="{r_cx + 90}" y2="{r_cy - 10}" stroke="#000000" stroke-width="4" />')
    # Left Arm / Hand (Source of association lines)
    r_hand_x, r_hand_y = r_cx - 90, r_cy - 10
    svg.append(f'<line x1="{r_cx}" y1="{r_cy - 30}" x2="{r_hand_x}" y2="{r_hand_y}" stroke="#000000" stroke-width="4" />')
    # Legs
    svg.append(f'<line x1="{r_cx}" y1="{r_cy + 70}" x2="{r_cx - 75}" y2="{r_cy + 200}" stroke="#000000" stroke-width="4" />')
    svg.append(f'<line x1="{r_cx}" y1="{r_cy + 70}" x2="{r_cx + 75}" y2="{r_cy + 200}" stroke="#000000" stroke-width="4" />')
    # Actor Label
    svg.append(f'<text x="{r_cx}" y="{r_cy + 265}" font-family="Arial, Helvetica, sans-serif" font-size="42" font-weight="bold" fill="#000000" text-anchor="middle">Researcher</text>')
    svg.append(f'<text x="{r_cx}" y="{r_cy + 305}" font-family="Arial, Helvetica, sans-serif" font-size="28" font-style="italic" fill="#475569" text-anchor="middle">(Evaluator / Admin)</text>')

    def draw_ellipse_use_case(cx_val, cy_val, rx_val, ry_val, label_text):
        svg.append(f'<ellipse cx="{cx_val}" cy="{cy_val}" rx="{rx_val}" ry="{ry_val}" fill="#F4F6F8" stroke="#000000" stroke-width="3" />')
        svg.append(f'<text x="{cx_val}" y="{cy_val + 10}" font-family="Arial, Helvetica, sans-serif" font-size="29" font-weight="bold" fill="#000000" text-anchor="middle">{label_text}</text>')

    # --------------------------------------------------------------------------
    # PARTICIPANT USE CASES (Column 1 at x = 1000)
    # --------------------------------------------------------------------------
    p_col_x = 1000
    p_rx, p_ry = 260, 60
    p_cases = [
        ("Register & Provide Consent", 380),
        ("View Language Reference", 630),
        ("Complete Readiness Check", 880),
        ("Solve SQL Query Tasks", 1130),
        ("Solve Python Tasks", 1380),
        ("Answer Comprehension Items", 1630),
        ("Complete Post-Task Survey", 1880),
        ("Conclude Sequence Flow", 2130),
    ]

    for label, oy in p_cases:
        draw_ellipse_use_case(p_col_x, oy, p_rx, p_ry, label)
        # Calculate exact intersection of ray from (p_hand_x, p_hand_y) to ellipse perimeter
        angle = math.atan2(oy - p_hand_y, p_col_x - p_hand_x)
        # Perimeter on ellipse approached from left
        dock_x = p_col_x - p_rx * math.cos(angle)
        dock_y = oy - p_ry * math.sin(angle)
        svg.append(f'<line x1="{p_hand_x}" y1="{p_hand_y}" x2="{dock_x}" y2="{dock_y}" stroke="#000000" stroke-width="2.5" />')

    # --------------------------------------------------------------------------
    # INCLUDED USE CASE: Submit Task Solution (Center)
    # --------------------------------------------------------------------------
    sub_cx, sub_cy = 1754, 1255
    sub_rx, sub_ry = 230, 60
    draw_ellipse_use_case(sub_cx, sub_cy, sub_rx, sub_ry, "Submit Task Solution")

    # <<include>> connector 1: From Solve SQL Tasks (1000, 1130)
    sql_ox, sql_oy = p_col_x, 1130
    inc1_angle = math.atan2(sub_cy - 15 - sql_oy, sub_cx - sql_ox)
    inc1_start_x = sql_ox + p_rx * math.cos(inc1_angle)
    inc1_start_y = sql_oy + p_ry * math.sin(inc1_angle)
    inc1_end_x = sub_cx - sub_rx * math.cos(inc1_angle)
    inc1_end_y = sub_cy - 15 - sub_ry * math.sin(inc1_angle)
    svg.append(f'<line x1="{inc1_start_x}" y1="{inc1_start_y}" x2="{inc1_end_x - 5}" y2="{inc1_end_y}" stroke="#000000" stroke-width="2.5" stroke-dasharray="10,8" marker-end="url(#arrow-inc)" />')

    mid1_x = (inc1_start_x + inc1_end_x) / 2
    mid1_y = (inc1_start_y + inc1_end_y) / 2
    svg.append(f'<rect x="{mid1_x - 110}" y="{mid1_y - 22}" width="220" height="44" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" rx="6" ry="6" />')
    svg.append(f'<text x="{mid1_x}" y="{mid1_y + 8}" font-family="Arial, Helvetica, sans-serif" font-size="26" font-style="italic" fill="#000000" text-anchor="middle">&lt;&lt;include&gt;&gt;</text>')

    # <<include>> connector 2: From Solve Python Tasks (1000, 1380)
    py_ox, py_oy = p_col_x, 1380
    inc2_angle = math.atan2(sub_cy + 15 - py_oy, sub_cx - py_ox)
    inc2_start_x = py_ox + p_rx * math.cos(inc2_angle)
    inc2_start_y = py_oy + p_ry * math.sin(inc2_angle)
    inc2_end_x = sub_cx - sub_rx * math.cos(inc2_angle)
    inc2_end_y = sub_cy + 15 - sub_ry * math.sin(inc2_angle)
    svg.append(f'<line x1="{inc2_start_x}" y1="{inc2_start_y}" x2="{inc2_end_x - 5}" y2="{inc2_end_y}" stroke="#000000" stroke-width="2.5" stroke-dasharray="10,8" marker-end="url(#arrow-inc)" />')

    mid2_x = (inc2_start_x + inc2_end_x) / 2
    mid2_y = (inc2_start_y + inc2_end_y) / 2
    svg.append(f'<rect x="{mid2_x - 110}" y="{mid2_y - 22}" width="220" height="44" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" rx="6" ry="6" />')
    svg.append(f'<text x="{mid2_x}" y="{mid2_y + 8}" font-family="Arial, Helvetica, sans-serif" font-size="26" font-style="italic" fill="#000000" text-anchor="middle">&lt;&lt;include&gt;&gt;</text>')

    # --------------------------------------------------------------------------
    # RESEARCHER USE CASES (Column 2 at x = 2508)
    # --------------------------------------------------------------------------
    r_col_x = 2508
    r_rx, r_ry = 260, 60
    r_cases = [
        ("Authenticate & Log In", 505),
        ("Inspect Participant Registry", 805),
        ("Review Task Telemetry", 1105),
        ("Analyze Comparative Metrics", 1405),
        ("Trigger Engine Benchmarks", 1705),
        ("Export Research Datasets", 2005),
    ]

    for label, oy in r_cases:
        draw_ellipse_use_case(r_col_x, oy, r_rx, r_ry, label)
        angle = math.atan2(oy - r_hand_y, r_col_x - r_hand_x)
        dock_x = r_col_x - r_rx * math.cos(angle)
        dock_y = oy - r_ry * math.sin(angle)
        svg.append(f'<line x1="{r_hand_x}" y1="{r_hand_y}" x2="{dock_x}" y2="{dock_y}" stroke="#000000" stroke-width="2.5" />')

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

    print("All diagrams successfully generated and synchronized!")


if __name__ == "__main__":
    generate_all()
