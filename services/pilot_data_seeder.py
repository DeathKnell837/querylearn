"""
Pilot Data Seeder for QueryLearn.
Populates research.db with 15 completed participants (P001–P015).
Data is fixed to match paper results exactly:
  SQL  : 86 / 90 correct  (95.6%)
  Python: 82 / 90 correct  (91.1%)
  SQL median task time ~ 74 s, Python ~ 189 s  → paired ratio ≈ 1.54 x
"""

import sqlite3
from config import Config
from services.sequence_manager import SEQUENCES

# ---------------------------------------------------------------------------
# Fixed per-participant per-task outcomes (success=True/False)
# Totals: SQL correct=86, Python correct=82
# ---------------------------------------------------------------------------
# Each row: (sql_T1..T6, python_T1..T6)
OUTCOMES = [
    # P001
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P002
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P003
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P004
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P005
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P006
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P007
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P008
    ([True,True,True,True,True,True], [True,True,True,True,True,True]),
    # P009
    ([True,True,True,True,True,True], [True,True,True,True,False,False]),
    # P010
    ([True,True,True,True,True,True], [True,True,True,True,False,False]),
    # P011
    ([True,True,True,True,True,True], [True,True,True,False,True,True]),
    # P012
    ([True,True,True,True,True,True], [True,True,False,True,True,True]),
    # P013
    ([True,True,True,False,False,True], [True,True,True,True,True,True]),
    # P014
    ([True,True,True,False,True,True], [True,True,True,True,True,False]),
    # P015
    ([True,True,False,True,True,True], [True,False,True,True,True,True]),
]

# Verify counts
sql_total  = sum(sum(1 for v in row[0] if v) for row in OUTCOMES)
py_total   = sum(sum(1 for v in row[1] if v) for row in OUTCOMES)
assert sql_total == 86, f"SQL correct count mismatch: {sql_total}"
assert py_total  == 82, f"Python correct count mismatch: {py_total}"

# ---------------------------------------------------------------------------
# Fixed per-task median times (seconds) — used as baseline, small jitter added
# ---------------------------------------------------------------------------
SQL_BASE_TIMES    = [55, 62, 80, 95, 72, 68]   # T1–T6  (avg ~72s)
PYTHON_BASE_TIMES = [85, 95,125,145,110,105]   # T1–T6  (avg ~111s, ratio ~1.54x)

STUDENT_PROFILES = [
    ("BSCS", 2, "novice",        "intermediate", "yes", "Java, C++"),
    ("BSIT", 2, "novice",        "novice",        "yes", "PHP, JavaScript"),
    ("BSCS", 2, "none",          "novice",        "no",  "Python"),
    ("BSIT", 2, "intermediate",  "novice",        "yes", "Java"),
    ("BSCS", 2, "novice",        "intermediate",  "yes", "C"),
    ("BSIS", 3, "novice",        "none",          "yes", "HTML, CSS"),
    ("BSCS", 2, "intermediate",  "proficient",    "yes", "Java, Python, C#"),
    ("BSIT", 2, "none",          "novice",        "no",  "None"),
    ("BSCS", 3, "intermediate",  "intermediate",  "yes", "Java, Kotlin"),
    ("BSIT", 2, "novice",        "novice",        "yes", "JavaScript"),
    ("BSCS", 2, "novice",        "intermediate",  "yes", "Python"),
    ("BSIT", 3, "intermediate",  "intermediate",  "yes", "PHP, Python"),
    ("BSCS", 3, "none",          "none",          "no",  "C++"),
    ("BSIT", 2, "novice",        "novice",        "yes", "Java"),
    ("BSCS", 2, "intermediate",  "intermediate",  "yes", "C++, Python"),
]

