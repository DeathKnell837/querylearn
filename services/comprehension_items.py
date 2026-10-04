"""
Comprehension Test Items for QueryLearn Research Protocol.

Covers 6 task families across Form A and Form B:
1. Selection and filtering (C1)
2. Filtering with sorting and limiting (C2)
3. Grouping and counting (C3)
4. Joining tables (C4)
5. Aggregation with a threshold (C5)
6. Finding records without a match (C6)

Domains and schemas are completely distinct from writing tasks and instructions:
- Form A: Employees & Projects
- Form B: Products & Orders

Scoring per item:
- Part 1 (Explanation): Fully correct = 2 pts, Partially correct = 1 pt, Wrong = 0 pts
- Part 2 (Prediction): Correct = 1 pt, Wrong = 0 pts
Max score per item: 3 pts.
Max score per condition (6 items): 18 pts.
"""

import random

# ==============================================================================
# FORM A: Employees & Projects Domain
# ==============================================================================

FORM_A_ITEMS = {
    "C1": {
        "item_id": "C1",
        "family": "Selection and filtering",
        "title": "1. Selection and Filtering",
        "schema_context": "Table Employees (emp_id INT, emp_name TEXT, department TEXT, salary REAL, hire_year INT)",
        "sql_code": """SELECT emp_name, salary
FROM Employees
WHERE department = 'Engineering' AND hire_year > 2020;""",
        "python_code": """recent_engineers = [
    {'name': e['emp_name'], 'salary': e['salary']}
    for e in employees
    if e['department'] == 'Engineering' and e['hire_year'] > 2020
]""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Selects the names and salaries of Engineering department employees who were hired after the year 2020.",
                    "points": 2
                },
                {
                    "id": "exp_b",
                    "text": "Retrieves employee names and salaries for everyone in the Engineering department regardless of hire date.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Calculates the total salary increase for engineers hired before 2020.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Updates employee records to assign them to Engineering if hired after 2020.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given employees Alice (Eng, 82k, 2021), Bob (Mkt, 65k, 2019), Charlie (Eng, 75k, 2018), and Fiona (Eng, 91k, 2023), what is the resulting output?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "[Alice Smith (82000), Fiona Gallagher (91000)]",
                    "points": 1
                },
                {
                    "id": "pred_b",
                    "text": "[Alice Smith (82000), Charlie Brown (75000), Fiona Gallagher (91000)]",
                    "points": 0
                },
                {
                    "id": "pred_c",
                    "text": "[Bob Jones (65000), Charlie Brown (75000)]",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "An empty result with no records",
                    "points": 0
                }
            ]
        }
    },

    "C2": {
        "item_id": "C2",
        "family": "Filtering with sorting and limiting",
        "title": "2. Filtering with Sorting and Limiting",
        "schema_context": "Table Employees (emp_id INT, emp_name TEXT, department TEXT, salary REAL, hire_year INT)",
        "sql_code": """SELECT emp_id, emp_name, salary
FROM Employees
WHERE department = 'Engineering'
ORDER BY salary DESC, emp_id ASC
LIMIT 2;""",
        "python_code": """engineers = [e for e in employees if e['department'] == 'Engineering']
engineers.sort(key=lambda e: (-e['salary'], e['emp_id']))
top_engineers = [
    {'id': e['emp_id'], 'name': e['emp_name'], 'salary': e['salary']}
    for e in engineers[:2]
]""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Finds Engineering employees and sorts them by salary in descending order, but returns all of them.",
                    "points": 1
                },
                {
                    "id": "exp_b",
                    "text": "Retrieves the top 2 highest-paid employees in Engineering, breaking any salary ties by lowest ID.",
                    "points": 2
                },
                {
                    "id": "exp_c",
                    "text": "Returns the two lowest-paid employees across all company departments.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Counts how many engineers earn more than the second highest salary.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given engineers Charlie (ID 3, 75k), Alice (ID 1, 82k), and Fiona (ID 6, 91k), what is the resulting output?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "[Charlie Brown (75000), Alice Smith (82000)]",
                    "points": 0
                },
                {
                    "id": "pred_b",
                    "text": "[Fiona Gallagher (91000), Alice Smith (82000)]",
                    "points": 1
                },
                {
                    "id": "pred_c",
                    "text": "[Fiona Gallagher (91000), Alice Smith (82000), Charlie Brown (75000)]",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "[Alice Smith (82000), Charlie Brown (75000)]",
                    "points": 0
                }
            ]
        }
    },

    "C3": {
        "item_id": "C3",
        "family": "Grouping and counting",
        "title": "3. Grouping and Counting",
        "schema_context": "Table Employees (emp_id INT, emp_name TEXT, department TEXT, salary REAL, hire_year INT)",
        "sql_code": """SELECT department, COUNT(*) AS staff_count
FROM Employees
GROUP BY department
ORDER BY department ASC;""",
        "python_code": """dept_counts = {}
for e in employees:
    dept = e['department']
    dept_counts[dept] = dept_counts.get(dept, 0) + 1
result = sorted(
    [{'department': d, 'staff_count': c} for d, c in dept_counts.items()],
    key=lambda x: x['department']
)""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Filters out departments that have more than one employee.",
                    "points": 0
                },
                {
                    "id": "exp_b",
                    "text": "Groups employees by department and sorts department names, but sums their salaries instead of counting staff.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Counts the total number of employees in each department, ordered alphabetically by department name.",
                    "points": 2
                },
                {
                    "id": "exp_d",
                    "text": "Returns each employee's name along with their department code.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "If the table contains 3 Engineering, 2 Marketing, and 1 Sales employee, what is the resulting output?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "Sales: 1, Marketing: 2, Engineering: 3",
                    "points": 0
                },
                {
                    "id": "pred_b",
                    "text": "Engineering: 3, Marketing: 2, Sales: 1",
                    "points": 1
                },
                {
                    "id": "pred_c",
                    "text": "Engineering: 6, Marketing: 6, Sales: 6",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "Engineering: 82000, Marketing: 65000, Sales: 58000",
                    "points": 0
                }
            ]
        }
    },

    "C4": {
        "item_id": "C4",
        "family": "Joining tables",
        "title": "4. Joining Tables",
        "schema_context": "Employees (emp_id, emp_name), Projects (project_id, emp_id, project_name, budget)",
        "sql_code": """SELECT e.emp_name, p.project_name, p.budget
FROM Employees e
JOIN Projects p ON e.emp_id = p.emp_id
WHERE p.budget >= 60000
ORDER BY e.emp_id ASC;""",
        "python_code": """emp_lookup = {e['emp_id']: e['emp_name'] for e in employees}
matched_projects = []
for p in projects:
    if p['budget'] >= 60000 and p['emp_id'] in emp_lookup:
        matched_projects.append({
            'emp_name': emp_lookup[p['emp_id']],
            'project_name': p['project_name'],
            'budget': p['budget']
        })
matched_projects.sort(key=lambda x: [e['emp_id'] for e in employees if e['emp_name'] == x['emp_name']][0])""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Combines employee details with their assigned projects for all projects with a budget of 60,000 or greater, ordered by employee ID.",
                    "points": 2
                },
                {
                    "id": "exp_b",
                    "text": "Matches employees to all their assigned projects regardless of budget, ordered by employee ID.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Lists all employees who do not have any projects assigned.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Replaces employee names with project titles in the database.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given Alice (Cloud Migration: 120k, Security Audit: 45k), Bob (Campaign Alpha: 30k), and Charlie (Data Pipeline: 85k), what output is generated?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "Alice Smith (Security Audit: 45k), Bob Jones (Campaign Alpha: 30k)",
                    "points": 0
                },
                {
                    "id": "pred_b",
                    "text": "Alice Smith (Cloud Migration: 120k), Charlie Brown (Data Pipeline: 85k)",
                    "points": 1
                },
                {
                    "id": "pred_c",
                    "text": "Alice Smith (Cloud Migration: 120k), Alice Smith (Security Audit: 45k), Bob Jones (30k), Charlie Brown (85k)",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "Charlie Brown (Data Pipeline: 85k)",
                    "points": 0
                }
            ]
        }
    },

    "C5": {
        "item_id": "C5",
        "family": "Aggregation with a threshold",
        "title": "5. Aggregation with a Threshold",
        "schema_context": "Table Employees (emp_id INT, emp_name TEXT, department TEXT, salary REAL, hire_year INT)",
        "sql_code": """SELECT department, ROUND(AVG(salary), 2) AS avg_salary
FROM Employees
GROUP BY department
HAVING AVG(salary) >= 70000
ORDER BY department ASC;""",
        "python_code": """dept_salaries = {}
for e in employees:
    dept_salaries.setdefault(e['department'], []).append(e['salary'])
result = []
for dept in sorted(dept_salaries.keys()):
    salaries = dept_salaries[dept]
    avg_sal = sum(salaries) / len(salaries)
    if avg_sal >= 70000:
        result.append({'department': dept, 'avg_salary': round(avg_sal, 2)})""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Computes the average salary for all departments and displays all of them without applying the 70,000 threshold.",
                    "points": 1
                },
                {
                    "id": "exp_b",
                    "text": "Returns individual employees who earn more than 70,000 without calculating department averages.",
                    "points": 0
                },
                {
                    "id": "exp_c",
                    "text": "Calculates the average salary for each department and returns only departments whose average salary is at least 70,000, ordered alphabetically.",
                    "points": 2
                },
                {
                    "id": "exp_d",
                    "text": "Sums the total salaries in departments that have at least 70 employees.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "If Engineering salaries average 82,666.67, Marketing salaries average 68,500.00, and Sales averages 58,000.00, what is the output?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "Engineering: 82666.67",
                    "points": 1
                },
                {
                    "id": "pred_b",
                    "text": "Engineering: 82666.67, Marketing: 68500.00",
                    "points": 0
                },
                {
                    "id": "pred_c",
                    "text": "Engineering: 82666.67, Marketing: 68500.00, Sales: 58000.00",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "No departments qualify",
                    "points": 0
                }
            ]
        }
    },

    "C6": {
        "item_id": "C6",
        "family": "Finding records without a match",
        "title": "6. Finding Records Without a Match",
        "schema_context": "Employees (emp_id, emp_name), Projects (project_id, emp_id, project_name, budget)",
        "sql_code": """SELECT e.emp_id, e.emp_name
FROM Employees e
LEFT JOIN Projects p ON e.emp_id = p.emp_id
WHERE p.project_id IS NULL
ORDER BY e.emp_id ASC;""",
        "python_code": """assigned_emp_ids = {p['emp_id'] for p in projects}
unassigned_employees = [
    {'emp_id': e['emp_id'], 'emp_name': e['emp_name']}
    for e in employees
    if e['emp_id'] not in assigned_emp_ids
]
unassigned_employees.sort(key=lambda x: x['emp_id'])""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Performs a join between employees and projects, but returns all employees whether or not they have a project.",
                    "points": 1
                },
                {
                    "id": "exp_b",
                    "text": "Finds all projects that have no employees working on them.",
                    "points": 0
                },
                {
                    "id": "exp_c",
                    "text": "Finds and returns the ID and name of all employees who are not assigned to any project, ordered by employee ID.",
                    "points": 2
                },
                {
                    "id": "exp_d",
                    "text": "Deletes all employee records that lack corresponding project entries.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "If employees 1, 2, 3 have assigned projects, but employee 5 (Evan Wright) and employee 6 (Fiona Gallagher) have none, what is returned?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "5: Evan Wright, 6: Fiona Gallagher",
                    "points": 1
                },
                {
                    "id": "pred_b",
                    "text": "1: Alice Smith, 2: Bob Jones, 3: Charlie Brown",
                    "points": 0
                },
                {
                    "id": "pred_c",
                    "text": "5: Evan Wright",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "Empty result (0 rows)",
                    "points": 0
                }
            ]
        }
    }
}

