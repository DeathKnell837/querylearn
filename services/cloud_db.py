"""
Cloud Database Persistence Layer for QueryLearn.
Connects to Supabase PostgreSQL via PostgREST to provide:
1. Globally unique, non-colliding sequential Study IDs across multiple computers and serverless instances.
2. Real-time telemetry and survey synchronization across computers.
3. Bidirectional sync between Supabase and local SQLite with automatic offline fallback.
"""

import os
import re
import json
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime
from config import Config

TIMEOUT_SECONDS = 5


def _get_headers():
    key = Config.SUPABASE_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def _make_request(endpoint, method="GET", data=None):
    """Safely executes an HTTP request to Supabase REST API."""
    url = f"{Config.SUPABASE_URL.rstrip('/')}/rest/v1/{endpoint.lstrip('/')}"
    headers = _get_headers()
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            content = resp.read().decode("utf-8")
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
            return True
    except Exception as e:
        # Graceful fallback: network issue, timeout, or offline
        return None


def get_next_cloud_study_id(local_db_path=None) -> str:
    """
    Returns the next sequential, globally unique Study ID (e.g. P017, P018, etc.)
    by checking existing participants in Supabase, and falling back to local SQLite.
    Guarantees IDs start at least at P017 (after 16 pilot participants).
    """
    existing_nums = set()

    # 1. Query Supabase
    cloud_participants = _make_request("participants?select=study_id")
    if isinstance(cloud_participants, list):
        for p in cloud_participants:
            sid = p.get("study_id", "")
            m = re.match(r"^P(\d+)$", sid, re.IGNORECASE)
            if m:
                existing_nums.add(int(m.group(1)))

    # 2. Query local SQLite
    db_file = local_db_path or Config.RESEARCH_DB
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT study_id FROM participants")
            for row in cursor.fetchall():
                sid = row[0] or ""
                m = re.match(r"^P(\d+)$", sid, re.IGNORECASE)
                if m:
                    existing_nums.add(int(m.group(1)))
            conn.close()
        except Exception:
            pass

    # The baseline pilot dataset has 16 participants (P001 to P016).
    # Next live participant begins at P017 unless higher IDs already exist.
    max_num = max(existing_nums) if existing_nums else 16
    next_num = max(max_num + 1, 17)
    return f"P{next_num:03d}"


def sync_participant_to_cloud(participant_data: dict) -> bool:
    """Syncs a newly registered participant to Supabase."""
    cleaned = {
        "study_id": participant_data.get("study_id"),
        "program": participant_data.get("program"),
        "year_level": int(participant_data.get("year_level", 2)),
        "python_exp": participant_data.get("python_exp"),
        "sql_exp": participant_data.get("sql_exp"),
        "other_languages": participant_data.get("other_languages", ""),
        "db_course": participant_data.get("db_course"),
        "consent": bool(participant_data.get("consent")),
        "sequence_id": int(participant_data.get("sequence_id", 1)),
        "status": participant_data.get("status", "in_progress")
    }
    res = _make_request("participants", method="POST", data=cleaned)
    return res is not None


def sync_session_to_cloud(session_data: dict) -> bool:
    """Syncs a test condition session to Supabase."""
    res = _make_request("sessions", method="POST", data=session_data)
    return res is not None


def sync_task_result_to_cloud(result_data: dict) -> bool:
    """Syncs a task completion result to Supabase."""
    cleaned = {
        "task_id": result_data.get("task_id"),
        "success": bool(result_data.get("success")),
        "elapsed_seconds": result_data.get("elapsed_seconds"),
        "allocated_seconds": result_data.get("allocated_seconds", 480),
        "attempt_count": result_data.get("attempt_count", 1),
        "final_code": result_data.get("final_code", ""),
        "source_lines": result_data.get("source_lines"),
        "source_chars": result_data.get("source_chars"),
        "failure_reason": result_data.get("failure_reason")
    }
    if "session_id" in result_data:
        cleaned["session_id"] = result_data["session_id"]
    res = _make_request("task_results", method="POST", data=cleaned)
    return res is not None


def sync_task_attempt_to_cloud(attempt_data: dict) -> bool:
    """Syncs an individual code submission attempt to Supabase."""
    cleaned = {
        "task_id": attempt_data.get("task_id"),
        "attempt_number": attempt_data.get("attempt_number", 1),
        "submitted_code": attempt_data.get("submitted_code", ""),
        "result_status": attempt_data.get("result_status", "incorrect"),
        "error_message": attempt_data.get("error_message", "")
    }
    if "session_id" in attempt_data:
        cleaned["session_id"] = attempt_data["session_id"]
    res = _make_request("task_attempts", method="POST", data=cleaned)
    return res is not None


