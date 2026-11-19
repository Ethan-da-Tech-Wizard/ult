# ==============================================================================
# Program: ch7_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating Byte Pair Encoding (BPE) subword tokenization algorithms. Evaluates iterative vocabulary merges and boundary preservation on natural language strings.
# ==============================================================================

# How this file fits the app: the validator for chapter 7. server/sandbox_manager.py runs it (inside the zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile, after server/main.py has saved the player's code as save_data/relic_save/ch7_token.py.
# What it checks: bpe_encode(text, merges) must apply byte-pair merges in order: with merges (t,h)->th, (e,s)->es, (th,e)->the the word 'these' must encode to ['the','es'].
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so messages are written for learners. Run it by hand from the repo root: python3 sandbox/test_frameworks/ch7_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside this process; use the Docker sandbox for untrusted code.
import os
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of returning a value.
def test_chapter_7():
    print("Testing Chapter 7: Whispering Woods BPE Tokenizer...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch7_token.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch7_token.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch7_token.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("solution_module", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        # Loads the player's file as a throwaway module so its functions can be called; a syntax error or an exception at import time is reported as a compile failure rather than a crash.
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_7()
