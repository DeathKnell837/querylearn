import sys
import os
sys.path.insert(0, r"C:\Users\USER\.gemini\antigravity\scratch\querylearn")

from app import create_app
from flask import render_template
from services.task_catalog import get_task, SCHEMA_METADATA
from services.comprehension_items import get_item
import sqlite3
from config import Config

app = create_app()

os.makedirs('screenshots_html', exist_ok=True)

with app.test_request_context('/'):
    # 1. Instructions
    with open('screenshots_html/instructions.html', 'w', encoding='utf-8') as f:
        f.write(render_template('instructions.html'))

    # 2. Practice
    with open('screenshots_html/practice.html', 'w', encoding='utf-8') as f:
        f.write(render_template('practice.html'))

    # 3. Readiness
    with open('screenshots_html/readiness.html', 'w', encoding='utf-8') as f:
        f.write(render_template('readiness_check.html'))

    # 4. Comprehension
    item_c1 = get_item('A', 'C1', randomize=False)
    with open('screenshots_html/comprehension.html', 'w', encoding='utf-8') as f:
        f.write(render_template('comprehension.html', language='sql', current_form='A', item=item_c1, item_num=1, total_items=6, remaining_seconds=180))

    # 5. Task SQL
    t1_a = get_task('A', '1')
    with open('screenshots_html/task_sql.html', 'w', encoding='utf-8') as f:
        f.write(render_template('task_sql.html', task=t1_a, current_task_num=1, total_tasks=6, schema=SCHEMA_METADATA, remaining_seconds=300, max_attempts=5, current_attempt=1, condition_language='sql'))

    # 6. Task Python
    t1_b = get_task('B', '1')
    with open('screenshots_html/task_python.html', 'w', encoding='utf-8') as f:
        f.write(render_template('task_python.html', task=t1_b, current_task_num=1, total_tasks=6, schema=SCHEMA_METADATA, remaining_seconds=300, max_attempts=5, current_attempt=1, condition_language='python'))

    # 7. Survey
    with open('screenshots_html/survey.html', 'w', encoding='utf-8') as f:
        f.write(render_template('survey.html', language='sql', condition_step=1))

print("Rendered all preview HTML files successfully!")
