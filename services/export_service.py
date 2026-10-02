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
    return get_csv_string_from_query(db_path, "SELECT * FROM participants")

def export_results_csv(db_path):
    return get_csv_string_from_query(db_path, "SELECT * FROM task_results")

def export_survey_csv(db_path):
    return get_csv_string_from_query(db_path, "SELECT * FROM survey_responses")

def export_comprehension_csv(db_path):
    return get_csv_string_from_query(db_path, "SELECT * FROM comprehension_responses")

def export_all_csv(db_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('participants.csv', export_participants_csv(db_path))
        zf.writestr('results.csv', export_results_csv(db_path))
        zf.writestr('survey.csv', export_survey_csv(db_path))
        zf.writestr('comprehension.csv', export_comprehension_csv(db_path))
    return zip_buffer.getvalue()
