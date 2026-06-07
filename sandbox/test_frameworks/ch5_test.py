import os
import sys
import time

def test_chapter_5():
    print("Testing Chapter 5: Iron Peaks C++ Array Optimization...")
    solution_path = "/workspace/ch5_opt.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch5_opt.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch5_opt.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "optimized_array_sum"):
        print("Error: Solution must define the 'optimized_array_sum' function wrapper.")
        sys.exit(1)

    # Performance comparison loop
    # We compare optimized_array_sum (compiled C++ shared objects) vs python native sum loop
    size = 100000
    test_data = list(range(size))
    
    # Pure Python benchmark
    start_py = time.perf_counter()
    py_sum = 0
    for x in test_data:
        py_sum += x
    duration_py = time.perf_counter() - start_py
    print(f"Pure Python Loop: {duration_py*1000:.3f} ms")
    
    # Student Optimized execution
    try:
        start_opt = time.perf_counter()
        opt_sum = module.optimized_array_sum(test_data)
        duration_opt = time.perf_counter() - start_opt
        print(f"Optimized C++ Bridge Loop: {duration_opt*1000:.3f} ms")
        
        if opt_sum != py_sum:
            print(f"Error: Sum mismatch. Got {opt_sum}, expected {py_sum}")
            sys.exit(1)
            
        # Verify optimization speed gain (C++ should be faster)
        # To avoid clock ticks issues in sandboxes, we require C++ to be under 15ms or faster than Python
        speedup = duration_py / max(duration_opt, 1e-9)
        print(f"Calculated Speedup factor: {speedup:.2f}x")
        
        if speedup < 2.0 and duration_opt > 0.05:
            print("Error: Optimization insufficient. Did you compile native C++ arrays via pybind11?")
            sys.exit(1)
            
        print("Performance optimization check: PASS")
    except Exception as e:
        print(f"Error during optimized array summation: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 5 tests passed! C++ matrix processing optimized.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_5()
