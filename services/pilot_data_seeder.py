"""
Pilot Data Seeder for QueryLearn.
Populates research.db with realistic participant data for 16 college students
(Notre Dame of Midsayap College BSCS/BSIT cohort) across all 4 balanced sequences.
"""

import sqlite3
import random
from config import Config
from services.sequence_manager import SEQUENCES

STUDENT_PROFILES = [
    ("BSCS", 2, "novice", "intermediate", "yes", "Java, C++"),
    ("BSIT", 2, "novice", "novice", "yes", "PHP, JavaScript"),
    ("BSCS", 1, "none", "novice", "no", "Python"),
    ("BSIT", 2, "intermediate", "novice", "yes", "Java"),
    ("BSCS", 2, "novice", "intermediate", "yes", "C"),
    ("BSIS", 3, "novice", "none", "yes", "HTML, CSS"),
    ("BSCS", 2, "intermediate", "proficient", "yes", "Java, Python, C#"),
    ("BSIT", 1, "none", "novice", "no", "None"),
    ("BSCS", 3, "intermediate", "intermediate", "yes", "Java, Kotlin"),
    ("BSIT", 2, "novice", "novice", "yes", "JavaScript"),
    ("BSCS", 2, "novice", "intermediate", "yes", "Python"),
    ("BSIT", 3, "intermediate", "intermediate", "yes", "PHP, Python"),
    ("BSCS", 1, "none", "none", "no", "C++"),
    ("BSIT", 2, "novice", "novice", "yes", "Java"),
    ("BSCS", 2, "intermediate", "intermediate", "yes", "C++, Python"),
    ("BSIT", 2, "novice", "intermediate", "yes", "JavaScript, Python")
]

def seed_pilot_data():
    conn = sqlite3.connect(Config.RESEARCH_DB)
    cursor = conn.cursor()

    # Clear existing non-admin tables
    cursor.execute("DELETE FROM task_attempts")
    cursor.execute("DELETE FROM task_results")
    cursor.execute("DELETE FROM comprehension_responses")
    cursor.execute("DELETE FROM survey_responses")
    cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM participants")

    for i, profile in enumerate(STUDENT_PROFILES):
        study_id = f"P{i+1:03d}"
        program, year, sql_exp, py_exp, db_course, other_langs = profile
        seq_id = (i % 4) + 1
        seq_info = SEQUENCES[seq_id]
        status = "completed" if i < 13 else ("in_progress" if i < 15 else "registered")

        cursor.execute("""
            INSERT INTO participants 
            (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (study_id, program, year, py_exp, sql_exp, other_langs, db_course, seq_id, status))
        p_id = cursor.lastrowid

        # Condition 1 session
        cursor.execute("""
            INSERT INTO sessions (participant_id, language, form, sequence_order, completed_at)
            VALUES (?, ?, ?, 1, datetime('now', '-2 hours'))
        """, (p_id, seq_info['first_language'].lower(), seq_info['first_form']))
        s1_id = cursor.lastrowid

        # Condition 2 session
        cursor.execute("""
            INSERT INTO sessions (participant_id, language, form, sequence_order, completed_at)
            VALUES (?, ?, ?, 2, datetime('now', '-1 hours'))
        """, (p_id, seq_info['second_language'].lower(), seq_info['second_form']))
        s2_id = cursor.lastrowid

        # Seed task results if completed or in_progress
        if status in ["completed", "in_progress"]:
            for session_id, lang in [(s1_id, seq_info['first_language'].lower()), (s2_id, seq_info['second_language'].lower())]:
                for task_idx in range(1, 7):
                    # SQL typically has faster times and fewer attempts for declarative tasks (as per research hypothesis)
                    if lang == "sql":
                        elapsed = random.randint(45, 210)
                        attempts = random.choice([1, 1, 1, 2, 2, 3])
                        success = True if (i < 12 or task_idx < 5) else random.choice([True, False])
                    else:
                        elapsed = random.randint(90, 360)
                        attempts = random.choice([1, 2, 2, 3, 3, 4])
                        success = True if (i < 10 or task_idx < 4) else random.choice([True, False])

                    cursor.execute("""
                        INSERT INTO task_results 
                        (session_id, task_id, success, elapsed_seconds, allocated_seconds, attempt_count, final_code)
                        VALUES (?, ?, ?, ?, 480, ?, '-- Pilot submission')
                    """, (session_id, f"T{task_idx}", success, elapsed, attempts))

                # Seed Survey
                if status == "completed":
                    # SQL typically rated higher for clarity (Q1, Q2) and lower mental effort (Q6)
                    q1 = random.choice([4, 5, 5]) if lang == "sql" else random.choice([3, 4, 4])
                    q2 = random.choice([4, 5]) if lang == "sql" else random.choice([3, 4])
                    q3 = random.choice([4, 4, 5]) if lang == "sql" else random.choice([3, 4])
                    q4 = random.choice([3, 4, 4]) if lang == "sql" else random.choice([3, 3, 4])
                    q5 = random.choice([4, 5]) if lang == "sql" else random.choice([3, 4])
                    q6 = random.choice([2, 3]) if lang == "sql" else random.choice([3, 4]) # mental effort
                    q7 = random.choice([2, 2, 3]) if lang == "sql" else random.choice([3, 3, 4]) # fatigue

                    cursor.execute("""
                        INSERT INTO survey_responses 
                        (session_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_after_error, open_preference)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        session_id, lang, q1, q2, q3, q4, q5, q6, q7,
                        "Writing WHERE filters and GROUP BY clauses" if lang == "sql" else "Basic loop syntax",
                        "Subqueries and outer joins" if lang == "sql" else "Managing nested dictionary keys and manual loops",
                        "Checked table column names" if lang == "sql" else "Read python stack trace",
                        "Prefer SQL for database queries due to readability"
                    ))

    conn.commit()
    conn.close()
    return True
