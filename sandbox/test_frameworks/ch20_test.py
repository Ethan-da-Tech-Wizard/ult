# ==============================================================================
# Program: ch20_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating end-to-end multi-modal pipeline integration. Evaluates spatial bounding box line grouping, relational database lookup, and synthetic response composition.
# ==============================================================================

# How this file fits the app: the validator for chapter 20. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch20_pipeline.py.
# What it checks: run_assembler_pipeline(layout_json_path, query_text, db_path) is run on a layout JSON of
# word boxes and a SQLite database built by this test; the result must contain ocr_text, db_results,
# graph_context and llm_response, the OCR text must contain 'Zeus Relic Shield' and 'Power: 95', and the first
# database row must have id ITM001.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch20_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys
import json
import sqlite3

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_20():
    print("Testing Chapter 20: The Grand Assembly (Integrated Pipeline)...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch20_pipeline.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch20_pipeline.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch20_pipeline.py' not found.")
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

    if not hasattr(module, "run_assembler_pipeline"):
        print("Error: Solution must define 'run_assembler_pipeline' function.")
        sys.exit(1)

    # Setup a mock test SQLite DB to verify DB hookup
    test_db_path = "test_assembly.db"
    try:
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS inventory (item_id TEXT PRIMARY KEY, name TEXT, power INT)")
        cursor.execute("INSERT OR REPLACE INTO inventory VALUES ('ITM001', 'Zeus Relic Shield', 95)")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Mock database setup issue: {e}")

    mock_json = "mock_scanned_relic.json"
    try:
        # Mock OCR layout JSON with coordinates
        # Group 1: "Zeus" (10) + "Relic" (50) + "Shield" (105) -> distances 10 and 15 -> merged into "Zeus Relic Shield"
        # Group 2: "Power:" (10) + "95" (60) -> distance 10 -> merged into "Power: 95"
        layout_data = [
            {"text": "Zeus", "x": 10, "y": 10, "w": 30, "h": 10},
            {"text": "Relic", "x": 50, "y": 10, "w": 40, "h": 10},
            {"text": "Shield", "x": 105, "y": 10, "w": 50, "h": 10},
            {"text": "Power:", "x": 10, "y": 30, "w": 40, "h": 10},
            {"text": "95", "x": 60, "y": 30, "w": 20, "h": 10}
        ]
        with open(mock_json, "w") as f:
            json.dump(layout_data, f)
            
        # Run test pipeline
        result = module.run_assembler_pipeline(
            layout_json_path=mock_json,
            query_text="Find power levels for our shield item",
            db_path=test_db_path
        )
        
        # Verify response keys
        required_keys = ["ocr_text", "db_results", "graph_context", "llm_response"]
        for key in required_keys:
            if key not in result:
                print(f"Error: Pipeline result is missing key: '{key}'")
                sys.exit(1)
                
        print("Pipeline schema verification: PASS")
        
        # Verify content integration
        if "Zeus Relic Shield" not in result["ocr_text"] or "Power: 95" not in result["ocr_text"]:
            print(f"Error: Pipeline returned incorrect OCR grouping results. Got:\n{result['ocr_text']}")
            sys.exit(1)
            
        if not isinstance(result["db_results"], list) or len(result["db_results"]) == 0 or result["db_results"][0][0] != 'ITM001':
            print(f"Error: Database results should return the matching 'Zeus Relic Shield' record. Got: {result.get('db_results')}")
            sys.exit(1)
            
        print("Integrated pipeline coordination: PASS")
        
    except Exception as e:
        print(f"Error testing run_assembler_pipeline: {e}")
        sys.exit(1)
    finally:
        # Cleanup mock files
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(mock_json):
            os.remove(mock_json)

    print("\n>>> All Chapter 20 tests passed! The Grand Assembly pipeline is fully synchronized.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_20()
