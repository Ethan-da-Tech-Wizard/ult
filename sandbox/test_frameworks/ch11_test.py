# Program: ult - ch11_test.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Automated check for chapter 11 (API Archipelago Loopback Binding Security): inspects the player's saved solution and exits 0 on pass or 1 on failure.

import os
import sys

def test_chapter_11():
    """Locate the chapter 11 solution (sandbox workspace first, local save folder as fallback), run the checks, print the result and exit with a status code."""
    print("Testing Chapter 11: API Archipelago Loopback Binding Security...")
    # Inside the sandbox the player's file lives under /workspace.
    solution_path = "/workspace/ch11_api.py"
    if not os.path.exists(solution_path):
        # Not found there, so fall back to the local save folder (running outside the sandbox).
        solution_path = "save_data/relic_save/ch11_api.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch11_api.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "get_launch_config"):
        print("Error: Solution must define the 'get_launch_config' configuration function.")
        sys.exit(1)

    # Verify launch parameters bound strictly to local loopback (127.0.0.1)
    try:
        config = module.get_launch_config()
        host = config.get("host", "")
        port = config.get("port", 0)
        
        print(f"Server configuration detected: {host}:{port}")
        
        if host == "0.0.0.0":
            print("Error: Port exposure vulnerability detected! Binding to '0.0.0.0' exposes your local API to anyone on your network. Correct to '127.0.0.1' to secure it.")
            sys.exit(1)
            
        if host not in ["127.0.0.1", "localhost"]:
            print(f"Error: Invalid binding host '{host}'. Server must bind strictly to local loopback interface.")
            sys.exit(1)
            
        print("Local port binding security check: PASS")
    except Exception as e:
        print(f"Error testing get_launch_config: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 11 tests passed! FastAPI local routing secure.")
    sys.exit(0)

# Run the check only when executed as a script, not when imported.
if __name__ == "__main__":
    test_chapter_11()
