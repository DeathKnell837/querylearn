import sqlite3
import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from services.task_catalog import get_task, SCHEMA_METADATA
from services.sequence_manager import get_sequence_details
from config import Config

experiment_bp = Blueprint('experiment', __name__, url_prefix='/experiment')


def participant_required(f):
    """Item 5: Route guard — ensures participant is logged in via session."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('participant_id'):
            return redirect(url_for('auth.register'))
        return f(*args, **kwargs)
    return wrapper


@experiment_bp.route('/instructions')
@participant_required
def instructions():
    session['instructions_completed'] = True
    return render_template('instructions.html')


@experiment_bp.route('/practice')
@participant_required
def practice():
    if not session.get('instructions_completed'):
        return redirect(url_for('experiment.instructions'))
    return render_template('practice.html')


@experiment_bp.route('/practice/run', methods=['POST'])
@participant_required
def practice_run():
    return jsonify({"success": True})


@experiment_bp.route('/practice/complete', methods=['POST'])
@participant_required
def practice_complete():
    """Item 5: Track practice completion server-side."""
    session['practice_completed'] = True
    return jsonify({"success": True, "redirect": url_for('experiment.readiness')})


@experiment_bp.route('/readiness', methods=['GET', 'POST'])
@participant_required
def readiness():
    """Item 5: Validate readiness answers server-side."""
    if not session.get('practice_completed'):
        return redirect(url_for('experiment.practice'))

    if request.method == 'POST':
        q1 = request.form.get('q1', '').strip().lower()
        q2 = request.form.get('q2', '').strip().lower()
        # Q1 correct is 'b', Q2 correct is 'c'
        if q1 == 'b' and q2 == 'c':
            session['readiness_completed'] = True
            return redirect(url_for('experiment.start'))
        else:
            flash("Please answer both readiness questions correctly to proceed.", "error")
            return render_template('readiness_check.html', error=True)

    return render_template('readiness_check.html')


@experiment_bp.route('/start')
@participant_required
def start():
    """Item 5: Enforce step order — readiness must be completed."""
    if not session.get('readiness_completed'):
        return redirect(url_for('experiment.readiness'))

    seq_id = session.get('sequence_id', 1)
    seq_info = get_sequence_details(seq_id)

    first_lang = seq_info.get('first_language', 'sql').lower()
    first_form = seq_info.get('first_form', 'A')

    session['current_condition_step'] = 1
    session['current_language'] = first_lang
    session['current_form'] = first_form
    session['current_session_id'] = session.get('session_1_id')
    session['highest_unlocked_task'] = 1

    # Redirect to Task 1 of first condition
    return redirect(url_for('experiment.task', language=first_lang, task_id=1))


@experiment_bp.route('/task/<language>/<task_id>')
@participant_required
def task(language, task_id):
    """
    Items 4 & 5:
    - Route guard: must have completed readiness
    - Order enforcement: cannot skip ahead to uncompleted tasks
    - Server-side timer: record start timestamp on first load, resume with remaining time on refresh
    """
    if not session.get('readiness_completed'):
        return redirect(url_for('experiment.readiness'))

    current_form = session.get('current_form', 'A')
    clean_id = str(task_id).upper().replace('T', '').strip()
    task_num = int(clean_id) if clean_id.isdigit() else 1

    # Enforce task order within condition
    highest_unlocked = session.get('highest_unlocked_task', 1)
    if task_num > highest_unlocked:
        return redirect(url_for('experiment.task', language=language, task_id=highest_unlocked))

    task_obj = get_task(current_form, task_num)
    if not task_obj:
        task_num = 1
        task_obj = get_task(current_form, 1)

    formatted_task_id = f"T{task_num}"
    session_id = session.get('current_session_id')
    if not session_id:
        # Fallback to session_1_id if step 1 or session_2_id if step 2
        step = session.get('current_condition_step', 1)
        session_id = session.get(f'session_{step}_id')
        session['current_session_id'] = session_id

    # --- Item 4: Server-side timer initialization / lookup ---
    remaining_seconds = Config.TASK_TIMEOUT_SECONDS
    if session_id:
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
                started = datetime.datetime.fromisoformat(row[0])
                now = datetime.datetime.now()
                elapsed = (now - started).total_seconds()
                remaining_seconds = max(0, int(Config.TASK_TIMEOUT_SECONDS - elapsed))
            else:
                now_str = datetime.datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO task_timers (session_id, task_id, task_started_at) VALUES (?, ?, ?)",
                    (session_id, formatted_task_id, now_str)
                )
                conn.commit()
            conn.close()
        except Exception:
            pass

    template_name = 'task_sql.html' if language == 'sql' else 'task_python.html'
    return render_template(
        template_name,
        task=task_obj,
        current_task_num=task_num,
        current_form=current_form,
        schema=SCHEMA_METADATA,
        remaining_seconds=remaining_seconds
    )


@experiment_bp.route('/comprehension/<language>', methods=['GET', 'POST'])
@participant_required
def comprehension(language):
    """Item 5: Comprehension questions assessed after condition tasks."""
    # Ensure participant completed all 6 tasks before comprehension
    if session.get('highest_unlocked_task', 1) < 7:
        task_id = session.get('highest_unlocked_task', 1)
        return redirect(url_for('experiment.task', language=language, task_id=min(6, task_id)))

    if request.method == 'POST':
        sess_id = session.get('current_session_id')
        q1 = request.form.get('q1', '')
        q2 = request.form.get('q2', '')
        q3 = request.form.get('q3', '')

        # Grade questions (q1 correct is 'b', q2 is 'c', q3 is 'b')
        score_1 = 1.0 if q1 == 'b' else 0.0
        score_2 = 1.0 if q2 == 'c' else 0.0
        score_3 = 1.0 if q3 == 'b' else 0.0

        if sess_id:
            try:
                conn = sqlite3.connect(Config.RESEARCH_DB)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO comprehension_responses
                    (session_id, item_id, language, explanation_score, prediction_score, condition_score, learner_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sess_id, f"comp_{language}", language, score_1, score_2, score_3, f"q1:{q1},q2:{q2},q3:{q3}"))
                conn.commit()
                conn.close()
            except Exception:
                pass

        session['comprehension_completed'] = True
        return redirect(url_for('experiment.survey', language=language))

    return render_template('comprehension.html', language=language)


@experiment_bp.route('/survey/<language>', methods=['GET', 'POST'])
@participant_required
def survey(language):
    """Item 5: Survey submitted after comprehension."""
    if not session.get('comprehension_completed'):
        return redirect(url_for('experiment.comprehension', language=language))

    if request.method == 'POST':
        sess_id = session.get('current_session_id')
        
        def parse_score(val):
            if val is None or str(val).strip().lower() in ('na', 'null', 'none', ''):
                return None
            try:
                iv = int(val)
                return iv if 1 <= iv <= 5 else None
            except (ValueError, TypeError):
                return None

        q1 = parse_score(request.form.get('survey_likert_1'))
        q2 = parse_score(request.form.get('survey_likert_2'))
        q3 = parse_score(request.form.get('survey_likert_3'))
        q4 = parse_score(request.form.get('survey_likert_4'))
        q5 = parse_score(request.form.get('survey_likert_5'))
        q6 = parse_score(request.form.get('survey_effort'))
        q7 = parse_score(request.form.get('survey_fatigue'))
        
        open_easiest = request.form.get('open_easiest') or request.form.get('survey_open_2') or ''
        open_hardest = request.form.get('open_hardest') or request.form.get('survey_open_1') or ''
        open_after_error = request.form.get('open_after_error') or request.form.get('survey_open_4') or ''
        open_pref = request.form.get('open_preference') or request.form.get('survey_open_3') or ''

        if sess_id:
            try:
                conn = sqlite3.connect(Config.RESEARCH_DB)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO survey_responses 
                    (session_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_after_error, open_preference)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (sess_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_after_error, open_pref))

                step = session.get('current_condition_step', 1)
                if step >= 2:
                    # Both conditions completed - update participant status to completed
                    part_id = session.get('participant_id')
                    if part_id:
                        c.execute("UPDATE participants SET status = 'completed' WHERE id = ?", (part_id,))

                conn.commit()
                conn.close()
            except Exception:
                pass

        step = session.get('current_condition_step', 1)
        if step == 1:
            return redirect(url_for('experiment.break_page'))
        else:
            return redirect(url_for('experiment.complete'))

    return render_template('survey.html', language=language, condition_step=session.get('current_condition_step', 1))


@experiment_bp.route('/break')
@participant_required
def break_page():
    """Item 5: Rest break between condition 1 and condition 2."""
    seq_id = session.get('sequence_id', 1)
    seq_info = get_sequence_details(seq_id)

    second_lang = seq_info.get('second_language', 'python').lower()
    second_form = seq_info.get('second_form', 'B')

    # Prepare condition 2 session state
    session['current_condition_step'] = 2
    session['current_language'] = second_lang
    session['current_form'] = second_form
    session['current_session_id'] = session.get('session_2_id')
    session['highest_unlocked_task'] = 1
    session['comprehension_completed'] = False

    return render_template('break.html', next_language=second_lang)


@experiment_bp.route('/complete')
@participant_required
def complete():
    return render_template('complete.html')
