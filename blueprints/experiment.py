import sqlite3
import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash, current_app
from services.task_catalog import get_task, SCHEMA_METADATA
from services.sequence_manager import get_sequence_details
from services.comprehension_items import get_item, grade_item
from config import Config

experiment_bp = Blueprint('experiment', __name__, url_prefix='/experiment')

def get_research_db_path():
    try:
        return current_app.config.get('RESEARCH_DB', Config.RESEARCH_DB)
    except RuntimeError:
        return Config.RESEARCH_DB


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
    total_seconds = Config.TASK_TIMEOUT_SECONDS
    remaining_seconds = total_seconds

    timer_session_key = f"timer_start_{session_id}_{formatted_task_id}"
    started_iso = session.get(timer_session_key)
    now = datetime.datetime.now()

    if not started_iso:
        db_started = None
        if session_id:
            try:
                conn = sqlite3.connect(get_research_db_path())
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
                    db_started = row[0]
                else:
                    now_str = now.isoformat()
                    cursor.execute(
                        "INSERT INTO task_timers (session_id, task_id, task_started_at) VALUES (?, ?, ?)",
                        (session_id, formatted_task_id, now_str)
                    )
                    conn.commit()
                    db_started = now_str
                conn.close()
            except Exception:
                pass
        started_iso = db_started or now.isoformat()
        session[timer_session_key] = started_iso

    try:
        started = datetime.datetime.fromisoformat(started_iso)
        elapsed = (now - started).total_seconds()
        remaining_seconds = max(0, int(total_seconds - elapsed))
    except Exception:
        remaining_seconds = total_seconds

    template_name = 'task_sql.html' if language == 'sql' else 'task_python.html'
    return render_template(
        template_name,
        task=task_obj,
        current_task_num=task_num,
        current_form=current_form,
        schema=SCHEMA_METADATA,
        remaining_seconds=remaining_seconds,
        total_seconds=total_seconds
    )


@experiment_bp.route('/comprehension', methods=['GET', 'POST'])
@participant_required
def comprehension_fallback():
    lang = session.get('current_language', 'sql')
    return redirect(url_for('experiment.comprehension', language=lang))


