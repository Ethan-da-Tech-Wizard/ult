# ==============================================================================
# Program: ch12_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating Neo4j Cypher graph traversal syntax generation. Asserts that shortestPath queries properly structure node patterns, edge wildcards, and return bindings.
# ==============================================================================

# How this file fits the app: the validator for chapter 12. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch12_graph.py.
# What it checks: generate_cypher_path_walk('UserDB','Transformer') must return a Cypher string containing
# MATCH and RETURN, plus either shortestPath or an edge pattern '-['.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch12_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_12():
    print("Testing Chapter 12: Graph Gardens Cypher Relationship Traversals...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch12_graph.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch12_graph.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch12_graph.py' not found.")
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_12()