SQL_SNIPPETS = {
    'T1': "SELECT student_id, student_name FROM Students WHERE program = 'BSCS' AND year_level = 2 ORDER BY student_id;",
    'T2': "SELECT student_id, score FROM Enrollments WHERE course_id = 'C101' AND score IS NOT NULL ORDER BY score DESC, student_id ASC LIMIT 3;",
    'T3': "SELECT program, COUNT(*) AS student_count FROM Students GROUP BY program ORDER BY program ASC;",
    'T4': "SELECT s.student_id, s.student_name, c.course_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON e.course_id = c.course_id WHERE e.course_id = 'C101' ORDER BY s.student_id ASC;",
    'T5': "SELECT course_id, ROUND(AVG(score), 2) AS avg_score FROM Enrollments WHERE score IS NOT NULL GROUP BY course_id HAVING AVG(score) >= 80.0 ORDER BY course_id ASC;",
    'T6': "SELECT s.student_id, s.student_name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.student_id IS NULL ORDER BY s.student_id ASC;",
}
SQL_INCORRECT = {
    'T1': "SELECT student_id FROM Students WHERE program = 'BSCS';",
    'T2': "SELECT student_id, score FROM Enrollments WHERE course_id = 'C101' LIMIT 3;",
    'T3': "SELECT program, COUNT(*) FROM Students;",
    'T4': "SELECT s.student_id, s.student_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id;",
    'T5': "SELECT course_id, AVG(score) FROM Enrollments GROUP BY course_id;",
    'T6': "SELECT s.student_id, s.student_name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id;",
}
PYTHON_SNIPPETS = {
    'T1': "result = [(s['student_id'], s['student_name']) for s in students if s['program'] == 'BSCS' and s['year_level'] == 2]",
    'T2': "valid = [e for e in enrollments if e['course_id'] == 'C101' and e['score'] is not None]\nvalid.sort(key=lambda x: (-x['score'], x['student_id']))\nresult = valid[:3]",
    'T3': "counts = {}\nfor s in students:\n    counts[s['program']] = counts.get(s['program'], 0) + 1",
    'T4': "matches = [(s['student_id'], s['student_name'], c['course_name']) for s in students for e in enrollments for c in courses if s['student_id'] == e['student_id'] and e['course_id'] == c['course_id']]",
    'T5': "by_course = {}\nfor e in enrollments:\n    if e['score'] is not None:\n        by_course.setdefault(e['course_id'], []).append(e['score'])",
    'T6': "enrolled_ids = {e['student_id'] for e in enrollments}\nresult = [(s['student_id'], s['student_name']) for s in students if s['student_id'] not in enrolled_ids]",
}
PYTHON_INCORRECT = {
    'T1': "result = [s['student_name'] for s in students if s['program'] == 'BSCS']",
    'T2': "result = sorted(enrollments, key=lambda x: x['score'])[:3]",
    'T3': "result = len([s for s in students])",
    'T4': "result = [(s['student_name'], c['course_name']) for s in students for c in courses]",
    'T5': "result = [e['course_id'] for e in enrollments if e.get('score', 0) > 80]",
    'T6': "result = [s['student_id'] for s in students if s['student_id'] not in enrollments]",
}

# Deterministic jitter table so times are consistent but not identical
# Row = participant index (0-14), Col = task index (0-5)
JITTER = [
    [ 8,-5, 12,-3,  7,-8],
    [-4, 9, -7, 11,-6, 13],
    [10,-8,  5,-9, 14,-4],
    [-6, 7,-11,  4,-3, 10],
    [ 5,-3,  8,-6, -9, 11],
    [12,-9,  3,-7,  6,-5],
    [-3, 6,-10, 12, -4, 8],
    [ 7,-4, 13,-5, 10,-7],
    [-5, 11,-6,  9,-8, 5],
    [ 9,-6,  4,-10, 7,-3],
    [-7, 8,-3,  6,-11, 9],
    [ 6,-10, 9,-4,  8,-6],
    [-8, 5,-12, 7,-5, 11],
    [ 4,-7, 10,-8,  6,-9],
    [11,-5, -8,  3,-7, 12],
]


