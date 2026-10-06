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

@dashboard_bp.route('/')
@require_researcher
def overview():
    # Sync latest cross-computer participant submissions from Supabase
    try:
        from services.cloud_db import sync_cloud_to_local
        sync_cloud_to_local(get_research_db_path())
    except Exception:
        pass

    conn = sqlite3.connect(get_research_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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

    # 3. Paired Successful-Task Time Ratio:
    # Median Python time / Median SQL time calculated ONLY on tasks that the same participant answered correctly in both conditions
    cursor.execute("""
        SELECT r_sql.elapsed_seconds as sql_time, r_py.elapsed_seconds as py_time
        FROM task_results r_sql
        JOIN sessions s_sql ON r_sql.session_id = s_sql.id AND s_sql.language = 'sql'
        JOIN task_results r_py ON r_sql.task_id = r_py.task_id
        JOIN sessions s_py ON r_py.session_id = s_py.id AND s_py.language = 'python' AND s_py.participant_id = s_sql.participant_id
        WHERE r_sql.success = 1 AND r_py.success = 1
    """)
    paired_rows = cursor.fetchall()
    if paired_rows:
        paired_sql_times = [r['sql_time'] for r in paired_rows if r['sql_time'] is not None]
        paired_py_times = [r['py_time'] for r in paired_rows if r['py_time'] is not None]
        med_paired_sql = statistics.median(paired_sql_times) if paired_sql_times else 0
        med_paired_py = statistics.median(paired_py_times) if paired_py_times else 0
        paired_time_ratio = round(med_paired_py / med_paired_sql, 2) if med_paired_sql > 0 else None
        paired_task_count = len(paired_rows)
    else:
        paired_time_ratio = None
        paired_task_count = 0

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
            (r['elapsed_seconds'] / 60.0) if (r['success'] == 1 and r['elapsed_seconds'] is not None) else (480.0 / 60.0)
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

    task_breakdown = {}
    for tid in sorted(list(all_tasks)):
        task_breakdown[tid] = {'task_id': tid}
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
        "paired_task_count": paired_task_count,
        "sql_ct_per_hour": sql_ct_per_hour,
        "python_ct_per_hour": py_ct_per_hour,
        "sql_median_comp": sql_median_comp,
        "python_median_comp": python_median_comp,
        "comp_session_count": comp_session_count,
        "tasks": list(task_breakdown.values())
    }

    return render_template('dashboard/overview.html', m=metrics)

@dashboard_bp.route('/participants')
@require_researcher
def participants():
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
    cursor.execute(data_sql, params + [per_page, offset])
    results_list = [dict(r) for r in cursor.fetchall()]
    conn.close()

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
        search_query=search
    )

@dashboard_bp.route('/analytics')
@dashboard_bp.route('/charts')
@require_researcher
def charts():
    """Comparative Analytics & Benchmarks combined page — uses medians."""
    conn = sqlite3.connect(get_research_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch raw rows for median computation in Python
    cursor.execute("""
        SELECT r.task_id, s.language, r.success, r.elapsed_seconds, r.attempt_count
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        ORDER BY r.task_id ASC
    """)
    raw_task_rows = cursor.fetchall()

    from collections import defaultdict
    task_groups = defaultdict(lambda: {'success': [], 'times': [], 'attempts': []})
    lang_times = defaultdict(list)
    lang_success = defaultdict(list)
    all_tasks = set()

    for row in raw_task_rows:
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

    task_breakdown = {}
    for tid in sorted(list(all_tasks)):
        task_breakdown[tid] = {'task_id': tid}
        for lang in ['sql', 'python']:
            group = task_groups.get((tid, lang), {'success': [], 'times': [], 'attempts': []})
            s_list = group['success']
            t_list = group['times']
            a_list = group['attempts']
            succ_pct = round((sum(s_list) / len(s_list)) * 100, 1) if s_list else 0.0
            med_time = round(statistics.median(t_list), 1) if t_list else 0.0
            avg_att = round(sum(a_list) / len(a_list), 1) if a_list else 0.0
            task_breakdown[tid][f"{lang}_success"] = succ_pct
            task_breakdown[tid][f"{lang}_time"] = med_time  # median
            task_breakdown[tid][f"{lang}_attempts"] = avg_att

    # Aggregate medians
    sql_med_time = round(statistics.median(lang_times['sql']), 1) if lang_times['sql'] else 0
    py_med_time = round(statistics.median(lang_times['python']), 1) if lang_times['python'] else 0
    sql_succ_rate = round((sum(lang_success['sql']) / len(lang_success['sql'])) * 100, 1) if lang_success['sql'] else 0
    py_succ_rate = round((sum(lang_success['python']) / len(lang_success['python'])) * 100, 1) if lang_success['python'] else 0

    # Fetch Benchmarks records
    cursor.execute("SELECT * FROM benchmarks ORDER BY measured_at DESC, dataset_size ASC")
    raw_records = [dict(r) for r in cursor.fetchall()]

    conn.close()

    metrics = {
        "tasks": list(task_breakdown.values()),
        "sql_success_rate": sql_succ_rate,
        "python_success_rate": py_succ_rate,
        "sql_median_time": sql_med_time,
        "python_median_time": py_med_time,
        # Keep avg_time keys for backward compat with charts template
        "sql_avg_time": sql_med_time,
        "python_avg_time": py_med_time,
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

    return render_template('dashboard/charts.html', m=metrics, benchmarks=bench_records)

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
