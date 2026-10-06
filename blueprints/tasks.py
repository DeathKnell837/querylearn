import os
import sqlite3
import time
import ast
from functools import wraps
from flask import Blueprint, request, jsonify, session, url_for
from config import Config
from services.sql_runner import execute_sql
from services.python_runner import execute_python
from services.answer_checker import check_answer, run_hidden_tests_sql, run_hidden_tests_python
from services.task_catalog import get_task, TASK_CATALOG

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')


def participant_api_required(f):
    """Item 5: Enforce participant session on every experiment API route. Never default to session 1."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('participant_id') or not session.get('current_session_id'):
            return jsonify({
                "success": False,
                "error": "Unauthorized: No active participant session. Please register first.",
                "correct": False,
                "task_complete": False
            }), 401
        return f(*args, **kwargs)
    return wrapper


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


def _get_server_elapsed(session_id, task_id):
    """Item 4: Get elapsed seconds calculated from server-side task_started_at timestamp."""
    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT task_started_at FROM task_timers WHERE session_id = ? AND task_id = ?",
            (session_id, task_id)
        )
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            import datetime
            started = datetime.datetime.fromisoformat(row[0])
            now = datetime.datetime.now()
            return (now - started).total_seconds()
    except Exception:
        pass
    return None


def _is_already_submitted(session_id, task_id):
    """Item 5: Check if a final result already exists for this session+task to reject duplicates."""
    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM task_results WHERE session_id = ? AND task_id = ?",
            (session_id, task_id)
        )
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False


@tasks_bp.route('/run', methods=['POST'])
@participant_api_required
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
@participant_api_required
def submit():
    data = request.get_json() or {}
    code = data.get('code', '').strip()
    language = data.get('language', 'sql').lower()
    task_id = str(data.get('task_id', '1'))
    form = data.get('form', session.get('current_form', 'A')).upper()
    timed_out = data.get('timed_out', False)
    client_elapsed = data.get('elapsed_seconds', 0)

    db_path = get_experiment_db_path(form)
    task_info = get_task(form, task_id)
    if not task_info:
        return jsonify({"correct": False, "feedback": "Unknown task identifier.", "task_complete": False})

    clean_num_str = str(task_id).upper().replace('T', '').strip()
    current_num = int(clean_num_str) if clean_num_str.isdigit() else 1
    formatted_task_id = f"T{current_num}"

    session_id = session['current_session_id']

    # Calculate next URL: tasks 1 to 5 go to next task, task 6 goes to comprehension!
    if current_num < Config.TASKS_PER_FORM:
        next_url = url_for('experiment.task', language=language, task_id=current_num + 1)
    else:
        next_url = url_for('experiment.comprehension', language=language)

    # --- Item 5: Reject duplicate submissions server-side ---
    if _is_already_submitted(session_id, formatted_task_id):
        # Unlock next task in session
        session['highest_unlocked_task'] = max(session.get('highest_unlocked_task', 1), current_num + 1)
        return jsonify({
            "correct": True,
            "feedback": "This task was already submitted.",
            "task_complete": True,
            "next_task_url": next_url
        })

    # --- Item 4: Server-side timer calculation ---
    server_elapsed = _get_server_elapsed(session_id, formatted_task_id)
    if server_elapsed is not None:
        elapsed_seconds = server_elapsed
        if server_elapsed >= Config.TASK_TIMEOUT_SECONDS:
            timed_out = True
    else:
        elapsed_seconds = client_elapsed

    if timed_out:
        log_attempt(session_id, language, form, formatted_task_id, code, "timed_out", "Time limit reached.")
        log_task_result(session_id, language, form, formatted_task_id, False, min(elapsed_seconds, Config.TASK_TIMEOUT_SECONDS), code, failure_reason="timed_out")
        session['highest_unlocked_task'] = max(session.get('highest_unlocked_task', 1), current_num + 1)
        return jsonify({
            "correct": False,
            "feedback": "Time limit of 8 minutes exceeded for this task.",
            "task_complete": True,
            "next_task_url": next_url
        })

    is_correct = False
    feedback = ""
    oracle_sql = task_info.get('oracle_sql', '')

    if language == 'sql':
        # Execute learner query on visible data
        learner_res = execute_sql(db_path, code, timeout=Config.CODE_EXECUTION_TIMEOUT)
        if learner_res['error']:
            log_attempt(session_id, language, form, formatted_task_id, code, "syntax_error", learner_res['error'])
            return jsonify({
                "correct": False,
                "feedback": f"SQL Error: {learner_res['error']}",
                "task_complete": False
            })

        # Execute oracle query on visible data
        oracle_res = execute_sql(db_path, oracle_sql, timeout=Config.CODE_EXECUTION_TIMEOUT)

        # Compare outputs on visible data
        check_res = check_answer(learner_res.get('rows', []), oracle_res.get('rows', []), task_info)
        is_correct = check_res['correct']
        feedback = check_res['feedback']

        # --- Item 1: Run hidden test datasets ---
        if is_correct:
            hidden_passed, hidden_detail = run_hidden_tests_sql(
                code, form, formatted_task_id, oracle_sql, Config.HIDDEN_TESTS
            )
            if not hidden_passed:
                is_correct = False
                feedback = f"Your query produced correct results on the visible data but failed on a hidden dataset: {hidden_detail}"

        log_attempt(session_id, language, form, formatted_task_id, code,
                    "correct" if is_correct else check_res['classification'], feedback)

    else:
        # Python check
        students = fetch_table_as_dicts(db_path, "Students")
        courses = fetch_table_as_dicts(db_path, "Courses")
        enrollments = fetch_table_as_dicts(db_path, "Enrollments")
        data_vars = {"students": students, "courses": courses, "enrollments": enrollments}

        learner_res = execute_python(code, data_vars, timeout=Config.CODE_EXECUTION_TIMEOUT)
        if learner_res['error']:
            log_attempt(session_id, language, form, formatted_task_id, code, "runtime_error", learner_res['error'])
            return jsonify({
                "correct": False,
                "feedback": f"Python Error: {learner_res['error']}",
                "task_complete": False
            })

        # Oracle expected rows on visible data
        oracle_res = execute_sql(db_path, oracle_sql, timeout=Config.CODE_EXECUTION_TIMEOUT)
        output_str = learner_res.get('output', '').strip()
        expected_rows = oracle_res.get('rows', [])

        parsed = None
        try:
            parsed = ast.literal_eval(output_str)
        except Exception:
            pass

        if not isinstance(parsed, list):
            lines = [l.strip() for l in output_str.splitlines() if l.strip()]
            line_parsed = []
            valid = True
            for line in lines:
                try:
                    val = ast.literal_eval(line)
                    line_parsed.append(val)
                except Exception:
                    valid = False
                    break
            if valid and line_parsed:
                parsed = line_parsed

        if isinstance(parsed, list):
            check_res = check_answer(parsed, expected_rows, task_info)
            is_correct = check_res['correct']
            feedback = check_res['feedback'] if not is_correct else "Correct procedural Python output generated!"

            # --- Item 1: Run hidden test datasets for Python ---
            if is_correct:
                hidden_passed, hidden_detail = run_hidden_tests_python(
                    code, form, formatted_task_id, oracle_sql,
                    Config.HIDDEN_TESTS, execute_python
                )
                if not hidden_passed:
                    is_correct = False
                    feedback = f"Your code produced correct results on the visible data but failed on a hidden dataset: {hidden_detail}"

            log_attempt(session_id, language, form, formatted_task_id, code,
                        "correct" if is_correct else check_res.get('classification', 'incorrect'), feedback)
        else:
            is_correct = False
            feedback = "Output printed to stdout did not match expected structure. Print a list of records/tuples."
            log_attempt(session_id, language, form, formatted_task_id, code, "incorrect", feedback)

    if is_correct:
        log_task_result(session_id, language, form, formatted_task_id, True, elapsed_seconds, code)
        session['highest_unlocked_task'] = max(session.get('highest_unlocked_task', 1), current_num + 1)
        return jsonify({
            "correct": True,
            "feedback": "Correct! Task completed successfully.",
            "task_complete": True,
            "next_task_url": next_url
        })
    else:
        # Check if participant reached maximum attempt limit (5 attempts)
        conn = sqlite3.connect(Config.RESEARCH_DB)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM task_attempts WHERE session_id = ? AND task_id = ?", (session_id, formatted_task_id))
        count_row = c.fetchone()
        attempts_so_far = count_row[0] if count_row else 1
        conn.close()

        if attempts_so_far >= 5:
            log_task_result(session_id, language, form, formatted_task_id, False, elapsed_seconds, code, failure_reason="max_attempts_reached")
            session['highest_unlocked_task'] = max(session.get('highest_unlocked_task', 1), current_num + 1)
            return jsonify({
                "correct": False,
                "feedback": f"{feedback} Maximum attempts (5) reached. Proceeding to next task...",
                "task_complete": True,
                "next_task_url": next_url,
                "attempt_count": attempts_so_far
            })

        return jsonify({
            "correct": False,
            "feedback": feedback,
            "task_complete": False,
            "attempt_count": attempts_so_far
        })


@tasks_bp.route('/skip', methods=['POST'])
@participant_api_required
def skip():
    """Item 6: Log skip as abandoned in task_attempts AND task_results with success=0, counted as full 480s."""
    data = request.get_json() or {}
    language = data.get('language', 'sql').lower()
    task_id = str(data.get('task_id', '1'))
    form = data.get('form', session.get('current_form', 'A')).upper()

    clean_num_str = task_id.upper().replace('T', '').strip()
    current_num = int(clean_num_str) if clean_num_str.isdigit() else 1
    formatted_task_id = f"T{current_num}"

    session_id = session['current_session_id']

    # Don't re-log if already recorded
    if not _is_already_submitted(session_id, formatted_task_id):
        log_attempt(session_id, language, form, formatted_task_id, "", "abandoned", "Task skipped by participant.")
        log_task_result(session_id, language, form, formatted_task_id, False, 480, "", failure_reason="abandoned")

    session['highest_unlocked_task'] = max(session.get('highest_unlocked_task', 1), current_num + 1)

    if current_num < Config.TASKS_PER_FORM:
        next_url = url_for('experiment.task', language=language, task_id=current_num + 1)
    else:
        next_url = url_for('experiment.comprehension', language=language)

    return jsonify({"next_task_url": next_url})


@tasks_bp.route('/start-timer', methods=['POST'])
@participant_api_required
def start_timer():
    """Item 4: Record server-side task_started_at timestamp on first load."""
    data = request.get_json() or {}
    task_id = str(data.get('task_id', '1'))
    clean_num_str = task_id.upper().replace('T', '').strip()
    current_num = int(clean_num_str) if clean_num_str.isdigit() else 1
    formatted_task_id = f"T{current_num}"

    session_id = session['current_session_id']

    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_timers (
                session_id INTEGER,
                task_id TEXT,
                task_started_at TEXT,
                PRIMARY KEY (session_id, task_id)
            )
        """)

        cursor.execute(
            "SELECT task_started_at FROM task_timers WHERE session_id = ? AND task_id = ?",
            (session_id, formatted_task_id)
        )
        row = cursor.fetchone()

        if row and row[0]:
            import datetime
            started = datetime.datetime.fromisoformat(row[0])
            now = datetime.datetime.now()
            elapsed = (now - started).total_seconds()
            remaining = max(0, Config.TASK_TIMEOUT_SECONDS - elapsed)
            conn.close()
            return jsonify({"remaining_seconds": remaining, "resumed": True})
        else:
            import datetime
            now_str = datetime.datetime.now().isoformat()
            cursor.execute(
                "INSERT OR REPLACE INTO task_timers (session_id, task_id, task_started_at) VALUES (?, ?, ?)",
                (session_id, formatted_task_id, now_str)
            )
            conn.commit()
            conn.close()
            return jsonify({"remaining_seconds": Config.TASK_TIMEOUT_SECONDS, "resumed": False})
    except Exception as e:
        return jsonify({"remaining_seconds": Config.TASK_TIMEOUT_SECONDS, "resumed": False, "error": str(e)})


