"""
Unit and Integration Tests for QueryLearn Comprehension Protocol Updates.

Tests:
1. Scoring of full (2pt), partial (1pt), and wrong (0pt) explanation answers.
2. Scoring of correct (1pt) and wrong (0pt) prediction answers.
3. 18-point maximum per condition (6 items * 3 pts).
4. Database row schema and per-item persistence (study_id, session_id, item_id, language, form,
   explanation_score, prediction_score, response_time_seconds, timed_out).
5. Countdown timeout behavior (timed_out=1, recorded time).
6. CSV export including per-item comprehension rows with proper columns.
7. Dashboard overview median calculation and exclusion of legacy 3-item participants.
8. Flask route flow: progression from C1 to C6 and redirect to survey.
"""

import unittest
import sqlite3
import os
import shutil
import tempfile
from app import create_app
from config import Config
from services.comprehension_items import get_form_items, get_item, grade_item
from services.export_service import export_comprehension_csv


class TestComprehensionUpdates(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary test database to protect research.db
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_research.db')
        
        # Copy schema from research.db or initialize
        src_db = Config.RESEARCH_DB
        if os.path.exists(src_db):
            shutil.copyfile(src_db, self.test_db_path)
        
        # Create test app with isolated DB
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['RESEARCH_DB'] = self.test_db_path
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_item_definitions_and_scoring(self):
        """Test full (2pt), partial (1pt), wrong (0pt) answers and 18-pt maximum."""
        for form in ['A', 'B']:
            items = get_form_items(form)
            self.assertEqual(len(items), 6, f"Form {form} must have exactly 6 items")
            
            condition_max = 0
            for item_id in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']:
                item = get_item(form, item_id, randomize=False)
                self.assertEqual(item['item_id'], item_id)
                self.assertEqual(len(item['explanation']['options']), 4)
                self.assertEqual(len(item['prediction']['options']), 4)
                
                # Check explanation options distribution: [0, 0, 1, 2]
                exp_points = sorted([opt['points'] for opt in item['explanation']['options']])
                self.assertEqual(exp_points, [0, 0, 1, 2])
                
                # Check prediction options distribution: [0, 0, 0, 1]
                pred_points = sorted([opt['points'] for opt in item['prediction']['options']])
                self.assertEqual(pred_points, [0, 0, 0, 1])
                
                full_exp = [opt['id'] for opt in item['explanation']['options'] if opt['points'] == 2][0]
                part_exp = [opt['id'] for opt in item['explanation']['options'] if opt['points'] == 1][0]
                wrong_exp = [opt['id'] for opt in item['explanation']['options'] if opt['points'] == 0][0]
                
                corr_pred = [opt['id'] for opt in item['prediction']['options'] if opt['points'] == 1][0]
                wrong_pred = [opt['id'] for opt in item['prediction']['options'] if opt['points'] == 0][0]
                
                # 1. Full score test: 2 + 1 = 3
                exp, pred, tot = grade_item(form, item_id, full_exp, corr_pred)
                self.assertEqual((exp, pred, tot), (2.0, 1.0, 3.0))
                
                # 2. Partial explanation test: 1 + 1 = 2
                exp, pred, tot = grade_item(form, item_id, part_exp, corr_pred)
                self.assertEqual((exp, pred, tot), (1.0, 1.0, 2.0))
                
                # 3. Partial explanation + wrong prediction: 1 + 0 = 1
                exp, pred, tot = grade_item(form, item_id, part_exp, wrong_pred)
                self.assertEqual((exp, pred, tot), (1.0, 0.0, 1.0))
                
                # 4. Wrong answer test: 0 + 0 = 0
                exp, pred, tot = grade_item(form, item_id, wrong_exp, wrong_pred)
                self.assertEqual((exp, pred, tot), (0.0, 0.0, 0.0))
                
                condition_max += 3

            # 18-point maximum check
            self.assertEqual(condition_max, 18, f"Form {form} max score must be exactly 18")

    def test_database_persistence_and_timeout(self):
        """Test per-item DB insertion, timeout handling, and required columns."""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Insert a mock test session
        cursor.execute("INSERT INTO participants (study_id, program, year_level, status) VALUES ('P999', 'BSCS', 1, 'in_progress')")
        p_id = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form, sequence_order) VALUES (?, 'sql', 'A', 1)", (p_id,))
        s_id = cursor.lastrowid
        conn.commit()
        conn.close()

        with self.client.session_transaction() as sess:
            sess['participant_id'] = p_id
            sess['study_id'] = 'P999'
            sess['current_session_id'] = s_id
            sess['current_form'] = 'A'
            sess['highest_unlocked_task'] = 7  # writing tasks done

        # 1. Normal submission of C1 (full points)
        full_exp = [opt['id'] for opt in get_item('A', 'C1', randomize=False)['explanation']['options'] if opt['points'] == 2][0]
        corr_pred = [opt['id'] for opt in get_item('A', 'C1', randomize=False)['prediction']['options'] if opt['points'] == 1][0]
        
        resp = self.client.post('/experiment/comprehension/sql', data={
            'item_id': 'C1',
            'explanation_choice': full_exp,
            'prediction_choice': corr_pred,
            'response_time_seconds': '45.2',
            'timed_out': '0'
        })
        self.assertEqual(resp.status_code, 302)

        # 2. Timeout submission of C2 (no answers selected, timed_out=1)
        resp = self.client.post('/experiment/comprehension/sql', data={
            'item_id': 'C2',
            'explanation_choice': '',
            'prediction_choice': '',
            'response_time_seconds': '180.0',
            'timed_out': '1'
        })
        self.assertEqual(resp.status_code, 302)

        # Verify DB rows
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM comprehension_responses WHERE session_id = ? ORDER BY item_id ASC", (s_id,)).fetchall()
        
        self.assertEqual(len(rows), 2)
        
        # Row 1 (C1): study_id, session_id, item_id, language, form, explanation_score, prediction_score, response_time_seconds, timed_out
        r1 = dict(rows[0])
        self.assertEqual(r1['study_id'], 'P999')
        self.assertEqual(r1['item_id'], 'C1')
        self.assertEqual(r1['language'], 'sql')
        self.assertEqual(r1['form'], 'A')
        self.assertEqual(r1['explanation_score'], 2.0)
        self.assertEqual(r1['prediction_score'], 1.0)
        self.assertEqual(r1['response_time_seconds'], 45.2)
        self.assertEqual(r1['timed_out'], 0)

        # Row 2 (C2): timed out
        r2 = dict(rows[1])
        self.assertEqual(r2['item_id'], 'C2')
        self.assertEqual(r2['explanation_score'], 0.0)
        self.assertEqual(r2['prediction_score'], 0.0)
        self.assertEqual(r2['response_time_seconds'], 180.0)
        self.assertEqual(r2['timed_out'], 1)
        
        conn.close()

    def test_comprehension_csv_export(self):
        """Test that comprehension CSV export includes all per-item columns and values."""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO participants (study_id, program, year_level, status) VALUES ('P998', 'BSIT', 2, 'completed')")
        p_id = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form, sequence_order) VALUES (?, 'python', 'B', 1)", (p_id,))
        s_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO comprehension_responses
            (study_id, session_id, item_id, language, form, explanation_score, prediction_score, condition_score, response_time, response_time_seconds, timed_out, learner_answer)
            VALUES ('P998', ?, 'C1', 'python', 'B', 2.0, 1.0, 3.0, 32.5, 32.5, 0, 'exp:exp_b,pred:pred_b')
        """, (s_id,))
        conn.commit()
        conn.close()

        csv_str = export_comprehension_csv(self.test_db_path)
        lines = [l.strip() for l in csv_str.strip().split('\n') if l.strip()]
        headers = lines[0].split(',')
        
        required_headers = [
            'study_id', 'session_id', 'item_id', 'language', 'form',
            'explanation_score', 'prediction_score', 'total_score',
            'response_time_seconds', 'timed_out'
        ]
        for rh in required_headers:
            self.assertIn(rh, headers, f"Missing {rh} in export header: {headers}")

        # Check data row
        data_rows = [l for l in lines if 'P998' in l]
        self.assertTrue(len(data_rows) >= 1)
        self.assertIn('python', data_rows[0])
        self.assertIn('C1', data_rows[0])
        self.assertIn('3.0', data_rows[0])

    def test_dashboard_median_calculation_and_legacy_exclusion(self):
        """Test median out of 18 and verification that legacy or incomplete items are excluded."""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Clear existing data in isolated test DB so test runs independently
        cursor.execute("DELETE FROM comprehension_responses")
        cursor.execute("DELETE FROM sessions")
        cursor.execute("DELETE FROM participants")
        
        # 1. Participant A with legacy 3-item data (only 1 row with old item_id 'comp_sql')
        cursor.execute("INSERT INTO participants (study_id, status) VALUES ('P_OLD', 'completed')")
        p_old = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form) VALUES (?, 'sql', 'A')", (p_old,))
        s_old = cursor.lastrowid
        cursor.execute("""
            INSERT INTO comprehension_responses
            (study_id, session_id, item_id, language, form, explanation_score, prediction_score, condition_score, response_time, learner_answer)
            VALUES ('P_OLD', ?, 'comp_sql', 'sql', 'A', 1.0, 1.0, 2.0, 120.0, 'q1:b,q2:c,q3:b')
        """, (s_old,))

        # 2. Participant B with incomplete 6-item data (only 3 items done: C1, C2, C3)
        cursor.execute("INSERT INTO participants (study_id, status) VALUES ('P_INC', 'in_progress')")
        p_inc = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form) VALUES (?, 'sql', 'A')", (p_inc,))
        s_inc = cursor.lastrowid
        for c in ['C1', 'C2', 'C3']:
            cursor.execute("""
                INSERT INTO comprehension_responses
                (study_id, session_id, item_id, language, form, explanation_score, prediction_score, response_time_seconds, timed_out)
                VALUES ('P_INC', ?, ?, 'sql', 'A', 2.0, 1.0, 30.0, 0)
            """, (s_inc, c))

        # 3. Participant C with complete 6 items for SQL (scored: 3, 3, 3, 2, 2, 2 = 15 total)
        cursor.execute("INSERT INTO participants (study_id, status) VALUES ('P_FULL1', 'completed')")
        p_full1 = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form) VALUES (?, 'sql', 'A')", (p_full1,))
        s_full1 = cursor.lastrowid
        scores = [(2,1), (2,1), (2,1), (1,1), (1,1), (1,1)] # 15/18
        for i, (exp, pred) in enumerate(scores, 1):
            cursor.execute("""
                INSERT INTO comprehension_responses
                (study_id, session_id, item_id, language, form, explanation_score, prediction_score, response_time_seconds, timed_out)
                VALUES ('P_FULL1', ?, ?, 'sql', 'A', ?, ?, 25.0, 0)
            """, (s_full1, f"C{i}", exp, pred))

        # 4. Participant D with complete 6 items for SQL (scored: 3, 3, 3, 3, 3, 3 = 18 total)
        cursor.execute("INSERT INTO participants (study_id, status) VALUES ('P_FULL2', 'completed')")
        p_full2 = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form) VALUES (?, 'sql', 'A')", (p_full2,))
        s_full2 = cursor.lastrowid
        for i in range(1, 7):
            cursor.execute("""
                INSERT INTO comprehension_responses
                (study_id, session_id, item_id, language, form, explanation_score, prediction_score, response_time_seconds, timed_out)
                VALUES ('P_FULL2', ?, ?, 'sql', 'A', 2.0, 1.0, 20.0, 0)
            """, (s_full2, f"C{i}"))

        conn.commit()
        conn.close()

        # Login as researcher and check overview page
        with self.client.session_transaction() as sess:
            sess['is_researcher'] = True

        resp = self.client.get('/dashboard/')
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode('utf-8')

        # Check tile rendering
        self.assertIn("Median Comprehension Score", html)
        self.assertIn("Out of 18 pts (excludes legacy 3-item pilot data)", html)
        
        # Expected median of [15.0, 18.0] = 16.5
        self.assertIn("16.5 / 18", html)

    def test_full_condition_progression(self):
        """Test progressing through C1 to C6 and redirecting to survey."""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO participants (study_id, program, year_level, status) VALUES ('P997', 'BSCS', 2, 'in_progress')")
        p_id = cursor.lastrowid
        cursor.execute("INSERT INTO sessions (participant_id, language, form) VALUES (?, 'sql', 'A')", (p_id,))
        s_id = cursor.lastrowid
        conn.commit()
        conn.close()

        with self.client.session_transaction() as sess:
            sess['participant_id'] = p_id
            sess['study_id'] = 'P997'
            sess['current_session_id'] = s_id
            sess['current_form'] = 'A'
            sess['highest_unlocked_task'] = 7

        # Progress through all 6 items
        for i in range(1, 7):
            # Verify GET renders Item i
            get_resp = self.client.get('/experiment/comprehension/sql')
            self.assertEqual(get_resp.status_code, 200)
            self.assertIn(f"Item {i} of 6".encode('utf-8'), get_resp.data)

            # POST item i
            full_exp = [opt['id'] for opt in get_item('A', f"C{i}", randomize=False)['explanation']['options'] if opt['points'] == 2][0]
            corr_pred = [opt['id'] for opt in get_item('A', f"C{i}", randomize=False)['prediction']['options'] if opt['points'] == 1][0]
            
            post_resp = self.client.post('/experiment/comprehension/sql', data={
                'item_id': f"C{i}",
                'explanation_choice': full_exp,
                'prediction_choice': corr_pred,
                'response_time_seconds': '15.0',
                'timed_out': '0'
            })
            
            if i < 6:
                # Should redirect back to comprehension (item i+1)
                self.assertEqual(post_resp.status_code, 302)
                self.assertIn('/experiment/comprehension/sql', post_resp.headers['Location'])
            else:
                # Last item C6 should redirect to survey!
                self.assertEqual(post_resp.status_code, 302)
                self.assertIn('/experiment/survey/sql', post_resp.headers['Location'])


if __name__ == '__main__':
    unittest.main()
