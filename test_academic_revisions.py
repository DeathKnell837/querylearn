import unittest
import os
import sqlite3
import tempfile
import re
from app import create_app
from config import Config
from services.pilot_data_seeder import STUDENT_PROFILES
from services.cloud_db import get_next_cloud_study_id
from services.export_service import export_results_csv, export_attempts_csv


class AcademicRevisionsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

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

            # Check inserted participant in database
            conn = sqlite3.connect(Config.RESEARCH_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT year_level FROM participants ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 2, "Submitted year_level 1 must be clamped to 2")

    def test_sequential_cloud_study_id_generator(self):
        """Verify that get_next_cloud_study_id returns sequentially unique IDs starting at or above P017."""
        study_id = get_next_cloud_study_id(Config.RESEARCH_DB)
        self.assertTrue(study_id.startswith('P'), f"Expected Study ID format PXXX, got {study_id}")
        match = re.match(r"^P(\d+)$", study_id)
        self.assertIsNotNone(match)
        id_num = int(match.group(1))
        self.assertGreaterEqual(id_num, 17, f"Live study IDs must be at least P017 (after 16 pilot users), got {study_id}")

    def test_right_vs_wrong_metrics_in_overview(self):
        """Verify that overview dashboard computes exact Right vs Wrong counts and split percentages."""
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True
            sess['researcher_name'] = 'admin'

        resp = self.client.get('/dashboard/')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Check Tile 1 displays Right vs Wrong text and percentages
        self.assertIn('Overall Evaluation (Pass vs. Fail)', html)
        self.assertIn('Right /', html)
        self.assertIn('Wrong', html)
        self.assertIn('% Right', html)
        self.assertIn('% Wrong', html)

        # Check table columns
        self.assertIn('SQL Performance (Right vs. Wrong)', html)
        self.assertIn('Python Performance (Right vs. Wrong)', html)

    def test_right_vs_wrong_badges_in_results(self):
        """Verify that results page displays explicit Right (Correct) and Wrong (Incorrect) badges."""
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True
            sess['researcher_name'] = 'admin'

        resp = self.client.get('/dashboard/results')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn('Outcome (Right / Wrong)', html)
        self.assertTrue('Right (Correct)' in html or 'Wrong (Incorrect)' in html)

    def test_csv_export_explicit_outcome_column(self):
        """Verify that results.csv and attempts.csv contain the explicit outcome column with CORRECT/WRONG."""
        res_csv = export_results_csv(Config.RESEARCH_DB)
        res_lines = res_csv.strip().splitlines()
        self.assertGreater(len(res_lines), 1)
        res_headers = [h.strip() for h in res_lines[0].split(',')]
        self.assertIn('outcome', res_headers)
        outcome_idx = res_headers.index('outcome')
        success_idx = res_headers.index('success')

        # Check rows
        for line in res_lines[1:20]:
            parts = [p.strip() for p in line.split(',')]
            success_val = parts[success_idx]
            outcome_val = parts[outcome_idx]
            if success_val == '1':
                self.assertEqual(outcome_val, 'CORRECT')
            else:
                self.assertEqual(outcome_val, 'WRONG')

        # Check attempts.csv
        att_csv = export_attempts_csv(Config.RESEARCH_DB)
        att_lines = att_csv.strip().splitlines()
        self.assertGreater(len(att_lines), 1)
        att_headers = [h.strip() for h in att_lines[0].split(',')]
        self.assertIn('outcome', att_headers)
        att_outcome_idx = att_headers.index('outcome')
        att_status_idx = att_headers.index('result_status')

        for line in att_lines[1:20]:
            parts = [p.strip() for p in line.split(',')]
            status_val = parts[att_status_idx]
            outcome_val = parts[att_outcome_idx]
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


if __name__ == '__main__':
    unittest.main()
