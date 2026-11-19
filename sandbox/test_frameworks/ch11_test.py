# ==============================================================================
# Program: ch11_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating FastAPI service launch configurations. Asserts that HTTP server listeners are bound strictly to local loopback interfaces for security isolation.
# ==============================================================================

# How this file fits the app: the validator for chapter 11. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch11_api.py.
# What it checks: get_launch_config() must return a host that is 127.0.0.1 or localhost; a host of 0.0.0.0
# gets its own error message. This mirrors the real server's rule of binding to loopback only.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch11_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_11():
    print("Testing Chapter 11: API Archipelago Loopback Binding Security...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch11_api.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch11_api.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch11_api.py' not found.")
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_11()
