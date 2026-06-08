import os
import sys

def test_chapter_7():
    print("Testing Chapter 7: Whispering Woods BPE Tokenizer...")
    solution_path = "/workspace/ch7_token.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch7_token.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch7_token.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "bpe_encode"):
        print("Error: Solution must define the 'bpe_encode' function.")
        sys.exit(1)

    # Test BPE encoding using a mock vocabulary merge dictionary
    # merges: maps tuple of characters/tokens to a merged token string
    vocab_merges = {
        ("t", "h"): "th",
        ("e", "s"): "es",
        ("th", "e"): "the"
    }
    
    try:
        # Test 1: Simple string
        tokens_out = module.bpe_encode("these", vocab_merges)
        # Expected merge progression:
        # t h e s e -> th e s e -> the s e -> the es
        expected = ["the", "es"]
        
        if tokens_out != expected:
            print(f"Error: BPE tokenization failed. Got {tokens_out}, expected {expected}")
            sys.exit(1)
            
        print("Subword tokenization merges: OK")
    except Exception as e:
        print(f"Error testing bpe_encode: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 7 tests passed! Whispering Woods tokenizer active.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_7()
