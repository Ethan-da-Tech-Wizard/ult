import os
import sys
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

    try:
        # Mock file check
        mock_img = "mock_scanned_relic.png"
        with open(mock_img, "w") as f:
            f.write("mock png payload")
            
        # Run test pipeline
        result = module.run_assembler_pipeline(
            image_path=mock_img,
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
        if not result["ocr_text"]:
            print("Error: Pipeline returned empty OCR results.")
            sys.exit(1)
            
        if not isinstance(result["db_results"], list):
            print("Error: Database results should be returned as a list of matching records.")
            sys.exit(1)
            
        print("Integrated pipeline coordination: PASS")
        
    except Exception as e:
        print(f"Error testing run_assembler_pipeline: {e}")
        sys.exit(1)
    finally:
        # Cleanup mock files
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(mock_img):
            os.remove(mock_img)

    print("\n>>> All Chapter 20 tests passed! The Grand Assembly pipeline is fully synchronized.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_20()
