# Program: ult - ch3_test.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Automated check for chapter 3 (Document Dunes Caching & Polymorphism): inspects the player's saved solution and exits 0 on pass or 1 on failure.

import os
import sys
import time

def test_chapter_3():
    """Locate the chapter 3 solution (sandbox workspace first, local save folder as fallback), run the checks, print the result and exit with a status code."""
    print("Testing Chapter 3: Document Dunes Caching & Polymorphism...")
    # Inside the sandbox the player's file lives under /workspace.
    solution_path = "/workspace/ch3_nosql.py"
    if not os.path.exists(solution_path):
        # Not found there, so fall back to the local save folder (running outside the sandbox).
        solution_path = "save_data/relic_save/ch3_nosql.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch3_nosql.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "PolymorphicItemParser") or not hasattr(module, "TimedCache"):
        print("Error: Solution must define 'PolymorphicItemParser' and 'TimedCache' classes.")
        sys.exit(1)

    # Test Polymorphic JSON parsing
    try:
        parser = module.PolymorphicItemParser()
        weapon_json = '{"type": "weapon", "name": "Assembly Sword", "atk": 40}'
        armor_json = '{"type": "armor", "name": "Dockerized Plate", "def": 18}'
        
        weapon_obj = parser.parse(weapon_json)
        armor_obj = parser.parse(armor_json)
        
        if weapon_obj.get("atk") != 40 or armor_obj.get("def") != 18:
            print("Error: PolymorphicItemParser failed to distinguish fields.")
            sys.exit(1)
        print("Polymorphic parsing: OK")
    except Exception as e:
        print(f"Error testing PolymorphicItemParser: {e}")
        sys.exit(1)

    # Test Timed Cache expiration
    try:
        cache = module.TimedCache(ttl_seconds=1)
        cache.set("relic_key", "KEY_VAL_DB")
        
        # Immediate read
        if cache.get("relic_key") != "KEY_VAL_DB":
            print("Error: TimedCache failed to retrieve active key value.")
            sys.exit(1)
            
        print("Waiting for cache TTL expiration...")
        time.sleep(1.2)
        
        # Expired read
        if cache.get("relic_key") is not None:
            print("Error: TimedCache did not expire key after TTL timeout.")
            sys.exit(1)
        print("Timed cache TTL eviction: OK")
    except Exception as e:
        print(f"Error testing TimedCache: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 3 tests passed! Document store database configured.")
    sys.exit(0)

# Run the check only when executed as a script, not when imported.
if __name__ == "__main__":
    test_chapter_3()
