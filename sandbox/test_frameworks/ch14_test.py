# ==============================================================================
# Program: ch14_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating Low-Rank Adaptation (LoRA) matrix factorizations. Evaluates low-rank delta matrix projections, scaling hyperparameters, and merged weight tensor recovery.
# ==============================================================================

# How this file fits the app: the validator for chapter 14. server/sandbox_manager.py runs it (inside the zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile, after server/main.py has saved the player's code as save_data/relic_save/ch14_lora.py.
# What it checks: lora_forward(x,W0,A,B,alpha,r) must equal x@W0.T + (alpha/r)*((x@A.T)@B.T), and merge_weights(W0,A,B,alpha,r) must equal the merged weight matrix, both on random numpy data with a fixed seed (rtol 1e-5).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so messages are written for learners. Run it by hand from the repo root: python3 sandbox/test_frameworks/ch14_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside this process; use the Docker sandbox for untrusted code.
import os
import sys
import numpy as np

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of returning a value.
def test_chapter_14():
    print("Testing Chapter 14: Fine-Tuning Fiord (LoRA Adapter)...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch14_lora.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch14_lora.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch14_lora.py' not found.")
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

    if not hasattr(module, "lora_forward") or not hasattr(module, "merge_weights"):
        print("Error: Solution must define 'lora_forward' and 'merge_weights' functions.")
        sys.exit(1)

    # Dimensions
    N, d_in, d_out, r = 2, 4, 3, 2
    alpha = 4.0

    # Mock inputs
    np.random.seed(42)
    x = np.random.randn(N, d_in)
    W0 = np.random.randn(d_out, d_in)
    A = np.random.randn(r, d_in)
    B = np.random.randn(d_out, r)

    # 1. Test LoRA Forward pass
    try:
        out = module.lora_forward(x, W0, A, B, alpha, r)
        
        # Expected manual calculation
        expected_base = x @ W0.T
        expected_delta = (x @ A.T) @ B.T
        expected_out = expected_base + (alpha / r) * expected_delta
        
        if not np.allclose(out, expected_out, rtol=1e-5):
            print("Error: lora_forward output does not match expected scaled values.")
            print(f"Got:\n{out}\nExpected:\n{expected_out}")
            sys.exit(1)
        print("LoRA forward pass scaling check: PASS")
    except Exception as e:
        print(f"Error testing lora_forward: {e}")
        sys.exit(1)

    # 2. Test Weight Merging
    try:
        merged = module.merge_weights(W0, A, B, alpha, r)
        
        # Expected: W_merged = W0 + (alpha/r) * B @ A
        expected_merged = W0 + (alpha / r) * (B @ A)
        
        if not np.allclose(merged, expected_merged, rtol=1e-5):
            print("Error: merge_weights output does not match expected merged matrix.")
            print(f"Got:\n{merged}\nExpected:\n{expected_merged}")
            sys.exit(1)
        print("LoRA weight merging check: PASS")
    except Exception as e:
        print(f"Error testing merge_weights: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 14 tests passed! LoRA parameter fine-tuning operational.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_14()
