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
            "sql_starter": "-- Task 1: Select BSCS 1st Year Students\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 1: Select BSCS 1st Year Students\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 2: Top 3 Scores in C101\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 2: Top 3 non-missing scores for C101\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 3: Count Students by Program\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 3: Count students per program\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 4: Multi-table JOIN for C101\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 4: Multi-entity Join for C101\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 5: Grouped Average with HAVING\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 5: Grouped average score >= 80.0\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 6: Find students without enrollments\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 1: Select BSIT 2nd Year Students (Form B)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 1: Select BSIT 2nd Year Students (Form B)\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 2: Top 3 Scores in C102 (Form B)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 2: Top 3 non-missing scores for C102 (Form B)\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 3: Count Students by Program (Form B)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 3: Count students per program (Form B)\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 4: Multi-table JOIN for C102 (Form B)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 4: Multi-entity Join for C102 (Form B)\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 5: Grouped Average with HAVING (Form B)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 5: Grouped average score >= 85.0 (Form B)\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
            "sql_starter": "-- Task 6: Anti-Join (Unenrolled Students - Form B)\n-- Write your SQL query below:\n\n",
            "python_starter": "# Task 6: Find students without enrollments (Form B)\n# Data you can use: students, courses, enrollments (lists of dicts)\n# Put each answer row in result as a tuple, e.g. (1, 'Ana'). Keep print(result) at the end.\nresult = []\n\n# Write your code here\n\nprint(result)",
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
