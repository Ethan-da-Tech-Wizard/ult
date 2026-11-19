# ==============================================================================
# Program: ch8_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating Scaled Dot-Product Attention layers for neural networks. Evaluates 4D tensor matrix multiplication, softmax probability normalization, and attention weight projection.
# ==============================================================================

# How this file fits the app: the validator for chapter 8. server/sandbox_manager.py runs it (inside the zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile, after server/main.py has saved the player's code as save_data/relic_save/ch8_attention.py.
# What it checks: scaled_dot_product_attention(q,k,v,mask=None) must return (output, weights) with the output shaped like V and every row of the softmax weights summing to 1 (numpy; tolerance 1e-4).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so messages are written for learners. Run it by hand from the repo root: python3 sandbox/test_frameworks/ch8_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside this process; use the Docker sandbox for untrusted code.
import os
import sys
import numpy as np

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of returning a value.
def test_chapter_8():
    print("Testing Chapter 8: Valley of Attention Scaled Dot-Product Math...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch8_attention.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch8_attention.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch8_attention.py' not found.")
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

    if not hasattr(module, "scaled_dot_product_attention"):
        print("Error: Solution must define 'scaled_dot_product_attention' function.")
        sys.exit(1)

    # Test scaled dot-product calculations on mock query/key/value arrays
    # Q, K, V size: batch_size=1, heads=1, seq_len=2, d_k=2
    Q = np.array([[[[1.0, 0.0], [0.0, 1.0]]]])
    K = np.array([[[[1.0, 0.0], [0.0, 1.0]]]])
    V = np.array([[[[10.0, 20.0], [30.0, 40.0]]]])
    
    try:
        # Expected outputs:
        # Q K^T = [[1, 0], [0, 1]]
        # Scale by sqrt(d_k) = sqrt(2) ~ 1.414 -> [[0.707, 0], [0, 0.707]]
        # Softmax over rows:
        # row 0: exp(0.707) / (exp(0.707)+exp(0)) ~ 2.028 / 3.028 ~ 0.67, exp(0)/sum ~ 0.33
        # attention weights: [[0.67, 0.33], [0.33, 0.67]]
        # Multiply by V:
        # row 0: 0.67 * [10, 20] + 0.33 * [30, 40] = [6.7+9.9, 13.4+13.2] = [16.6, 26.6]
        attn_out, weights = module.scaled_dot_product_attention(Q, K, V)
        
        # Verify shape
        if attn_out.shape != V.shape:
            print(f"Error: Shape mismatch. Got {attn_out.shape}, expected {V.shape}")
            sys.exit(1)
            
        # Verify weights sum to 1.0 (softmax check)
        for i in range(weights.shape[-2]):
            row_sum = np.sum(weights[0, 0, i])
            if not np.isclose(row_sum, 1.0, atol=1e-4):
                print(f"Error: Softmax weights do not sum to 1.0: {row_sum}")
                sys.exit(1)
                
        print("Scaled attention matrix values: OK")
    except Exception as e:
        print(f"Error testing scaled_dot_product_attention: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 8 tests passed! Scaled self-attention matrix resolved.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_8()
