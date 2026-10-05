import unittest
import os
import json
import sqlite3
import tempfile
import shutil
from app import create_app
from config import Config
from services.python_runner import execute_python
from services.sql_runner import execute_sql
from services.answer_checker import check_answer
from services.export_service import (
    export_participants_csv, export_results_csv,
    export_survey_csv, export_comprehension_csv,
    export_attempts_csv, export_all_csv
)


class TestPlatformCorrections(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_python_sandbox_security(self):
        """Verify that dunder subclass traversal and blocked imports are blocked statically."""
        data_vars = {'students': [], 'courses': [], 'enrollments': []}

        # 1. Traversal exploit must be blocked
        exploit_code = "for c in ().__class__.__base__.__subclasses__(): pass"
        res = execute_python(exploit_code, data_vars)
        self.assertIn("Security restriction", res['error'])
        self.assertIn("__subclasses__", res['error'])

        # 2. Blocked import must be blocked
        res2 = execute_python("import os", data_vars)
        self.assertIn("ImportError", res2['error'])

        # 3. Allowed import must succeed
        res3 = execute_python("import math; print(math.sqrt(16))", data_vars)
        self.assertIsNone(res3['error'])
        self.assertEqual(res3['output'].strip(), "4.0")

    def test_python_traceback_offset_and_path_sanitization(self):
        """Verify that runtime errors report user line numbers and do not leak temp paths."""
        data_vars = {'students': [], 'courses': [], 'enrollments': []}
        res = execute_python("x = 1 / 0", data_vars)
        self.assertIn('File "<user_code>", line 1', res['error'])
        self.assertNotIn("AppData", res['error'])
        self.assertNotIn("tempfile", res['error'])

    def test_sql_runner_word_boundary_and_comments(self):
        """Verify that legitimate identifiers like updated_at and comments are not falsely blocked."""
        # Query with updated_at column alias
        res = execute_sql(Config.EXPERIMENT_A_DB, "SELECT student_id, score AS updated_at FROM Enrollments LIMIT 1")
        self.assertIsNone(res['error'])
        self.assertEqual(res['columns'], ['student_id', 'updated_at'])

        # Query with comment containing 'created'
        res2 = execute_sql(Config.EXPERIMENT_A_DB, "-- created by test\nSELECT student_id FROM Students LIMIT 1")
        self.assertIsNone(res2['error'])

        # Forbidden statement must still be blocked
        res3 = execute_sql(Config.EXPERIMENT_A_DB, "DROP TABLE Students")
        self.assertIn("DDL/DML operations", res3['error'])

    def test_answer_checker_dict_records(self):
        """Verify that check_answer supports lists of dicts from python novice outputs."""
        learner_output = [{'student_id': 1, 'name': 'Alice'}, {'student_id': 2, 'name': 'Bob'}]
        expected_output = [(1, 'Alice'), (2, 'Bob')]
        res = check_answer(learner_output, expected_output)
        self.assertTrue(res['correct'])

    def test_route_fallbacks(self):
        """Verify that unparameterized /experiment/comprehension and /survey redirect instead of 404."""
        # Unauthenticated redirects to /register
        r1 = self.client.get('/experiment/comprehension')
        self.assertEqual(r1.status_code, 302)
        self.assertIn('/register', r1.headers['Location'])

        r2 = self.client.get('/experiment/survey')
        self.assertEqual(r2.status_code, 302)
        self.assertIn('/register', r2.headers['Location'])

        # Authenticated redirects to parameterized route
        with self.client.session_transaction() as sess:
            sess['participant_id'] = 1
            sess['current_language'] = 'python'

        r3 = self.client.get('/experiment/comprehension')
        self.assertEqual(r3.status_code, 302)
        self.assertIn('/experiment/comprehension/python', r3.headers['Location'])

        r4 = self.client.get('/experiment/survey')
        self.assertEqual(r4.status_code, 302)
        self.assertIn('/experiment/survey/python', r4.headers['Location'])

    def test_telemetry_csv_exports(self):
        """Verify that all CSV exports including attempts and zip archive export valid data."""
        db = Config.RESEARCH_DB
        p_csv = export_participants_csv(db)
        self.assertIn("study_id", p_csv)

        r_csv = export_results_csv(db)
        self.assertIn("task_id", r_csv)

        s_csv = export_survey_csv(db)
        self.assertIn("study_id", s_csv)

        c_csv = export_comprehension_csv(db)
        self.assertIn("item_id", c_csv)
        self.assertIn("P001", c_csv)

        a_csv = export_attempts_csv(db)
        self.assertIn("attempt_number", a_csv)
        self.assertIn("submitted_code", a_csv)

        zip_bytes = export_all_csv(db)
        self.assertGreater(len(zip_bytes), 1000)

    def test_dashboard_metrics_rendering(self):
        """Verify that dashboard displays valid comprehension medians and telemetry."""
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True

        res = self.client.get('/dashboard/')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn("16.0 / 18", html)
        self.assertIn("12.0 / 18", html)
        self.assertIn("Comparative Productivity Summary", html)


if __name__ == '__main__':
    unittest.main()
