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
            "sql_starter": "-- Task 1: Select BSCS 1st Year Students\n-- Debug: This query currently selects all BSCS students.\n-- Add \"AND year_level = 1\" to the WHERE clause to select only 1st year students:\n\nSELECT student_id, student_name\nFROM Students\nWHERE program = 'BSCS'\nORDER BY student_id ASC;\n",
            "python_starter": "# Task 1: Select BSCS 1st Year Students\n# Debug: This code currently selects all BSCS students.\n# Update the condition to also check: and s['year_level'] == 1\nresult = []\n\nfor s in students:\n    if s['program'] == 'BSCS':\n        result.append((s['student_id'], s['student_name']))\n\n# Sort by student_id ascending\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 2: Top 3 Scores in C101\n-- Debug: This query currently returns 10 rows.\n-- Change LIMIT 10 to LIMIT 3 to keep only the top 3 scores:\n\nSELECT student_id, score\nFROM Enrollments\nWHERE course_id = 'C101' AND score IS NOT NULL\nORDER BY score DESC, student_id ASC\nLIMIT 10;\n",
            "python_starter": "# Task 2: Top 3 non-missing scores for C101\n# Debug: This code currently keeps 10 items.\n# Change [:10] to [:3] to keep only the top 3 scores:\nresult = []\n\nfor e in enrollments:\n    # Keep course C101 with valid scores\n    if e['course_id'] == 'C101' and e['score'] is not None:\n        result.append((e['student_id'], e['score']))\n\n# Sort: highest score first, tie-break by student_id ascending\nresult.sort(key=lambda x: (-x[1], x[0]))\n\n# Change 10 to 3\nresult = result[:10]\n\nprint(result)",
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
            "sql_starter": "-- Task 3: Count Students by Program\n-- Debug: This query currently sorts in reverse order (DESC).\n-- Change DESC to ASC to sort alphabetically by program name:\n\nSELECT program, COUNT(*) AS student_count\nFROM Students\nGROUP BY program\nORDER BY program DESC;\n",
            "python_starter": "# Task 3: Count students per program\n# Debug: This code currently sorts in reverse order (reverse=True).\n# Change reverse=True to reverse=False to sort alphabetically:\ncounts = {}\n\nfor s in students:\n    prog = s['program']\n    counts[prog] = counts.get(prog, 0) + 1\n\n# Convert to list of tuples: (program, student_count)\nresult = [(prog, count) for prog, count in counts.items()]\nresult.sort(key=lambda x: x[0], reverse=True)\n\nprint(result)",
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
            "sql_starter": "-- Task 4: Multi-table JOIN for C101\n-- Debug: This query currently filters for course 'C102'.\n-- Change 'C102' to 'C101' in the WHERE clause:\n\nSELECT s.student_id, s.student_name, c.course_name\nFROM Students s\nJOIN Enrollments e ON s.student_id = e.student_id\nJOIN Courses c ON e.course_id = c.course_id\nWHERE e.course_id = 'C102'\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 4: Multi-entity Join for C101\n# Debug: This code currently filters for course 'C102'.\n# Change 'C102' to 'C101' in the if-condition below:\nresult = []\n\nstudent_names = {s['student_id']: s['student_name'] for s in students}\ncourse_names = {c['course_id']: c['course_name'] for c in courses}\n\nfor e in enrollments:\n    # Change 'C102' to 'C101'\n    if e['course_id'] == 'C102':\n        s_id = e['student_id']\n        s_name = student_names.get(s_id)\n        c_name = course_names.get(e['course_id'])\n        result.append((s_id, s_name, c_name))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 5: Grouped Average with HAVING\n-- Debug: The threshold is currently 70.0 instead of 80.0.\n-- Change 70.0 to 80.0 in the HAVING clause:\n\nSELECT course_id, ROUND(AVG(score), 2) AS avg_score\nFROM Enrollments\nWHERE score IS NOT NULL\nGROUP BY course_id\nHAVING AVG(score) >= 70.0\nORDER BY course_id ASC;\n",
            "python_starter": "# Task 5: Grouped average score >= 80.0\n# Debug: The threshold is currently 70.0 instead of 80.0.\n# Change 70.0 to 80.0 in the threshold check below:\nscores_by_course = {}\n\nfor e in enrollments:\n    if e['score'] is not None:\n        c_id = e['course_id']\n        scores_by_course.setdefault(c_id, []).append(e['score'])\n\nresult = []\nfor c_id, score_list in scores_by_course.items():\n    avg_score = round(sum(score_list) / len(score_list), 2)\n    # Change 70.0 to 80.0\n    if avg_score >= 70.0:\n        result.append((c_id, avg_score))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students)\n-- Debug: This query currently selects ENROLLED students (IS NOT NULL).\n-- Change IS NOT NULL to IS NULL to find students WITHOUT enrollments:\n\nSELECT s.student_id, s.student_name\nFROM Students s\nLEFT JOIN Enrollments e ON s.student_id = e.student_id\nWHERE e.student_id IS NOT NULL\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 6: Find students without enrollments\n# Debug: This code currently checks 'in' (enrolled students).\n# Change 'in' to 'not in' to find students WITHOUT enrollments:\nenrolled_ids = {e['student_id'] for e in enrollments}\n\nresult = []\nfor s in students:\n    # Change 'in' to 'not in'\n    if s['student_id'] in enrolled_ids:\n        result.append((s['student_id'], s['student_name']))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 1: Select BSIT 2nd Year Students (Form B)\n-- Debug: This query currently selects all BSIT students across all year levels.\n-- Add \"AND year_level = 2\" to the WHERE clause to select only 2nd year students:\n\nSELECT student_id, student_name\nFROM Students\nWHERE program = 'BSIT'\nORDER BY student_id ASC;\n",
            "python_starter": "# Task 1: Select BSIT 2nd Year Students (Form B)\n# Debug: This code currently selects all BSIT students across all year levels.\n# Update the condition to also check: and s['year_level'] == 2\nresult = []\n\nfor s in students:\n    if s['program'] == 'BSIT':\n        result.append((s['student_id'], s['student_name']))\n\n# Sort by student_id ascending\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 2: Top 3 Scores in C102 (Form B)\n-- Debug: This query currently returns 10 rows.\n-- Change LIMIT 10 to LIMIT 3 to keep only the top 3 scores:\n\nSELECT student_id, score\nFROM Enrollments\nWHERE course_id = 'C102' AND score IS NOT NULL\nORDER BY score DESC, student_id ASC\nLIMIT 10;\n",
            "python_starter": "# Task 2: Top 3 non-missing scores for C102 (Form B)\n# Debug: This code currently keeps 10 items.\n# Change [:10] to [:3] to keep only the top 3 scores:\nresult = []\n\nfor e in enrollments:\n    # Keep course C102 with valid scores\n    if e['course_id'] == 'C102' and e['score'] is not None:\n        result.append((e['student_id'], e['score']))\n\n# Sort: highest score first, tie-break by student_id ascending\nresult.sort(key=lambda x: (-x[1], x[0]))\n\n# Change 10 to 3\nresult = result[:10]\n\nprint(result)",
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
            "sql_starter": "-- Task 3: Count Students by Program (Form B)\n-- Debug: This query currently sorts in reverse order (DESC).\n-- Change DESC to ASC to sort alphabetically by program name:\n\nSELECT program, COUNT(*) AS student_count\nFROM Students\nGROUP BY program\nORDER BY program ASC;\n",
            "python_starter": "# Task 3: Count students per program (Form B)\n# Debug: This code currently sorts in reverse order (reverse=True).\n# Change reverse=True to reverse=False to sort alphabetically:\ncounts = {}\n\nfor s in students:\n    prog = s['program']\n    counts[prog] = counts.get(prog, 0) + 1\n\n# Convert to list of tuples: (program, student_count)\nresult = [(prog, count) for prog, count in counts.items()]\nresult.sort(key=lambda x: x[0], reverse=True)\n\nprint(result)",
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
            "sql_starter": "-- Task 4: Multi-table JOIN for C102 (Form B)\n-- Debug: This query currently filters for course 'C101'.\n-- Change 'C101' to 'C102' in the WHERE clause:\n\nSELECT s.student_id, s.student_name, c.course_name\nFROM Students s\nJOIN Enrollments e ON s.student_id = e.student_id\nJOIN Courses c ON e.course_id = c.course_id\nWHERE e.course_id = 'C101'\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 4: Multi-entity Join for C102 (Form B)\n# Debug: This code currently filters for course 'C101'.\n# Change 'C101' to 'C102' in the if-condition below:\nresult = []\n\nstudent_names = {s['student_id']: s['student_name'] for s in students}\ncourse_names = {c['course_id']: c['course_name'] for c in courses}\n\nfor e in enrollments:\n    # Change 'C101' to 'C102'\n    if e['course_id'] == 'C101':\n        s_id = e['student_id']\n        s_name = student_names.get(s_id)\n        c_name = course_names.get(e['course_id'])\n        result.append((s_id, s_name, c_name))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 5: Grouped Average with HAVING (Form B)\n-- Debug: The threshold is currently 70.0 instead of 85.0.\n-- Change 70.0 to 85.0 in the HAVING clause:\n\nSELECT course_id, ROUND(AVG(score), 2) AS avg_score\nFROM Enrollments\nWHERE score IS NOT NULL\nGROUP BY course_id\nHAVING AVG(score) >= 70.0\nORDER BY course_id ASC;\n",
            "python_starter": "# Task 5: Grouped average score >= 85.0 (Form B)\n# Debug: The threshold is currently 70.0 instead of 85.0.\n# Change 70.0 to 85.0 in the threshold check below:\nscores_by_course = {}\n\nfor e in enrollments:\n    if e['score'] is not None:\n        c_id = e['course_id']\n        scores_by_course.setdefault(c_id, []).append(e['score'])\n\nresult = []\nfor c_id, score_list in scores_by_course.items():\n    avg_score = round(sum(score_list) / len(score_list), 2)\n    # Change 70.0 to 85.0\n    if avg_score >= 70.0:\n        result.append((c_id, avg_score))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students - Form B)\n-- Debug: This query currently selects ENROLLED students (IS NOT NULL).\n-- Change IS NOT NULL to IS NULL to find students WITHOUT enrollments:\n\nSELECT s.student_id, s.student_name\nFROM Students s\nLEFT JOIN Enrollments e ON s.student_id = e.student_id\nWHERE e.student_id IS NOT NULL\nORDER BY s.student_id ASC;\n",
            "python_starter": "# Task 6: Find students without enrollments (Form B)\n# Debug: This code currently checks 'in' (enrolled students).\n# Change 'in' to 'not in' to find students WITHOUT enrollments:\nenrolled_ids = {e['student_id'] for e in enrollments}\n\nresult = []\nfor s in students:\n    # Change 'in' to 'not in'\n    if s['student_id'] in enrolled_ids:\n        result.append((s['student_id'], s['student_name']))\n\nresult.sort(key=lambda x: x[0])\n\nprint(result)",
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
