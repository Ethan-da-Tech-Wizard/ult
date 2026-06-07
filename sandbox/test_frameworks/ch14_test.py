import os
import sys
import numpy as np

def test_chapter_14():
    print("Testing Chapter 14: Fine-Tuning Fiord (LoRA Adapter)...")
    solution_path = "/workspace/ch14_lora.py"
    if not os.path.exists(solution_path):
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

if __name__ == "__main__":
    test_chapter_14()