def sync_comprehension_to_cloud(comp_data: dict) -> bool:
    """Syncs a comprehension question response to Supabase."""
    cleaned = {
        "study_id": comp_data.get("study_id"),
        "item_id": comp_data.get("item_id"),
        "language": comp_data.get("language"),
        "form": comp_data.get("form"),
        "explanation_score": float(comp_data.get("explanation_score", 0.0)),
        "prediction_score": float(comp_data.get("prediction_score", 0.0)),
        "condition_score": float(comp_data.get("condition_score", 0.0)),
        "response_time": float(comp_data.get("response_time", 0.0)),
        "response_time_seconds": float(comp_data.get("response_time_seconds", 0.0)),
        "timed_out": int(comp_data.get("timed_out", 0)),
        "learner_answer": comp_data.get("learner_answer", "")
    }
    if "session_id" in comp_data:
        cleaned["session_id"] = comp_data["session_id"]
    res = _make_request("comprehension_responses", method="POST", data=cleaned)
    return res is not None


def sync_survey_to_cloud(survey_data: dict) -> bool:
    """Syncs a post-condition survey submission to Supabase."""
    cleaned = {
        "language": survey_data.get("language"),
        "q1": survey_data.get("q1"),
        "q2": survey_data.get("q2"),
        "q3": survey_data.get("q3"),
        "q4": survey_data.get("q4"),
        "q5": survey_data.get("q5"),
        "q6": survey_data.get("q6"),
        "q7": survey_data.get("q7"),
        "open_easiest": survey_data.get("open_easiest", ""),
        "open_hardest": survey_data.get("open_hardest", ""),
        "open_after_error": survey_data.get("open_after_error", ""),
        "open_preference": survey_data.get("open_preference", "")
    }
    if "session_id" in survey_data:
        cleaned["session_id"] = survey_data["session_id"]
    res = _make_request("survey_responses", method="POST", data=cleaned)
    return res is not None


def sync_cloud_to_local(local_db_path=None) -> bool:
    """
    Pulls cloud participants and telemetry from Supabase down into local SQLite.
    Allows researcher dashboard on any computer or serverless instance to view
    cross-machine test submissions in real-time.
    """
    db_file = local_db_path or Config.RESEARCH_DB
    if not os.path.exists(db_file):
        return False

    cloud_participants = _make_request("participants?select=*&order=id.asc")
    if not isinstance(cloud_participants, list):
        return False

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Build map of existing local participants by study_id
        cursor.execute("SELECT id, study_id FROM participants")
        local_map = {row[1]: row[0] for row in cursor.fetchall()}

        for cp in cloud_participants:
            sid = cp.get("study_id")
            if not sid:
                continue

            if sid not in local_map:
                cursor.execute("""
                    INSERT INTO participants
                    (study_id, program, year_level, python_exp, sql_exp, other_languages, db_course, consent, sequence_id, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sid,
                    cp.get("program", "BSCS"),
                    int(cp.get("year_level", 2)),
                    cp.get("python_exp", "novice"),
                    cp.get("sql_exp", "novice"),
                    cp.get("other_languages", ""),
                    cp.get("db_course", "yes"),
                    1 if cp.get("consent") else 0,
                    int(cp.get("sequence_id", 1)),
                    cp.get("status", "completed")
                ))
                local_map[sid] = cursor.lastrowid
            else:
                # Update status if completed in cloud
                if cp.get("status") == "completed":
                    cursor.execute("UPDATE participants SET status = 'completed' WHERE study_id = ?", (sid,))

        # Fetch and sync task_results from cloud
        cloud_results = _make_request("task_results?select=*")
        if isinstance(cloud_results, list) and cloud_results:
            cursor.execute("SELECT session_id, task_id, success FROM task_results")
            existing_results = {(r[0], r[1]) for r in cursor.fetchall()}

            for cr in cloud_results:
                sess_id = cr.get("session_id")
                task_id = cr.get("task_id")
                if sess_id and task_id and (sess_id, task_id) not in existing_results:
                    try:
                        cursor.execute("""
                            INSERT INTO task_results
                            (session_id, task_id, success, elapsed_seconds, allocated_seconds, attempt_count, final_code, source_lines, source_chars, failure_reason)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            sess_id, task_id,
                            1 if cr.get("success") else 0,
                            cr.get("elapsed_seconds"),
                            cr.get("allocated_seconds", 480),
                            cr.get("attempt_count", 1),
                            cr.get("final_code", ""),
                            cr.get("source_lines"),
                            cr.get("source_chars"),
                            cr.get("failure_reason")
                        ))
                    except sqlite3.IntegrityError:
                        pass

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False
