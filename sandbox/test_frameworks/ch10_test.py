import os
import sys

def test_chapter_10():
    print("Testing Chapter 10: Reranking Reefs Advanced RAG...")
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

    # Verify functions exist
    required_fns = ["hybrid_search_blend", "expand_query", "rerank_and_filter"]
    for fn in required_fns:
        if not hasattr(module, fn):
            print(f"Error: Solution must define the '{fn}' function.")
            sys.exit(1)

    # 1. Test expand_query (Pre-Retrieval query expansion)
    try:
        query = "relic shield power"
        expansions = module.expand_query(query)
        if not isinstance(expansions, list) or len(expansions) < 2:
            print("Error: expand_query must return a list of query variations.")
            sys.exit(1)
        if any(not isinstance(q, str) for q in expansions):
            print("Error: All query expansions must be strings.")
            sys.exit(1)
        print("Pre-Retrieval query expansion: OK")
    except Exception as e:
        print(f"Error testing expand_query: {e}")
        sys.exit(1)

    # 2. Test hybrid score blending calculations
    bm25 = {"doc1": 0.8, "doc2": 0.2, "doc3": 0.5}
    cosine = {"doc1": 0.4, "doc2": 0.9, "doc3": 0.6}
    
    try:
        # alpha = 0.5
        blended = module.hybrid_search_blend(bm25, cosine, alpha=0.5)
        # Expected scores:
        # doc1: 0.5*0.8 + 0.5*0.4 = 0.60
        # doc2: 0.5*0.2 + 0.5*0.9 = 0.55
        # doc3: 0.5*0.5 + 0.5*0.6 = 0.55
        
        if blended[0][0] != "doc1":
            print(f"Error: Hybrid sorting failed. Got {blended}, expected doc1 to be top.")
            sys.exit(1)
            
        print("Score blending calculations: OK")
        
        # alpha = 1.0 (pure BM25)
        blended_pure = module.hybrid_search_blend(bm25, cosine, alpha=1.0)
        if blended_pure[0][0] != "doc1" or blended_pure[1][0] != "doc3" or blended_pure[2][0] != "doc2":
            print("Error: Pure BM25 filtering failed.")
            sys.exit(1)
            
        print("Alpha bounds verification: OK")
    except Exception as e:
        print(f"Error testing hybrid_search_blend: {e}")
        sys.exit(1)

    # 3. Test rerank_and_filter (Post-Retrieval filtering heuristic)
    try:
        sample_results = [("doc1", 0.60), ("doc2", 0.55), ("doc3", 0.45)]
        filtered = module.rerank_and_filter(sample_results, threshold=0.50)
        doc_ids = [item[0] for item in filtered]
        if "doc3" in doc_ids:
            print("Error: rerank_and_filter failed to exclude items below relevance threshold.")
            sys.exit(1)
        if "doc1" not in doc_ids or "doc2" not in doc_ids:
            print("Error: rerank_and_filter excluded items above relevance threshold.")
            sys.exit(1)
        print("Post-Retrieval reranking and filtering: OK")
    except Exception as e:
        print(f"Error testing rerank_and_filter: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 10 tests passed! Advanced RAG indexing configured.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_10()
