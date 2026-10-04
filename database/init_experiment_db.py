import sqlite3
import os

def init_experiment_db(db_path, form):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE Students (
        student_id INTEGER PRIMARY KEY,
        student_name TEXT,
        program TEXT,
        year_level INTEGER
    );

    CREATE TABLE Courses (
        course_id TEXT PRIMARY KEY,
        course_name TEXT
    );

    CREATE TABLE Enrollments (
        student_id INTEGER,
        course_id TEXT,
        score REAL,
        PRIMARY KEY (student_id, course_id),
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id)
    );
    """)

    if form == 'A':
        # --- FORM A ---
        students = [
            (1, 'Alice Smith', 'BSCS', 1), (2, 'Bob Johnson', 'BSIT', 2), (3, 'Charlie Brown', 'BSIS', 3),
            (4, 'David Lee', 'BSCS', 1), (5, 'Eve Davis', 'BSCS', 1), (6, 'Frank White', 'BSIT', 1),
            (7, 'Grace Hall', 'BSCS', 2), (8, 'Heidi Moore', 'BSIS', 1), (9, 'Ivan Clark', 'BSCS', 1),
            (10, 'Judy Lewis', 'BSIT', 2), (11, 'Kevin Walker', 'BSCS', 1), (12, 'Laura Perez', 'BSCS', 1),
            (13, 'Mallory Scott', 'BSCS', 1), (14, 'Niaj Rivera', 'BSIT', 2), (15, 'Oscar Torres', 'BSIS', 1),
            (16, 'Peggy Flores', 'BSCS', 3), (17, 'Quentin Gomez', 'BSCS', 1), (18, 'Romeo Reed', 'BSIT', 1),
            (19, 'Sybil Cook', 'BSCS', 1), (20, 'Trent Bell', 'BSIS', 2)
        ]
        courses = [
            ('C101', 'Intro to Programming'), ('C102', 'Data Structures'),
            ('C103', 'Database Systems'), ('C104', 'Software Engineering'), ('C105', 'Web Development')
        ]
        # Task 5 fix: C101 avg(non-null) = (90+88+95+95+75+95+82+60+95+88)/10 = 86.3 => passes >=80
        # C102: scores 85, 70, 88 => avg 81.0 => passes >=80
        # C103: score NULL, NULL => no non-null => excluded
        # C104: score 80 => avg 80.0 => passes >=80
        # C105: scores 92, 72 => avg 82.0 => passes >=80
        # Need one course averaging 70.0-79.9: Add C105 with 72 so avg = (92+72)/2 = 82 — too high.
        # Better: make C102 have avg in 70-79.9 range.
        # C102: 85.0, 70.0, 88.0, 65.0 → avg = 77.0 — in range!
        # Also add NULL scores to C102 so that treating NULL as 0 changes whether it passes >=80.
        # C102 with NULLs: if null=0 → (85+70+88+65+0)/5 = 61.6 (fails). If nulls excluded → 77.0 (still fails >=80 but passes the 70-79.9 check)
        # Actually we need it to still appear in results: the course has avg 77.0 which is below threshold 80.
        # Wait - re-read the requirement: "at least one course has an average between 70.0 and 79.9"
        # This means the avg should be in that range. The HAVING threshold is >=80 so this course gets excluded.
        # That's fine — it tests that the threshold works correctly.
        # But we need NULLs that change whether courses pass: if you avg NULL as 0, a course that should pass might fail.
        # Let's adjust: C105 avg(non-null) = 92 => passes. Add a NULL score. If null=0 → avg=(92+0)/2=46 → fails.
        # C104 avg(non-null) = 80.0 => passes >=80. Add NULL. If null=0 → avg=(80+0)/2=40 → fails.
        enrollments = [
            # C101 enrollments (avg = 86.3, passes >=80)
            (1, 'C101', 90.0), (2, 'C101', 88.0), (4, 'C101', 95.0), (5, 'C101', 95.0),
            (9, 'C101', 75.0), (11, 'C101', 95.0), (12, 'C101', 82.0), (15, 'C101', 60.0),
            (16, 'C101', 95.0), (19, 'C101', 88.0),
            # C102 enrollments (avg non-null = 77.0 → in 70-79.9 range, fails HAVING >=80)
            (1, 'C102', 85.0), (6, 'C102', 70.0), (13, 'C102', 88.0), (15, 'C102', 65.0),
            (7, 'C102', None),  # NULL score — if treated as 0, avg drops drastically
            # C103 enrollments (all NULLs → excluded from T5)
            (3, 'C103', None), (14, 'C103', None),
            # C104 enrollments (avg non-null = 80.0, passes >=80; NULL would break if counted as 0)
            (7, 'C104', 80.0), (10, 'C104', None),
            # C105 enrollments (avg non-null = 92.0, passes >=80; NULL would break if counted as 0)
            (10, 'C105', 92.0), (20, 'C105', None),
        ]
        # Task 5 oracle results with threshold >=80:
        # C101: avg=86.3 ✓, C104: avg=80.0 ✓, C105: avg=92.0 ✓
        # C102: avg=77.0 ✗ (in 70-79.9 range — tests correct threshold)
        # C103: no non-null scores — excluded

    elif form == 'B':
        # --- FORM B ---
        students = [
            (101, 'Zane Adams', 'BSIT', 2), (102, 'Yara Baker', 'BSCS', 1), (103, 'Xander Cruz', 'BSIS', 3),
            (104, 'Will Diaz', 'BSIT', 2), (105, 'Vera Evans', 'BSIT', 2), (106, 'Umar Foster', 'BSCS', 2),
            (107, 'Tara Gray', 'BSIT', 2), (108, 'Sara Hayes', 'BSIS', 2), (109, 'Rick Ibarra', 'BSIT', 2),
            (110, 'Quincy Jenkins', 'BSCS', 1), (111, 'Paul King', 'BSIT', 2), (112, 'Olivia Lopez', 'BSIT', 2),
            (113, 'Noah Miller', 'BSIT', 2), (114, 'Mia Nelson', 'BSCS', 3), (115, 'Liam Ortiz', 'BSIS', 2),
            (116, 'Kira Patel', 'BSIT', 2), (117, 'Jack Quinn', 'BSIT', 2), (118, 'Isla Ross', 'BSCS', 1),
            (119, 'Harry Smith', 'BSIT', 2), (120, 'Gia Taylor', 'BSIS', 1)
        ]
        courses = [
            ('C101', 'Intro to Programming'), ('C102', 'Data Structures'),
            ('C103', 'Database Systems'), ('C104', 'Software Engineering'), ('C105', 'Web Development')
        ]
        # Task 5 fix: threshold is >=85 for Form B
        # C102 avg(non-null): want some courses in 75-84.9 range
        # C102: 92, 88, 95, 95, 75, 95, 82, 60, 95, 88 => avg = 86.5 → passes >=85
        # C101: 70 → avg = 70.0 → fails
        # C103: 88, NULL → avg = 88.0 → passes
        # C104: NULL → excluded
        # C105: 92, 78 → avg = 85.0 → passes (borderline)
        # Need one course averaging 75.0-84.9: C101 avg = (70 + 90)/2 = 80.0 → in range, fails >=85
        enrollments = [
            # C102 enrollments (avg non-null = 86.5, passes >=85)
            (101, 'C102', 92.0), (102, 'C102', 88.0), (104, 'C102', 95.0), (105, 'C102', 95.0),
            (109, 'C102', 75.0), (111, 'C102', 95.0), (112, 'C102', 82.0), (115, 'C102', 60.0),
            (116, 'C102', 95.0), (119, 'C102', 88.0),
            # C101 enrollments (avg non-null = 80.0, in 75-84.9 range, fails HAVING >=85)
            (106, 'C101', 70.0), (110, 'C101', 90.0),
            (120, 'C101', None),  # NULL — if treated as 0, avg drops
            # C103 enrollments (avg non-null = 88.0, passes >=85; NULL would break)
            (113, 'C103', 88.0), (103, 'C103', None), (114, 'C103', None),
            # C104 enrollments (all NULLs → excluded)
            (103, 'C104', None), (114, 'C104', None),
            # C105 enrollments (avg non-null = 85.0, passes >=85; NULL would break)
            (110, 'C105', 92.0), (108, 'C105', 78.0), (107, 'C105', None),
        ]
        # Task 5 oracle results with threshold >=85:
        # C102: avg=86.5 ✓, C103: avg=88.0 ✓, C105: avg=85.0 ✓
        # C101: avg=80.0 ✗ (in 75-84.9 range — tests correct threshold)
        # C104: no non-null → excluded
    else:
        raise ValueError("Form must be 'A' or 'B'")

    cursor.executemany("INSERT INTO Students (student_id, student_name, program, year_level) VALUES (?, ?, ?, ?)", students)
    cursor.executemany("INSERT INTO Courses (course_id, course_name) VALUES (?, ?)", courses)
    cursor.executemany("INSERT INTO Enrollments (student_id, course_id, score) VALUES (?, ?, ?)", enrollments)

    conn.commit()
    conn.close()
    print(f"Experiment DB ({form}) initialized at {db_path}")

if __name__ == "__main__":
    db_dir = os.path.dirname(__file__)
    init_experiment_db(os.path.join(db_dir, "experiment_a.db"), 'A')
    init_experiment_db(os.path.join(db_dir, "experiment_b.db"), 'B')
