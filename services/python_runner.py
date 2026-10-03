import sys
import subprocess
import json
import tempfile
import os
import time

def execute_python(code, data_variables, timeout=10):
    # Restricted execution wrapper
    wrapper_header = (
        "import sys\n"
        "import json\n"
        "import builtins\n\n"
        f"students = {repr(data_variables.get('students', []))}\n"
        f"courses = {repr(data_variables.get('courses', []))}\n"
        f"enrollments = {repr(data_variables.get('enrollments', []))}\n\n"
        "for _fn in ['open', 'exec', 'eval']:\n"
        "    if hasattr(builtins, _fn):\n"
        "        setattr(builtins, _fn, None)\n\n"
        "# User code below\n"
    )
    wrapper_code = wrapper_header + code + "\n"

    fd, path = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    try:
        with open(path, 'w', encoding='utf-8') as f:
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
                "execution_time": round(elapsed, 4)
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": "Execution timed out.",
                "execution_time": timeout
            }
    finally:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
