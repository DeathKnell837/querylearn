import sqlite3
import threading
import time

def execute_sql(db_path, sql_code, timeout=10):
    # Basic DDL/DML blocking
    forbidden = ["CREATE", "DROP", "ALTER", "INSERT", "UPDATE", "DELETE", "ATTACH"]
    if any(keyword in sql_code.upper() for keyword in forbidden):
        return {"columns": [], "rows": [], "error": "DDL/DML operations are not allowed.", "execution_time": 0}

    result = {}
    t0 = time.time()
    def target():
        try:
            # Using read-only mode URI
            uri = f"file:{db_path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)
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

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return {"columns": [], "rows": [], "error": "Execution timed out.", "execution_time": timeout}
    
    result['execution_time'] = round(time.time() - t0, 4)
    return result
