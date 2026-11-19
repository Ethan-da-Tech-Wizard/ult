# ==============================================================================
# Program: ch3_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating in-memory key-value caching engines with TTL expiration semantics. Validates polymorphic JSON payload deserialization and cache eviction deadlines.
# ==============================================================================

# How this file fits the app: the validator for chapter 3. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch3_nosql.py.
# What it checks: PolymorphicItemParser.parse() must return a dict with the right fields for weapon and armor
# JSON; TimedCache(ttl_seconds) must return a value immediately and None after the TTL (the test sleeps 1.2
# s).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch3_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys
import time

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_3():
    print("Testing Chapter 3: Document Dunes Caching & Polymorphism...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch3_nosql.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch3_nosql.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch3_nosql.py' not found.")
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_3()
