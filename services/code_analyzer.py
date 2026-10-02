import ast

def analyze_code(code, language):
    metrics = {
        "lines": len(code.splitlines()),
        "chars": len(code),
        "sql_clauses": 0,
        "joins": 0,
        "subqueries": 0,
        "python_loops": 0,
        "python_conditions": 0
    }

    if language.lower() == 'sql':
        code_upper = code.upper()
        metrics["sql_clauses"] = sum(code_upper.count(kw) for kw in ["SELECT", "FROM", "WHERE", "GROUP BY", "HAVING", "ORDER BY"])
        metrics["joins"] = code_upper.count("JOIN")
        metrics["subqueries"] = code_upper.count("SELECT") - 1 if code_upper.count("SELECT") > 0 else 0
    elif language.lower() == 'python':
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    metrics["python_loops"] += 1
                elif isinstance(node, ast.If):
                    metrics["python_conditions"] += 1
        except:
            pass

    return metrics
