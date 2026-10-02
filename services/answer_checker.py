import math

def check_answer(learner_output, expected_output, task_config):
    # Basic answer checker, assuming lists of tuples/lists for simplicity
    try:
        if not isinstance(learner_output, list) or not isinstance(expected_output, list):
            return {"correct": False, "feedback": "Output format mismatch", "classification": "runtime_error"}

        if len(learner_output) != len(expected_output):
            return {"correct": False, "feedback": f"Expected {len(expected_output)} rows, got {len(learner_output)}", "classification": "incorrect"}

        for l_row, e_row in zip(learner_output, expected_output):
            if len(l_row) != len(e_row):
                return {"correct": False, "feedback": "Column count mismatch", "classification": "incorrect"}
            
            for l_val, e_val in zip(l_row, e_row):
                if isinstance(l_val, (int, float)) and isinstance(e_val, (int, float)):
                    if not math.isclose(l_val, e_val, rel_tol=1e-6):
                        return {"correct": False, "feedback": f"Value mismatch: {l_val} != {e_val}", "classification": "incorrect"}
                elif str(l_val).strip() != str(e_val).strip():
                    return {"correct": False, "feedback": f"Value mismatch: {l_val} != {e_val}", "classification": "incorrect"}

        return {"correct": True, "feedback": "Correct!", "classification": "correct"}
    except Exception as e:
         return {"correct": False, "feedback": str(e), "classification": "runtime_error"}
