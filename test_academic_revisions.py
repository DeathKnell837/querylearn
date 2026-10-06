import unittest
import os
import sqlite3
import tempfile
import shutil
import re
import csv
import io
from app import create_app
from config import Config
from database.init_research_db import init_research_db
from services.pilot_data_seeder import STUDENT_PROFILES
from services.cloud_db import get_next_cloud_study_id, sync_cloud_to_local
from services.export_service import export_results_csv, export_attempts_csv, export_comprehension_csv, export_survey_csv


class AcademicRevisionsTestCase(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary test database to protect production research.db
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_research.db')
        if os.path.exists(Config.RESEARCH_DB):
            shutil.copyfile(Config.RESEARCH_DB, self.test_db_path)

        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['RESEARCH_DB'] = self.test_db_path
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_no_freshman_in_student_profiles(self):
        """Verify that all pilot dataset profiles have year >= 2 (freshmen excluded)."""
        for profile in STUDENT_PROFILES:
            year = profile[1]
            self.assertGreaterEqual(year, 2, f"Found freshman (year {year}) in STUDENT_PROFILES: {profile}")
            self.assertLessEqual(year, 4)

    def test_registration_dropdown_excludes_freshman(self):
        """Verify that register.html template does not offer 1st Year (Freshman)."""
        resp = self.client.get('/register')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertNotIn('<option value="1">', html)
        self.assertNotIn('1st Year', html)
        self.assertIn('2nd Year', html)
        self.assertIn('3rd Year', html)
        self.assertIn('4th Year', html)

    def test_registration_clamps_year_level(self):
        """Verify that attempting to submit year_level < 2 clamps to 2."""
        with self.app.test_request_context():
            resp = self.client.post('/register', data={
                'program': 'BSCS',
                'year_level': '1',  # attempted freshman submission
                'sql_exp': 'novice',
                'python_exp': 'novice',
                'db_course': 'yes',
                'consent': '1'
            }, follow_redirects=False)
            self.assertEqual(resp.status_code, 302)

            # Check inserted participant in isolated test database
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT year_level FROM participants ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 2, "Submitted year_level 1 must be clamped to 2")

    def test_sequential_cloud_study_id_generator(self):
        """Verify that get_next_cloud_study_id returns sequentially unique IDs starting at or above P017."""
        study_id = get_next_cloud_study_id(self.test_db_path)
        self.assertTrue(study_id.startswith('P'), f"Expected Study ID format PXXX, got {study_id}")
        match = re.match(r"^P(\d+)$", study_id)
        self.assertIsNotNone(match)
        id_num = int(match.group(1))
        self.assertGreaterEqual(id_num, 17, f"Live study IDs must be at least P017 (after 16 pilot users), got {study_id}")

    def test_headline_cards_in_overview(self):
        """Verify that overview dashboard keeps only 4 headline cards, link to comparison, and sample data banner."""
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True
            sess['researcher_name'] = 'admin'

        resp = self.client.get('/dashboard/')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # 4 Headline Cards
        self.assertIn('Median Duration', html)
        self.assertIn('Correct Tasks / Hour', html)
        self.assertIn('Paired Successful Time Ratio', html)
        self.assertIn('Median Comprehension Score', html)

        # Single Link to Comparison
        self.assertIn('View Comparison', html)

        # Tile 1 and duplicate table removed
        self.assertNotIn('Overall Evaluation (Pass vs. Fail)', html)
        self.assertNotIn('Task Telemetry & Evaluation Analysis', html)

        # Sample data banner when seeded participants exist
        self.assertIn('Sample data: these 16 participants are generated for testing and are not study results.', html)

    def test_badges_and_headers_in_results(self):
        """Verify that results page displays Correct and Incorrect pills, Time (s) column, and sample data banner."""
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True
            sess['researcher_name'] = 'admin'

        resp = self.client.get('/dashboard/results')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Time (s)', html)
        self.assertIn('Outcome', html)
        self.assertIn('Correct', html)
        self.assertNotIn('Right (Correct)', html)
        self.assertNotIn('Wrong (Incorrect)', html)
        self.assertIn('Sample data: these 16 participants are generated for testing and are not study results.', html)

    def test_comparison_page_clean_wording_and_matrix(self):
        """Verify that comparison page displays neutral What it tests, Accuracy difference, 0 pts, and clean duration."""
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True
            sess['researcher_name'] = 'admin'

        resp = self.client.get('/dashboard/charts')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Task Comparison', html)
        self.assertIn('What it tests', html)
        self.assertIn('Accuracy difference', html)
        self.assertIn('task attempts', html)
        self.assertIn('0 pts', html)
        self.assertNotIn('Qualitative Synthesis', html)
        self.assertNotIn('Empirical Task Evaluation Matrix', html)
        self.assertIn('Sample data: these 16 participants are generated for testing and are not study results.', html)

    def test_csv_export_explicit_outcome_column(self):
        """Verify that results.csv and attempts.csv contain the explicit outcome column with CORRECT/WRONG."""
        res_csv = export_results_csv(self.test_db_path)
        res_reader = list(csv.reader(io.StringIO(res_csv)))
        self.assertGreater(len(res_reader), 1)
        res_headers = [h.strip() for h in res_reader[0]]
        self.assertIn('outcome', res_headers)
        outcome_idx = res_headers.index('outcome')
        success_idx = res_headers.index('success')

        # Check rows
        for row in res_reader[1:20]:
            success_val = row[success_idx].strip()
            outcome_val = row[outcome_idx].strip()
            if success_val == '1':
                self.assertEqual(outcome_val, 'CORRECT')
            else:
                self.assertEqual(outcome_val, 'WRONG')

        # Check attempts.csv
        att_csv = export_attempts_csv(self.test_db_path)
        att_reader = list(csv.reader(io.StringIO(att_csv)))
        self.assertGreater(len(att_reader), 1)
        att_headers = [h.strip() for h in att_reader[0]]
        self.assertIn('outcome', att_headers)
        att_outcome_idx = att_headers.index('outcome')
        att_status_idx = att_headers.index('result_status')

        for row in att_reader[1:20]:
            status_val = row[att_status_idx].strip()
            outcome_val = row[att_outcome_idx].strip()
            if status_val == 'correct':
                self.assertEqual(outcome_val, 'CORRECT')
            else:
                self.assertEqual(outcome_val, 'WRONG')

    def test_diagram_files_exist(self):
        """Verify that the 3 formal engineering diagram assets exist."""
        diagrams_dir = os.path.join(Config.BASE_DIR, "diagrams")
        d1 = os.path.join(diagrams_dir, "01_system_architecture.png")
        d2 = os.path.join(diagrams_dir, "02_system_context_dfd0.png")
        d3 = os.path.join(diagrams_dir, "03_use_case_diagram.png")

        self.assertTrue(os.path.exists(d1), f"Missing architecture diagram: {d1}")
        self.assertTrue(os.path.exists(d2), f"Missing context diagram: {d2}")
        self.assertTrue(os.path.exists(d3), f"Missing use case diagram: {d3}")

        # Check files have non-zero size
        self.assertGreater(os.path.getsize(d1), 10000)
        self.assertGreater(os.path.getsize(d2), 10000)
        self.assertGreater(os.path.getsize(d3), 10000)

    def test_handbook_pdf_generated(self):
        """Verify that the Defense Handbook PDF exists in the repository and has valid content."""
        pdf_path = os.path.join(Config.BASE_DIR, "QueryLearn_System_Guide_and_Defense_Handbook.pdf")
        self.assertTrue(os.path.exists(pdf_path), f"Missing PDF handbook: {pdf_path}")
        self.assertGreater(os.path.getsize(pdf_path), 50000)

    def test_cloud_to_local_sync_and_relational_integrity(self):
        """Verify that sync_cloud_to_local populates participants, sessions, results, comp, and surveys with valid relational joins."""
        clean_db_path = os.path.join(self.test_dir, 'clean_sync.db')
        init_research_db(clean_db_path)

        synced = sync_cloud_to_local(clean_db_path)
        self.assertTrue(synced, "sync_cloud_to_local must return True when pulling from cloud")

        conn = sqlite3.connect(clean_db_path)
        c = conn.cursor()

        # 1. Verify participants and sessions exist
        part_count = c.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
        sess_count = c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        self.assertGreaterEqual(part_count, 16, "Must sync at least 16 pilot participants from cloud")
        self.assertEqual(sess_count, part_count * 2, "Each participant must have exactly 2 local sessions (SQL and Python)")

        # 2. Verify task results join correctly to sessions
        c.execute("""
            SELECT s.language, COUNT(r.id), SUM(CASE WHEN r.success = 1 THEN 1 ELSE 0 END)
            FROM task_results r
            JOIN sessions s ON r.session_id = s.id
            GROUP BY s.language
        """)
        lang_rows = {row[0]: (row[1], row[2]) for row in c.fetchall()}
        self.assertIn('sql', lang_rows, "SQL task results must join to local sessions")
        self.assertIn('python', lang_rows, "Python task results must join to local sessions")
        self.assertGreater(lang_rows['sql'][0], 0)
        self.assertGreater(lang_rows['python'][0], 0)

        # 3. Verify comprehension responses join to sessions
        c.execute("""
            SELECT COUNT(cr.id)
            FROM comprehension_responses cr
            JOIN sessions s ON cr.session_id = s.id
        """)
        comp_joined_count = c.execute("SELECT COUNT(cr.id) FROM comprehension_responses cr JOIN sessions s ON cr.session_id = s.id").fetchone()[0]
        self.assertGreater(comp_joined_count, 0, "Comprehension responses must join to local sessions")

        # 4. Verify survey responses join to sessions
        survey_joined_count = c.execute("SELECT COUNT(sr.id) FROM survey_responses sr JOIN sessions s ON sr.session_id = s.id").fetchone()[0]
        self.assertGreater(survey_joined_count, 0, "Survey responses must join to local sessions")

        conn.close()


if __name__ == '__main__':
    unittest.main()
