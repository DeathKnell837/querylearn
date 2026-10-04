import sqlite3
import os

SEQUENCES = {
    1: {"first_language": "SQL", "first_form": "A", "second_language": "Python", "second_form": "B"},
    2: {"first_language": "Python", "first_form": "B", "second_language": "SQL", "second_form": "A"},
    3: {"first_language": "SQL", "first_form": "B", "second_language": "Python", "second_form": "A"},
    4: {"first_language": "Python", "first_form": "A", "second_language": "SQL", "second_form": "B"},
}

def get_next_sequence(research_db_path, python_exp="none"):
    """
    Item 9: Atomic sequence assignment balanced by Python experience level.
    Within each experience level, assigns to the sequence with the fewest
    participants. Ties are broken by lowest sequence number.
    Uses a DB transaction for atomicity.
    """
    conn = sqlite3.connect(research_db_path)
    conn.isolation_level = 'EXCLUSIVE'
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN EXCLUSIVE")

        # Count participants per sequence within this experience level
        cursor.execute("""
            SELECT sequence_id, COUNT(*) as cnt
            FROM participants
            WHERE python_exp = ?
            GROUP BY sequence_id
        """, (python_exp,))

        counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Find the sequence with fewest participants (ties → lowest number)
        min_count = float('inf')
        best_seq = 1
        for seq_id in [1, 2, 3, 4]:
            cnt = counts.get(seq_id, 0)
            if cnt < min_count:
                min_count = cnt
                best_seq = seq_id

        conn.commit()
        conn.close()
        return best_seq

    except Exception:
        conn.rollback()
        conn.close()
        # Fallback: simple round-robin
        try:
            conn2 = sqlite3.connect(research_db_path)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT sequence_id FROM participants ORDER BY id DESC LIMIT 1")
            row = cursor2.fetchone()
            conn2.close()
            if not row or not row[0]:
                return 1
            return (row[0] % 4) + 1
        except Exception:
            return 1

def get_sequence_details(sequence_id):
    return SEQUENCES.get(sequence_id, SEQUENCES[1])
