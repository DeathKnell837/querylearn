import sqlite3
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

    # Total counts
    cursor.execute("SELECT COUNT(*) FROM participants")
    total_participants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM participants WHERE status = 'completed'")
    completed_participants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM participants WHERE status = 'in_progress'")
    in_progress_participants = cursor.fetchone()[0]

    # Task performance comparison: SQL vs Python
    cursor.execute("""
        SELECT 
            s.language,
            COUNT(r.id) as total_attempts,
            SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END) as successful_tasks,
            ROUND(AVG(r.elapsed_seconds), 1) as avg_duration_sec,
            ROUND(AVG(r.attempt_count), 2) as avg_attempts
        FROM task_results r
        JOIN sessions s ON r.session_id = s.id
        GROUP BY s.language
    """)
    lang_stats = {row['language']: dict(row) for row in cursor.fetchall()}

    sql_stats = lang_stats.get('sql', {'successful_tasks': 0, 'total_attempts': 0, 'avg_duration_sec': 0, 'avg_attempts': 0})
    py_stats = lang_stats.get('python', {'successful_tasks': 0, 'total_attempts': 0, 'avg_duration_sec': 0, 'avg_attempts': 0})

    sql_total = sql_stats['total_attempts'] or 1
    sql_success_pct = round((sql_stats['successful_tasks'] / sql_total) * 100, 1) if sql_stats['total_attempts'] else 0

    py_total = py_stats['total_attempts'] or 1
    py_success_pct = round((py_stats['successful_tasks'] / py_total) * 100, 1) if py_stats['total_attempts'] else 0

    # Task-by-Task Comparison (T1 to T6)
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

    # Recent participants
    cursor.execute("""
        SELECT p.*, 
            (SELECT COUNT(*) FROM task_results tr JOIN sessions s ON tr.session_id = s.id WHERE s.participant_id = p.id AND tr.success = 1) as solved_tasks
        FROM participants p 
        ORDER BY p.id DESC LIMIT 10
    """)
    recent_participants = [dict(r) for r in cursor.fetchall()]

    conn.close()

    metrics = {
        "total_participants": total_participants,
        "completed": completed_participants,
        "in_progress": in_progress_participants,
        "sql_success_rate": sql_success_pct,
        "python_success_rate": py_success_pct,
        "sql_avg_time": sql_stats['avg_duration_sec'],
        "python_avg_time": py_stats['avg_duration_sec'],
        "sql_avg_attempts": sql_stats['avg_attempts'],
        "python_avg_attempts": py_stats['avg_attempts'],
        "tasks": list(task_breakdown.values()),
        "participants": recent_participants
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
