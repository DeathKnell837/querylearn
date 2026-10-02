import sys
import subprocess
import json
import tempfile
import os
import time

def execute_python(code, data_variables, timeout=10):
    # Restricted execution wrapper
    wrapper_code = f"""import sys
import json
import builtins

# Pre-inject data
students = {data_variables.get('students', [])}
courses = {data_variables.get('courses', [])}
enrollments = {data_variables.get('enrollments', [])}

# Restrict builtins safely
for _fn in ['open', 'exec', 'eval']:
    if hasattr(builtins, _fn):
        setattr(builtins, _fn, None)

# User code below
{code}
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            os.close(fd)
            f.write(wrapper_code)
        
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start_time
            return {
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "execution_time": elapsed
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": "Execution timed out.",
                "execution_time": timeout
            }
    finally:
        os.remove(path)
