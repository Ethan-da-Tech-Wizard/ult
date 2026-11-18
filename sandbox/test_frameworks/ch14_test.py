# Program: ult - ch14_test.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Automated check for chapter 14 (Fine-Tuning Fiord (LoRA Adapter)): inspects the player's saved solution and exits 0 on pass or 1 on failure.

import os
import sys
import numpy as np

def test_chapter_14():
    """Locate the chapter 14 solution (sandbox workspace first, local save folder as fallback), run the checks, print the result and exit with a status code."""
    print("Testing Chapter 14: Fine-Tuning Fiord (LoRA Adapter)...")
    # Inside the sandbox the player's file lives under /workspace.
    solution_path = "/workspace/ch14_lora.py"
    if not os.path.exists(solution_path):
        # Not found there, so fall back to the local save folder (running outside the sandbox).
        solution_path = "save_data/relic_save/ch14_lora.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch14_lora.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
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

# Run the check only when executed as a script, not when imported.
if __name__ == "__main__":
    test_chapter_14()
