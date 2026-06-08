import os
import sys
import numpy as np

def test_chapter_16():
    print("Testing Chapter 16: Deployment Cliffs (Model Quantization)...")
    solution_path = "/workspace/ch16_quant.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch16_quant.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch16_quant.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
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

if __name__ == "__main__":
    test_chapter_16()
