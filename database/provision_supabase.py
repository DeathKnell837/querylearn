import urllib.request
import json
import os

token = "sbp_oauth_f67ea76247cae31ebb4b2a5d0857344971fb2211"
url = "https://api.supabase.com/v1/projects/jjndlvtzqowvbcrjlzro/database/query"

ddl = """
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    language TEXT,
    form TEXT,
    sequence_order INTEGER,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_attempts (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    task_id TEXT,
    attempt_number INTEGER,
    submitted_code TEXT,
    result_status TEXT,
    error_message TEXT,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_results (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    task_id TEXT,
    success BOOLEAN,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    elapsed_seconds REAL,
    allocated_seconds INTEGER DEFAULT 480,
    attempt_count INTEGER,
    final_code TEXT,
    source_lines INTEGER,
    source_chars INTEGER,
    failure_reason TEXT,
    assistance TEXT
);

CREATE TABLE IF NOT EXISTS comprehension_responses (
    id SERIAL PRIMARY KEY,
    study_id TEXT,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    item_id TEXT,
    language TEXT,
    form TEXT,
    explanation_score REAL,
    prediction_score REAL,
    condition_score REAL,
    response_time REAL,
    response_time_seconds REAL,
    timed_out INTEGER DEFAULT 0,
    learner_answer TEXT
);

CREATE TABLE IF NOT EXISTS survey_responses (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
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
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_participants" ON participants;
CREATE POLICY "anon_participants" ON participants FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_sessions" ON sessions;
CREATE POLICY "anon_sessions" ON sessions FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER TABLE task_attempts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_task_attempts" ON task_attempts;
CREATE POLICY "anon_task_attempts" ON task_attempts FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER TABLE task_results ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_task_results" ON task_results;
CREATE POLICY "anon_task_results" ON task_results FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER TABLE comprehension_responses ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_comprehension_responses" ON comprehension_responses;
CREATE POLICY "anon_comprehension_responses" ON comprehension_responses FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_survey_responses" ON survey_responses;
CREATE POLICY "anon_survey_responses" ON survey_responses FOR ALL TO anon USING (true) WITH CHECK (true);

NOTIFY pgrst, 'reload schema';
"""

def provision():
    req = urllib.request.Request(
        url,
        data=json.dumps({"query": ddl}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        print("Provisioning response:", resp.status, resp.read().decode("utf-8"))

if __name__ == "__main__":
    provision()
