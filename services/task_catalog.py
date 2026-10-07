"""
Task catalog containing complete specifications for Forms A and B (Tasks T1 to T6).
Matches the case study specification from Appendix A of the research paper.
Provides scaffolded, half-filled debugging starters designed for novice/beginner learners.
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
            "sql_starter": "-- Task 1: Select BSCS 1st Year Students\n-- Complete the filter condition below (fill in program and year_level):\n\nSELECT student_id, student_name\nFROM Students\nWHERE program = '' AND year_level = 0\nORDER BY student_id ASC;\n",
            "python_starter": "# Task 1: Select BSCS 1st Year Students\n# Complete the filter condition below (fill in program and year_level):\nresult = []\n\nfor s in students:\n    # Change '' to 'BSCS' and 0 to 1\n    if s['program'] == '' and s['year_level'] == 0:\n        result.append((s['student_id'], s['student_name']))\n\n# Sort by student_id ascending\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
            "expected_columns": ["student_id", "student_name"],
            "oracle_sql": "SELECT student_id, student_name FROM Students WHERE program = 'BSCS' AND year_level = 1 ORDER BY student_id;"
        },
        "2": {
            "id": "T2",
            "title": "Filtering, Sorting, and Limiting",
            "concept": "Filtering with NULL checks, multiple sort keys, and row limits",
            "instruction": "Find the top 3 highest scores (ignore empty scores) in course 'C101'. Display the student ID and score. Sort by score descending, then by student ID ascending for ties.",
            "requirements": [
                "Select columns: student_id, score",
                "Filter condition: course_id = 'C101' and score is not empty",
                "Sort order: score highest first, then student_id lowest first",
                "Keep only the first 3 rows"
            ],
            "sql_starter": "-- Task 2: Top 3 Scores in C101\n-- Complete the query below (set the LIMIT to the requested number of rows):\n\nSELECT student_id, score\nFROM Enrollments\nWHERE course_id = 'C101' AND score IS NOT NULL\nORDER BY score DESC, student_id ASC\nLIMIT 0;\n",
            "python_starter": "# Task 2: Top 3 non-missing scores for C101\n# Complete the row limit slice below (change 0 to the requested limit):\nresult = []\n\nfor e in enrollments:\n    # Keep course C101 with valid scores\n    if e['course_id'] == 'C101' and e['score'] is not None:\n        result.append((e['student_id'], e['score']))\n\n# Sort: highest score first, tie-break by student_id ascending\nresult.sort(key=lambda x: (-x[1], x[0]))\n\n# Keep top 3 items (change 0 to 3)\nresult = result[:0]\n\nprint(result)",
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
            "sql_starter": "-- Task 3: Count Students by Program\n-- Complete the GROUP BY column below:\n\nSELECT program, COUNT(*) AS student_count\nFROM Students\nGROUP BY program\nORDER BY program ASC;\n",
            "python_starter": "# Task 3: Count students per program\n# Complete the counting logic below (change 0 to 1):\ncounts = {}\n\nfor s in students:\n    prog = s['program']\n    # Add 1 to the count for this program (change 0 to 1)\n    counts[prog] = counts.get(prog, 0) + 0\n\n# Convert to list of tuples: (program, student_count)\nresult = [(prog, count) for prog, count in counts.items()]\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
                "Use all three: Students, Enrollments, and Courses",
                "Filter condition: course_id = 'C101'",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 4: Multi-table JOIN for C101\n-- Complete the course filter below (fill in 'C101'):\n\nSELECT s.student_id, s.student_name, c.course_name\nFROM Students s\nJOIN Enrollments e ON s.student_id = e.student_id\nJOIN Courses c ON e.course_id = c.course_id\nWHERE e.course_id = ''\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 4: Multi-entity Join for C101\n# Complete the course filter below (change '' to 'C101'):\nresult = []\n\nstudent_names = {s['student_id']: s['student_name'] for s in students}\ncourse_names = {c['course_id']: c['course_name'] for c in courses}\n\nfor e in enrollments:\n    # Filter for course C101\n    if e['course_id'] == '':\n        s_id = e['student_id']\n        s_name = student_names.get(s_id)\n        c_name = course_names.get(e['course_id'])\n        result.append((s_id, s_name, c_name))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
            "expected_columns": ["student_id", "student_name", "course_name"],
            "oracle_sql": "SELECT s.student_id, s.student_name, c.course_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON e.course_id = c.course_id WHERE e.course_id = 'C101' ORDER BY s.student_id ASC;"
        },
        "5": {
            "id": "T5",
            "title": "Average per Group",
            "concept": "Grouped aggregates filtered with HAVING clause",
            "instruction": "Calculate the average score for each course (ignore empty scores). Keep only courses where the average score is 80.0 or higher. Display course_id and average score rounded to 2 decimals. Sort by course_id ascending.",
            "requirements": [
                "Select columns: course_id, avg_score",
                "Group by: course_id",
                "Keep only groups where the average score is 80.0 or higher (ignore empty scores)",
                "Order by: course_id ASC"
            ],
            "sql_starter": "-- Task 5: Grouped Average with HAVING\n-- Complete the HAVING threshold below (change 0.0 to 80.0):\n\nSELECT course_id, ROUND(AVG(score), 2) AS avg_score\nFROM Enrollments\nWHERE score IS NOT NULL\nGROUP BY course_id\nHAVING AVG(score) >= 0.0\nORDER BY course_id ASC;\n",
            "python_starter": "# Task 5: Grouped average score >= 80.0\n# Complete the threshold check below (change 0.0 to 80.0):\nscores_by_course = {}\n\nfor e in enrollments:\n    if e['score'] is not None:\n        c_id = e['course_id']\n        scores_by_course.setdefault(c_id, []).append(e['score'])\n\nresult = []\nfor c_id, score_list in scores_by_course.items():\n    avg_score = round(sum(score_list) / len(score_list), 2)\n    # Keep courses with average score >= 80.0 (change 0.0 to 80.0)\n    if avg_score >= 0.0:\n        result.append((c_id, avg_score))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
            "expected_columns": ["course_id", "avg_score"],
            "oracle_sql": "SELECT course_id, ROUND(AVG(score), 2) AS avg_score FROM Enrollments WHERE score IS NOT NULL GROUP BY course_id HAVING AVG(score) >= 80.0 ORDER BY course_id ASC;"
        },
        "6": {
            "id": "T6",
            "title": "Finding Records With No Match",
            "concept": "LEFT JOIN with NULL check or NOT IN subquery",
            "instruction": "Find all students who are not enrolled in any course. Display their student ID and student name. Sort by student ID ascending.",
            "requirements": [
                "Select columns: student_id, student_name",
                "Only students who have no row in Enrollments",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students)\n-- Debug the WHERE condition below (change IS NOT NULL to IS NULL):\n\nSELECT s.student_id, s.student_name\nFROM Students s\nLEFT JOIN Enrollments e ON s.student_id = e.student_id\nWHERE e.student_id IS NOT NULL\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 6: Find students without enrollments\n-- Debug the condition below (change 'in' to 'not in'):\nenrolled_ids = {e['student_id'] for e in enrollments}\n\nresult = []\nfor s in students:\n    # Change 'in' to 'not in' to find students without enrollments\n    if s['student_id'] in enrolled_ids:\n        result.append((s['student_id'], s['student_name']))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 1: Select BSIT 2nd Year Students (Form B)\n-- Complete the filter condition below (fill in program and year_level):\n\nSELECT student_id, student_name\nFROM Students\nWHERE program = '' AND year_level = 0\nORDER BY student_id ASC;\n",
            "python_starter": "# Task 1: Select BSIT 2nd Year Students (Form B)\n# Complete the filter condition below (fill in program and year_level):\nresult = []\n\nfor s in students:\n    # Change '' to 'BSIT' and 0 to 2\n    if s['program'] == '' and s['year_level'] == 0:\n        result.append((s['student_id'], s['student_name']))\n\n# Sort by student_id ascending\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
            "expected_columns": ["student_id", "student_name"],
            "oracle_sql": "SELECT student_id, student_name FROM Students WHERE program = 'BSIT' AND year_level = 2 ORDER BY student_id;"
        },
        "2": {
            "id": "T2",
            "title": "Filtering, Sorting, and Limiting",
            "concept": "Filtering with NULL checks, multiple sort keys, and row limits",
            "instruction": "Find the top 3 highest scores (ignore empty scores) in course 'C102'. Display the student ID and score. Sort by score descending, then by student ID ascending for ties.",
            "requirements": [
                "Select columns: student_id, score",
                "Filter condition: course_id = 'C102' and score is not empty",
                "Sort order: score highest first, then student_id lowest first",
                "Keep only the first 3 rows"
            ],
            "sql_starter": "-- Task 2: Top 3 Scores in C102 (Form B)\n-- Complete the query below (set the LIMIT to the requested number of rows):\n\nSELECT student_id, score\nFROM Enrollments\nWHERE course_id = 'C102' AND score IS NOT NULL\nORDER BY score DESC, student_id ASC\nLIMIT 0;\n",
            "python_starter": "# Task 2: Top 3 non-missing scores for C102 (Form B)\n# Complete the row limit slice below (change 0 to the requested limit):\nresult = []\n\nfor e in enrollments:\n    # Keep course C102 with valid scores\n    if e['course_id'] == 'C102' and e['score'] is not None:\n        result.append((e['student_id'], e['score']))\n\n# Sort: highest score first, tie-break by student_id ascending\nresult.sort(key=lambda x: (-x[1], x[0]))\n\n# Keep top 3 items (change 0 to 3)\nresult = result[:0]\n\nprint(result)",
            "expected_columns": ["student_id", "score"],
            "oracle_sql": "SELECT student_id, score FROM Enrollments WHERE course_id = 'C102' AND score IS NOT NULL ORDER BY score DESC, student_id ASC LIMIT 3;"
        },
        "3": {
            "id": "T3",
            "title": "Grouping and Counting",
            "concept": "Aggregate functions with GROUP BY and sorting",
            "instruction": "Count the total number of students enrolled in each academic program. Display the program name and the count. Sort alphabetically by program name.",
            "requirements": [
                "Select columns: program, student_count",
                "Group by: program",
                "Order by: program ASC"
            ],
            "sql_starter": "-- Task 3: Count Students by Program (Form B)\n-- Complete the GROUP BY column below:\n\nSELECT program, COUNT(*) AS student_count\nFROM Students\nGROUP BY program\nORDER BY program ASC;\n",
            "python_starter": "# Task 3: Count students per program (Form B)\n# Complete the counting logic below (change 0 to 1):\ncounts = {}\n\nfor s in students:\n    prog = s['program']\n    # Add 1 to the count for this program (change 0 to 1)\n    counts[prog] = counts.get(prog, 0) + 0\n\n# Convert to list of tuples: (program, student_count)\nresult = [(prog, count) for prog, count in counts.items()]\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
                "Use all three: Students, Enrollments, and Courses",
                "Filter condition: course_id = 'C102'",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 4: Multi-table JOIN for C102 (Form B)\n-- Complete the course filter below (fill in 'C102'):\n\nSELECT s.student_id, s.student_name, c.course_name\nFROM Students s\nJOIN Enrollments e ON s.student_id = e.student_id\nJOIN Courses c ON e.course_id = c.course_id\nWHERE e.course_id = ''\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 4: Multi-entity Join for C102 (Form B)\n# Complete the course filter below (change '' to 'C102'):\nresult = []\n\nstudent_names = {s['student_id']: s['student_name'] for s in students}\ncourse_names = {c['course_id']: c['course_name'] for c in courses}\n\nfor e in enrollments:\n    # Filter for course C102\n    if e['course_id'] == '':\n        s_id = e['student_id']\n        s_name = student_names.get(s_id)\n        c_name = course_names.get(e['course_id'])\n        result.append((s_id, s_name, c_name))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
            "expected_columns": ["student_id", "student_name", "course_name"],
            "oracle_sql": "SELECT s.student_id, s.student_name, c.course_name FROM Students s JOIN Enrollments e ON s.student_id = e.student_id JOIN Courses c ON e.course_id = c.course_id WHERE e.course_id = 'C102' ORDER BY s.student_id ASC;"
        },
        "5": {
            "id": "T5",
            "title": "Average per Group",
            "concept": "Grouped aggregates filtered with HAVING threshold >= 85",
            "instruction": "Calculate the average score for each course (ignore empty scores). Keep only courses where the average score is 85.0 or higher. Display course_id and average score rounded to 2 decimals. Sort by course_id ascending.",
            "requirements": [
                "Select columns: course_id, avg_score",
                "Group by: course_id",
                "Keep only groups where the average score is 85.0 or higher (ignore empty scores)",
                "Order by: course_id ASC"
            ],
            "sql_starter": "-- Task 5: Grouped Average with HAVING (Form B)\n-- Complete the HAVING threshold below (change 0.0 to 85.0):\n\nSELECT course_id, ROUND(AVG(score), 2) AS avg_score\nFROM Enrollments\nWHERE score IS NOT NULL\nGROUP BY course_id\nHAVING AVG(score) >= 0.0\nORDER BY course_id ASC;\n",
            "python_starter": "# Task 5: Grouped average score >= 85.0 (Form B)\n# Complete the threshold check below (change 0.0 to 85.0):\nscores_by_course = {}\n\nfor e in enrollments:\n    if e['score'] is not None:\n        c_id = e['course_id']\n        scores_by_course.setdefault(c_id, []).append(e['score'])\n\nresult = []\nfor c_id, score_list in scores_by_course.items():\n    avg_score = round(sum(score_list) / len(score_list), 2)\n    # Keep courses with average score >= 85.0 (change 0.0 to 85.0)\n    if avg_score >= 0.0:\n        result.append((c_id, avg_score))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
            "expected_columns": ["course_id", "avg_score"],
            "oracle_sql": "SELECT course_id, ROUND(AVG(score), 2) AS avg_score FROM Enrollments WHERE score IS NOT NULL GROUP BY course_id HAVING AVG(score) >= 85.0 ORDER BY course_id ASC;"
        },
        "6": {
            "id": "T6",
            "title": "Finding Records With No Match",
            "concept": "Anti-join on Form B records",
            "instruction": "Find all students who have no enrollments. Display student ID and student name. Sort by student ID ascending.",
            "requirements": [
                "Select columns: student_id, student_name",
                "Only students who have no row in Enrollments",
                "Order by: student_id ASC"
            ],
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students - Form B)\n-- Debug the WHERE condition below (change IS NOT NULL to IS NULL):\n\nSELECT s.student_id, s.student_name\nFROM Students s\nLEFT JOIN Enrollments e ON s.student_id = e.student_id\nWHERE e.student_id IS NOT NULL\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 6: Find students without enrollments (Form B)\n# Debug the condition below (change 'in' to 'not in'):\nenrolled_ids = {e['student_id'] for e in enrollments}\n\nresult = []\nfor s in students:\n    # Change 'in' to 'not in' to find students without enrollments\n    if s['student_id'] in enrolled_ids:\n        result.append((s['student_id'], s['student_name']))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
