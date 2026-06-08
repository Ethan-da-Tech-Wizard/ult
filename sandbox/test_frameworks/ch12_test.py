import os
import sys

def test_chapter_12():
    print("Testing Chapter 12: Graph Gardens Cypher Relationship Traversals...")
    solution_path = "/workspace/ch12_graph.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch12_graph.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch12_graph.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "generate_cypher_path_walk"):
        print("Error: Solution must define 'generate_cypher_path_walk' function.")
        sys.exit(1)

    # Test Cypher string output formatting
    try:
        cypher = module.generate_cypher_path_walk("UserDB", "Transformer")
        print(f"Generated Cypher Query:\n{cypher}\n")
        
        # We assert that the query matches standard path lookup operations
        if "MATCH" not in cypher or "RETURN" not in cypher:
            print("Error: Invalid Cypher format. Missing MATCH or RETURN clauses.")
            sys.exit(1)
            
        if "shortestPath" not in cypher and "-[" not in cypher:
            print("Error: Query does not traverse relationships. Must specify path walks (e.g. shortestPath or relationship arrows).")
            sys.exit(1)
            
        print("Cypher path matching: OK")
    except Exception as e:
        print(f"Error testing generate_cypher_path_walk: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 12 tests passed! Graph Gardens traverses active.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_12()
