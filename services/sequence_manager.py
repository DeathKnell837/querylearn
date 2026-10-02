import sqlite3
import os

SEQUENCES = {
    1: {"first_language": "SQL", "first_form": "A", "second_language": "Python", "second_form": "B"},
    2: {"first_language": "Python", "first_form": "B", "second_language": "SQL", "second_form": "A"},
    3: {"first_language": "SQL", "first_form": "B", "second_language": "Python", "second_form": "A"},
    4: {"first_language": "Python", "first_form": "A", "second_language": "SQL", "second_form": "B"},
}

def get_next_sequence(research_db_path, python_exp="none"):
    """Assign sequences 1-4 round-robin, balanced by Python experience (simplified for now)."""
    conn = sqlite3.connect(research_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sequence_id FROM participants ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return 1
    
    last_seq = row[0]
    next_seq = (last_seq % 4) + 1
    return next_seq

def get_sequence_details(sequence_id):
    return SEQUENCES.get(sequence_id, SEQUENCES[1])
