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

def test_chapter_2():
    print("Testing Chapter 2: Relational Meadows Security Auditing...")
    solution_path = "/workspace/ch2_sql.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch2_sql.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch2_sql.py' not found.")
            sys.exit(1)
            
    # Import student functions
    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
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

if __name__ == "__main__":
    test_chapter_2()
