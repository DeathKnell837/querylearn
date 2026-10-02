"""
Task catalog containing complete specifications for Forms A and B (Tasks T1 to T6).
Matches the case study specification from Appendix A of the research paper.
"""

TASK_CATALOG = {
    "A": {
        "1": {
            "id": "T1",
            "title": "Selection and Filtering",
            "concept": "Basic selection and filtering using WHERE clause",
            "instruction": "Display the ID and name of all first-year BSCS students. Arrange the result by student ID in ascending order.",
            "requirements": [
                "Select columns: student_id, student_name",
                "Filter condition: program = 'BSCS' and year_level = 1",
                "Order by: student_id ascending"
            ],
            "sql_starter": "-- Task 1: Select BSCS 1st Year Students\nSELECT student_id, student_name\nFROM Students\nWHERE program = 'BSCS' AND year_level = 1\nORDER BY student_id;",
            "python_starter": "# Task 1: Procedural Python\n# Available lists of dicts: students, courses, enrollments\nresult = []\nfor student in students:\n    if student['program'] == 'BSCS' and student['year_level'] == 1:\n        result.append((student['student_id'], student['student_name']))\n\nresult.sort(key=lambda row: row[0])\nprint(result)",
            "expected_columns": ["student_id", "student_name"],
            "oracle_sql": "SELECT student_id, student_name FROM Students WHERE program = 'BSCS' AND year_level = 1 ORDER BY student_id;"
        },
        "2": {
            "id": "T2",
            "title": "Filtering, Sorting, and Limiting",
            "concept": "Filtering with NULL checks, multiple sort keys, and row limits",
            "instruction": "Find the top 3 highest non-missing scores in course 'C101'. Display the student ID and score. Sort by score descending, then by student ID ascending for ties.",
            "requirements": [
                "Select columns: student_id, score",
                "Filter condition: course_id = 'C101' and score IS NOT NULL",
                "Sort order: score DESC, then student_id ASC",
                "Limit result to top 3 rows"
            ],
            "sql_starter": "-- Task 2: Top 3 Scores in C101\nSELECT student_id, score\nFROM Enrollments\nWHERE course_id = 'C101' AND score IS NOT NULL\nORDER BY score DESC, student_id ASC\nLIMIT 3;",
            "python_starter": "# Task 2: Top 3 non-missing scores for C101\nresult = []\nfor e in enrollments:\n    if e['course_id'] == 'C101' and e['score'] is not None:\n        result.append((e['student_id'], float(e['score'])))\n\n# Sort by score descending, then student_id ascending\nresult.sort(key=lambda x: (-x[1], x[0]))\nresult = result[:3]\nprint(result)",
            "expected_columns": ["student_id", "score"],
            "oracle_sql": "SELECT student_id, score FROM Enrollments WHERE course_id = 'C101' AND score IS NOT NULL ORDER BY score DESC, student_id ASC LIMIT 3;"
        },
        "3": {
            "id": "T3",
            "title": "Grouping and Counting",
            "concept": "Aggregate functions with GROUP BY and sorting",
            "instruction": "Count the total number of students enrolled in each academic program. Display the program name and the student count. Sort alphabetically by program name.",
            "requirements": [
                "Select columns: program, student_count",
                "Group by: program",
                "Order by: program ASC"
            ],
            "sql_starter": "-- Task 3: Count Students by Program\nSELECT program, COUNT(*) AS student_count\nFROM Students\nGROUP BY program\nORDER BY program ASC;",
            "python_starter": "# Task 3: Count students per program\ncounts = {}\nfor s in students:\n    prog = s['program']\n    counts[prog] = counts.get(prog, 0) + 1\n\nresult = [(k, v) for k, v in counts.items()]\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["program", "student_count"],
            "oracle_sql": "SELECT program, COUNT(*) AS student_count FROM Students GROUP BY program ORDER BY program ASC;"
        },
        "4": {
            "id": "T4",
            "title": "Joining Tables",
            "concept": "Relational INNER JOIN across multiple related tables",
            "instruction": "Display the student ID, student name, and course name for all students enrolled in course 'C101'. Sort the results by student ID ascending.",
            "requirements": [
                "Select columns: student_id, student_name, course_name",
                "Join: Students, Enrollments, and Courses",
                "Filter condition: course_id = 'C101'",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 4: Multi-table JOIN for C101\nSELECT s.student_id, s.student_name, c.course_name\nFROM Students s\nJOIN Enrollments e ON s.student_id = e.student_id\nJOIN Courses c ON e.course_id = c.course_id\nWHERE e.course_id = 'C101'\nORDER BY s.student_id ASC;",
            "python_starter": "# Task 4: Multi-entity Join\ncourse_map = {c['course_id']: c['course_name'] for c in courses}\nstudent_map = {s['student_id']: s['student_name'] for s in students}\n\nresult = []\nfor e in enrollments:\n    if e['course_id'] == 'C101' and e['student_id'] in student_map:\n        s_id = e['student_id']\n        result.append((s_id, student_map[s_id], course_map.get(e['course_id'], '')))\n\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["student_id", "student_name", "course_name"],
            "oracle_sql": "SELECT s.student_id, s.student_name, c.course_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON e.course_id = c.course_id WHERE e.course_id = 'C101' ORDER BY s.student_id ASC;"
        },
        "5": {
            "id": "T5",
            "title": "Aggregation and HAVING",
            "concept": "Grouped aggregates filtered with HAVING clause",
            "instruction": "Calculate the average non-missing score for each course. Keep only courses where the average score is 80.0 or higher. Display course_id and average score rounded to 2 decimals. Sort by course_id ascending.",
            "requirements": [
                "Select columns: course_id, avg_score",
                "Group by: course_id",
                "Filter group: average score >= 80.0 (excluding NULLs)",
                "Order by: course_id ASC"
            ],
            "sql_starter": "-- Task 5: Grouped Average with HAVING\nSELECT course_id, ROUND(AVG(score), 2) AS avg_score\nFROM Enrollments\nWHERE score IS NOT NULL\nGROUP BY course_id\nHAVING AVG(score) >= 80.0\nORDER BY course_id ASC;",
            "python_starter": "# Task 5: Aggregation with group threshold (>= 80.0)\ngroups = {}\nfor e in enrollments:\n    if e['score'] is not None:\n        c_id = e['course_id']\n        groups.setdefault(c_id, []).append(float(e['score']))\n\nresult = []\nfor c_id, scores in groups.items():\n    avg_val = sum(scores) / len(scores)\n    if avg_val >= 80.0:\n        result.append((c_id, round(avg_val, 2)))\n\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["course_id", "avg_score"],
            "oracle_sql": "SELECT course_id, ROUND(AVG(score), 2) AS avg_score FROM Enrollments WHERE score IS NOT NULL GROUP BY course_id HAVING AVG(score) >= 80.0 ORDER BY course_id ASC;"
        },
        "6": {
            "id": "T6",
            "title": "Finding Records Without Matches (Anti-Join)",
            "concept": "LEFT JOIN with NULL check or NOT IN subquery",
            "instruction": "Find all students who are currently NOT enrolled in any course. Display their student ID and student name. Sort by student ID ascending.",
            "requirements": [
                "Select columns: student_id, student_name",
                "Anti-join: Students with zero records in Enrollments",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students)\nSELECT s.student_id, s.student_name\nFROM Students s\nLEFT JOIN Enrollments e ON s.student_id = e.student_id\nWHERE e.student_id IS NULL\nORDER BY s.student_id ASC;",
            "python_starter": "# Task 6: Find students without enrollments\nenrolled_ids = {e['student_id'] for e in enrollments}\nresult = []\nfor s in students:\n    if s['student_id'] not in enrolled_ids:\n        result.append((s['student_id'], s['student_name']))\n\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["student_id", "student_name"],
            "oracle_sql": "SELECT s.student_id, s.student_name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.student_id IS NULL ORDER BY s.student_id ASC;"
        }
    },
    "B": {
        "1": {
            "id": "T1",
            "title": "Selection and Filtering",
            "concept": "Basic selection and filtering using WHERE clause",
            "instruction": "Display the ID and name of all second-year BSIT students. Arrange the result by student ID in ascending order.",
            "requirements": [
                "Select columns: student_id, student_name",
                "Filter condition: program = 'BSIT' and year_level = 2",
                "Order by: student_id ascending"
            ],
            "sql_starter": "-- Task 1: Select BSIT 2nd Year Students\nSELECT student_id, student_name\nFROM Students\nWHERE program = 'BSIT' AND year_level = 2\nORDER BY student_id;",
            "python_starter": "# Task 1: Procedural Python\nresult = []\nfor student in students:\n    if student['program'] == 'BSIT' and student['year_level'] == 2:\n        result.append((student['student_id'], student['student_name']))\n\nresult.sort(key=lambda row: row[0])\nprint(result)",
            "expected_columns": ["student_id", "student_name"],
            "oracle_sql": "SELECT student_id, student_name FROM Students WHERE program = 'BSIT' AND year_level = 2 ORDER BY student_id;"
        },
        "2": {
            "id": "T2",
            "title": "Filtering, Sorting, and Limiting",
            "concept": "Filtering with NULL checks, multiple sort keys, and row limits",
            "instruction": "Find the top 3 highest non-missing scores in course 'C102'. Display the student ID and score. Sort by score descending, then by student ID ascending for ties.",
            "requirements": [
                "Select columns: student_id, score",
                "Filter condition: course_id = 'C102' and score IS NOT NULL",
                "Sort order: score DESC, then student_id ASC",
                "Limit result to top 3 rows"
            ],
            "sql_starter": "-- Task 2: Top 3 Scores in C102\nSELECT student_id, score\nFROM Enrollments\nWHERE course_id = 'C102' AND score IS NOT NULL\nORDER BY score DESC, student_id ASC\nLIMIT 3;",
            "python_starter": "# Task 2: Top 3 non-missing scores for C102\nresult = []\nfor e in enrollments:\n    if e['course_id'] == 'C102' and e['score'] is not None:\n        result.append((e['student_id'], float(e['score'])))\n\nresult.sort(key=lambda x: (-x[1], x[0]))\nresult = result[:3]\nprint(result)",
            "expected_columns": ["student_id", "score"],
            "oracle_sql": "SELECT student_id, score FROM Enrollments WHERE course_id = 'C102' AND score IS NOT NULL ORDER BY score DESC, student_id ASC LIMIT 3;"
        },
        "3": {
            "id": "T3",
            "title": "Grouping and Counting",
            "concept": "Aggregate functions with GROUP BY and sorting",
            "instruction": "Count the total number of students enrolled in each academic program in Form B records. Display program name and count. Sort alphabetically by program name.",
            "requirements": [
                "Select columns: program, student_count",
                "Group by: program",
                "Order by: program ASC"
            ],
            "sql_starter": "-- Task 3: Count Students by Program (Form B)\nSELECT program, COUNT(*) AS student_count\nFROM Students\nGROUP BY program\nORDER BY program ASC;",
            "python_starter": "# Task 3: Count students per program\ncounts = {}\nfor s in students:\n    prog = s['program']\n    counts[prog] = counts.get(prog, 0) + 1\n\nresult = [(k, v) for k, v in counts.items()]\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["program", "student_count"],
            "oracle_sql": "SELECT program, COUNT(*) AS student_count FROM Students GROUP BY program ORDER BY program ASC;"
        },
        "4": {
            "id": "T4",
            "title": "Joining Tables",
            "concept": "Relational INNER JOIN across multiple related tables",
            "instruction": "Display student ID, student name, and course name for all enrollments in course 'C102'. Sort the result by student ID ascending.",
            "requirements": [
                "Select columns: student_id, student_name, course_name",
                "Join: Students, Enrollments, and Courses",
                "Filter condition: course_id = 'C102'",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 4: Multi-table JOIN for C102\nSELECT s.student_id, s.student_name, c.course_name\nFROM Students s\nJOIN Enrollments e ON s.student_id = e.student_id\nJOIN Courses c ON e.course_id = c.course_id\nWHERE e.course_id = 'C102'\nORDER BY s.student_id ASC;",
            "python_starter": "# Task 4: Multi-entity Join\ncourse_map = {c['course_id']: c['course_name'] for c in courses}\nstudent_map = {s['student_id']: s['student_name'] for s in students}\n\nresult = []\nfor e in enrollments:\n    if e['course_id'] == 'C102' and e['student_id'] in student_map:\n        s_id = e['student_id']\n        result.append((s_id, student_map[s_id], course_map.get(e['course_id'], '')))\n\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["student_id", "student_name", "course_name"],
            "oracle_sql": "SELECT s.student_id, s.student_name, c.course_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON e.course_id = c.course_id WHERE e.course_id = 'C102' ORDER BY s.student_id ASC;"
        },
        "5": {
            "id": "T5",
            "title": "Aggregation and HAVING",
            "concept": "Grouped aggregates filtered with HAVING threshold >= 85",
            "instruction": "Calculate the average non-missing score for each course. Retain only courses where the average score is 85.0 or higher. Display course_id and average score rounded to 2 decimals. Sort by course_id ascending.",
            "requirements": [
                "Select columns: course_id, avg_score",
                "Group by: course_id",
                "Filter group: average score >= 85.0 (excluding NULLs)",
                "Order by: course_id ASC"
            ],
            "sql_starter": "-- Task 5: Grouped Average with HAVING (Threshold >= 85.0)\nSELECT course_id, ROUND(AVG(score), 2) AS avg_score\nFROM Enrollments\nWHERE score IS NOT NULL\nGROUP BY course_id\nHAVING AVG(score) >= 85.0\nORDER BY course_id ASC;",
            "python_starter": "# Task 5: Aggregation with group threshold (>= 85.0)\ngroups = {}\nfor e in enrollments:\n    if e['score'] is not None:\n        c_id = e['course_id']\n        groups.setdefault(c_id, []).append(float(e['score']))\n\nresult = []\nfor c_id, scores in groups.items():\n    avg_val = sum(scores) / len(scores)\n    if avg_val >= 85.0:\n        result.append((c_id, round(avg_val, 2)))\n\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["course_id", "avg_score"],
            "oracle_sql": "SELECT course_id, ROUND(AVG(score), 2) AS avg_score FROM Enrollments WHERE score IS NOT NULL GROUP BY course_id HAVING AVG(score) >= 85.0 ORDER BY course_id ASC;"
        },
        "6": {
            "id": "T6",
            "title": "Finding Records Without Matches (Anti-Join)",
            "concept": "Anti-join on Form B records",
            "instruction": "Find all students who have zero enrollments in Form B records. Display student ID and student name. Sort by student ID ascending.",
            "requirements": [
                "Select columns: student_id, student_name",
                "Anti-join: Students with no match in Enrollments",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students)\nSELECT s.student_id, s.student_name\nFROM Students s\nLEFT JOIN Enrollments e ON s.student_id = e.student_id\nWHERE e.student_id IS NULL\nORDER BY s.student_id ASC;",
            "python_starter": "# Task 6: Find students without enrollments\nenrolled_ids = {e['student_id'] for e in enrollments}\nresult = []\nfor s in students:\n    if s['student_id'] not in enrolled_ids:\n        result.append((s['student_id'], s['student_name']))\n\nresult.sort(key=lambda x: x[0])\nprint(result)",
            "expected_columns": ["student_id", "student_name"],
            "oracle_sql": "SELECT s.student_id, s.student_name FROM Students s LEFT JOIN Enrollments e ON s.student_id = e.student_id WHERE e.student_id IS NULL ORDER BY s.student_id ASC;"
        }
    }
}

SCHEMA_METADATA = [
    {
        "table": "Students",
        "description": "Learner demographic and enrollment records",
        "columns": [
            {"name": "student_id", "type": "INTEGER", "pk": True},
            {"name": "student_name", "type": "TEXT", "pk": False},
            {"name": "program", "type": "TEXT", "pk": False},
            {"name": "year_level", "type": "INTEGER", "pk": False}
        ]
    },
    {
        "table": "Courses",
        "description": "Academic course offerings catalog",
        "columns": [
            {"name": "course_id", "type": "TEXT", "pk": True},
            {"name": "course_name", "type": "TEXT", "pk": False}
        ]
    },
    {
        "table": "Enrollments",
        "description": "Student course registrations and grades",
        "columns": [
            {"name": "student_id", "type": "INTEGER", "pk": True, "fk": "Students.student_id"},
            {"name": "course_id", "type": "TEXT", "pk": True, "fk": "Courses.course_id"},
            {"name": "score", "type": "REAL", "pk": False}
        ]
    }
]

def get_task(form, task_id):
    form = form.upper() if form else "A"
    clean_id = str(task_id).upper().replace("T", "").strip()
    return TASK_CATALOG.get(form, {}).get(clean_id)
