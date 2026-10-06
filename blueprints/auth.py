import sqlite3
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from config import Config
from services.sequence_manager import get_next_sequence, get_sequence_details
from services.cloud_db import get_next_cloud_study_id, sync_participant_to_cloud

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        program = request.form.get('program') or 'BSCS'
        year_level_raw = request.form.get('year_level')
        try:
            year_level = int(year_level_raw) if year_level_raw else 2
        except (ValueError, TypeError):
            year_level = 2
        # Strict enforcement: 1st Year (Freshman) excluded per thesis panel directive
        if year_level < 2:
            year_level = 2
        if year_level > 4:
            year_level = 4
        sql_exp = request.form.get('sql_exp') or 'novice'
        python_exp = request.form.get('python_exp') or 'novice'
        db_course = request.form.get('db_course') or 'yes'
        other_languages = request.form.get('other_languages', '')
        consent = bool(request.form.get('consent'))

        # Get balanced sequence 1-4
        sequence_id = get_next_sequence(Config.RESEARCH_DB, python_exp)
        seq_info = get_sequence_details(sequence_id)

        # Generate next sequential study_id via shared cloud database (Supabase)
        study_id = get_next_cloud_study_id(Config.RESEARCH_DB)

        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()

        # Insert participant
        cursor.execute("""
            INSERT INTO participants 
            (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress')
        """, (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id))
        
        participant_id = cursor.lastrowid

        # Asynchronously/safely sync participant to Supabase cloud database
        try:
            sync_participant_to_cloud({
                'study_id': study_id,
                'program': program,
                'year_level': year_level,
                'python_exp': python_exp,
                'sql_exp': sql_exp,
                'other_languages': other_languages,
                'db_course': db_course,
                'consent': consent,
                'sequence_id': sequence_id,
                'status': 'in_progress'
            })
        except Exception:
            pass

        # Create Session 1
        cursor.execute("""
            INSERT INTO sessions (participant_id, language, form, sequence_order)
            VALUES (?, ?, ?, 1)
        """, (participant_id, seq_info['first_language'].lower(), seq_info['first_form']))
        session_1_id = cursor.lastrowid

        # Create Session 2
        cursor.execute("""
            INSERT INTO sessions (participant_id, language, form, sequence_order)
            VALUES (?, ?, ?, 2)
        """, (participant_id, seq_info['second_language'].lower(), seq_info['second_form']))
        session_2_id = cursor.lastrowid

        conn.commit()
        conn.close()

        # Store session context
        session['participant_id'] = participant_id
        session['study_id'] = study_id
        session['sequence_id'] = sequence_id
        session['session_1_id'] = session_1_id
        session['session_2_id'] = session_2_id
        session['current_session_id'] = session_1_id
        session['current_language'] = seq_info['first_language'].lower()
        session['current_form'] = seq_info['first_form']
        session['current_condition_step'] = 1

        return redirect(url_for('experiment.instructions'))

    return render_template('register.html')

@auth_bp.route('/researcher/login', methods=['GET', 'POST'])
def researcher_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Check against default credentials
        if username == Config.DEFAULT_RESEARCHER and password == Config.DEFAULT_PASSWORD:
            session['is_researcher'] = True
            session['researcher_name'] = username
            return redirect(url_for('dashboard.overview'))
        else:
            flash("Invalid researcher credentials", "error")

    return render_template('researcher_login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
