import urllib.request
import json
import os

token = "sbp_oauth_f67ea76247cae31ebb4b2a5d0857344971fb2211"
url = "https://api.supabase.com/v1/projects/jjndlvtzqowvbcrjlzro/database/query"

ddl = """
-- Drop old foreign key constraints if they exist to prevent sync blocking
ALTER TABLE IF EXISTS sessions DROP CONSTRAINT IF EXISTS sessions_participant_id_fkey;
ALTER TABLE IF EXISTS task_attempts DROP CONSTRAINT IF EXISTS task_attempts_session_id_fkey;
ALTER TABLE IF EXISTS task_results DROP CONSTRAINT IF EXISTS task_results_session_id_fkey;
ALTER TABLE IF EXISTS comprehension_responses DROP CONSTRAINT IF EXISTS comprehension_responses_session_id_fkey;
ALTER TABLE IF EXISTS survey_responses DROP CONSTRAINT IF EXISTS survey_responses_session_id_fkey;

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
    study_id TEXT NOT NULL,
    participant_id INTEGER,
    language TEXT NOT NULL,
    form TEXT,
    sequence_order INTEGER,
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- Ensure study_id and language exist on sessions
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS study_id TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS language TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS form TEXT;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS sequence_order INTEGER;
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_study_lang ON sessions(study_id, language);

CREATE TABLE IF NOT EXISTS task_attempts (
    id SERIAL PRIMARY KEY,
    study_id TEXT NOT NULL,
    language TEXT NOT NULL,
    task_id TEXT NOT NULL,
    session_id INTEGER,
    attempt_number INTEGER NOT NULL,
    submitted_code TEXT,
    result_status TEXT,
    error_message TEXT,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE task_attempts ADD COLUMN IF NOT EXISTS study_id TEXT;
ALTER TABLE task_attempts ADD COLUMN IF NOT EXISTS language TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_task_attempts_unique ON task_attempts(study_id, language, task_id, attempt_number);

CREATE TABLE IF NOT EXISTS task_results (
    id SERIAL PRIMARY KEY,
    study_id TEXT NOT NULL,
    language TEXT NOT NULL,
    task_id TEXT NOT NULL,
    session_id INTEGER,
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
    assistance TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE task_results ADD COLUMN IF NOT EXISTS study_id TEXT;
ALTER TABLE task_results ADD COLUMN IF NOT EXISTS language TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_task_results_unique ON task_results(study_id, language, task_id);

CREATE TABLE IF NOT EXISTS comprehension_responses (
    id SERIAL PRIMARY KEY,
    study_id TEXT NOT NULL,
    session_id INTEGER,
    item_id TEXT NOT NULL,
    language TEXT NOT NULL,
    form TEXT,
    explanation_score REAL,
    prediction_score REAL,
    condition_score REAL,
    response_time REAL,
    response_time_seconds REAL,
    timed_out INTEGER DEFAULT 0,
    learner_answer TEXT,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE comprehension_responses ADD COLUMN IF NOT EXISTS study_id TEXT;
ALTER TABLE comprehension_responses ADD COLUMN IF NOT EXISTS language TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_comp_unique ON comprehension_responses(study_id, language, item_id);

CREATE TABLE IF NOT EXISTS survey_responses (
    id SERIAL PRIMARY KEY,
    study_id TEXT NOT NULL,
    session_id INTEGER,
    language TEXT NOT NULL,
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

ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS study_id TEXT;
ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS language TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_survey_unique ON survey_responses(study_id, language);

-- Ensure explicit unique constraints for PostgREST upsert resolution
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_sessions_study_lang') THEN
        ALTER TABLE sessions ADD CONSTRAINT uq_sessions_study_lang UNIQUE (study_id, language);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_task_results_study_lang_task') THEN
        ALTER TABLE task_results ADD CONSTRAINT uq_task_results_study_lang_task UNIQUE (study_id, language, task_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_task_attempts_unique') THEN
        ALTER TABLE task_attempts ADD CONSTRAINT uq_task_attempts_unique UNIQUE (study_id, language, task_id, attempt_number);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_comp_unique') THEN
        ALTER TABLE comprehension_responses ADD CONSTRAINT uq_comp_unique UNIQUE (study_id, language, item_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_survey_unique') THEN
        ALTER TABLE survey_responses ADD CONSTRAINT uq_survey_unique UNIQUE (study_id, language);
    END IF;
END $$;

-- Grants
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- RLS setup with full anon access
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