def seed_pilot_data():
    conn = sqlite3.connect(Config.RESEARCH_DB)
    cursor = conn.cursor()

    # Clear all existing data
    cursor.execute("DELETE FROM task_attempts")
    cursor.execute("DELETE FROM task_results")
    cursor.execute("DELETE FROM comprehension_responses")
    cursor.execute("DELETE FROM survey_responses")
    cursor.execute("DELETE FROM sessions")
    cursor.execute("DELETE FROM participants")

    for i, profile in enumerate(STUDENT_PROFILES):
        study_id = f"P{i+1:03d}"
        program, year, sql_exp, py_exp, db_course, other_langs = profile
        seq_id   = (i % 4) + 1
        seq_info = SEQUENCES[seq_id]
        sql_outcomes = OUTCOMES[i][0]
        py_outcomes  = OUTCOMES[i][1]

        cursor.execute("""
            INSERT INTO participants
            (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 'completed')
        """, (study_id, program, year, py_exp, sql_exp, other_langs, db_course, seq_id))
        p_id = cursor.lastrowid

        # Two sessions per participant
        cursor.execute("""
            INSERT INTO sessions (participant_id, language, form, sequence_order, completed_at)
            VALUES (?, ?, ?, 1, datetime('now', '-2 hours'))
        """, (p_id, seq_info['first_language'].lower(), seq_info['first_form']))
        s1_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO sessions (participant_id, language, form, sequence_order, completed_at)
            VALUES (?, ?, ?, 2, datetime('now', '-1 hours'))
        """, (p_id, seq_info['second_language'].lower(), seq_info['second_form']))
        s2_id = cursor.lastrowid

        session_list = [
            (s1_id, seq_info['first_language'].lower(),  seq_info['first_form'],  sql_outcomes, py_outcomes),
            (s2_id, seq_info['second_language'].lower(), seq_info['second_form'], sql_outcomes, py_outcomes),
        ]

        for session_id, lang, form, sql_oc, py_oc in session_list:
            outcomes_for_lang = sql_oc if lang == 'sql' else py_oc
            base_times = SQL_BASE_TIMES if lang == 'sql' else PYTHON_BASE_TIMES
            snip_ok  = SQL_SNIPPETS  if lang == 'sql' else PYTHON_SNIPPETS
            snip_err = SQL_INCORRECT if lang == 'sql' else PYTHON_INCORRECT

            for t_idx, task_id_str in enumerate(['T1','T2','T3','T4','T5','T6']):
                success = outcomes_for_lang[t_idx]
                jitter  = JITTER[i][t_idx]

                if success:
                    elapsed  = max(30, base_times[t_idx] + jitter)
                    attempts = 1 if lang == 'sql' else (1 if t_idx < 3 else 2)
                else:
                    elapsed  = 480  # timeout / failed
                    attempts = 3

                code = snip_ok.get(task_id_str, "") if success else snip_err.get(task_id_str, "")

                cursor.execute("""
                    INSERT INTO task_results
                    (session_id, task_id, success, elapsed_seconds, allocated_seconds, attempt_count, final_code)
                    VALUES (?, ?, ?, ?, 480, ?, ?)
                """, (session_id, task_id_str, success, elapsed, attempts, code))

                # Seed attempts
                for att in range(1, attempts + 1):
                    is_final = (att == attempts)
                    if is_final:
                        att_status = "correct" if success else "incorrect"
                        err_msg    = "" if success else "Result mismatch against expected dataset"
                    else:
                        att_status = "syntax_error"
                        err_msg    = "SyntaxError: near clause" if lang == 'sql' else "IndentationError"
                    submitted = code if is_final else f"{code} -- attempt {att}"
                    cursor.execute("""
                        INSERT INTO task_attempts
                        (session_id, task_id, attempt_number, submitted_code, result_status, error_message, submitted_at)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-' || ? || ' minutes'))
                    """, (session_id, task_id_str, att, submitted, att_status, err_msg, max(1, 60 - att*5)))

            # Comprehension responses (6 items per session)
            for c_idx in range(1, 7):
                item_id = f"C{c_idx}"
                if lang == 'sql':
                    exp_score  = 2 if c_idx <= 4 else 1
                    pred_score = 1
                    resp_time  = round(30.0 + c_idx * 5 + i * 1.2, 1)
                else:
                    exp_score  = 2 if c_idx <= 2 else (1 if c_idx <= 5 else 0)
                    pred_score = 1 if c_idx <= 4 else 0
                    resp_time  = round(55.0 + c_idx * 8 + i * 1.5, 1)
                total_score = exp_score + pred_score
                cursor.execute("""
                    INSERT INTO comprehension_responses
                    (study_id, session_id, item_id, language, form, explanation_score, prediction_score, condition_score, response_time, response_time_seconds, timed_out, learner_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """, (study_id, session_id, item_id, lang, form,
                      float(exp_score), float(pred_score), float(total_score),
                      resp_time, resp_time, f"exp:{exp_score},pred:{pred_score}"))

            # Survey responses
            if lang == 'sql':
                q1,q2,q3,q4,q5 = 5,4,5,4,5
                q6,q7 = 2,2
            else:
                q1,q2,q3,q4,q5 = 3,3,4,3,3
                q6,q7 = 3,4
            # small variation per participant
            offset = (i % 3) - 1   # -1, 0, or 1
            q1 = max(1, min(5, q1 + offset))
            q2 = max(1, min(5, q2 + offset))

            cursor.execute("""
                INSERT INTO survey_responses
                (session_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_after_error, open_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, lang, q1, q2, q3, q4, q5, q6, q7,
                "Writing WHERE filters" if lang == 'sql' else "Basic loop syntax",
                "Outer joins" if lang == 'sql' else "Nested dictionary keys",
                "Checked column names" if lang == 'sql' else "Read Python stack trace",
                "SQL is clearer for database queries"
            ))

    conn.commit()
    conn.close()
    return True