@experiment_bp.route('/comprehension/<language>', methods=['GET', 'POST'])
@participant_required
def comprehension(language):
    """Comprehension assessment: 6 items (C1 to C6), one per task family."""
    # Ensure participant completed all 6 tasks before comprehension
    if session.get('highest_unlocked_task', 1) < 7:
        task_id = session.get('highest_unlocked_task', 1)
        return redirect(url_for('experiment.task', language=language, task_id=min(6, task_id)))

    sess_id = session.get('current_session_id')
    if not sess_id:
        step = session.get('current_condition_step', 1)
        sess_id = session.get(f'session_{step}_id')
        session['current_session_id'] = sess_id

    current_form = session.get('current_form', 'A')
    study_id = session.get('study_id', 'UNKNOWN')

    # Query completed comprehension items (combine session cookie & DB for serverless multi-worker resilience)
    session_comp_key = f"comp_{sess_id}_items"
    completed_item_ids = list(session.get(session_comp_key, []))

    if sess_id:
        try:
            conn = sqlite3.connect(get_research_db_path())
            cursor = conn.cursor()
            cursor.execute(
                "SELECT item_id FROM comprehension_responses WHERE session_id = ? AND item_id IN ('C1','C2','C3','C4','C5','C6') ORDER BY id ASC",
                (sess_id,)
            )
            for r in cursor.fetchall():
                if r[0] not in completed_item_ids:
                    completed_item_ids.append(r[0])
            conn.close()
        except Exception:
            pass

    # If all 6 items completed, advance to survey
    if len(completed_item_ids) >= 6:
        session['comprehension_completed'] = True
        return redirect(url_for('experiment.survey', language=language))

    current_item_num = len(completed_item_ids) + 1
    current_item_id = f"C{current_item_num}"

    timer_key = f"comp_{sess_id}_{current_item_id}_start"
    started_str = session.get(timer_key)
    now = datetime.datetime.now()
    if not started_str:
        started_str = now.isoformat()
        session[timer_key] = started_str
        remaining_seconds = 180
    else:
        try:
            started = datetime.datetime.fromisoformat(started_str)
            elapsed = (now - started).total_seconds()
            remaining_seconds = max(0, int(180 - elapsed))
        except Exception:
            remaining_seconds = 180

    if request.method == 'POST':
        submitted_item_id = request.form.get('item_id', current_item_id)
        exp_choice = request.form.get('explanation_choice', '')
        pred_choice = request.form.get('prediction_choice', '')
        is_timed_out = 1 if request.form.get('timed_out') in ('1', 'true', 'True') else 0
        resp_time_param = request.form.get('response_time_seconds')

        # Calculate authoritative response time from server session timestamp
        try:
            started = datetime.datetime.fromisoformat(session.get(timer_key, now.isoformat()))
            server_elapsed = round((now - started).total_seconds(), 1)
        except Exception:
            server_elapsed = 0.0

        try:
            client_elapsed = float(resp_time_param) if resp_time_param else 0.0
        except (ValueError, TypeError):
            client_elapsed = 0.0

        # Authoritative time is max of server elapsed and client elapsed
        resp_time = max(server_elapsed, client_elapsed)
        resp_time = max(0.0, min(180.0, resp_time))
        if resp_time >= 180.0 or is_timed_out:
            is_timed_out = 1

        # Grade item: 2/1/0 for explanation, 1/0 for prediction
        exp_score, pred_score, total_score = grade_item(current_form, submitted_item_id, exp_choice, pred_choice)

        if sess_id:
            try:
                conn = sqlite3.connect(get_research_db_path())
                c = conn.cursor()
                # Check for existing row to prevent duplicate insert on double submit
                c.execute("SELECT id FROM comprehension_responses WHERE session_id = ? AND item_id = ?", (sess_id, submitted_item_id))
                if not c.fetchone():
                    c.execute("""
                        INSERT INTO comprehension_responses
                        (study_id, session_id, item_id, language, form, explanation_score, prediction_score, condition_score, response_time, response_time_seconds, timed_out, learner_answer)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        study_id, sess_id, submitted_item_id, language, current_form,
                        exp_score, pred_score, total_score,
                        resp_time, resp_time, is_timed_out,
                        f"exp:{exp_choice},pred:{pred_choice}"
                    ))
                    conn.commit()
                conn.close()

                # Sync to Supabase cloud (skipped during testing)
                from flask import current_app
                if not current_app.config.get('TESTING'):
                    try:
                        from services.cloud_db import sync_comprehension_to_cloud
                        sync_comprehension_to_cloud({
                            "study_id": study_id,
                            "session_id": sess_id,
                            "item_id": submitted_item_id,
                            "language": language,
                            "form": current_form,
                            "explanation_score": exp_score,
                            "prediction_score": pred_score,
                            "condition_score": total_score,
                            "response_time": resp_time,
                            "response_time_seconds": resp_time,
                            "timed_out": is_timed_out,
                            "learner_answer": f"exp:{exp_choice},pred:{pred_choice}"
                        }, local_db_path=get_research_db_path())
                    except Exception:
                        pass
            except Exception as e:
                print(f"Error saving comprehension response: {e}")

        # Track completed items in session for multi-worker continuity
        if submitted_item_id not in completed_item_ids:
            completed_item_ids.append(submitted_item_id)
        session[session_comp_key] = completed_item_ids

        # Clear timer for submitted item
        session.pop(timer_key, None)

        # Check if condition complete
        if submitted_item_id == 'C6' or len(completed_item_ids) >= 6:
            session['comprehension_completed'] = True
            return redirect(url_for('experiment.survey', language=language))
        else:
            return redirect(url_for('experiment.comprehension', language=language))

    # GET request: load current item definition
    item_data = get_item(current_form, current_item_id, randomize=True, seed=f"{study_id}_{current_item_id}")

    return render_template(
        'comprehension.html',
        language=language,
        current_form=current_form,
        item=item_data,
        item_num=current_item_num,
        total_items=6,
        remaining_seconds=remaining_seconds
    )


@experiment_bp.route('/survey', methods=['GET', 'POST'])
@participant_required
def survey_fallback():
    lang = session.get('current_language', 'sql')
    return redirect(url_for('experiment.survey', language=lang))


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
                conn = sqlite3.connect(get_research_db_path())
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

                # Sync survey response to Supabase cloud (skipped during testing)
                from flask import current_app
                if not current_app.config.get('TESTING'):
                    try:
                        from services.cloud_db import sync_survey_to_cloud
                        sync_survey_to_cloud({
                            "study_id": session.get('study_id'),
                            "session_id": sess_id,
                            "language": language,
                            "q1": q1,
                            "q2": q2,
                            "q3": q3,
                            "q4": q4,
                            "q5": q5,
                            "q6": q6,
                            "q7": q7,
                            "open_easiest": open_easiest,
                            "open_hardest": open_hardest,
                            "open_after_error": open_after_error,
                            "open_preference": open_pref
                        }, local_db_path=get_research_db_path())
                    except Exception:
                        pass
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
