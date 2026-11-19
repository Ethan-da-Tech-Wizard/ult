# ==============================================================================
# Program: ch16_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating symmetric INT8 neural network quantization. Evaluates dynamic absolute maximum scaling, round-and-clamp clipping bounds, and floating-point dequantization.
# ==============================================================================

# How this file fits the app: the validator for chapter 16. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch16_quant.py.
# What it checks: quantize_symmetric(x) must return (int tensor, scale) with scale = max|x| / 127 (here
# 10/127); dequantize_symmetric(q, scale) must return the expected reconstructed floats (rtol 1e-5).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch16_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys
import numpy as np

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_16():
    print("Testing Chapter 16: Deployment Cliffs (Model Quantization)...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch16_quant.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch16_quant.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch16_quant.py' not found.")
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

    if not hasattr(module, "quantize_symmetric") or not hasattr(module, "dequantize_symmetric"):
        print("Error: Solution must define 'quantize_symmetric' and 'dequantize_symmetric' functions.")
        sys.exit(1)

    # Test array
    x = np.array([-5.0, -2.5, 0.0, 1.25, 10.0])

    # 1. Test Quantization
    try:
        q_tensor, scale = module.quantize_symmetric(x)
        
        # Max absolute value is 10.0
        # Expected scale S = 10.0 / 127 = 0.07874...
        expected_scale = 10.0 / 127
        if not np.isclose(scale, expected_scale, rtol=1e-5):
            print(f"Error: Calculated scale {scale} does not match expected symmetric scale {expected_scale}")
            sys.exit(1)
            
        # Check quantized values: round(x / S) clamped to [-127, 127]
        expected_q = np.round(x / expected_scale).astype(np.int8)
        if not np.array_equal(q_tensor, expected_q):
            print(f"Error: Quantized INT8 values do not match expected arrays.\nGot: {q_tensor}\nExpected: {expected_q}")
            sys.exit(1)
            
        print("Symmetric INT8 quantization: PASS")
    except Exception as e:
        print(f"Error testing quantize_symmetric: {e}")
        sys.exit(1)

    # 2. Test Dequantization
    try:
        dequantized = module.dequantize_symmetric(q_tensor, scale)
        expected_dequant = q_tensor.astype(np.float32) * scale
        
        if not np.allclose(dequantized, expected_dequant, rtol=1e-5):
            print(f"Error: Dequantized values do not match.\nGot: {dequantized}\nExpected: {expected_dequant}")
            sys.exit(1)
            
        # Reconstructed values should be close to original
        max_error = np.max(np.abs(x - dequantized))
        if max_error > (scale / 2.0 + 1e-4):
            print(f"Error: Reconstructed error {max_error} exceeds expected quantization bounds.")
            sys.exit(1)
            
        print("Symmetric INT8 dequantization: PASS")
    except Exception as e:
        print(f"Error testing dequantize_symmetric: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 16 tests passed! INT8 quantization operations validated.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_16()
