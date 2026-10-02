import os
import sqlite3
import time
import ast
from flask import Blueprint, request, jsonify, session, url_for
from config import Config
from services.sql_runner import execute_sql
from services.python_runner import execute_python
from services.answer_checker import check_answer
from services.task_catalog import get_task, TASK_CATALOG

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')

def get_experiment_db_path(form):
    form = form.upper() if form else "A"
    return Config.EXPERIMENT_A_DB if form == "A" else Config.EXPERIMENT_B_DB

def fetch_table_as_dicts(db_path, table_name):
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []

@tasks_bp.route('/run', methods=['POST'])
def run():
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    language = data.get('language', 'sql').lower()
    form = data.get('form', session.get('current_form', 'A')).upper()
    db_path = get_experiment_db_path(form)

    if not code:
        return jsonify({"success": False, "error": "No code provided to execute.", "columns": [], "rows": [], "execution_time": 0})

    if language == 'sql':
        result = execute_sql(db_path, code, timeout=Config.CODE_EXECUTION_TIMEOUT)
        return jsonify({
            "success": result['error'] is None,
            "columns": result.get('columns', []),
            "rows": result.get('rows', []),
            "error": result.get('error'),
            "execution_time": result.get('execution_time', 0.01)
        })
    else:
        # Load python environment data objects
        students = fetch_table_as_dicts(db_path, "Students")
        courses = fetch_table_as_dicts(db_path, "Courses")
        enrollments = fetch_table_as_dicts(db_path, "Enrollments")
        data_vars = {
            "students": students,
            "courses": courses,
            "enrollments": enrollments
        }
        try:
            result = execute_python(code, data_vars, timeout=Config.CODE_EXECUTION_TIMEOUT)
            return jsonify({
                "success": result['error'] is None,
                "output": result.get('output', ''),
                "error": result.get('error'),
                "execution_time": result.get('execution_time', 0.05)
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "execution_time": 0
            })

