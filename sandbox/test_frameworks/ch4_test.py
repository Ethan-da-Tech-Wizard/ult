# ==============================================================================
# Program: ch4_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating multi-threaded concurrency safety. Evaluates threading mutex lock primitives protecting shared bank account balances against race conditions.
# ==============================================================================

# How this file fits the app: the validator for chapter 4. server/sandbox_manager.py runs it (inside the zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile, after server/main.py has saved the player's code as save_data/relic_save/ch4_concurrency.py.
# What it checks: ThreadedBank(initial_balance) used by 20 threads each withdrawing 50 from 1000 must end at exactly 0, which only holds if withdraw() is protected by a lock (detects the race condition).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so messages are written for learners. Run it by hand from the repo root: python3 sandbox/test_frameworks/ch4_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside this process; use the Docker sandbox for untrusted code.
import os
import sys
import threading

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of returning a value.
def test_chapter_4():
    print("Testing Chapter 4: Parallel Swamp Mutex Safeguards...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch4_concurrency.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch4_concurrency.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch4_concurrency.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("solution_module", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        # Loads the player's file as a throwaway module so its functions can be called; a syntax error or an exception at import time is reported as a compile failure rather than a crash.
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "ThreadedBank"):
        print("Error: Solution must define the 'ThreadedBank' class.")
        sys.exit(1)

    # Test bank transfers in multiple parallel threads
    try:
        bank = module.ThreadedBank(initial_balance=1000)
        
        # Spawn 20 parallel threads withdrawing 50 gold each
        threads = []
        for _ in range(20):
            t = threading.Thread(target=lambda: bank.withdraw(50))
            threads.append(t)
            
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        # Correct balance should be exactly 1000 - 20*50 = 0
        final_balance = bank.get_balance()
        print(f"Final bank balance: {final_balance} (Expected: 0)")
        
        if final_balance != 0:
            print("Error: Race condition detected! Withdrawals were not atomic. Did you implement lock mutexes?")
            sys.exit(1)
            
        print("Thread-safe bank transaction verification: PASS")
    except Exception as e:
        print(f"Error during parallel execution check: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 4 tests passed! Parallel race conditions neutralized.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_4()