# ==============================================================================
# FORM B: Products & Orders Domain
# ==============================================================================

FORM_B_ITEMS = {
    "C1": {
        "item_id": "C1",
        "family": "Selection and filtering",
        "title": "1. Selection and Filtering",
        "schema_context": "Table Products (product_id INT, product_name TEXT, category TEXT, unit_price REAL, stock_qty INT)",
        "sql_code": """SELECT product_name, unit_price
FROM Products
WHERE category = 'Hardware' AND unit_price > 50.0;""",
        "python_code": """premium_hardware = [
    {'name': p['product_name'], 'price': p['unit_price']}
    for p in products
    if p['category'] == 'Hardware' and p['unit_price'] > 50.0
]""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Retrieves all products in the Hardware category regardless of their price.",
                    "points": 1
                },
                {
                    "id": "exp_b",
                    "text": "Selects product names and unit prices of Hardware items that cost more than 50.00.",
                    "points": 2
                },
                {
                    "id": "exp_c",
                    "text": "Counts how many products cost less than 50.00 across all categories.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Reduces the price of all Hardware products to 50.00.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given products Keyboard (Hardware, 85.00), USB Hub (Hardware, 28.00), Tumbler (Kitchen, 19.50), and Mouse (Hardware, 55.00), what output is returned?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "[Keyboard (85.00), USB Hub (28.00), Mouse (55.00)]",
                    "points": 0
                },
                {
                    "id": "pred_b",
                    "text": "[Keyboard (85.00), Mouse (55.00)]",
                    "points": 1
                },
                {
                    "id": "pred_c",
                    "text": "[USB Hub (28.00), Tumbler (19.50)]",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "An empty result with no records",
                    "points": 0
                }
            ]
        }
    },

    "C2": {
        "item_id": "C2",
        "family": "Filtering with sorting and limiting",
        "title": "2. Filtering with Sorting and Limiting",
        "schema_context": "Table Products (product_id INT, product_name TEXT, category TEXT, unit_price REAL, stock_qty INT)",
        "sql_code": """SELECT product_id, product_name, stock_qty
FROM Products
WHERE category = 'Hardware'
ORDER BY stock_qty DESC, product_id ASC
LIMIT 2;""",
        "python_code": """hardware = [p for p in products if p['category'] == 'Hardware']
hardware.sort(key=lambda p: (-p['stock_qty'], p['product_id']))
top_stock = [
    {'id': p['product_id'], 'name': p['product_name'], 'stock': p['stock_qty']}
    for p in hardware[:2]
]""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Selects the 2 lowest-stock items in the catalog regardless of category.",
                    "points": 0
                },
                {
                    "id": "exp_b",
                    "text": "Finds all Hardware items sorted by stock in descending order, without restricting to the top 2.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Retrieves the 2 Hardware products with the highest stock quantity, breaking any ties by lowest product ID.",
                    "points": 2
                },
                {
                    "id": "exp_d",
                    "text": "Computes the average stock quantity of all hardware items.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given hardware items Keyboard (ID 101, stock 45), USB Hub (ID 102, stock 120), and Mouse (ID 105, stock 80), what is returned?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "[102: USB Hub (120), 105: Mouse (80)]",
                    "points": 1
                },
                {
                    "id": "pred_b",
                    "text": "[101: Keyboard (45), 105: Mouse (80)]",
                    "points": 0
                },
                {
                    "id": "pred_c",
                    "text": "[102: USB Hub (120), 105: Mouse (80), 101: Keyboard (45)]",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "[101: Keyboard (45), 102: USB Hub (120)]",
                    "points": 0
                }
            ]
        }
    },

    "C3": {
        "item_id": "C3",
        "family": "Grouping and counting",
        "title": "3. Grouping and Counting",
        "schema_context": "Table Products (product_id INT, product_name TEXT, category TEXT, unit_price REAL, stock_qty INT)",
        "sql_code": """SELECT category, COUNT(*) AS item_count
FROM Products
GROUP BY category
ORDER BY category ASC;""",
        "python_code": """category_counts = {}
for p in products:
    cat = p['category']
    category_counts[cat] = category_counts.get(cat, 0) + 1
result = sorted(
    [{'category': c, 'item_count': count} for c, count in category_counts.items()],
    key=lambda x: x['category']
)""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Counts the number of products in each category, ordered alphabetically by category name.",
                    "points": 2
                },
                {
                    "id": "exp_b",
                    "text": "Groups products by category but calculates total stock rather than counting the items.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Finds categories that have only 1 item and removes all others.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Returns all product names along with their category codes.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "If Products has 1 Furniture item, 3 Hardware items, and 2 Kitchen items, what is the output?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "Kitchen: 2, Hardware: 3, Furniture: 1",
                    "points": 0
                },
                {
                    "id": "pred_b",
                    "text": "Furniture: 1, Hardware: 3, Kitchen: 2",
                    "points": 1
                },
                {
                    "id": "pred_c",
                    "text": "Furniture: 6, Hardware: 6, Kitchen: 6",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "Hardware: 3, Kitchen: 2",
                    "points": 0
                }
            ]
        }
    },

    "C4": {
        "item_id": "C4",
        "family": "Joining tables",
        "title": "4. Joining Tables",
        "schema_context": "Products (product_id, product_name), Orders (order_id, product_id, customer_name, order_qty)",
        "sql_code": """SELECT p.product_name, o.customer_name, o.order_qty
FROM Products p
JOIN Orders o ON p.product_id = o.product_id
WHERE o.order_qty >= 10
ORDER BY p.product_id ASC;""",
        "python_code": """prod_lookup = {p['product_id']: p['product_name'] for p in products}
matched_orders = []
for o in orders:
    if o['order_qty'] >= 10 and o['product_id'] in prod_lookup:
        matched_orders.append({
            'product_name': prod_lookup[o['product_id']],
            'customer_name': o['customer_name'],
            'order_qty': o['order_qty']
        })
matched_orders.sort(key=lambda x: [p['product_id'] for p in products if p['product_name'] == x['product_name']][0])""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Combines products and customer orders for all orders regardless of order quantity.",
                    "points": 1
                },
                {
                    "id": "exp_b",
                    "text": "Joins products with their orders and returns product name, customer name, and quantity for orders of 10 or more units, sorted by product ID.",
                    "points": 2
                },
                {
                    "id": "exp_c",
                    "text": "Lists only products that have zero customer orders.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Increases the price of any product ordered by 10 or more customers.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given Keyboard (Order: Metro Corp, qty 12; TechLabs, qty 4) and USB Hub (Order: Delta Inc, qty 25), what is returned?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "Keyboard (Metro Corp: 12), USB Hub (Delta Inc: 25)",
                    "points": 1
                },
                {
                    "id": "pred_b",
                    "text": "Keyboard (TechLabs: 4)",
                    "points": 0
                },
                {
                    "id": "pred_c",
                    "text": "Keyboard (Metro Corp: 12), Keyboard (TechLabs: 4), USB Hub (Delta Inc: 25)",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "USB Hub (Delta Inc: 25)",
                    "points": 0
                }
            ]
        }
    },

    "C5": {
        "item_id": "C5",
        "family": "Aggregation with a threshold",
        "title": "5. Aggregation with a Threshold",
        "schema_context": "Table Products (product_id INT, product_name TEXT, category TEXT, unit_price REAL, stock_qty INT)",
        "sql_code": """SELECT category, ROUND(AVG(unit_price), 2) AS avg_price
FROM Products
GROUP BY category
HAVING AVG(unit_price) >= 50.0
ORDER BY category ASC;""",
        "python_code": """cat_prices = {}
for p in products:
    cat_prices.setdefault(p['category'], []).append(p['unit_price'])
result = []
for cat in sorted(cat_prices.keys()):
    prices = cat_prices[cat]
    avg_p = sum(prices) / len(prices)
    if avg_p >= 50.0:
        result.append({'category': cat, 'avg_price': round(avg_p, 2)})""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Calculates the average unit price for each category and returns only categories whose average price is at least 50.00, sorted alphabetically.",
                    "points": 2
                },
                {
                    "id": "exp_b",
                    "text": "Computes the average unit price across every category without applying the 50.00 threshold.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Selects individual products whose price exceeds 50.00 without grouping.",
                    "points": 0
                },
                {
                    "id": "exp_d",
                    "text": "Finds categories where the total sum of prices is greater than 50.00.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "If Furniture average price is 340.00, Hardware average is 56.00, and Kitchen average is 16.75, what is returned?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "Furniture: 340.00, Hardware: 56.00, Kitchen: 16.75",
                    "points": 0
                },
                {
                    "id": "pred_b",
                    "text": "Furniture: 340.00, Hardware: 56.00",
                    "points": 1
                },
                {
                    "id": "pred_c",
                    "text": "Furniture: 340.00",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "Hardware: 56.00",
                    "points": 0
                }
            ]
        }
    },

    "C6": {
        "item_id": "C6",
        "family": "Finding records without a match",
        "title": "6. Finding Records Without a Match",
        "schema_context": "Products (product_id, product_name), Orders (order_id, product_id, customer_name, order_qty)",
        "sql_code": """SELECT p.product_id, p.product_name
FROM Products p
LEFT JOIN Orders o ON p.product_id = o.product_id
WHERE o.order_id IS NULL
ORDER BY p.product_id ASC;""",
        "python_code": """ordered_prod_ids = {o['product_id'] for o in orders}
unordered_products = [
    {'product_id': p['product_id'], 'product_name': p['product_name']}
    for p in products
    if p['product_id'] not in ordered_prod_ids
]
unordered_products.sort(key=lambda x: x['product_id'])""",
        "explanation": {
            "prompt": "What does this code accomplish?",
            "options": [
                {
                    "id": "exp_a",
                    "text": "Finds all orders that do not correspond to any valid product.",
                    "points": 0
                },
                {
                    "id": "exp_b",
                    "text": "Performs a left join between products and orders, returning all products whether ordered or not.",
                    "points": 1
                },
                {
                    "id": "exp_c",
                    "text": "Finds and returns the product ID and name of all products that have never been ordered, ordered by product ID.",
                    "points": 2
                },
                {
                    "id": "exp_d",
                    "text": "Deletes all products that have zero recorded orders.",
                    "points": 0
                }
            ]
        },
        "prediction": {
            "prompt": "Given products 101, 102, 103, 104 with existing orders, and products 105 (Mouse) and 106 (Ceramic Mug) with no orders, what is returned?",
            "options": [
                {
                    "id": "pred_a",
                    "text": "105: Mouse, 106: Ceramic Mug",
                    "points": 1
                },
                {
                    "id": "pred_b",
                    "text": "101: Keyboard, 102: USB Hub, 103: Tumbler, 104: Desk",
                    "points": 0
                },
                {
                    "id": "pred_c",
                    "text": "106: Ceramic Mug",
                    "points": 0
                },
                {
                    "id": "pred_d",
                    "text": "Empty result (0 rows)",
                    "points": 0
                }
            ]
        }
    }
}


def get_form_items(form):
    """Retrieve items dictionary for Form A or Form B."""
    return FORM_B_ITEMS if str(form).upper() == 'B' else FORM_A_ITEMS


def get_item(form, item_id, randomize=True, seed=None):
    """
    Get a single comprehension item definition with randomized option ordering.
    Options retain their stable option IDs so grading is independent of visual position.
    """
    items = get_form_items(form)
    clean_id = str(item_id).upper().strip()
    if clean_id not in items:
        # Default fallback to C1
        clean_id = "C1"
    
    item = items[clean_id]
    
    # Create a deep copy of options to allow shuffling
    exp_opts = list(item["explanation"]["options"])
    pred_opts = list(item["prediction"]["options"])
    
    if randomize:
        rng = random.Random(seed) if seed is not None else random.Random()
        rng.shuffle(exp_opts)
        rng.shuffle(pred_opts)
    
    return {
        "item_id": item["item_id"],
        "family": item["family"],
        "title": item["title"],
        "schema_context": item["schema_context"],
        "sql_code": item["sql_code"],
        "python_code": item["python_code"],
        "explanation": {
            "prompt": item["explanation"]["prompt"],
            "options": exp_opts
        },
        "prediction": {
            "prompt": item["prediction"]["prompt"],
            "options": pred_opts
        }
    }


def grade_item(form, item_id, explanation_choice_id, prediction_choice_id):
    """
    Grades submitted choices against the master key.
    Returns: (explanation_score, prediction_score, total_score)
    """
    items = get_form_items(form)
    clean_id = str(item_id).upper().strip()
    if clean_id not in items:
        return 0.0, 0.0, 0.0
    
    item = items[clean_id]
    
    exp_score = 0.0
    for opt in item["explanation"]["options"]:
        if opt["id"] == explanation_choice_id:
            exp_score = float(opt["points"])
            break
            
    pred_score = 0.0
    for opt in item["prediction"]["options"]:
        if opt["id"] == prediction_choice_id:
            pred_score = float(opt["points"])
            break
            
    return exp_score, pred_score, exp_score + pred_score