@tasks_bp.route('/submit', methods=['POST'])
def submit():
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    language = data.get('language', 'sql').lower()
    task_id = str(data.get('task_id', '1'))
    form = data.get('form', session.get('current_form', 'A')).upper()
    timed_out = data.get('timed_out', False)
    elapsed_seconds = data.get('elapsed_seconds', 0)

    db_path = get_experiment_db_path(form)
    task_info = get_task(form, task_id)
    if not task_info:
        return jsonify({"correct": False, "feedback": "Unknown task identifier.", "task_complete": False})

    # Calculate next URL
    clean_num_str = task_id.upper().replace('T', '').strip()
    current_num = int(clean_num_str) if clean_num_str.isdigit() else 1
    if current_num < Config.TASKS_PER_FORM:
        next_url = url_for('experiment.task', language=language, task_id=current_num + 1)
    else:
        next_url = url_for('experiment.survey', language=language)

    if timed_out:
        log_attempt(language, form, task_id, code, "timed_out", "Time limit reached.")
        return jsonify({
            "correct": False,
            "feedback": "Time limit of 8 minutes exceeded for this task.",
            "task_complete": True,
            "next_task_url": next_url
        })

    is_correct = False
    feedback = ""

    if language == 'sql':
        # Execute learner query
        learner_res = execute_sql(db_path, code, timeout=Config.CODE_EXECUTION_TIMEOUT)
        if learner_res['error']:
            log_attempt(language, form, task_id, code, "syntax_error", learner_res['error'])
            return jsonify({
                "correct": False,
                "feedback": f"SQL Error: {learner_res['error']}",
                "task_complete": False
            })

        # Execute oracle query
        oracle_sql = task_info.get('oracle_sql', '')
        oracle_res = execute_sql(db_path, oracle_sql, timeout=Config.CODE_EXECUTION_TIMEOUT)

        # Compare outputs
        check_res = check_answer(learner_res.get('rows', []), oracle_res.get('rows', []), task_info)
        is_correct = check_res['correct']
        feedback = check_res['feedback']
        log_attempt(language, form, task_id, code, check_res['classification'], feedback)

    else:
        # Python check
        students = fetch_table_as_dicts(db_path, "Students")
        courses = fetch_table_as_dicts(db_path, "Courses")
        enrollments = fetch_table_as_dicts(db_path, "Enrollments")
        data_vars = {"students": students, "courses": courses, "enrollments": enrollments}

        learner_res = execute_python(code, data_vars, timeout=Config.CODE_EXECUTION_TIMEOUT)
        if learner_res['error']:
            log_attempt(language, form, task_id, code, "runtime_error", learner_res['error'])
            return jsonify({
                "correct": False,
                "feedback": f"Python Error: {learner_res['error']}",
                "task_complete": False
            })

        # Evaluate expected python output using oracle sql rows
        oracle_sql = task_info.get('oracle_sql', '')
        oracle_res = execute_sql(db_path, oracle_sql, timeout=Config.CODE_EXECUTION_TIMEOUT)
        
        # Check if output contains expected result representation
        output_str = learner_res.get('output', '').strip()
        expected_rows = oracle_res.get('rows', [])
        
        parsed = None
        try:
            parsed = ast.literal_eval(output_str)
        except Exception:
            pass

        if isinstance(parsed, list):
            check_res = check_answer(parsed, expected_rows, task_info)
            is_correct = check_res['correct']
            feedback = check_res['feedback'] if not is_correct else "Correct procedural Python output generated!"
            log_attempt(language, form, task_id, code, check_res['classification'], feedback)
        elif expected_rows and (str(len(expected_rows)) in output_str or any(str(r[0]) in output_str for r in expected_rows)):
            is_correct = True
            feedback = "Correct procedural Python output generated!"
            log_attempt(language, form, task_id, code, "correct", feedback)
        else:
            is_correct = False
            feedback = "Output printed to stdout did not match expected structure."
            log_attempt(language, form, task_id, code, "incorrect", feedback)

    if is_correct:
        log_task_result(language, form, task_id, True, elapsed_seconds, code)
        return jsonify({
            "correct": True,
            "feedback": "Correct! Task completed successfully.",
            "task_complete": True,
            "next_task_url": next_url
        })
    else:
        return jsonify({
            "correct": False,
            "feedback": feedback,
            "task_complete": False
        })

@tasks_bp.route('/skip', methods=['POST'])
def skip():
    data = request.get_json() or {}
    language = data.get('language', 'sql').lower()
    task_id = str(data.get('task_id', '1'))
    form = data.get('form', session.get('current_form', 'A')).upper()

    log_task_result(language, form, task_id, False, 480, "")

    current_num = int(task_id) if task_id.isdigit() else 1
    if current_num < Config.TASKS_PER_FORM:
        next_url = url_for('experiment.task', language=language, task_id=current_num + 1)
    else:
        next_url = url_for('experiment.survey', language=language)

    return jsonify({"next_task_url": next_url})

def log_attempt(language, form, task_id, code, status, error_msg):
    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()
        session_id = session.get('current_session_id', 1)
        cursor.execute("""
            INSERT INTO task_attempts (session_id, task_id, attempt_number, submitted_code, result_status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, task_id, 1, code, status, str(error_msg)))
        conn.commit()
        conn.close()
    except Exception:
        pass

def log_task_result(language, form, task_id, success, elapsed, code):
    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()
        session_id = session.get('current_session_id', 1)
        cursor.execute("""
            INSERT OR REPLACE INTO task_results (session_id, task_id, success, start_time, end_time, elapsed_seconds, allocated_seconds, final_code)
            VALUES (?, ?, ?, datetime('now', '-8 minutes'), datetime('now'), ?, 480, ?)
        """, (session_id, task_id, success, elapsed, code))
        conn.commit()
        conn.close()
    except Exception:
        pass
