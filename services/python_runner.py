import sys
import subprocess
import json
import tempfile
import os
import time

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


def execute_python(code, data_variables, timeout=10):
    """Execute user Python code in a restricted subprocess sandbox."""
    safe_list = repr(list(SAFE_IMPORTS))
    blocked_list = repr(list(BLOCKED_IMPORTS))

    wrapper_header = f"""
import json as _json

# Pre-inject data variables
students = _json.loads('''{json.dumps(data_variables.get('students', []))}''')
courses = _json.loads('''{json.dumps(data_variables.get('courses', []))}''')
enrollments = _json.loads('''{json.dumps(data_variables.get('enrollments', []))}''')

# Pre-import safe modules so standard library dependencies are already loaded
import math as _math
import statistics as _stat
import collections as _coll
import itertools as _iter
import functools as _func

import builtins as _builtins

_SAFE_IMPORTS = frozenset({safe_list})
_BLOCKED_IMPORTS = frozenset({blocked_list})
_orig_import = _builtins.__import__

def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    top = name.split('.')[0]
    if top in _BLOCKED_IMPORTS or top not in _SAFE_IMPORTS:
        raise ImportError(f"Import of '{{name}}' is not permitted in this sandbox. Allowed: {{sorted(_SAFE_IMPORTS)}}")
    return _orig_import(name, globals, locals, fromlist, level)

_builtins.__import__ = _restricted_import
_builtins.open = None
_builtins.exec = None
_builtins.eval = None
_builtins.compile = None

# Clean up private setup variables
del _json, _builtins, _math, _stat, _coll, _iter, _func

# --- User code below ---
"""
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
