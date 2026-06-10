import os
import sys
import threading

def test_chapter_4():
    print("Testing Chapter 4: Parallel Swamp Mutex Safeguards...")
    solution_path = "/workspace/ch4_concurrency.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch4_concurrency.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch4_concurrency.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
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

if __name__ == "__main__":
    test_chapter_4()
