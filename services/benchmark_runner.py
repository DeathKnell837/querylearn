import time
import tracemalloc

def run_benchmark(task_id, language, reference_code, sizes=[1000, 10000, 100000]):
    results = []
    
    for size in sizes:
        # Dummy benchmarking loop
        tracemalloc.start()
        start = time.time()
        
        # Simulate execution
        time.sleep(0.01)
        
        end = time.time()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed = end - start
        
        results.append({
            "task_id": task_id,
            "language": language,
            "dataset_size": size,
            "execution_time": elapsed,
            "memory_usage": peak,
            "executions_per_second": 1.0 / elapsed if elapsed > 0 else 0
        })
        
    return results
