# QueryLearn

> **Evaluating SQL Readability and Productivity Among Novice Database Learners**  
> An Empirical Case Study in Parallel and Distributed Computing  
> *Notre Dame of Midsayap College*

---

## Overview

**QueryLearn** is an experimental evaluation instrument designed to empirically compare the readability, comprehension, and developer productivity of:
- **Domain-Specific Declarative Languages:** Structured Query Language (SQL)
- **General-Purpose Procedural Languages:** Procedural Python (iterative data transformations)

The platform evaluates novice computer science learners through a within-subjects, counterbalanced experimental design across 6 canonical data manipulation tasks.

---

## System Architecture

- **Backend:** Python / Flask WSGI application with modular blueprint architecture (`auth`, `experiment`, `tasks`, `dashboard`).
- **Data Stores:** Isolated SQLite instances:
  - `research.db`: Participant registry, session state, telemetry logs, task attempts, comprehension items, Likert surveys, and engine benchmarks.
  - `experiment_a.db` / `experiment_b.db`: Counterbalanced relational schemas (`Students`, `Courses`, `Enrollments`) with controlled data conditions (ties, nulls, edge cases).
- **Execution Engines:**
  - SQL Runner: Read-only SQLite execution with query timeout and AST safety checks.
  - Python Runner: Sandboxed subprocess execution with restricted builtins and injected data frames.
  - Automated Oracle Checker: Result set normalization, order verification, and floating-point tolerance matching.
- **Frontend:** Dark navy glassmorphism interface styled with pure CSS (Inter + JetBrains Mono, Lucide SVG iconography, CodeMirror 5 editors, Chart.js analytics).

---

## Features

- **Participant Registration Wizard:** Multi-step intake capturing academic program, prior SQL/Python experience, and ethics consent.
- **Counterbalanced Sequencing:** Automatic round-robin assignment to 4 experimental sequences (SQL-A → Py-B, SQL-B → Py-A, Py-A → SQL-B, Py-B → SQL-A).
- **Code Comprehension Assessment:** Pre-task code reading and output prediction battery.
- **Live Programming Workspace:** Dual-panel workspace with active countdown timers, attempt tracking, schema viewers, live query execution, and test grading.
- **Post-Condition Feedback Survey:** 5-point Likert usability scales, NASA-TLX mental workload items, and open-ended feedback.
- **Researcher Analytics Dashboard:** Live cohort telemetry, pass rates, completion times, interactive charts, and engine scaling benchmarks.
- **Telemetry Export:** Full dataset export to CSV and ZIP archive for statistical analysis (R, SPSS, Python Pandas).

---

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DeathKnell837/querylearn.git
   cd querylearn
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

5. **Researcher Credentials:**
   - **Username:** `admin`
   - **Password:** `querylearn2026`
   - **URL:** `http://127.0.0.1:5000/researcher/login`

---

## License

Academic Research Instrument &copy; 2026 QueryLearn Project. All rights reserved.
