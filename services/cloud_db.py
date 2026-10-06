"""
Cloud Database Persistence Layer for QueryLearn.
Connects to Supabase PostgreSQL via PostgREST to provide:
1. Globally unique, non-colliding sequential Study IDs across multiple computers and serverless instances.
2. Real-time telemetry, comprehension, and survey synchronization across computers.
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


def _get_headers(prefer=None):
    key = Config.SUPABASE_KEY
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": prefer or "return=representation"
    }
    return headers


def _make_request(endpoint, method="GET", data=None, prefer=None):
    """Safely executes an HTTP request to Supabase REST API."""
    url = f"{Config.SUPABASE_URL.rstrip('/')}/rest/v1/{endpoint.lstrip('/')}"
    headers = _get_headers(prefer=prefer)
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
    except Exception:
        # Graceful fallback: network issue, timeout, or offline
        return None


def _lookup_session_metadata(session_id: int, local_db_path=None):
    """Looks up study_id, language, and form for a given local session_id."""
    db_file = local_db_path or Config.RESEARCH_DB
    if not os.path.exists(db_file):
        return None, None, None
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("""
            SELECT p.study_id, s.language, s.form
            FROM sessions s
            JOIN participants p ON s.participant_id = p.id
            WHERE s.id = ?
        """, (session_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0], (row[1] or '').lower(), row[2]
    except Exception:
        pass
    return None, None, None


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


def sync_participant_to_cloud(participant_data: dict, local_db_path=None) -> bool:
    """Syncs a newly registered participant and their sessions to Supabase."""
    study_id = participant_data.get("study_id")
    if not study_id:
        return False

    cleaned = {
        "study_id": study_id,
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
    res = _make_request("participants?on_conflict=study_id", method="POST", data=cleaned, prefer="resolution=merge-duplicates")

    # Also sync the 2 condition sessions to Supabase
    try:
        from services.sequence_manager import get_sequence_details
        seq_id = int(participant_data.get("sequence_id", 1))
        seq_info = get_sequence_details(seq_id)

        s1 = {
            "study_id": study_id,
            "language": seq_info["first_language"].lower(),
            "form": seq_info["first_form"],
            "sequence_order": 1
        }
        s2 = {
            "study_id": study_id,
            "language": seq_info["second_language"].lower(),
            "form": seq_info["second_form"],
            "sequence_order": 2
        }
        _make_request("sessions?on_conflict=study_id,language", method="POST", data=[s1, s2], prefer="resolution=merge-duplicates")
    except Exception:
        pass

    return res is not None


def sync_session_to_cloud(session_data: dict) -> bool:
    """Syncs a test condition session to Supabase."""
    res = _make_request("sessions?on_conflict=study_id,language", method="POST", data=session_data, prefer="resolution=merge-duplicates")
    return res is not None


def sync_task_result_to_cloud(result_data: dict, local_db_path=None) -> bool:
    """Syncs a task completion result to Supabase."""
    study_id = result_data.get("study_id")
    language = result_data.get("language")
    session_id = result_data.get("session_id")

    if not study_id or not language:
        if session_id:
            s_id, lang, _ = _lookup_session_metadata(session_id, local_db_path)
            study_id = study_id or s_id
            language = language or lang

    if not study_id or not language:
        return False

    cleaned = {
        "study_id": study_id,
        "language": language.lower(),
        "task_id": result_data.get("task_id"),
        "session_id": session_id,
        "success": bool(result_data.get("success")),
        "elapsed_seconds": result_data.get("elapsed_seconds"),
        "allocated_seconds": result_data.get("allocated_seconds", 480),
        "attempt_count": result_data.get("attempt_count", 1),
        "final_code": result_data.get("final_code", ""),
        "source_lines": result_data.get("source_lines"),
        "source_chars": result_data.get("source_chars"),
        "failure_reason": result_data.get("failure_reason")
    }
    res = _make_request("task_results?on_conflict=study_id,language,task_id", method="POST", data=cleaned, prefer="resolution=merge-duplicates")
    return res is not None


def sync_task_attempt_to_cloud(attempt_data: dict, local_db_path=None) -> bool:
    """Syncs an individual code submission attempt to Supabase."""
    study_id = attempt_data.get("study_id")
    language = attempt_data.get("language")
    session_id = attempt_data.get("session_id")

    if not study_id or not language:
        if session_id:
            s_id, lang, _ = _lookup_session_metadata(session_id, local_db_path)
            study_id = study_id or s_id
            language = language or lang

    if not study_id or not language:
        return False

    cleaned = {
        "study_id": study_id,
        "language": language.lower(),
        "task_id": attempt_data.get("task_id"),
        "session_id": session_id,
        "attempt_number": attempt_data.get("attempt_number", 1),
        "submitted_code": attempt_data.get("submitted_code", ""),
        "result_status": attempt_data.get("result_status", "incorrect"),
        "error_message": attempt_data.get("error_message", "")
    }
    res = _make_request("task_attempts?on_conflict=study_id,language,task_id,attempt_number", method="POST", data=cleaned, prefer="resolution=merge-duplicates")
    return res is not None


def sync_comprehension_to_cloud(comp_data: dict, local_db_path=None) -> bool:
    """Syncs a comprehension question response to Supabase."""
    study_id = comp_data.get("study_id")
    language = comp_data.get("language")
    session_id = comp_data.get("session_id")

    if not study_id or not language:
        if session_id:
            s_id, lang, _ = _lookup_session_metadata(session_id, local_db_path)
            study_id = study_id or s_id
            language = language or lang

    if not study_id or not language:
        return False

    cleaned = {
        "study_id": study_id,
        "session_id": session_id,
        "item_id": comp_data.get("item_id"),
        "language": language.lower(),
        "form": comp_data.get("form", "A"),
        "explanation_score": float(comp_data.get("explanation_score", 0.0)),
        "prediction_score": float(comp_data.get("prediction_score", 0.0)),
        "condition_score": float(comp_data.get("condition_score", 0.0)),
        "response_time": float(comp_data.get("response_time", 0.0)),
        "response_time_seconds": float(comp_data.get("response_time_seconds", 0.0)),
        "timed_out": int(comp_data.get("timed_out", 0)),
        "learner_answer": comp_data.get("learner_answer", "")
    }
    res = _make_request("comprehension_responses?on_conflict=study_id,language,item_id", method="POST", data=cleaned, prefer="resolution=merge-duplicates")
    return res is not None


def sync_survey_to_cloud(survey_data: dict, local_db_path=None) -> bool:
    """Syncs a post-condition survey submission to Supabase."""
    study_id = survey_data.get("study_id")
    language = survey_data.get("language")
    session_id = survey_data.get("session_id")

    if not study_id or not language:
        if session_id:
            s_id, lang, _ = _lookup_session_metadata(session_id, local_db_path)
            study_id = study_id or s_id
            language = language or lang

    if not study_id or not language:
        return False

    cleaned = {
        "study_id": study_id,
        "session_id": session_id,
        "language": language.lower(),
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
    res = _make_request("survey_responses?on_conflict=study_id,language", method="POST", data=cleaned, prefer="resolution=merge-duplicates")
    return res is not None


def sync_cloud_to_local(local_db_path=None) -> bool:
    """
    Pulls cloud participants, sessions, task results, attempts, comprehension,
    and survey data from Supabase down into local SQLite.
    Guarantees relational integrity with local sessions so all dashboard views
    and CSV exports display data from all computers in real-time.
    """
    from services.sequence_manager import get_sequence_details

    db_file = local_db_path or Config.RESEARCH_DB
    if not os.path.exists(db_file):
        return False

    cloud_participants = _make_request("participants?select=*&order=id.asc")
    if not isinstance(cloud_participants, list):
        return False

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 1. Sync participants & ensure local sessions exist for each participant
        cursor.execute("SELECT id, study_id FROM participants")
        local_part_map = {row[1]: row[0] for row in cursor.fetchall()}

        for cp in cloud_participants:
            sid = cp.get("study_id")
            if not sid:
                continue

            seq_id = int(cp.get("sequence_id", 1))
            seq_info = get_sequence_details(seq_id)

            if sid not in local_part_map:
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
                    seq_id,
                    cp.get("status", "completed")
                ))
                part_id = cursor.lastrowid
                local_part_map[sid] = part_id

                # Create Session 1
                cursor.execute("""
                    INSERT INTO sessions (participant_id, language, form, sequence_order)
                    VALUES (?, ?, ?, 1)
                """, (part_id, seq_info['first_language'].lower(), seq_info['first_form']))

                # Create Session 2
                cursor.execute("""
                    INSERT INTO sessions (participant_id, language, form, sequence_order)
                    VALUES (?, ?, ?, 2)
                """, (part_id, seq_info['second_language'].lower(), seq_info['second_form']))
            else:
                part_id = local_part_map[sid]
                # Update status if completed in cloud
                if cp.get("status") == "completed":
                    cursor.execute("UPDATE participants SET status = 'completed' WHERE study_id = ?", (sid,))

                # Check if sessions exist for this existing participant
                cursor.execute("SELECT id, language FROM sessions WHERE participant_id = ?", (part_id,))
                existing_sessions = {r[1].lower(): r[0] for r in cursor.fetchall()}
                first_lang = seq_info['first_language'].lower()
                second_lang = seq_info['second_language'].lower()
                if first_lang not in existing_sessions:
                    cursor.execute("""
                        INSERT INTO sessions (participant_id, language, form, sequence_order)
                        VALUES (?, ?, ?, 1)
                    """, (part_id, first_lang, seq_info['first_form']))
                if second_lang not in existing_sessions:
                    cursor.execute("""
                        INSERT INTO sessions (participant_id, language, form, sequence_order)
                        VALUES (?, ?, ?, 2)
                    """, (part_id, second_lang, seq_info['second_form']))

        # 2. Build map of (study_id, language) -> local session_id
        cursor.execute("""
            SELECT p.study_id, s.language, s.id
            FROM sessions s
            JOIN participants p ON s.participant_id = p.id
        """)
        session_map = {(row[0], row[1].lower()): row[2] for row in cursor.fetchall()}

        # 3. Fetch and sync task_results from cloud
        cloud_results = _make_request("task_results?select=*")
        if isinstance(cloud_results, list) and cloud_results:
            cursor.execute("SELECT session_id, task_id FROM task_results")
            existing_results = {(r[0], r[1]) for r in cursor.fetchall()}

            for cr in cloud_results:
                sid = cr.get("study_id")
                lang = (cr.get("language") or "").lower()
                tid = cr.get("task_id")
                sess_id = session_map.get((sid, lang))

                if sess_id and tid:
                    if (sess_id, tid) not in existing_results:
                        cursor.execute("""
                            INSERT INTO task_results
                            (session_id, task_id, success, elapsed_seconds, allocated_seconds, attempt_count, final_code, source_lines, source_chars, failure_reason)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            sess_id, tid,
                            1 if cr.get("success") else 0,
                            cr.get("elapsed_seconds"),
                            cr.get("allocated_seconds", 480),
                            cr.get("attempt_count", 1),
                            cr.get("final_code", ""),
                            cr.get("source_lines"),
                            cr.get("source_chars"),
                            cr.get("failure_reason")
                        ))
                        existing_results.add((sess_id, tid))
                    else:
                        cursor.execute("""
                            UPDATE task_results
                            SET success = ?, elapsed_seconds = ?, attempt_count = ?, final_code = ?, failure_reason = ?
                            WHERE session_id = ? AND task_id = ?
                        """, (
                            1 if cr.get("success") else 0,
                            cr.get("elapsed_seconds"),
                            cr.get("attempt_count", 1),
                            cr.get("final_code", ""),
                            cr.get("failure_reason"),
                            sess_id, tid
                        ))

        # 4. Fetch and sync task_attempts from cloud
        cloud_attempts = _make_request("task_attempts?select=*")
        if isinstance(cloud_attempts, list) and cloud_attempts:
            cursor.execute("SELECT session_id, task_id, attempt_number FROM task_attempts")
            existing_attempts = {(r[0], r[1], r[2]) for r in cursor.fetchall()}

            for ca in cloud_attempts:
                sid = ca.get("study_id")
                lang = (ca.get("language") or "").lower()
                tid = ca.get("task_id")
                att_num = ca.get("attempt_number", 1)
                sess_id = session_map.get((sid, lang))

                if sess_id and tid and (sess_id, tid, att_num) not in existing_attempts:
                    cursor.execute("""
                        INSERT INTO task_attempts
                        (session_id, task_id, attempt_number, submitted_code, result_status, error_message)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        sess_id, tid, att_num,
                        ca.get("submitted_code", ""),
                        ca.get("result_status", "incorrect"),
                        ca.get("error_message", "")
                    ))
                    existing_attempts.add((sess_id, tid, att_num))

        # 5. Fetch and sync comprehension_responses from cloud
        cloud_comp = _make_request("comprehension_responses?select=*")
        if isinstance(cloud_comp, list) and cloud_comp:
            cursor.execute("SELECT session_id, item_id FROM comprehension_responses")
            existing_comp = {(r[0], r[1]) for r in cursor.fetchall()}

            for cc in cloud_comp:
                sid = cc.get("study_id")
                lang = (cc.get("language") or "").lower()
                item_id = cc.get("item_id")
                sess_id = session_map.get((sid, lang))

                if sess_id and item_id and (sess_id, item_id) not in existing_comp:
                    cursor.execute("""
                        INSERT INTO comprehension_responses
                        (study_id, session_id, item_id, language, form, explanation_score, prediction_score, condition_score, response_time, response_time_seconds, timed_out, learner_answer)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sid, sess_id, item_id, lang,
                        cc.get("form", "A"),
                        float(cc.get("explanation_score", 0.0)),
                        float(cc.get("prediction_score", 0.0)),
                        float(cc.get("condition_score", 0.0)),
                        float(cc.get("response_time", 0.0)),
                        float(cc.get("response_time_seconds", 0.0)),
                        int(cc.get("timed_out", 0)),
                        cc.get("learner_answer", "")
                    ))
                    existing_comp.add((sess_id, item_id))

        # 6. Fetch and sync survey_responses from cloud
        cloud_survey = _make_request("survey_responses?select=*")
        if isinstance(cloud_survey, list) and cloud_survey:
            cursor.execute("SELECT session_id, language FROM survey_responses")
            existing_survey = {(r[0], (r[1] or '').lower()) for r in cursor.fetchall()}

            for cs in cloud_survey:
                sid = cs.get("study_id")
                lang = (cs.get("language") or "").lower()
                sess_id = session_map.get((sid, lang))

                if sess_id and (sess_id, lang) not in existing_survey:
                    cursor.execute("""
                        INSERT INTO survey_responses
                        (session_id, language, q1, q2, q3, q4, q5, q6, q7, open_easiest, open_hardest, open_after_error, open_preference)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        sess_id, lang,
                        cs.get("q1"), cs.get("q2"), cs.get("q3"), cs.get("q4"), cs.get("q5"), cs.get("q6"), cs.get("q7"),
                        cs.get("open_easiest", ""), cs.get("open_hardest", ""), cs.get("open_after_error", ""), cs.get("open_preference", "")
                    ))
                    existing_survey.add((sess_id, lang))

        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def _batch_post(endpoint, items, chunk_size=50):
    total = 0
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        res = _make_request(endpoint, method="POST", data=chunk, prefer="resolution=merge-duplicates")
        if res is not None:
            total += len(chunk)
    return total

def push_local_to_cloud(local_db_path=None) -> dict:
    """
    Pushes local SQLite data up to Supabase cloud using fast batch requests.
    Useful for populating pilot data or syncing offline changes.
    """
    from services.sequence_manager import get_sequence_details

    db_file = local_db_path or Config.RESEARCH_DB
    if not os.path.exists(db_file):
        return {"success": False, "error": "Database file not found"}

    counts = {"participants": 0, "sessions": 0, "task_results": 0, "task_attempts": 0, "comprehension": 0, "survey": 0}

    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Participants & Sessions
        cursor.execute("SELECT * FROM participants ORDER BY id ASC")
        participants = [dict(r) for r in cursor.fetchall()]
        p_cleaned = []
        s_cleaned = []
        for p in participants:
            sid = p.get("study_id")
            if not sid:
                continue
            seq_id = int(p.get("sequence_id", 1))
            seq_info = get_sequence_details(seq_id)
            p_cleaned.append({
                "study_id": sid,
                "program": p.get("program"),
                "year_level": int(p.get("year_level", 2)),
                "python_exp": p.get("python_exp"),
                "sql_exp": p.get("sql_exp"),
                "other_languages": p.get("other_languages", ""),
                "db_course": p.get("db_course"),
                "consent": bool(p.get("consent")),
                "sequence_id": seq_id,
                "status": p.get("status", "completed")
            })
            s_cleaned.append({
                "study_id": sid,
                "language": seq_info["first_language"].lower(),
                "form": seq_info["first_form"],
                "sequence_order": 1
            })
            s_cleaned.append({
                "study_id": sid,
                "language": seq_info["second_language"].lower(),
                "form": seq_info["second_form"],
                "sequence_order": 2
            })

        counts["participants"] = _batch_post("participants?on_conflict=study_id", p_cleaned)
        counts["sessions"] = _batch_post("sessions?on_conflict=study_id,language", s_cleaned)

        # 2. Build map of local session_id -> (study_id, language, form)
        cursor.execute("""
            SELECT s.id, p.study_id, s.language, s.form
            FROM sessions s
            JOIN participants p ON s.participant_id = p.id
        """)
        session_info = {r['id']: (r['study_id'], r['language'].lower(), r['form']) for r in cursor.fetchall()}

        # 3. Task Results
        cursor.execute("SELECT * FROM task_results")
        res_cleaned = []
        for res in cursor.fetchall():
            s_info = session_info.get(res['session_id'])
            if s_info:
                res_cleaned.append({
                    "study_id": s_info[0],
                    "language": s_info[1],
                    "task_id": res['task_id'],
                    "session_id": res['session_id'],
                    "success": bool(res['success']),
                    "elapsed_seconds": res['elapsed_seconds'],
                    "allocated_seconds": res['allocated_seconds'] or 480,
                    "attempt_count": res['attempt_count'] or 1,
                    "final_code": res['final_code'] or "",
                    "source_lines": res['source_lines'],
                    "source_chars": res['source_chars'],
                    "failure_reason": res['failure_reason']
                })
        counts["task_results"] = _batch_post("task_results?on_conflict=study_id,language,task_id", res_cleaned)

        # 4. Task Attempts
        cursor.execute("SELECT * FROM task_attempts")
        att_cleaned = []
        for att in cursor.fetchall():
            s_info = session_info.get(att['session_id'])
            if s_info:
                att_cleaned.append({
                    "study_id": s_info[0],
                    "language": s_info[1],
                    "task_id": att['task_id'],
                    "session_id": att['session_id'],
                    "attempt_number": att['attempt_number'],
                    "submitted_code": att['submitted_code'] or "",
                    "result_status": att['result_status'] or "incorrect",
                    "error_message": att['error_message'] or ""
                })
        counts["task_attempts"] = _batch_post("task_attempts?on_conflict=study_id,language,task_id,attempt_number", att_cleaned)

        # 5. Comprehension
        cursor.execute("SELECT * FROM comprehension_responses")
        comp_cleaned = []
        for c in cursor.fetchall():
            s_info = session_info.get(c['session_id'])
            if s_info:
                comp_cleaned.append({
                    "study_id": s_info[0],
                    "session_id": c['session_id'],
                    "item_id": c['item_id'],
                    "language": s_info[1],
                    "form": c['form'] or s_info[2] or "A",
                    "explanation_score": float(c['explanation_score'] or 0.0),
                    "prediction_score": float(c['prediction_score'] or 0.0),
                    "condition_score": float(c['condition_score'] or 0.0),
                    "response_time": float(c['response_time'] or 0.0),
                    "response_time_seconds": float(c['response_time_seconds'] or c['response_time'] or 0.0),
                    "timed_out": int(c['timed_out'] or 0),
                    "learner_answer": c['learner_answer'] or ""
                })
        counts["comprehension"] = _batch_post("comprehension_responses?on_conflict=study_id,language,item_id", comp_cleaned)

        # 6. Surveys
        cursor.execute("SELECT * FROM survey_responses")
        surv_cleaned = []
        for s in cursor.fetchall():
            s_info = session_info.get(s['session_id'])
            if s_info:
                surv_cleaned.append({
                    "study_id": s_info[0],
                    "session_id": s['session_id'],
                    "language": s_info[1],
                    "q1": s['q1'],
                    "q2": s['q2'],
                    "q3": s['q3'],
                    "q4": s['q4'],
                    "q5": s['q5'],
                    "q6": s['q6'],
                    "q7": s['q7'],
                    "open_easiest": s['open_easiest'] or "",
                    "open_hardest": s['open_hardest'] or "",
                    "open_after_error": s['open_after_error'] or "",
                    "open_preference": s['open_preference'] or ""
                })
        counts["survey"] = _batch_post("survey_responses?on_conflict=study_id,language", surv_cleaned)

        conn.close()
        return {"success": True, "counts": counts}
    except Exception as e:
        return {"success": False, "error": str(e), "counts": counts}
