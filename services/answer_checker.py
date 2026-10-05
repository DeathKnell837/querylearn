import math
import json
import sqlite3
import os


def check_answer(learner_output, expected_output, task_config=None):
    """Compare learner output with expected output from the visible dataset."""
    try:
        if not isinstance(learner_output, list) or not isinstance(expected_output, list):
            return {"correct": False, "feedback": "Output format mismatch: expected a list of records.", "classification": "runtime_error"}

        if len(learner_output) != len(expected_output):
            return {"correct": False, "feedback": f"Expected {len(expected_output)} rows, got {len(learner_output)} rows.", "classification": "incorrect"}

        for l_row, e_row in zip(learner_output, expected_output):
            if isinstance(l_row, dict):
                l_items = list(l_row.values())
            elif isinstance(l_row, (list, tuple)):
                l_items = list(l_row)
            else:
                l_items = [l_row]

            if isinstance(e_row, dict):
                e_items = list(e_row.values())
            elif isinstance(e_row, (list, tuple)):
                e_items = list(e_row)
            else:
                e_items = [e_row]

            if len(l_items) != len(e_items):
                return {"correct": False, "feedback": f"Column count mismatch: expected {len(e_items)} columns, got {len(l_items)}.", "classification": "incorrect"}

            for l_val, e_val in zip(l_items, e_items):
                if l_val is None and e_val is None:
                    continue
                if l_val is None or e_val is None:
                    return {"correct": False, "feedback": f"Value mismatch: got {l_val}, expected {e_val}", "classification": "incorrect"}
                if isinstance(l_val, (int, float)) and isinstance(e_val, (int, float)):
                    if not math.isclose(float(l_val), float(e_val), rel_tol=1e-5, abs_tol=1e-5):
                        return {"correct": False, "feedback": f"Value mismatch: got {l_val}, expected {e_val}", "classification": "incorrect"}
                elif str(l_val).strip() != str(e_val).strip():
                    return {"correct": False, "feedback": f"Value mismatch: got '{l_val}', expected '{e_val}'", "classification": "incorrect"}

        return {"correct": True, "feedback": "Correct! Task completed successfully.", "classification": "correct"}
    except Exception as e:
        return {"correct": False, "feedback": f"Verification error: {str(e)}", "classification": "runtime_error"}


def _load_hidden_tests(hidden_tests_path):
    """Load hidden test datasets from JSON file."""
    if not os.path.exists(hidden_tests_path):
        return {}
    with open(hidden_tests_path, 'r') as f:
        return json.load(f)


def _build_in_memory_db(test_data):
    """Build an in-memory SQLite DB from a hidden test dataset dict."""
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE Students(student_id INTEGER PRIMARY KEY, student_name TEXT, program TEXT, year_level INTEGER)')
    conn.execute('CREATE TABLE Courses(course_id TEXT PRIMARY KEY, course_name TEXT)')
    conn.execute('CREATE TABLE Enrollments(student_id INTEGER, course_id TEXT, score REAL, PRIMARY KEY(student_id, course_id))')

    for s in test_data.get('students', []):
        conn.execute('INSERT INTO Students VALUES(?,?,?,?)',
                     (s['student_id'], s['student_name'], s['program'], s['year_level']))
    for c in test_data.get('courses', []):
        conn.execute('INSERT INTO Courses VALUES(?,?)',
                     (c['course_id'], c['course_name']))
    for e in test_data.get('enrollments', []):
        conn.execute('INSERT INTO Enrollments VALUES(?,?,?)',
                     (e['student_id'], e['course_id'], e.get('score')))
    conn.commit()
    return conn


def run_hidden_tests_sql(sql_code, form, task_id, oracle_sql, hidden_tests_path):
    """
    Run learner SQL and oracle SQL against all hidden test datasets.
    Returns (all_passed: bool, failure_detail: str or None).
    """
    tests_data = _load_hidden_tests(hidden_tests_path)
    form_tests = tests_data.get(form, {})
    task_key = task_id if task_id.startswith('T') else f"T{task_id}"
    task_tests = form_tests.get(task_key, {}).get('tests', [])

    if not task_tests:
        return True, None  # No hidden tests available — pass by default

    for i, test in enumerate(task_tests):
        try:
            conn = _build_in_memory_db(test)

            # Run learner query
            try:
                learner_rows = [list(r) for r in conn.execute(sql_code).fetchall()]
            except Exception as e:
                conn.close()
                return False, f"Hidden test {i+1}: SQL error — {str(e)}"

            # Run oracle query
            oracle_rows = [list(r) for r in conn.execute(oracle_sql).fetchall()]
            conn.close()

            # Compare
            result = check_answer(learner_rows, oracle_rows)
            if not result['correct']:
                return False, f"Hidden test {i+1}: {result['feedback']}"

        except Exception as e:
            return False, f"Hidden test {i+1}: Internal error — {str(e)}"

    return True, None


def run_hidden_tests_python(python_code, form, task_id, oracle_sql, hidden_tests_path, python_runner_fn):
    """
    Run learner Python code and oracle SQL against all hidden test datasets.
    Returns (all_passed: bool, failure_detail: str or None).
    """
    import ast as ast_module

    tests_data = _load_hidden_tests(hidden_tests_path)
    form_tests = tests_data.get(form, {})
    task_key = task_id if task_id.startswith('T') else f"T{task_id}"
    task_tests = form_tests.get(task_key, {}).get('tests', [])

    if not task_tests:
        return True, None

    for i, test in enumerate(task_tests):
        try:
            # Build test data variables
            data_vars = {
                'students': test.get('students', []),
                'courses': test.get('courses', []),
                'enrollments': test.get('enrollments', []),
            }

            # Run learner Python code
            learner_res = python_runner_fn(python_code, data_vars, timeout=10)
            if learner_res.get('error'):
                return False, f"Hidden test {i+1}: Python error — {learner_res['error']}"

            # Run oracle SQL to get expected output
            conn = _build_in_memory_db(test)
            oracle_rows = [list(r) for r in conn.execute(oracle_sql).fetchall()]
            conn.close()

            # Parse learner output
            output_str = learner_res.get('output', '').strip()
            parsed = None
            try:
                parsed = ast_module.literal_eval(output_str)
            except Exception:
                pass

            if not isinstance(parsed, list):
                lines = [l.strip() for l in output_str.splitlines() if l.strip()]
                line_parsed = []
                valid = True
                for line in lines:
                    try:
                        val = ast_module.literal_eval(line)
                        line_parsed.append(val)
                    except Exception:
                        valid = False
                        break
                if valid and line_parsed:
                    parsed = line_parsed

            if isinstance(parsed, list):
                result = check_answer(parsed, oracle_rows)
                if not result['correct']:
                    return False, f"Hidden test {i+1}: {result['feedback']}"
            else:
                return False, f"Hidden test {i+1}: Could not parse output as a list of records."

        except Exception as e:
            return False, f"Hidden test {i+1}: Internal error — {str(e)}"

    return True, None
