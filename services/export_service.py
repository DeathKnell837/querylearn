import sqlite3
import csv
import io
import zipfile

def get_csv_string_from_query(db_path, query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    headers = [description[0] for description in cursor.description]
    writer.writerow(headers)

    # Write data
    writer.writerows(cursor.fetchall())

    conn.close()
    return output.getvalue()

def export_participants_csv(db_path):
    """Export participants with study_id (no real names)."""
    return get_csv_string_from_query(db_path, """
        SELECT study_id, program, year_level, python_exp, sql_exp,
               other_languages, db_course, consent, sequence_id, status, created_at
        FROM participants
        ORDER BY id ASC
    """)

def export_results_csv(db_path):
    """Item 3: Export results.csv with all required columns joined across tables, including explicit outcome."""
    return get_csv_string_from_query(db_path, """
        SELECT
            p.study_id,
            p.sequence_id AS sequence,
            s.language,
            s.form,
            r.task_id,
            r.start_time,
            r.end_time,
            r.elapsed_seconds,
            r.allocated_seconds,
            r.attempt_count,
            r.success,
            CASE WHEN r.success = 1 THEN 'CORRECT' ELSE 'WRONG' END AS outcome,
            r.failure_reason,
            r.source_lines,
            r.source_chars
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        ORDER BY p.study_id ASC, s.language ASC, r.task_id ASC
    """)

def export_survey_csv(db_path):
    """Export survey responses with study_id."""
    return get_csv_string_from_query(db_path, """
        SELECT p.study_id, sr.language, sr.q1, sr.q2, sr.q3, sr.q4, sr.q5,
               sr.q6, sr.q7, sr.open_easiest, sr.open_hardest,
               sr.open_after_error, sr.open_preference, sr.submitted_at
        FROM survey_responses sr
        JOIN sessions s ON sr.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        ORDER BY p.study_id ASC, sr.language ASC
    """)

def export_comprehension_csv(db_path):
    """Export per-item comprehension responses with study_id, session_id, item_id, language, form, scores, and response time."""
    return get_csv_string_from_query(db_path, """
        SELECT 
            COALESCE(cr.study_id, p.study_id) AS study_id,
            cr.session_id,
            cr.item_id,
            cr.language,
            COALESCE(cr.form, s.form) AS form,
            COALESCE(cr.explanation_score, 0) AS explanation_score,
            COALESCE(cr.prediction_score, 0) AS prediction_score,
            (COALESCE(cr.explanation_score, 0) + COALESCE(cr.prediction_score, 0)) AS total_score,
            COALESCE(cr.response_time_seconds, cr.response_time, 0) AS response_time_seconds,
            COALESCE(cr.timed_out, 0) AS timed_out
        FROM comprehension_responses cr
        JOIN sessions s ON cr.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        ORDER BY p.study_id ASC, s.id ASC, cr.item_id ASC
    """)

def export_attempts_csv(db_path):
    """Export all individual code execution attempts with participant and session details, including explicit outcome."""
    return get_csv_string_from_query(db_path, """
        SELECT
            p.study_id,
            s.language,
            s.form,
            ta.task_id,
            ta.attempt_number,
            ta.result_status,
            CASE WHEN ta.result_status = 'correct' THEN 'CORRECT' ELSE 'WRONG' END AS outcome,
            ta.error_message,
            ta.submitted_code,
            ta.submitted_at
        FROM task_attempts ta
        JOIN sessions s ON ta.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        ORDER BY p.study_id ASC, s.language ASC, ta.task_id ASC, ta.attempt_number ASC
    """)

def export_all_csv(db_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('participants.csv', export_participants_csv(db_path))
        zf.writestr('results.csv', export_results_csv(db_path))
        zf.writestr('attempts.csv', export_attempts_csv(db_path))
        zf.writestr('survey.csv', export_survey_csv(db_path))
        zf.writestr('comprehension.csv', export_comprehension_csv(db_path))
    return zip_buffer.getvalue()