def log_attempt(session_id, language, form, task_id, code, status, error_msg):
    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM task_attempts WHERE session_id = ? AND task_id = ?", (session_id, task_id))
        count_row = cursor.fetchone()
        attempt_number = (count_row[0] if count_row else 0) + 1

        cursor.execute("""
            INSERT INTO task_attempts (session_id, task_id, attempt_number, submitted_code, result_status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, task_id, attempt_number, code, status, str(error_msg)))
        conn.commit()
        conn.close()

        # Sync attempt to Supabase cloud database
        try:
            from services.cloud_db import sync_task_attempt_to_cloud
            sync_task_attempt_to_cloud({
                "session_id": session_id,
                "task_id": task_id,
                "attempt_number": attempt_number,
                "submitted_code": code,
                "result_status": status,
                "error_message": str(error_msg)
            })
        except Exception:
            pass
    except Exception:
        pass


def log_task_result(session_id, language, form, task_id, success, elapsed, code, failure_reason=None):
    try:
        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM task_attempts WHERE session_id = ? AND task_id = ?", (session_id, task_id))
        count_row = cursor.fetchone()
        attempt_count = max(1, count_row[0] if count_row else 1)

        lines_count = len(code.splitlines()) if code else 0
        chars_count = len(code) if code else 0

        # Remove previous result for same session and task if exists to ensure idempotency
        cursor.execute("DELETE FROM task_results WHERE session_id = ? AND task_id = ?", (session_id, task_id))

        cursor.execute("""
            INSERT INTO task_results (session_id, task_id, success, start_time, end_time, elapsed_seconds, allocated_seconds, attempt_count, final_code, source_lines, source_chars, failure_reason)
            VALUES (?, ?, ?, datetime('now', '-' || ? || ' seconds'), datetime('now'), ?, 480, ?, ?, ?, ?, ?)
        """, (session_id, task_id, 1 if success else 0, str(int(elapsed)), elapsed, attempt_count, code, lines_count, chars_count, failure_reason))
        conn.commit()
        conn.close()

        # Sync result to Supabase cloud database
        try:
            from services.cloud_db import sync_task_result_to_cloud
            sync_task_result_to_cloud({
                "session_id": session_id,
                "task_id": task_id,
                "success": bool(success),
                "elapsed_seconds": elapsed,
                "allocated_seconds": 480,
                "attempt_count": attempt_count,
                "final_code": code,
                "source_lines": lines_count,
                "source_chars": chars_count,
                "failure_reason": failure_reason
            })
        except Exception:
            pass
    except Exception:
        pass
