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
        enrollments = [
            (1, 'C101', 90.0), (1, 'C102', 85.0), (2, 'C101', 88.0), (3, 'C103', None),
            (4, 'C101', 95.0), (5, 'C101', 95.0), (6, 'C102', 70.0), (7, 'C104', 80.0),
            (9, 'C101', 75.0), (10, 'C105', 92.0), (11, 'C101', 95.0), (12, 'C101', 82.0),
            (13, 'C102', 88.0), (14, 'C103', None), (15, 'C101', 60.0), (16, 'C101', 95.0),
            (19, 'C101', 88.0)
            # Some students have no enrollments
        ]
    elif form == 'B':
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
        enrollments = [
            (101, 'C102', 92.0), (101, 'C103', 85.0), (102, 'C102', 88.0), (103, 'C104', None),
            (104, 'C102', 95.0), (105, 'C102', 95.0), (106, 'C101', 70.0), (107, 'C102', 80.0),
            (109, 'C102', 75.0), (110, 'C105', 92.0), (111, 'C102', 95.0), (112, 'C102', 82.0),
            (113, 'C103', 88.0), (114, 'C104', None), (115, 'C102', 60.0), (116, 'C102', 95.0),
            (119, 'C102', 88.0)
            # Some students have no enrollments
        ]
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
