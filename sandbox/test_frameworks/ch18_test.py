import os
import sys

def test_chapter_18():
    print("Testing Chapter 18: State Vaults (Agentic RAG State Machines)...")
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

    required_fns = ["run_react_loop", "find_skeleton_ancestors", "run_self_corrective_rag"]
    for fn in required_fns:
        if not hasattr(module, fn):
            print(f"Error: Solution must define the '{fn}' function.")
            sys.exit(1)

    # 1. Test run_react_loop (Thought-Action loop with recursion safeguards)
    try:
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
        def infinite_step_fn(state):
            state["steps"] = state.get("steps", 0) + 1
            state["status"] = "running"
            return state

        limit_state = module.run_react_loop(looping_state, infinite_step_fn, max_steps=2)
        if limit_state.get("steps") > 2:
            print(f"Error: Loop safeguard failed. Expected steps <= 2, got {limit_state.get('steps')}")
            sys.exit(1)

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

        # Circular reference check
        circular_lineage = {
            "A": "B",
            "B": "C",
            "C": "A"
        }
        circular_ancestors = module.find_skeleton_ancestors(circular_lineage, "A")
        if len(circular_ancestors) > 10:
            print("Error: Lineage traversal does not handle circular references. Stack overflow risk!")
            sys.exit(1)

        print("Ancestry recursion tree walk: PASS")
    except Exception as e:
        print(f"Error testing find_skeleton_ancestors: {e}")
        sys.exit(1)

    # 3. Test run_self_corrective_rag (Agentic RAG corrective loop)
    try:
        def mock_retrieve(q):
            if "relic" in q:
                return ["Relic Found"]
            return ["No results"]
        
        def mock_evaluate(chunks):
            return "Relic Found" in chunks
            
        def mock_rewrite(q):
            return q + " relic"
            
        # Case A: Succeeds on first try
        res_first = module.run_self_corrective_rag("relic query", mock_retrieve, mock_evaluate, mock_rewrite)
        if res_first["status"] != "success" or res_first["steps"] != 0 or res_first["context"] != ["Relic Found"]:
            print(f"Error: run_self_corrective_rag failed on first try. Got {res_first}")
            sys.exit(1)
        
        # Case B: Succeeds after rewrite
        res_rewrite = module.run_self_corrective_rag("query", mock_retrieve, mock_evaluate, mock_rewrite)
        if res_rewrite["status"] != "success" or res_rewrite["steps"] != 1 or res_rewrite["context"] != ["Relic Found"]:
            print(f"Error: run_self_corrective_rag failed after rewrite. Got {res_rewrite}")
            sys.exit(1)
        
        # Case C: Fails after max steps
        res_fail = module.run_self_corrective_rag("unrelated", mock_retrieve, mock_evaluate, lambda q: q, max_steps=2)
        if res_fail["status"] != "failed" or res_fail["steps"] != 2:
            print(f"Error: run_self_corrective_rag failed to abort on max steps. Got {res_fail}")
            sys.exit(1)
        
        print("Self-Corrective Agentic RAG loop: PASS")
    except Exception as e:
        print(f"Error testing run_self_corrective_rag: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 18 tests passed! Spooky Town lineage records complete.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_18()
