import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'querylearn-dev-key-2026')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database paths (supports local execution and Vercel serverless /tmp)
    IS_VERCEL = bool(os.environ.get('VERCEL'))
    if IS_VERCEL:
        DB_DIR = '/tmp'
        import shutil
        for db_name in ['research.db', 'experiment_a.db', 'experiment_b.db']:
            src = os.path.join(BASE_DIR, 'database', db_name)
            dst = os.path.join(DB_DIR, db_name)
            if not os.path.exists(dst) and os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                except Exception:
                    pass
        RESEARCH_DB = os.path.join(DB_DIR, 'research.db')
        EXPERIMENT_A_DB = os.path.join(DB_DIR, 'experiment_a.db')
        EXPERIMENT_B_DB = os.path.join(DB_DIR, 'experiment_b.db')
    else:
        RESEARCH_DB = os.path.join(BASE_DIR, 'database', 'research.db')
        EXPERIMENT_A_DB = os.path.join(BASE_DIR, 'database', 'experiment_a.db')
        EXPERIMENT_B_DB = os.path.join(BASE_DIR, 'database', 'experiment_b.db')
    HIDDEN_TESTS = os.path.join(BASE_DIR, 'database', 'hidden_tests.json')

    # Task settings
    TASK_TIMEOUT_SECONDS = 300        # 5 minutes per task (standard for novice debugging)
    CODE_EXECUTION_TIMEOUT = 10       # 10 seconds for code execution
    COMPREHENSION_MAX_TIME = 180      # 3 minutes per comprehension item
    TASKS_PER_FORM = 6
    COMPREHENSION_ITEMS = 6
    NUMERIC_TOLERANCE = 0.000001

    # Benchmark settings
    BENCHMARK_SIZES = [1000, 10000, 100000]
    BENCHMARK_RUNS = 5

    # Researcher default credentials
    DEFAULT_RESEARCHER = 'admin'
    DEFAULT_PASSWORD = 'querylearn2026'

    # Cloud Persistence (Supabase PostgreSQL REST API)
    SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://jjndlvtzqowvbcrjlzro.supabase.co')
    SUPABASE_KEY = os.environ.get(
        'SUPABASE_KEY',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqbmRsdnR6cW93dmJjcmpsenJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0MzA1MzYsImV4cCI6MjA3NjAwNjUzNn0.Bh6JJEQdBn0wrqRSc1ycdjJe4siCh2oS85RwCSMyh8E'
    )
