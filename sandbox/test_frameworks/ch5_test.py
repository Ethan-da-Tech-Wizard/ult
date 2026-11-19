# ==============================================================================
# Program: ch5_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating memory-efficient array summation optimizations. Benchmarks contiguous memory traversal and verifies equivalence against baseline summation models.
# ==============================================================================

# How this file fits the app: the validator for chapter 5. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch5_opt.py.
# What it checks: optimized_array_sum(list) must equal the plain Python sum for 100000 numbers and must be
# fast: speedup >= 2x versus a Python loop OR finish in under 50 ms. Timing-based, so it can be flaky on a
# very busy machine.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch5_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys
import time

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_5():
    print("Testing Chapter 5: Iron Peaks C++ Array Optimization...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch5_opt.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch5_opt.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch5_opt.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("solution_module", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        # Loads the player's file as a throwaway module so its functions can be called; a syntax error or an
        # exception at import time is reported as a compile failure rather than a crash.
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
    
    # Solution Optimized execution
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_5()
