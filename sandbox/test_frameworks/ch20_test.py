import os
import sys
import json
import sqlite3

def test_chapter_20():
    print("Testing Chapter 20: The Grand Assembly (Integrated Pipeline)...")
    solution_path = "/workspace/ch20_pipeline.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch20_pipeline.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch20_pipeline.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
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

if __name__ == "__main__":
    test_chapter_20()
