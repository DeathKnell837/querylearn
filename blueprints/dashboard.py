import sqlite3
import statistics
import time
from flask import Blueprint, render_template, redirect, url_for, session, Response, request, flash, jsonify
from config import Config
from services.export_service import export_participants_csv, export_results_csv, export_all_csv
from services.pilot_data_seeder import seed_pilot_data
from services.benchmark_runner import run_benchmark

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

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
    conn = sqlite3.connect(Config.RESEARCH_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Overall Language Stats (Success Rate)
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

    sql_total = sql_stats['total_attempts'] or 1
    sql_success_pct = round((sql_stats['successful_tasks'] / sql_total) * 100, 1) if sql_stats['total_attempts'] else 0

    py_total = py_stats['total_attempts'] or 1
    py_success_pct = round((py_stats['successful_tasks'] / py_total) * 100, 1) if py_stats['total_attempts'] else 0

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

    # 5. Task-by-Task Comparison (T1 to T6)
    cursor.execute("""
        SELECT 
            r.task_id,
            s.language,
            ROUND(AVG(CASE WHEN r.success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate,
            ROUND(AVG(r.elapsed_seconds), 1) as avg_time,
            ROUND(AVG(r.attempt_count), 1) as avg_attempts
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        GROUP BY r.task_id, s.language
        ORDER BY r.task_id ASC
    """)
    task_rows = cursor.fetchall()
    task_breakdown = {}
    for row in task_rows:
        tid = row['task_id']
        lang = row['language']
        if tid not in task_breakdown:
            task_breakdown[tid] = {'task_id': tid}
        task_breakdown[tid][f"{lang}_success"] = row['success_rate']
        task_breakdown[tid][f"{lang}_time"] = row['avg_time']
        task_breakdown[tid][f"{lang}_attempts"] = row['avg_attempts']

    conn.close()

    metrics = {
        "sql_success_rate": sql_success_pct,
        "python_success_rate": py_success_pct,
        "sql_median_time": sql_median_time,
        "python_median_time": py_median_time,
        "paired_time_ratio": paired_time_ratio,
        "paired_task_count": paired_task_count,
        "sql_ct_per_hour": sql_ct_per_hour,
        "python_ct_per_hour": py_ct_per_hour,
        "tasks": list(task_breakdown.values())
    }

    return render_template('dashboard/overview.html', m=metrics)

@dashboard_bp.route('/participants')
@require_researcher
def participants():
    conn = sqlite3.connect(Config.RESEARCH_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM participants ORDER BY id DESC")
    participants_list = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('dashboard/participants.html', participants=participants_list)

@dashboard_bp.route('/results')
@require_researcher
def results():
    conn = sqlite3.connect(Config.RESEARCH_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, p.study_id, s.language, s.form
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        JOIN participants p ON s.participant_id = p.id
        ORDER BY r.id DESC LIMIT 100
    """)
    results_list = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return render_template('dashboard/results.html', results=results_list)

@dashboard_bp.route('/analytics')
@dashboard_bp.route('/charts')
@require_researcher
def charts():
    """Comparative Analytics & Benchmarks combined page."""
    conn = sqlite3.connect(Config.RESEARCH_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Task-by-Task metrics for charts
    cursor.execute("""
        SELECT 
            r.task_id,
            s.language,
            ROUND(AVG(CASE WHEN r.success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate,
            ROUND(AVG(r.elapsed_seconds), 1) as avg_time,
            ROUND(AVG(r.attempt_count), 1) as avg_attempts
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        GROUP BY r.task_id, s.language
        ORDER BY r.task_id ASC
    """)
    task_rows = cursor.fetchall()
    task_breakdown = {}
    for row in task_rows:
        tid = row['task_id']
        lang = row['language']
        if tid not in task_breakdown:
            task_breakdown[tid] = {'task_id': tid}
        task_breakdown[tid][f"{lang}_success"] = row['success_rate']
        task_breakdown[tid][f"{lang}_time"] = row['avg_time']
        task_breakdown[tid][f"{lang}_attempts"] = row['avg_attempts']

    # Aggregate stats
    cursor.execute("""
        SELECT s.language,
            ROUND(AVG(CASE WHEN r.success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate,
            ROUND(AVG(r.elapsed_seconds), 1) as avg_time,
            ROUND(AVG(r.attempt_count), 2) as avg_attempts
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        GROUP BY s.language
    """)
    lang_stats = {row['language']: dict(row) for row in cursor.fetchall()}

    # Fetch Benchmarks records
    cursor.execute("SELECT * FROM benchmarks ORDER BY measured_at DESC, dataset_size ASC")
    raw_records = [dict(r) for r in cursor.fetchall()]

    conn.close()

    sql_stats = lang_stats.get('sql', {})
    py_stats = lang_stats.get('python', {})

    metrics = {
        "tasks": list(task_breakdown.values()),
        "sql_success_rate": sql_stats.get('success_rate', 0),
        "python_success_rate": py_stats.get('success_rate', 0),
        "sql_avg_time": sql_stats.get('avg_time', 0),
        "python_avg_time": py_stats.get('avg_time', 0),
        "sql_avg_attempts": sql_stats.get('avg_attempts', 0),
        "python_avg_attempts": py_stats.get('avg_attempts', 0),
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
        conn = sqlite3.connect(Config.RESEARCH_DB)
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
        csv_data = export_participants_csv(Config.RESEARCH_DB)
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=participants_telemetry.csv"})
    elif type == 'results':
        csv_data = export_results_csv(Config.RESEARCH_DB)
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=task_results_telemetry.csv"})
    elif type == 'all':
        zip_bytes = export_all_csv(Config.RESEARCH_DB)
        return Response(zip_bytes, mimetype="application/zip", headers={"Content-Disposition": "attachment;filename=querylearn_case_study_dataset.zip"})
    else:
        csv_data = export_participants_csv(Config.RESEARCH_DB)
        return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=participants.csv"})
