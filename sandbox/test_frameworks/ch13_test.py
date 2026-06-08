import os
import sys
import math

def calculate_lcs(x, y):
    m = len(x)
    n = len(y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif x[i - 1] == y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L[m][n]

def test_chapter_13():
    print("Testing Chapter 13: Testing Tundra Model Evaluations...")
    solution_path = "/workspace/ch13_eval.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch13_eval.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch13_eval.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "calculate_bleu") or not hasattr(module, "calculate_rouge_l"):
        print("Error: Solution must define 'calculate_bleu' and 'calculate_rouge_l' functions.")
        sys.exit(1)

    # Test inputs
    hypothesis1 = "the quick brown fox jumps over the lazy dog"
    reference1 = "the quick brown fox jumps over a lazy dog"

    # BLEU calculation verification (1-gram precision with brevity penalty)
    try:
        bleu = module.calculate_bleu(hypothesis1, reference1)
        # 1-gram tokens:
        # hypo: ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'] (length 9)
        # ref: ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'a', 'lazy', 'dog'] (length 9)
        # Overlapping 1-gram counts (clipped to max in ref):
        # 'the' -> ref has 1, hypo has 2, clipped count is 1
        # 'quick' -> 1
        # 'brown' -> 1
        # 'fox' -> 1
        # 'jumps' -> 1
        # 'over' -> 1
        # 'lazy' -> 1
        # 'dog' -> 1
        # Total overlapping = 8. Hypo len = 9. Precision = 8/9.
        # Brevity penalty: c=9, r=9, BP=1.0.
        # BLEU-1 = 1.0 * (8/9) = 0.88888...
        expected_bleu = 8 / 9
        if not math.isclose(bleu, expected_bleu, rel_tol=1e-3):
            print(f"Error: calculate_bleu returned {bleu}, expected approximately {expected_bleu:.4f}")
            sys.exit(1)
        print("BLEU calculation check: PASS")
    except Exception as e:
        print(f"Error testing calculate_bleu: {e}")
        sys.exit(1)

    # ROUGE-L calculation verification
    try:
        rouge_l = module.calculate_rouge_l(hypothesis1, reference1)
        # LCS(hypo, ref) is "the quick brown fox jumps over lazy dog" (length 8 tokens)
        # Recall R = LCS / len(ref) = 8 / 9
        # Precision P = LCS / len(hypo) = 8 / 9
        # F1 = 2 * P * R / (P + R) = 8 / 9 = 0.88888...
        expected_rouge = 8 / 9
        if not math.isclose(rouge_l, expected_rouge, rel_tol=1e-3):
            print(f"Error: calculate_rouge_l returned {rouge_l}, expected approximately {expected_rouge:.4f}")
            sys.exit(1)
        print("ROUGE-L calculation check: PASS")
    except Exception as e:
        print(f"Error testing calculate_rouge_l: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 13 tests passed! Model evaluation suite active.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_13()
