import sqlite3
import statistics
import time
from flask import Blueprint, render_template, redirect, url_for, session, Response, request, flash, jsonify, current_app
from config import Config
from services.export_service import (
    export_participants_csv, export_results_csv, export_survey_csv,
    export_comprehension_csv, export_attempts_csv, export_all_csv
)
from services.pilot_data_seeder import seed_pilot_data
from services.benchmark_runner import run_benchmark

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def get_research_db_path():
    try:
        return current_app.config.get('RESEARCH_DB', Config.RESEARCH_DB)
    except RuntimeError:
        return Config.RESEARCH_DB

def require_researcher(f):
    def wrapper(*args, **kwargs):
        if not session.get('is_researcher'):
            return redirect(url_for('auth.researcher_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def _safe_sync_cloud():
    try:
        if current_app and current_app.config.get('TESTING'):
            return
        from services.cloud_db import sync_cloud_to_local
        sync_cloud_to_local(get_research_db_path())
    except Exception:
        pass

def compute_paired_speedup_data(cursor, cohort_only=False):
    """
    Computes paired task speedup ratios and overall learner-level cluster bootstrap 95% CI.
    A paired record requires that the same participant succeeded (success = 1) in BOTH
    SQL and Python conditions on the same task_id.
    """
    where_extra = "AND CAST(SUBSTR(p.study_id, 2) AS INTEGER) BETWEEN 1 AND 15" if cohort_only else ""
    cursor.execute(f"""
        SELECT r_sql.task_id, s_sql.participant_id, r_sql.elapsed_seconds as sql_time, r_py.elapsed_seconds as py_time
        FROM task_results r_sql
        JOIN sessions s_sql ON r_sql.session_id = s_sql.id AND s_sql.language = 'sql'
        JOIN participants p ON s_sql.participant_id = p.id
        JOIN task_results r_py ON r_sql.task_id = r_py.task_id
        JOIN sessions s_py ON r_py.session_id = s_py.id AND s_py.language = 'python' AND s_py.participant_id = s_sql.participant_id
        WHERE r_sql.success = 1 AND r_py.success = 1
          {where_extra}
        ORDER BY r_sql.task_id ASC, s_sql.participant_id ASC
    """)
    rows = cursor.fetchall()
    if not rows:
        return {
            'overall_ratio': 1.0,
            'ci_low': 1.0,
            'ci_high': 1.0,
            'paired_task_count': 0,
            'task_ratios': {}
        }

    from collections import defaultdict
    import random
    task_map = defaultdict(lambda: {'sql': [], 'py': []})
    learner_map = defaultdict(list)
    all_sql_times = []
    all_py_times = []

    for r in rows:
        tid = r['task_id']
        pid = r['participant_id']
        sq = r['sql_time']
        py = r['py_time']
        if sq is not None and py is not None:
            task_map[tid]['sql'].append(sq)
            task_map[tid]['py'].append(py)
            learner_map[pid].append((sq, py))
            all_sql_times.append(sq)
            all_py_times.append(py)

    task_ratios = {}
    for tid, times in task_map.items():
        n = len(times['sql'])
        med_sql = statistics.median(times['sql']) if times['sql'] else 0.0
        med_py = statistics.median(times['py']) if times['py'] else 0.0
        ratio = round(med_py / med_sql, 2) if med_sql > 0 else 1.0
        task_ratios[tid] = {
            'n': n,
            'sql_median': round(med_sql, 1),
            'py_median': round(med_py, 1),
            'ratio': ratio
        }

    med_paired_sql = statistics.median(all_sql_times) if all_sql_times else 0.0
    med_paired_py = statistics.median(all_py_times) if all_py_times else 0.0
    overall_ratio = round(med_paired_py / med_paired_sql, 2) if med_paired_sql > 0 else 1.0

    unique_pids = sorted(list(learner_map.keys()))
    if len(unique_pids) > 1:
        rng = random.Random(42)
        boot_ratios = []
        n_learners = len(unique_pids)
        for _ in range(2000):
            sampled_pids = rng.choices(unique_pids, k=n_learners)
            boot_sql = []
            boot_py = []
            for pid in sampled_pids:
                for sq, py in learner_map[pid]:
                    boot_sql.append(sq)
                    boot_py.append(py)
            if boot_sql and boot_py:
                m_s = statistics.median(boot_sql)
                m_p = statistics.median(boot_py)
                if m_s > 0:
                    boot_ratios.append(m_p / m_s)
        boot_ratios.sort()
        ci_low = round(boot_ratios[int(0.025 * len(boot_ratios))], 2)
        ci_high = round(boot_ratios[int(0.975 * len(boot_ratios))], 2)
    else:
        ci_low = overall_ratio
        ci_high = overall_ratio

    return {
        'overall_ratio': overall_ratio,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'paired_task_count': len(rows),
        'task_ratios': task_ratios
    }

def _has_seeded_data(cursor):
    try:
        cursor.execute("SELECT 1 FROM participants WHERE study_id LIKE 'P0%' AND CAST(SUBSTR(study_id, 2) AS INTEGER) <= 16 LIMIT 1")
        return cursor.fetchone() is not None
    except Exception:
        return False

@dashboard_bp.route('/')
@require_researcher
def overview():
    # Sync latest cross-computer participant submissions from Supabase
    _safe_sync_cloud()

    conn = sqlite3.connect(get_research_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    has_seeded = _has_seeded_data(cursor)

    # 1. Overall Language Stats (Success & Failure Breakdown)
    cursor.execute("""
        SELECT 
            s.language,
            COUNT(r.id) as total_attempts,
            SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) as successful_tasks
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        GROUP BY s.language
    """)
    lang_stats = {row['language']: dict(row) for row in cursor.fetchall()}

    sql_stats = lang_stats.get('sql', {'successful_tasks': 0, 'total_attempts': 0})
    py_stats = lang_stats.get('python', {'successful_tasks': 0, 'total_attempts': 0})

    sql_total = sql_stats['total_attempts'] or 0
    sql_correct = sql_stats['successful_tasks'] or 0
    sql_wrong = max(0, sql_total - sql_correct)
    sql_success_pct = round((sql_correct / sql_total) * 100, 1) if sql_total else 0.0
    sql_fail_pct = round((sql_wrong / sql_total) * 100, 1) if sql_total else 0.0

    py_total = py_stats['total_attempts'] or 0
    py_correct = py_stats['successful_tasks'] or 0
    py_wrong = max(0, py_total - py_correct)
    py_success_pct = round((py_correct / py_total) * 100, 1) if py_total else 0.0
    py_fail_pct = round((py_wrong / py_total) * 100, 1) if py_total else 0.0

    # 2. Median Duration per condition
    cursor.execute("""
        SELECT s.language, r.elapsed_seconds
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        WHERE r.elapsed_seconds IS NOT NULL
    """)
    all_time_rows = cursor.fetchall()
    sql_durations = [r['elapsed_seconds'] for r in all_time_rows if r['language'] == 'sql']
    py_durations = [r['elapsed_seconds'] for r in all_time_rows if r['language'] == 'python']

    sql_median_time = round(statistics.median(sql_durations), 1) if sql_durations else 0.0
    py_median_time = round(statistics.median(py_durations), 1) if py_durations else 0.0

    # 3. Paired Successful-Task Time Ratio & Learner Bootstrap 95% CI
    paired_data = compute_paired_speedup_data(cursor)
    paired_time_ratio = paired_data['overall_ratio']
    paired_task_count = paired_data['paired_task_count']
    paired_ratio_ci_low = paired_data['ci_low']
    paired_ratio_ci_high = paired_data['ci_high']

    # 4. Correct Tasks per Hour (CT/h)
    # Formula: 60 * (number of correct tasks) / (total task minutes)
    # Correct task contributes its actual elapsed minutes (elapsed_seconds / 60)
    # Unsuccessful / timed-out / abandoned contributes full 8-minute allocation (480s)
    cursor.execute("""
        SELECT s.language, r.success, r.elapsed_seconds
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
    """)
    ct_rows = cursor.fetchall()

    def calc_ct_per_hour(lang):
        l_rows = [r for r in ct_rows if r['language'] == lang]
        if not l_rows:
            return None
        correct_count = sum(1 for r in l_rows if r['success'] == 1)
        total_mins = sum(
            (r['elapsed_seconds'] / 60.0) if (r['success'] == 1 and r['elapsed_seconds'] is not None) else (Config.TASK_TIMEOUT_SECONDS / 60.0)
            for r in l_rows
        )
        return round(60.0 * correct_count / total_mins, 1) if total_mins > 0 else 0.0

    sql_ct_per_hour = calc_ct_per_hour('sql')
    py_ct_per_hour = calc_ct_per_hour('python')

    # 5. Task-by-Task Comparison (T1 to T6) with Medians
    cursor.execute("""
        SELECT r.task_id, s.language, r.success, r.elapsed_seconds, r.attempt_count
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        ORDER BY r.task_id ASC
    """)
    raw_task_rows = cursor.fetchall()
    from collections import defaultdict
    task_groups = defaultdict(lambda: {'success': [], 'times': [], 'attempts': []})
    all_tasks = set()
    for row in raw_task_rows:
        tid = row['task_id']
        lang = row['language']
        all_tasks.add(tid)
        task_groups[(tid, lang)]['success'].append(1 if row['success'] else 0)
        if row['elapsed_seconds'] is not None:
            task_groups[(tid, lang)]['times'].append(row['elapsed_seconds'])
        if row['attempt_count'] is not None:
            task_groups[(tid, lang)]['attempts'].append(row['attempt_count'])

    task_constructs = {
        'T1': 'Filtered Projection (WHERE / ORDER BY)',
        'T2': 'Aggregation & Ranking (ORDER BY / LIMIT / NULLs)',
        'T3': 'Group Aggregation (GROUP BY / COUNT)',
        'T4': 'Multi-Table Relational Join (INNER JOIN)',
        'T5': 'Group Filtering (HAVING / Aggregate Predicates)',
        'T6': 'Set Difference / Anti-Join (LEFT JOIN ... NULL)'
    }

    task_what_it_tests = {
        'T1': 'Filtering and sorting rows',
        'T2': 'Top N with a tie-break',
        'T3': 'Counting per group',
        'T4': 'Joining three tables',
        'T5': 'Group filter with a threshold',
        'T6': 'Rows with no match'
    }

    task_breakdown = {}
    for tid in sorted(list(all_tasks)):
        task_breakdown[tid] = {
            'task_id': tid,
            'construct': task_constructs.get(tid, 'Relational Operation'),
            'what_it_tests': task_what_it_tests.get(tid, 'Relational Operation')
        }
        for lang in ['sql', 'python']:
            group = task_groups.get((tid, lang), {'success': [], 'times': [], 'attempts': []})
            s_list = group['success']
            t_list = group['times']
            a_list = group['attempts']
            t_total = len(s_list)
            t_right = sum(s_list)
            t_wrong = max(0, t_total - t_right)
            succ_pct = round((t_right / t_total) * 100, 1) if t_total else 0.0
            fail_pct = round((t_wrong / t_total) * 100, 1) if t_total else 0.0
            med_time = round(statistics.median(t_list), 1) if t_list else 0.0
            avg_att = round(sum(a_list) / len(a_list), 1) if a_list else 0.0
            task_breakdown[tid][f"{lang}_total"] = t_total
            task_breakdown[tid][f"{lang}_right"] = t_right
            task_breakdown[tid][f"{lang}_wrong"] = t_wrong
            task_breakdown[tid][f"{lang}_success"] = succ_pct
            task_breakdown[tid][f"{lang}_fail"] = fail_pct
            task_breakdown[tid][f"{lang}_median_time"] = med_time
            task_breakdown[tid][f"{lang}_time"] = med_time
            task_breakdown[tid][f"{lang}_attempts"] = avg_att

        sql_s = task_breakdown[tid].get('sql_success', 0.0)
        py_s = task_breakdown[tid].get('python_success', 0.0)
        task_breakdown[tid]['accuracy_delta'] = round(sql_s - py_s, 1)
        
        sql_t = task_breakdown[tid].get('sql_median_time', 0.0)
        py_t = task_breakdown[tid].get('python_median_time', 0.0)
        task_breakdown[tid]['speed_ratio'] = round(py_t / sql_t, 2) if sql_t > 0 else 1.0

    # 6. Comprehension Score Medians (out of 18)
    # Exclude legacy 3-item pilot data by requiring complete 6-item protocol (C1 to C6)
    cursor.execute("""
        SELECT 
            s.language,
            cr.session_id,
            SUM(COALESCE(cr.explanation_score, 0) + COALESCE(cr.prediction_score, 0)) AS total_score,
            COUNT(cr.id) AS item_count
        FROM comprehension_responses cr
        JOIN sessions s ON cr.session_id = s.id
        WHERE cr.item_id IN ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')
        GROUP BY cr.session_id, s.language
        HAVING COUNT(cr.id) = 6
    """)
    comp_rows = cursor.fetchall()
    sql_comp_scores = [r['total_score'] for r in comp_rows if r['language'] == 'sql']
    py_comp_scores = [r['total_score'] for r in comp_rows if r['language'] == 'python']

    sql_median_comp = round(statistics.median(sql_comp_scores), 1) if sql_comp_scores else None
    python_median_comp = round(statistics.median(py_comp_scores), 1) if py_comp_scores else None
    comp_session_count = len(comp_rows)

    # 7. Participant Enrollment & Progress Statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'registered' THEN 1 ELSE 0 END) as registered
        FROM participants
    """)
    p_counts = cursor.fetchone()
    total_participants = p_counts['total'] or 0
    completed_participants = p_counts['completed'] or 0
    in_progress_participants = p_counts['in_progress'] or 0
    registered_participants = p_counts['registered'] or 0
    completion_rate = round((completed_participants / total_participants * 100), 1) if total_participants > 0 else 0.0

    # Recent enrolled participants (preview)
    cursor.execute("SELECT * FROM participants ORDER BY id DESC LIMIT 6")
    recent_participants = [dict(r) for r in cursor.fetchall()]

    # Cohort breakdown
    cursor.execute("SELECT program, COUNT(*) as cnt FROM participants GROUP BY program ORDER BY cnt DESC")
    cohort_programs = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT year_level, COUNT(*) as cnt FROM participants GROUP BY year_level ORDER BY year_level ASC")
    cohort_years = [dict(r) for r in cursor.fetchall()]

    conn.close()

    metrics = {
        "sql_correct_count": sql_correct,
        "sql_wrong_count": sql_wrong,
        "sql_total_count": sql_total,
        "sql_success_rate": sql_success_pct,
        "sql_fail_rate": sql_fail_pct,
        "python_correct_count": py_correct,
        "python_wrong_count": py_wrong,
        "python_total_count": py_total,
        "python_success_rate": py_success_pct,
        "python_fail_rate": py_fail_pct,
        "sql_median_time": sql_median_time,
        "python_median_time": py_median_time,
        "paired_time_ratio": paired_time_ratio,
        "paired_ratio_ci_low": paired_ratio_ci_low,
        "paired_ratio_ci_high": paired_ratio_ci_high,
        "paired_task_count": paired_task_count,
        "sql_ct_per_hour": sql_ct_per_hour,
        "python_ct_per_hour": py_ct_per_hour,
        "sql_median_comp": sql_median_comp,
        "python_median_comp": python_median_comp,
        "comp_session_count": comp_session_count,
        "total_participants": total_participants,
        "completed": completed_participants,
        "in_progress": in_progress_participants,
        "registered": registered_participants,
        "completion_rate": completion_rate,
        "recent_participants": recent_participants,
        "cohort_programs": cohort_programs,
        "cohort_years": cohort_years,
        "has_seeded": has_seeded,
        "tasks": list(task_breakdown.values())
    }

    return render_template('dashboard/overview.html', m=metrics, has_seeded=has_seeded)

@dashboard_bp.route('/participants')
@require_researcher
def participants():
    _safe_sync_cloud()
    conn = sqlite3.connect(get_research_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM participants ORDER BY id DESC")
    participants_list = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('dashboard/participants.html', participants=participants_list)

@dashboard_bp.route('/results')
@require_researcher
def results():
    _safe_sync_cloud()
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    per_page = 50
    offset = (page - 1) * per_page

    language = request.args.get('language', '').strip().lower()
    task = request.args.get('task', '').strip().upper()
    search = request.args.get('search', '').strip()

    conn = sqlite3.connect(get_research_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Build WHERE conditions
    conditions = []
    params = []

    if language and language != 'all':
        conditions.append("s.language = ?")
        params.append(language)

    if task and task != 'all':
        clean_task = task if task.startswith('T') else f"T{task}"
        conditions.append("r.task_id = ?")
        params.append(clean_task)

    if search:
        conditions.append("p.study_id LIKE ?")
        params.append(f"%{search}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # 1. Compute summary stats on ALL matching rows (not just the 50 paginated rows)
    count_sql = f"""
        SELECT 
            COUNT(r.id) as total_matching,
            SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) as success_count
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        {where_clause}
    """
    cursor.execute(count_sql, params)
    stat_row = cursor.fetchone()
    total_matching = stat_row['total_matching'] or 0
    success_count = stat_row['success_count'] or 0
    wrong_count = max(0, total_matching - success_count)
    success_rate = round((success_count / total_matching * 100), 1) if total_matching > 0 else 0.0
    wrong_rate = round((wrong_count / total_matching * 100), 1) if total_matching > 0 else 0.0

    # Compute median duration across ALL matching rows
    cursor.execute(f"""
        SELECT r.elapsed_seconds
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        {where_clause}
    """, params)
    time_rows = [row['elapsed_seconds'] for row in cursor.fetchall() if row['elapsed_seconds'] is not None]
    median_time = round(statistics.median(time_rows), 1) if time_rows else 0.0

    total_pages = max(1, (total_matching + per_page - 1) // per_page)

    # 2. Fetch paginated records (50 rows/page)
    data_sql = f"""
        SELECT r.*, p.study_id, s.language, s.form
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        {where_clause}
        ORDER BY r.id DESC
        LIMIT ? OFFSET ?
    """
    has_seeded = _has_seeded_data(cursor)
    cursor.execute(data_sql, params + [per_page, offset])
    results_list = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for r in results_list:
        raw_code = r.get('final_code') or r.get('code_submitted') or ''
        if raw_code:
            lines = [line.strip() for line in raw_code.splitlines() if line.strip()]
            r['code_preview'] = lines[0] if lines else '—'
        else:
            r['code_preview'] = '—'

    summary_stats = {
        "total_results": total_matching,
        "success_count": success_count,
        "wrong_count": wrong_count,
        "success_rate": success_rate,
        "wrong_rate": wrong_rate,
        "median_time": median_time,
        "avg_time": median_time
    }

    return render_template(
        'dashboard/results.html',
        results=results_list,
        stats=summary_stats,
        page=page,
        total_pages=total_pages,
        total_count=total_matching,
        selected_lang=language,
        selected_task=task,
        search_query=search,
        has_seeded=has_seeded
    )

@dashboard_bp.route('/analytics')
@dashboard_bp.route('/charts')
@require_researcher
def charts():
    """Comparative Analytics page for publication in the case study paper."""
    conn = sqlite3.connect(get_research_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Unified paired speedup data & learner bootstrap 95% CI (Cohort P001-P015)
    paired_data = compute_paired_speedup_data(cursor, cohort_only=True)
    task_paired_ratios = paired_data['task_ratios']

    # 2. Fetch raw task results for task breakdown and duration stats (Cohort P001-P015 only)
    cursor.execute("""
        SELECT r.task_id, s.language, p.study_id, r.success, r.elapsed_seconds, r.attempt_count
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        WHERE CAST(SUBSTR(p.study_id, 2) AS INTEGER) BETWEEN 1 AND 15
        ORDER BY r.task_id ASC, p.study_id ASC
    """)
    raw_task_rows = cursor.fetchall()
    seen_tasks = set()
    deduped_task_rows = []
    for r in raw_task_rows:
        k = (r['task_id'], r['language'], r['study_id'])
        if k not in seen_tasks:
            seen_tasks.add(k)
            deduped_task_rows.append(r)

    from collections import defaultdict
    task_groups = defaultdict(lambda: {'success': [], 'times': [], 'attempts': []})
    lang_times = defaultdict(list)
    lang_success = defaultdict(list)
    all_tasks = set()

    for row in deduped_task_rows:
        tid = row['task_id']
        lang = row['language']
        all_tasks.add(tid)
        task_groups[(tid, lang)]['success'].append(1 if row['success'] else 0)
        if row['elapsed_seconds'] is not None:
            task_groups[(tid, lang)]['times'].append(row['elapsed_seconds'])
            lang_times[lang].append(row['elapsed_seconds'])
        if row['attempt_count'] is not None:
            task_groups[(tid, lang)]['attempts'].append(row['attempt_count'])
        lang_success[lang].append(1 if row['success'] else 0)

    task_constructs = {
        'T1': 'Filtered Projection (WHERE / ORDER BY)',
        'T2': 'Aggregation & Ranking (ORDER BY / LIMIT / NULLs)',
        'T3': 'Group Aggregation (GROUP BY / COUNT)',
        'T4': 'Multi-Table Relational Join (INNER JOIN)',
        'T5': 'Group Filtering (HAVING / Aggregate Predicates)',
        'T6': 'Set Difference / Anti-Join (LEFT JOIN ... NULL)'
    }

    task_what_it_tests = {
        'T1': 'Filtering and sorting rows',
        'T2': 'Top N with a tie-break',
        'T3': 'Counting per group',
        'T4': 'Joining three tables',
        'T5': 'Group filter with a threshold',
        'T6': 'Rows with no match'
    }

    task_breakdown = {}
    for tid in sorted(list(all_tasks)):
        task_breakdown[tid] = {
            'task_id': tid,
            'construct': task_constructs.get(tid, 'Relational Operation'),
            'what_it_tests': task_what_it_tests.get(tid, 'Relational Operation')
        }
        for lang in ['sql', 'python']:
            group = task_groups.get((tid, lang), {'success': [], 'times': [], 'attempts': []})
            s_list = group['success']
            t_list = sorted(group['times'])
            a_list = group['attempts']
            t_total = len(s_list)
            t_right = sum(s_list)
            t_wrong = max(0, t_total - t_right)
            succ_pct = round((t_right / t_total) * 100, 1) if t_total else 0.0
            fail_pct = round((t_wrong / t_total) * 100, 1) if t_total else 0.0
            
            n_t = len(t_list)
            med_time = round(statistics.median(t_list), 1) if t_list else 0.0
            q1_time = round(t_list[int(0.25 * n_t)], 1) if t_list else 0.0
            q3_time = round(t_list[int(0.75 * n_t)], 1) if t_list else 0.0
            avg_att = round(sum(a_list) / len(a_list), 1) if a_list else 0.0
            
            task_breakdown[tid][f"{lang}_total"] = t_total
            task_breakdown[tid][f"{lang}_right"] = t_right
            task_breakdown[tid][f"{lang}_wrong"] = t_wrong
            task_breakdown[tid][f"{lang}_success"] = succ_pct
            task_breakdown[tid][f"{lang}_fail"] = fail_pct
            task_breakdown[tid][f"{lang}_time"] = med_time
            task_breakdown[tid][f"{lang}_median_time"] = med_time
            task_breakdown[tid][f"{lang}_q1_time"] = q1_time
            task_breakdown[tid][f"{lang}_q3_time"] = q3_time
            task_breakdown[tid][f"{lang}_n"] = n_t
            task_breakdown[tid][f"{lang}_attempts"] = avg_att

        sql_s = task_breakdown[tid].get('sql_success', 0.0)
        py_s = task_breakdown[tid].get('python_success', 0.0)
        task_breakdown[tid]['accuracy_delta'] = round(sql_s - py_s, 1)
        
        # Paired speedup definition: median Python time / median SQL time using only learners correct in both conditions
        p_info = task_paired_ratios.get(tid, {'ratio': 1.0, 'n': 0})
        task_breakdown[tid]['speed_ratio'] = p_info['ratio']
        task_breakdown[tid]['speed_ratio_n'] = p_info['n']

    # 3. Overall Accuracy Totals
    sql_total = len(lang_success['sql'])
    sql_correct = sum(lang_success['sql'])
    sql_wrong = max(0, sql_total - sql_correct)
    sql_succ_rate = round((sql_correct / sql_total) * 100, 1) if sql_total else 0.0
    sql_fail_rate = round((sql_wrong / sql_total) * 100, 1) if sql_total else 0.0

    py_total = len(lang_success['python'])
    py_correct = sum(lang_success['python'])
    py_wrong = max(0, py_total - py_correct)
    py_succ_rate = round((py_correct / py_total) * 100, 1) if py_total else 0.0
    py_fail_rate = round((py_wrong / py_total) * 100, 1) if py_total else 0.0

    sql_med_time = round(statistics.median(lang_times['sql']), 1) if lang_times['sql'] else 0.0
    py_med_time = round(statistics.median(lang_times['python']), 1) if lang_times['python'] else 0.0

    # 4. Attempt Averages
    cursor.execute("""
        SELECT s.language, AVG(r.attempt_count) as avg_att
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        GROUP BY s.language
    """)
    att_rows = {r['language']: round(r['avg_att'] or 0, 1) for r in cursor.fetchall()}
    sql_avg_att = att_rows.get('sql', 1.0)
    py_avg_att = att_rows.get('python', 1.0)

    # 5. Correct Tasks per Learner (out of 6)
    cursor.execute("""
        SELECT p.study_id, s.language,
               SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) as correct_count
        FROM participants p
        JOIN sessions s ON s.participant_id = p.id
        LEFT JOIN task_results r ON r.session_id = s.id
        WHERE CAST(SUBSTR(p.study_id, 2) AS INTEGER) BETWEEN 1 AND 15
        GROUP BY p.id, s.language
        ORDER BY p.study_id ASC
    """)
    p_score_rows = cursor.fetchall()
    p_scores = {}
    for r in p_score_rows:
        sid = r['study_id']
        if sid not in p_scores:
            p_scores[sid] = {'study_id': sid, 'sql': 0, 'python': 0}
        p_scores[sid][r['language']] = r['correct_count'] or 0
    learner_scores = list(p_scores.values())
    for l in learner_scores:
        l['diff'] = (l['python'] or 0) - (l['sql'] or 0)
    # Sort by Python minus SQL difference ascending, then by numeric study_id
    learner_scores.sort(key=lambda x: (x['diff'], int(x['study_id'][1:])))
    learner_sql_scores = [l['sql'] for l in learner_scores]
    learner_py_scores = [l['python'] for l in learner_scores]
    learner_sql_median = round(statistics.median(learner_sql_scores), 1) if learner_sql_scores else 0.0
    learner_python_median = round(statistics.median(learner_py_scores), 1) if learner_py_scores else 0.0

    # 6. Correct Tasks per Hour (Learner Level)
    cursor.execute("""
        SELECT p.study_id, s.language, r.task_id, r.success, r.elapsed_seconds
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        WHERE CAST(SUBSTR(p.study_id, 2) AS INTEGER) BETWEEN 1 AND 15
        ORDER BY p.study_id, s.language, r.task_id
    """)
    ct_all_rows = cursor.fetchall()
    seen_ct = set()
    p_task_data = defaultdict(list)
    for r in ct_all_rows:
        k = (r['study_id'], r['language'], r['task_id'])
        if k not in seen_ct:
            seen_ct.add(k)
            p_task_data[(r['study_id'], r['language'])].append(r)

    ct_sql_learners = []
    ct_py_learners = []
    for (sid, lang), t_rows in sorted(p_task_data.items()):
        corr = sum(1 for r in t_rows if r['success'] == 1)
        tot_mins = sum(
            (r['elapsed_seconds'] / 60.0) if (r['success'] == 1 and r['elapsed_seconds'] is not None) else (Config.TASK_TIMEOUT_SECONDS / 60.0)
            for r in t_rows
        )
        rate = round(60.0 * corr / tot_mins, 1) if tot_mins > 0 else 0.0
        if lang == 'sql':
            ct_sql_learners.append({'study_id': sid, 'rate': rate})
        else:
            ct_py_learners.append({'study_id': sid, 'rate': rate})

    def calc_stat_iqr(data_list):
        vals = sorted([d['rate'] for d in data_list])
        if not vals:
            return {'median': 0.0, 'q1': 0.0, 'q3': 0.0}
        n = len(vals)
        med = round(statistics.median(vals), 1)
        q1 = round(vals[int(0.25 * n)], 1)
        q3 = round(vals[int(0.75 * n)], 1)
        return {'median': med, 'q1': q1, 'q3': q3}

    ct_per_hour_data = {
        'sql': {
            'learners': ct_sql_learners,
            **calc_stat_iqr(ct_sql_learners)
        },
        'python': {
            'learners': ct_py_learners,
            **calc_stat_iqr(ct_py_learners)
        }
    }

    # 7. Code Comprehension Scores (0 to 18 by condition)
    cursor.execute("""
        SELECT s.language, p.study_id,
               SUM(COALESCE(cr.explanation_score, 0) + COALESCE(cr.prediction_score, 0)) AS total_score
        FROM comprehension_responses cr
        JOIN sessions s ON cr.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        WHERE cr.item_id IN ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')
          AND CAST(SUBSTR(p.study_id, 2) AS INTEGER) BETWEEN 1 AND 15
        GROUP BY cr.session_id, s.language, p.study_id
        HAVING COUNT(cr.id) = 6
    """)
    comp_raw = cursor.fetchall()
    comp_sql_learners = [{'study_id': r['study_id'], 'score': r['total_score']} for r in comp_raw if r['language'] == 'sql']
    comp_py_learners = [{'study_id': r['study_id'], 'score': r['total_score']} for r in comp_raw if r['language'] == 'python']

    def calc_comp_stats(learners):
        vals = sorted([l['score'] for l in learners])
        if not vals:
            return {'median': 0.0, 'q1': 0.0, 'q3': 0.0}
        n = len(vals)
        med = round(statistics.median(vals), 1)
        q1 = round(vals[int(0.25 * n)], 1)
        q3 = round(vals[int(0.75 * n)], 1)
        return {'median': med, 'q1': q1, 'q3': q3}

    comprehension_data = {
        'sql': {
            'learners': comp_sql_learners,
            **calc_comp_stats(comp_sql_learners)
        },
        'python': {
            'learners': comp_py_learners,
            **calc_comp_stats(comp_py_learners)
        }
    }

    # 8. Survey Likert Responses by Condition (Q1 to Q5)
    cursor.execute("""
        SELECT sr.language, sr.q1, sr.q2, sr.q3, sr.q4, sr.q5
        FROM survey_responses sr
        JOIN sessions s ON sr.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        WHERE CAST(SUBSTR(p.study_id, 2) AS INTEGER) BETWEEN 1 AND 15
    """)
    survey_raw = cursor.fetchall()
    survey_likert_data = {'sql': {}, 'python': {}}
    for lang in ['sql', 'python']:
        l_rows = [r for r in survey_raw if r['language'] == lang]
        for q in ['q1', 'q2', 'q3', 'q4', 'q5']:
            # counts for [1 (SD), 2 (D), 3 (N), 4 (A), 5 (SA)]
            survey_likert_data[lang][q] = [sum(1 for r in l_rows if r[q] == score) for score in range(1, 6)]

    # Fetch Benchmarks records
    cursor.execute("SELECT * FROM benchmarks ORDER BY measured_at DESC, dataset_size ASC")
    raw_records = [dict(r) for r in cursor.fetchall()]

    has_seeded = _has_seeded_data(cursor)
    conn.close()

    metrics = {
        "tasks": list(task_breakdown.values()),
        "sql_correct_count": sql_correct,
        "sql_wrong_count": sql_wrong,
        "sql_total_count": sql_total,
        "sql_success_rate": sql_succ_rate,
        "sql_fail_rate": sql_fail_rate,
        "python_correct_count": py_correct,
        "python_wrong_count": py_wrong,
        "python_total_count": py_total,
        "python_success_rate": py_succ_rate,
        "python_fail_rate": py_fail_rate,
        "sql_median_time": sql_med_time,
        "python_median_time": py_med_time,
        "sql_avg_time": sql_med_time,
        "python_avg_time": py_med_time,
        "sql_avg_attempts": sql_avg_att,
        "python_avg_attempts": py_avg_att,
        "paired_time_ratio": paired_data['overall_ratio'],
        "paired_ratio_ci_low": paired_data['ci_low'],
        "paired_ratio_ci_high": paired_data['ci_high'],
        "paired_task_count": paired_data['paired_task_count'],
        "learner_scores": learner_scores,
        "learner_sql_median": learner_sql_median,
        "learner_python_median": learner_python_median,
        "ct_per_hour_data": ct_per_hour_data,
        "comprehension_data": comprehension_data,
        "survey_likert_data": survey_likert_data,
        "has_seeded": has_seeded,
    }

    grouped = {}
    for r in raw_records:
        key = (r['task_id'], r['language'])
        if key not in grouped:
            grouped[key] = {
                'task_id': r['task_id'],
                'language': r['language'],
                'scale_1k_ms': 0,
                'scale_10k_ms': 0,
                'scale_100k_ms': 0,
                'peak_memory_mb': round((r['memory_usage'] or 0) / 1024, 2),
                'measured_at': r['measured_at']
            }
        ms = round(r['execution_time'] * 1000, 2)
        if r['dataset_size'] == 1000:
            grouped[key]['scale_1k_ms'] = ms
        elif r['dataset_size'] == 10000:
            grouped[key]['scale_10k_ms'] = ms
        elif r['dataset_size'] == 100000:
            grouped[key]['scale_100k_ms'] = ms
        if r.get('memory_usage'):
            grouped[key]['peak_memory_mb'] = round(r['memory_usage'] / 1024, 2)

    bench_records = list(grouped.values())

    return render_template('dashboard/charts.html', m=metrics, benchmarks=bench_records, has_seeded=has_seeded)

@dashboard_bp.route('/benchmarks', methods=['GET'])
@require_researcher
def benchmarks():
    return redirect(url_for('dashboard.charts'))

@dashboard_bp.route('/benchmarks/run', methods=['POST'])
@require_researcher
def run_benchmarks():
    try:
        # Run real synthetic scaling benchmark
        sql_ref = "SELECT student_id, score FROM Enrollments WHERE course_id = 'C101' AND score IS NOT NULL ORDER BY score DESC, student_id ASC LIMIT 3"
        sql_res = run_benchmark("T2", "sql", sql_ref, sizes=[1000, 10000, 100000])

        py_ref = """
res = [ (e['student_id'], float(e['score'])) for e in enrollments if e['course_id'] == 'C101' and e['score'] is not None ]
res.sort(key=lambda x: (-x[1], x[0]))
res = res[:3]
"""
        py_res = run_benchmark("T2", "python", py_ref, sizes=[1000, 10000, 100000])

        # Save to research database
        conn = sqlite3.connect(get_research_db_path())
        cursor = conn.cursor()
        for r in sql_res:
            cursor.execute("""
                INSERT INTO benchmarks (task_id, language, dataset_size, execution_time, memory_usage, executions_per_second, reference_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (r['task_id'], r['language'], r['dataset_size'], r['execution_time'], r['memory_usage'], r['executions_per_second'], sql_ref))
        for r in py_res:
            cursor.execute("""
                INSERT INTO benchmarks (task_id, language, dataset_size, execution_time, memory_usage, executions_per_second, reference_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (r['task_id'], r['language'], r['dataset_size'], r['execution_time'], r['memory_usage'], r['executions_per_second'], py_ref))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "sql_results": sql_res, "python_results": py_res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@dashboard_bp.route('/seed-data', methods=['POST'])
@require_researcher
def seed_data():
    seed_pilot_data()
    flash("Pilot dataset generated successfully (16 participants).", "success")
    return redirect(url_for('dashboard.overview'))

@dashboard_bp.route('/export/<type>')
@require_researcher
def export(type):
    _safe_sync_cloud()
    if type == 'participants':
        csv_data = export_participants_csv(get_research_db_path())
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=participants_telemetry.csv"})
    elif type == 'results':
        csv_data = export_results_csv(get_research_db_path())
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=task_results_telemetry.csv"})
    elif type == 'survey':
        csv_data = export_survey_csv(get_research_db_path())
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=survey_responses.csv"})
    elif type == 'comprehension':
        csv_data = export_comprehension_csv(get_research_db_path())
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=comprehension_responses.csv"})
    elif type == 'attempts':
        csv_data = export_attempts_csv(get_research_db_path())
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=task_attempts_telemetry.csv"})
    elif type == 'all':
        zip_bytes = export_all_csv(get_research_db_path())
        return Response(zip_bytes, mimetype="application/zip", headers={"Content-Disposition": "attachment;filename=querylearn_case_study_dataset.zip"})
    else:
        csv_data = export_participants_csv(get_research_db_path())
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=participants.csv"})
