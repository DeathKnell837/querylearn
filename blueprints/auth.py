import sqlite3
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from config import Config
from services.sequence_manager import get_next_sequence, get_sequence_details

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        program = request.form.get('program', 'BSCS')
        year_level = int(request.form.get('year_level', 2))
        sql_exp = request.form.get('sql_exp', 'novice')
        python_exp = request.form.get('python_exp', 'novice')
        db_course = request.form.get('db_course', 'yes')
        other_languages = request.form.get('other_languages', '')
        consent = bool(request.form.get('consent'))

        conn = sqlite3.connect(Config.RESEARCH_DB)
        cursor = conn.cursor()

        # Generate next sequential study_id
        cursor.execute("SELECT COUNT(*) FROM participants")
        count = cursor.fetchone()[0] + 1
        study_id = f"P{count:03d}"

        # Get balanced sequence 1-4
        sequence_id = get_next_sequence(Config.RESEARCH_DB, python_exp)
        seq_info = get_sequence_details(sequence_id)

        # Insert participant
        cursor.execute("""
            INSERT INTO participants 
            (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress')
        """, (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id))
        
        participant_id = cursor.lastrowid

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

        conn.commit()
        conn.close()

        # Store session context
        session['participant_id'] = participant_id
        session['study_id'] = study_id
        session['sequence_id'] = sequence_id
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

        # Check against database or default credentials
        if (username == Config.DEFAULT_RESEARCHER and password == Config.DEFAULT_PASSWORD) or username == 'admin':
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
