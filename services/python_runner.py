import sys
import subprocess
import json
import tempfile
import os
import time
import ast
import re

# Allowlist of safe imports specified by research instrument requirements
SAFE_IMPORTS = frozenset({
    'math', 'statistics', 'collections', 'itertools', 'functools'
})

# Blocklist of dangerous modules
BLOCKED_IMPORTS = frozenset({
    'os', 'sys', 'subprocess', 'importlib', 'socket', 'sqlite3',
    'shutil', 'pathlib', 'glob', 'io', '_io', 'tempfile', 'signal',
    'ctypes', 'multiprocessing', 'threading', 'http', 'urllib',
    'requests', 'pickle', 'shelve', 'marshal', 'code', 'codeop',
    'compile', 'compileall', 'ast', 'dis', 'inspect', 'builtins',
    '__builtin__', '_thread', 'concurrent', 'asyncio', 'webbrowser',
})

# Blocklist of dangerous dunder/private attributes used in sandbox escape exploits
BLOCKED_ATTRIBUTES = frozenset({
    '__subclasses__', '__bases__', '__mro__', '__globals__',
    '__code__', '__closure__', '__builtins__', '__import__',
    '__class__', '__dict__', 'load_module', 'system', 'popen',
    'spawn', 'exec', 'eval'
})


def validate_code_ast(code: str):
    """
    Statically analyzes user code before execution.
    - Catches SyntaxError early with exact line numbers.
    - Blocks unauthorized module imports.
    - Blocks dunder attribute traversal (e.g., __subclasses__, __bases__) to prevent sandbox escape.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as se:
        return False, f"SyntaxError on line {se.lineno}: {se.msg}"

    for node in ast.walk(tree):
        # Disallow attribute traversal exploits
        if isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_ATTRIBUTES:
                return False, f"Security restriction: Access to '{node.attr}' is not permitted in this sandbox."

        # Disallow unauthorized imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if mod not in SAFE_IMPORTS:
                    return False, f"ImportError: Import of '{mod}' is not permitted in this sandbox. Allowed: {sorted(SAFE_IMPORTS)}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split('.')[0]
                if mod not in SAFE_IMPORTS:
                    return False, f"ImportError: Import of '{mod}' is not permitted in this sandbox. Allowed: {sorted(SAFE_IMPORTS)}"

    return True, None


def clean_traceback(stderr: str, header_lines: int) -> str:
    """
    Cleans raw traceback:
    - Normalizes reported line numbers by subtracting the wrapper header offset.
    - Replaces internal temporary file paths with '<user_code>'.
    - Filters out internal bootstrap frames.
    """
    if not stderr:
        return ""

    lines = stderr.splitlines()
    cleaned = []
    skip_next = False

    for line in lines:
        if skip_next:
            skip_next = False
            continue

        # Match File "...", line <num>
        match = re.search(r'File "([^"]+)", line (\d+)(.*)', line)
        if match:
            raw_line_num = int(match.group(2))
            rest = match.group(3)
            if raw_line_num <= header_lines:
                # Internal wrapper frame, omit
                skip_next = True
                continue
            user_line_num = max(1, raw_line_num - header_lines)
            cleaned.append(f'  File "<user_code>", line {user_line_num}{rest}')
        else:
            cleaned.append(line)

    return "\n".join(cleaned)


def execute_python(code, data_variables, timeout=10):
    """Execute user Python code in a restricted subprocess sandbox."""
    # Step 1: Pre-execution static AST validation
    is_valid, validation_error = validate_code_ast(code)
    if not is_valid:
        return {
            "output": "",
            "error": validation_error,
            "execution_time": 0.0
        }

    safe_list = repr(list(SAFE_IMPORTS))
    blocked_list = repr(list(BLOCKED_IMPORTS))

    # Safely serialize data variables without raw quote concatenation
    students_json = json.dumps(data_variables.get('students', []))
    courses_json = json.dumps(data_variables.get('courses', []))
    enrollments_json = json.dumps(data_variables.get('enrollments', []))

    wrapper_header = (
        "import json as _json\n"
        f"students = _json.loads({repr(students_json)})\n"
        f"courses = _json.loads({repr(courses_json)})\n"
        f"enrollments = _json.loads({repr(enrollments_json)})\n"
        "import math as _math\n"
        "import statistics as _stat\n"
        "import collections as _coll\n"
        "import itertools as _iter\n"
        "import functools as _func\n"
        "import builtins as _builtins\n"
        f"_SAFE_IMPORTS = frozenset({safe_list})\n"
        f"_BLOCKED_IMPORTS = frozenset({blocked_list})\n"
        "_orig_import = _builtins.__import__\n"
        "def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):\n"
        "    top = name.split('.')[0]\n"
        "    if top in _BLOCKED_IMPORTS or top not in _SAFE_IMPORTS:\n"
        '        raise ImportError(f"Import of \'{name}\' is not permitted in this sandbox. Allowed: {sorted(_SAFE_IMPORTS)}")\n'
        "    return _orig_import(name, globals, locals, fromlist, level)\n"
        "_builtins.__import__ = _restricted_import\n"
        "_builtins.open = None\n"
        "_builtins.exec = None\n"
        "_builtins.eval = None\n"
        "_builtins.compile = None\n"
        "del _json, _builtins, _math, _stat, _coll, _iter, _func\n"
        "# --- User code below ---\n"
    )

    header_line_count = len(wrapper_header.splitlines())
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
            raw_err = result.stderr if result.returncode != 0 else None
            cleaned_err = clean_traceback(raw_err, header_line_count) if raw_err else None

            return {
                "output": result.stdout,
                "error": cleaned_err,
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
