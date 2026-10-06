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
    ("BSCS", 2, "none", "novice", "no", "Python"),
    ("BSIT", 2, "intermediate", "novice", "yes", "Java"),
    ("BSCS", 2, "novice", "intermediate", "yes", "C"),
    ("BSIS", 3, "novice", "none", "yes", "HTML, CSS"),
    ("BSCS", 2, "intermediate", "proficient", "yes", "Java, Python, C#"),
    ("BSIT", 2, "none", "novice", "no", "None"),
    ("BSCS", 3, "intermediate", "intermediate", "yes", "Java, Kotlin"),
    ("BSIT", 2, "novice", "novice", "yes", "JavaScript"),
    ("BSCS", 2, "novice", "intermediate", "yes", "Python"),
    ("BSIT", 3, "intermediate", "intermediate", "yes", "PHP, Python"),
    ("BSCS", 3, "none", "none", "no", "C++"),
    ("BSIT", 2, "novice", "novice", "yes", "Java"),
    ("BSCS", 2, "intermediate", "intermediate", "yes", "C++, Python"),
    ("BSIT", 2, "novice", "intermediate", "yes", "JavaScript, Python")
]

# Set fixed seed for consistent, reproducible research pilot benchmark data
random.seed(2026)


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

        # Seed task results and attempts if completed or in_progress
        if status in ["completed", "in_progress"]:
            session_list = [
                (s1_id, seq_info['first_language'].lower(), seq_info['first_form']),
                (s2_id, seq_info['second_language'].lower(), seq_info['second_form'])
            ]
            for session_id, lang, form in session_list:
                for task_idx in range(1, 7):
                    task_id_str = f"T{task_idx}"
                    # SQL typically has faster times and fewer attempts for declarative tasks (as per research hypothesis)
                    if lang == "sql":
                        elapsed = random.randint(45, 210)
                        attempts = random.choice([1, 1, 1, 2, 2, 3])
                        success = True if (i < 12 or task_idx < 5) else random.choice([True, False])
                    else:
                        elapsed = random.randint(90, 360)
                        attempts = random.choice([1, 2, 2, 3, 3, 4])
                        success = True if (i < 10 or task_idx < 4) else random.choice([True, False])

                    SQL_SNIPPETS = {
                        'T1': "SELECT student_id, student_name FROM Students WHERE program = 'BSCS' AND year_level = 2 ORDER BY student_id;",
                        'T2': "SELECT student_id, score FROM Enrollments WHERE course_id = 'C101' AND score IS NOT NULL ORDER BY score DESC, student_id ASC LIMIT 3;",
                        'T3': "SELECT program, COUNT(*) AS student_count FROM Students GROUP BY program ORDER BY program ASC;",
                        'T4': "SELECT s.student_id, s.student_name, c.course_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON e.course_id = c.course_id WHERE e.course_id = 'C101' ORDER BY s.student_id ASC;",
                        'T5': "SELECT course_id, ROUND(AVG(score), 2) AS avg_score FROM Enrollments WHERE score IS NOT NULL GROUP BY course_id HAVING AVG(score) >= 80.0 ORDER BY course_id ASC;",
                        'T6': "SELECT s.student_id, s.student_name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.student_id IS NULL ORDER BY s.student_id ASC;"
                    }
                    SQL_INCORRECT_SNIPPETS = {
                        'T1': "SELECT student_id FROM Students WHERE program = 'BSCS';",
                        'T2': "SELECT student_id, score FROM Enrollments WHERE course_id = 'C101' LIMIT 3;",
                        'T3': "SELECT program, COUNT(*) FROM Students;",
                        'T4': "SELECT s.student_id, s.student_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id;",
                        'T5': "SELECT course_id, AVG(score) FROM Enrollments GROUP BY course_id;",
                        'T6': "SELECT s.student_id, s.student_name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id;"
                    }
                    PYTHON_SNIPPETS = {
                        'T1': "result = [(s['student_id'], s['student_name']) for s in students if s['program'] == 'BSCS' and s['year_level'] == 2]",
                        'T2': "valid = [e for e in enrollments if e['course_id'] == 'C101' and e['score'] is not None]\nvalid.sort(key=lambda x: (-x['score'], x['student_id']))\nresult = valid[:3]",
                        'T3': "counts = {}\nfor s in students:\n    counts[s['program']] = counts.get(s['program'], 0) + 1",
                        'T4': "matches = [(s['student_id'], s['student_name'], c['course_name']) for s in students for e in enrollments for c in courses if s['student_id'] == e['student_id'] and e['course_id'] == c['course_id']]",
                        'T5': "by_course = {}\nfor e in enrollments:\n    if e['score'] is not None:\n        by_course.setdefault(e['course_id'], []).append(e['score'])",
                        'T6': "enrolled_ids = {e['student_id'] for e in enrollments}\nresult = [(s['student_id'], s['student_name']) for s in students if s['student_id'] not in enrolled_ids]"
                    }
                    PYTHON_INCORRECT_SNIPPETS = {
                        'T1': "result = [s['student_name'] for s in students if s['program'] == 'BSCS']",
                        'T2': "result = sorted(enrollments, key=lambda x: x['score'])[:3]",
                        'T3': "result = len([s for s in students])",
                        'T4': "result = [(s['student_name'], c['course_name']) for s in students for c in courses]",
                        'T5': "result = [e['course_id'] for e in enrollments if e.get('score', 0) > 80]",
                        'T6': "result = [s['student_id'] for s in students if s['student_id'] not in enrollments]"
                    }

                    if lang == "sql":
                        code_sample = SQL_SNIPPETS.get(task_id_str, "") if success else SQL_INCORRECT_SNIPPETS.get(task_id_str, "")
                    else:
                        code_sample = PYTHON_SNIPPETS.get(task_id_str, "") if success else PYTHON_INCORRECT_SNIPPETS.get(task_id_str, "")

                    cursor.execute("""
                        INSERT INTO task_results 
                        (session_id, task_id, success, elapsed_seconds, allocated_seconds, attempt_count, final_code)
                        VALUES (?, ?, ?, ?, 480, ?, ?)
                    """, (session_id, task_id_str, success, elapsed, attempts, code_sample))

                    # Seed matching task attempts
                    for att in range(1, attempts + 1):
                        is_final = (att == attempts)
                        if is_final:
                            att_status = "correct" if success else "incorrect"
                            err_msg = "" if success else "Result mismatch against expected dataset"
                        else:
                            att_status = random.choice(["syntax_error", "incorrect"])
                            err_msg = "SyntaxError: near clause" if att_status == "syntax_error" else "Column count or value mismatch"

                        submitted = code_sample if is_final else (f"{code_sample} -- attempt {att}" if lang == 'sql' else f"{code_sample} # attempt {att}")
                        cursor.execute("""
                            INSERT INTO task_attempts
                            (session_id, task_id, attempt_number, submitted_code, result_status, error_message, submitted_at)
                            VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-' || ? || ' minutes'))
                        """, (session_id, task_id_str, att, submitted, att_status, err_msg, max(1, 60 - att * 5)))

                # Seed Comprehension Responses (6 items C1 to C6 per session) for completed participants
                if status == "completed":
                    for c_idx in range(1, 7):
                        item_id = f"C{c_idx}"
                        if lang == "sql":
                            exp_score = random.choices([2, 1, 0], weights=[0.75, 0.20, 0.05])[0]
                            pred_score = random.choices([1, 0], weights=[0.85, 0.15])[0]
                            resp_time = round(random.uniform(22.0, 68.0), 1)
                        else:
                            exp_score = random.choices([2, 1, 0], weights=[0.55, 0.35, 0.10])[0]
                            pred_score = random.choices([1, 0], weights=[0.70, 0.30])[0]
                            resp_time = round(random.uniform(38.0, 115.0), 1)

                        total_score = exp_score + pred_score

                        cursor.execute("""
                            INSERT INTO comprehension_responses
                            (study_id, session_id, item_id, language, form, explanation_score, prediction_score, condition_score, response_time, response_time_seconds, timed_out, learner_answer)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                        """, (
                            study_id, session_id, item_id, lang, form,
                            float(exp_score), float(pred_score), float(total_score),
                            resp_time, resp_time, f"exp:{exp_score},pred:{pred_score}"
                        ))

                    # Seed Survey Responses
                    q1 = random.choice([4, 5, 5]) if lang == "sql" else random.choice([3, 4, 4])
                    q2 = random.choice([4, 5]) if lang == "sql" else random.choice([3, 4])
                    q3 = random.choice([4, 4, 5]) if lang == "sql" else random.choice([3, 4])
                    q4 = random.choice([3, 4, 4]) if lang == "sql" else random.choice([3, 3, 4])
                    q5 = random.choice([4, 5]) if lang == "sql" else random.choice([3, 4])
                    q6 = random.choice([2, 3]) if lang == "sql" else random.choice([3, 4])  # mental effort
                    q7 = random.choice([2, 2, 3]) if lang == "sql" else random.choice([3, 3, 4])  # fatigue

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
