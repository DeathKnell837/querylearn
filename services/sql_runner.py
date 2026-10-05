import sqlite3
import threading
import time
import re

# Block list of DDL / DML / state-altering statements matching whole words only
FORBIDDEN_PATTERN = re.compile(
    r'\b(CREATE|DROP|ALTER|INSERT|UPDATE|DELETE|ATTACH|DETACH|PRAGMA|VACUUM|REINDEX)\b',
    re.IGNORECASE
)


def execute_sql(db_path, sql_code, timeout=10):
    """
    Safely executes read-only SQL queries against experiment databases.
    - Uses whole-word regex matching to prevent false positives (e.g. 'updated_at', 'water_drop').
    - Opens database connection in read-only mode (mode=ro).
    - Interrupts runaway queries with conn.interrupt() and bounds execution via daemon thread.
    """
    clean_code = sql_code.strip() if sql_code else ""
    if not clean_code:
        return {"columns": [], "rows": [], "error": "No SQL query provided.", "execution_time": 0}

    # Remove standard SQL line comments (-- ...) before checking keywords to avoid blocking queries with comments
    uncommented_code = re.sub(r'--[^\n]*', '', clean_code)

    if FORBIDDEN_PATTERN.search(uncommented_code):
        return {
            "columns": [],
            "rows": [],
            "error": "DDL/DML operations (CREATE, DROP, ALTER, INSERT, UPDATE, DELETE, ATTACH) are not permitted.",
            "execution_time": 0
        }

    result = {}
    active_conn = [None]
    t0 = time.time()

    def target():
        try:
            uri = f"file:{db_path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
            active_conn[0] = conn
            cursor = conn.cursor()
            cursor.execute(sql_code)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            conn.close()
            result['columns'] = columns
            result['rows'] = rows
            result['error'] = None
        except Exception as e:
            result['error'] = str(e)
            result['columns'] = []
            result['rows'] = []

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # Interrupt connection to unblock SQLite engine immediately
        if active_conn[0]:
            try:
                active_conn[0].interrupt()
            except Exception:
                pass
        return {
            "columns": [],
            "rows": [],
            "error": "Query execution timed out.",
            "execution_time": timeout
        }

    result['execution_time'] = round(time.time() - t0, 4)
    return result
