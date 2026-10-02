import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_research_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS researchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        study_id TEXT UNIQUE NOT NULL,
        program TEXT,
        year_level INTEGER,
        python_exp TEXT,
        sql_exp TEXT,
        other_languages TEXT,
        db_course TEXT,
        consent BOOLEAN,
        sequence_id INTEGER,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_id INTEGER,
        language TEXT,
        form TEXT,
        sequence_order INTEGER,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (participant_id) REFERENCES participants(id)
    );

    CREATE TABLE IF NOT EXISTS task_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        task_id TEXT,
        attempt_number INTEGER,
        submitted_code TEXT,
        result_status TEXT,
        error_message TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS task_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        task_id TEXT,
        success BOOLEAN,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        elapsed_seconds REAL,
        allocated_seconds INTEGER DEFAULT 480,
        attempt_count INTEGER,
        final_code TEXT,
        source_lines INTEGER,
        source_chars INTEGER,
        failure_reason TEXT,
        assistance TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS comprehension_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        item_id TEXT,
        language TEXT,
        explanation_score REAL,
        prediction_score REAL,
        condition_score REAL,
        response_time REAL,
        learner_answer TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS survey_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        language TEXT,
        q1 INTEGER,
        q2 INTEGER,
        q3 INTEGER,
        q4 INTEGER,
        q5 INTEGER,
        q6 INTEGER,
        q7 INTEGER,
        open_easiest TEXT,
        open_hardest TEXT,
        open_after_error TEXT,
        open_preference TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS benchmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT,
        language TEXT,
        dataset_size INTEGER,
        execution_time REAL,
        memory_usage REAL,
        executions_per_second REAL,
        reference_code TEXT,
        measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Insert default admin user
    cursor.execute("SELECT id FROM researchers WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO researchers (username, password_hash) VALUES (?, ?)", 
                       ("admin", generate_password_hash("querylearn2026")))
        
    conn.commit()
    conn.close()
    print(f"Research DB initialized at {db_path}")

if __name__ == "__main__":
    init_research_db(os.path.join(os.path.dirname(__file__), "research.db"))
