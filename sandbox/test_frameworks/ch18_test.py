import os
import sys

def test_chapter_18():
    print("Testing Chapter 18: State Vaults (Agentic State Machines)...")
    solution_path = "/workspace/ch18_state.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch18_state.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch18_state.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "run_react_loop") or not hasattr(module, "find_skeleton_ancestors"):
        print("Error: Solution must define 'run_react_loop' and 'find_skeleton_ancestors' functions.")
        sys.exit(1)

    # 1. Test run_react_loop (Thought-Action loop with recursion safeguards)
    try:
        # A simple step function that continues until it reaches "done"
        def step_fn(state):
            current_step = state.get("steps", 0)
            state["steps"] = current_step + 1
            if current_step >= 3:
                state["status"] = "success"
                state["thought"] = "Goal achieved!"
            else:
                state["thought"] = f"Thought at step {current_step}"
            return state

        # Case A: Succeeds within bounds
        init_state = {"steps": 0, "status": "running"}
        final_state = module.run_react_loop(init_state, step_fn, max_steps=5)
        if final_state.get("status") != "success" or final_state.get("steps") != 4:
            print(f"Error: run_react_loop failed to run successfully. Got: {final_state}")
            sys.exit(1)

        # Case B: Exceeds max steps safeguard
        looping_state = {"steps": 0, "status": "running"}
        # Never completes
        def infinite_step_fn(state):
            state["steps"] = state.get("steps", 0) + 1
            state["status"] = "running"
            return state

        limit_state = module.run_react_loop(looping_state, infinite_step_fn, max_steps=2)
        if limit_state.get("steps") > 2:
            print(f"Error: Loop safeguard failed. Expected steps <= 2, got {limit_state.get('steps')}")
            sys.exit(1)
        if "max_steps_exceeded" not in limit_state.get("status", "") and limit_state.get("status") == "running":
            # The status should be updated to show boundary hit or loop halted
            pass # We accept either as long as execution terminates

        print("ReAct agent state machine loop: PASS")
    except Exception as e:
        print(f"Error testing run_react_loop: {e}")
        sys.exit(1)

    # 2. Test find_skeleton_ancestors (Recursive graph traversal for lineage)
    try:
        lineage = {
            "Bones": "Specter",
            "Specter": "Terry",
            "Terry": "Assembly Ancestor",
            "Assembly Ancestor": None
        }
        
        # Linear walk check
        ancestors = module.find_skeleton_ancestors(lineage, "Bones")
        expected = ["Specter", "Terry", "Assembly Ancestor"]
        if ancestors != expected:
            print(f"Error: Ancestry list incorrect. Got {ancestors}, expected {expected}")
            sys.exit(1)

        # Circular reference check - should detect loop and terminate
        circular_lineage = {
            "A": "B",
            "B": "C",
            "C": "A"
        }
        circular_ancestors = module.find_skeleton_ancestors(circular_lineage, "A")
        # Should not get stuck in infinite recursion; should stop when loop is detected
        if len(circular_ancestors) > 10:
            print("Error: Lineage traversal does not handle circular references. Stack overflow risk!")
            sys.exit(1)

        print("Ancestry recursion tree walk: PASS")
    except Exception as e:
        print(f"Error testing find_skeleton_ancestors: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 18 tests passed! Spooky Town lineage records complete.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_18()
