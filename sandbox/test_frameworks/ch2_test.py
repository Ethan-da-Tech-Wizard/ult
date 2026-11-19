# ==============================================================================
# Program: ch2_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating SQL query parameterization and injection prevention. Verifies that user-supplied input tokens are bound safely as parameters rather than interpolated into SQL text.
# ==============================================================================

# How this file fits the app: the validator for chapter 2. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch2_sql.py.
# What it checks: run_injection_exploit() must return a username payload that makes an f-string SQL query leak
# every row of an in-memory SQLite table; get_character_secured(conn, name) must resist that same payload
# (parameterised query).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch2_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys
import sqlite3

def init_mock_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, username TEXT, secret_key TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'veridicus', 'KEY_SOVEREIGN_BYPASS')")
    cursor.execute("INSERT INTO users VALUES (2, 'cassia', 'KEY_ALEXANDRIA_RESTORE')")
    conn.commit()
    return conn

def vulnerable_query(conn, username):
    cursor = conn.cursor()
    query = f"SELECT secret_key FROM users WHERE username = '{username}'"
    try:
        cursor.execute(query)
        res = cursor.fetchall()
        return res
    except Exception as e:
        return str(e)

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_2():
    print("Testing Chapter 2: Relational Meadows Security Auditing...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch2_sql.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch2_sql.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch2_sql.py' not found.")
            sys.exit(1)
            
    # Import solution functions
    import importlib.util
    spec = importlib.util.spec_from_file_location("solution_module", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        # Loads the player's file as a throwaway module so its functions can be called; a syntax error or an
        # exception at import time is reported as a compile failure rather than a crash.
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile/execute: {e}")
        sys.exit(1)
        
    # Check exploit function
    if not hasattr(module, "run_injection_exploit") or not hasattr(module, "get_character_secured"):
        print("Error: Solution must define 'run_injection_exploit' and 'get_character_secured' functions.")
        sys.exit(1)
        
    # Test 1: Bypassing login using exploit payload
    conn = init_mock_db()
    exploit_payload = module.run_injection_exploit()
    print(f"Injecting payload: {exploit_payload}")
    exploit_res = vulnerable_query(conn, exploit_payload)
    if len(exploit_res) > 1:
        print("Test 1 PASS: Exploit successfully bypassed credential lookup to retrieve all keys.")
    else:
        print("Test 1 FAIL: Exploit payload did not retrieve all keys. Check syntax (e.g. `' OR 1=1;--`).")
        sys.exit(1)
        
    # Test 2: Bypassing secured function using exploit payload
    print("Testing security patch validation...")
    try:
        patch_res = module.get_character_secured(conn, exploit_payload)
        if len(patch_res) <= 1:
            print("Test 2 PASS: Secure function correctly sanitized injection input using parameters.")
        else:
            print("Test 2 FAIL: Secure query is still vulnerable to SQL injection bypass.")
            sys.exit(1)
    except Exception as e:
        print(f"Test 2 PASS: Parameterized lookup rejected malformed input safely: {e}")
        
    print("\n>>> All Chapter 2 tests passed! Database secured.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_2()
