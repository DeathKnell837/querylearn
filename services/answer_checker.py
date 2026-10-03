import math

def check_answer(learner_output, expected_output, task_config=None):
    try:
        if not isinstance(learner_output, list) or not isinstance(expected_output, list):
            return {"correct": False, "feedback": "Output format mismatch: expected a list of records.", "classification": "runtime_error"}

        if len(learner_output) != len(expected_output):
            return {"correct": False, "feedback": f"Expected {len(expected_output)} rows, got {len(learner_output)} rows.", "classification": "incorrect"}

        for l_row, e_row in zip(learner_output, expected_output):
            l_items = list(l_row) if isinstance(l_row, (list, tuple)) else [l_row]
            e_items = list(e_row) if isinstance(e_row, (list, tuple)) else [e_row]

            if len(l_items) != len(e_items):
                return {"correct": False, "feedback": f"Column count mismatch: expected {len(e_items)} columns, got {len(l_items)}.", "classification": "incorrect"}
            
            for l_val, e_val in zip(l_items, e_items):
                if l_val is None and e_val is None:
                    continue
                if l_val is None or e_val is None:
                    return {"correct": False, "feedback": f"Value mismatch: got {l_val}, expected {e_val}", "classification": "incorrect"}
                if isinstance(l_val, (int, float)) and isinstance(e_val, (int, float)):
                    if not math.isclose(float(l_val), float(e_val), rel_tol=1e-5, abs_tol=1e-5):
                        return {"correct": False, "feedback": f"Value mismatch: got {l_val}, expected {e_val}", "classification": "incorrect"}
                elif str(l_val).strip() != str(e_val).strip():
                    return {"correct": False, "feedback": f"Value mismatch: got '{l_val}', expected '{e_val}'", "classification": "incorrect"}

        return {"correct": True, "feedback": "Correct! Task completed successfully.", "classification": "correct"}
    except Exception as e:
         return {"correct": False, "feedback": f"Verification error: {str(e)}", "classification": "runtime_error"}
