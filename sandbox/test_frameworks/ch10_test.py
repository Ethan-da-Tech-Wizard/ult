import os
import sys

def test_chapter_10():
    print("Testing Chapter 10: Reranking Reefs Hybrid Blend...")
    solution_path = "/workspace/ch10_search.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch10_search.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch10_search.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "hybrid_search_blend"):
        print("Error: Solution must define the 'hybrid_search_blend' function.")
        sys.exit(1)

    # Test hybrid score blending outputs
    # scores dictionaries mapping document_id: float
    bm25 = {"doc1": 0.8, "doc2": 0.2, "doc3": 0.5}
    cosine = {"doc1": 0.4, "doc2": 0.9, "doc3": 0.6}
    
    try:
        # Test 1: alpha = 0.5
        blended = module.hybrid_search_blend(bm25, cosine, alpha=0.5)
        # Expected scores:
        # doc1: 0.5*0.8 + 0.5*0.4 = 0.60
        # doc2: 0.5*0.2 + 0.5*0.9 = 0.55
        # doc3: 0.5*0.5 + 0.5*0.6 = 0.55
        # Sorted result expected: [("doc1", 0.60), ("doc2", 0.55), ("doc3", 0.55)] (or doc3, doc2 depending on tie break)
        
        if blended[0][0] != "doc1":
            print(f"Error: Hybrid sorting failed. Got {blended}, expected doc1 to be top.")
            sys.exit(1)
            
        print("Score blending calculations: OK")
        
        # Test 2: alpha = 1.0 (pure BM25)
        blended_pure = module.hybrid_search_blend(bm25, cosine, alpha=1.0)
        # doc1: 0.8, doc3: 0.5, doc2: 0.2
        if blended_pure[0][0] != "doc1" or blended_pure[1][0] != "doc3" or blended_pure[2][0] != "doc2":
            print("Error: Pure BM25 filtering failed.")
            sys.exit(1)
            
        print("Alpha bounds verification: OK")
    except Exception as e:
        print(f"Error testing hybrid_search_blend: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 10 tests passed! Hybrid search indexing configured.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_10()
