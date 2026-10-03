from flask import Blueprint, render_template, redirect, url_for, session, request
from services.task_catalog import get_task, SCHEMA_METADATA
from services.sequence_manager import get_sequence_details

experiment_bp = Blueprint('experiment', __name__, url_prefix='/experiment')

@experiment_bp.route('/instructions')
def instructions():
    return render_template('instructions.html')

@experiment_bp.route('/practice')
def practice():
    return render_template('practice.html')

@experiment_bp.route('/practice/run', methods=['POST'])
def practice_run():
    return {"success": True}

@experiment_bp.route('/readiness', methods=['GET', 'POST'])
def readiness():
    if request.method == 'POST':
        return redirect(url_for('experiment.start'))
    return render_template('readiness_check.html')

@experiment_bp.route('/start')
def start():
    seq_id = session.get('sequence_id', 1)
    seq_info = get_sequence_details(seq_id)
    
    first_lang = seq_info.get('first_language', 'sql').lower()
    first_form = seq_info.get('first_form', 'A')
    
    session['current_condition_step'] = 1
    session['current_language'] = first_lang
    session['current_form'] = first_form
    session['current_session_id'] = session.get('session_1_id', 1)
    
    # Send to comprehension test first as per protocol
    return redirect(url_for('experiment.comprehension', language=first_lang))

import sqlite3
from config import Config

@experiment_bp.route('/comprehension/<language>', methods=['GET', 'POST'])
def comprehension(language):
    if request.method == 'POST':
        sess_id = session.get('current_session_id', 1)
        q1 = request.form.get('q1', '')
        q2 = request.form.get('q2', '')
        q3 = request.form.get('q3', '')
        
        # Grade questions (q1 correct is 'b', q2 is 'c', q3 is 'b')
        score_1 = 1.0 if q1 == 'b' else 0.0
        score_2 = 1.0 if q2 == 'c' else 0.0
        score_3 = 1.0 if q3 == 'b' else 0.0
        
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

        return redirect(url_for('experiment.task', language=language, task_id=1))
    return render_template('comprehension.html', language=language)

@experiment_bp.route('/task/<language>/<task_id>')
def task(language, task_id):
    current_form = session.get('current_form', 'A')
    clean_id = str(task_id).upper().replace('T', '').strip()
    task_num = int(clean_id) if clean_id.isdigit() else 1
    task_obj = get_task(current_form, task_num)
    
    if not task_obj:
        # Fallback to Task 1 if invalid
        task_num = 1
        task_obj = get_task(current_form, 1)

    template_name = 'task_sql.html' if language == 'sql' else 'task_python.html'
    return render_template(
        template_name,
        task=task_obj,
        current_task_num=task_num,
        current_form=current_form,
        schema=SCHEMA_METADATA
    )

@experiment_bp.route('/survey/<language>', methods=['GET', 'POST'])
def survey(language):
    if request.method == 'POST':
        sess_id = session.get('current_session_id', 1)
        q1 = int(request.form.get('survey_likert_1', 3))
        q2 = int(request.form.get('survey_likert_2', 3))
        q3 = int(request.form.get('survey_likert_3', 3))
        q4 = int(request.form.get('survey_likert_4', 3))
        q5 = int(request.form.get('survey_likert_5', 3))
        q6 = int(request.form.get('survey_effort', 3))
        q7 = int(request.form.get('survey_fatigue', 3))
        open_hardest = request.form.get('survey_open_1', '')
        open_easiest = request.form.get('survey_open_2', '')
        open_pref = request.form.get('survey_open_3', '')
        open_other = request.form.get('survey_open_4', '')

        try:
            conn = sqlite3.connect(Config.RESEARCH_DB)
            c = conn.cursor()
            c.execute("""
                INSERT INTO survey_responses 
                (session_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_after_error, open_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sess_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_other, open_pref))
            
            step = session.get('current_condition_step', 1)
            if step >= 2:
                # Both conditions completed - update participant status
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
    return render_template('survey.html', language=language)

@experiment_bp.route('/break')
def break_page():
    # Advance to condition 2
    seq_id = session.get('sequence_id', 1)
    seq_info = get_sequence_details(seq_id)
    
    second_lang = seq_info.get('second_language', 'python').lower()
    second_form = seq_info.get('second_form', 'B')
    
    session['current_condition_step'] = 2
    session['current_language'] = second_lang
    session['current_form'] = second_form
    session['current_session_id'] = session.get('session_2_id', 2)
    
    return render_template('break.html', next_language=second_lang)

@experiment_bp.route('/complete')
def complete():
    return render_template('complete.html')
