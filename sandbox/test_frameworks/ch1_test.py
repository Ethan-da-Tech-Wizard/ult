import os
import sys

def test_chapter_1():
    print("Testing Chapter 1: Alexandria Library OCR Prep...")
    solution_path = "/workspace/ch1_ocr.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch1_ocr.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch1_ocr.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "monochrome_filter") or not hasattr(module, "threshold_filter"):
        print("Error: Solution must define 'monochrome_filter' and 'threshold_filter' functions.")
        sys.exit(1)

    # Test grayscale conversions on mock RGB matrix
    mock_rgb = [
        [(255, 0, 0), (0, 255, 0)],
        [(0, 0, 255), (255, 255, 255)]
    ]
    try:
        gray_out = module.monochrome_filter(mock_rgb)
        # Expected outputs: Gray = 0.299*R + 0.587*G + 0.114*B or simple average
        # We verify it returns a 2D grid of numbers
        if len(gray_out) != 2 or len(gray_out[0]) != 2:
            print("Error: monochrome_filter must return a 2D matrix matching dimensions.")
            sys.exit(1)
        print("Grayscale matrix conversion: OK")
    except Exception as e:
        print(f"Error in monochrome_filter: {e}")
        sys.exit(1)

    # Test binarized threshold logic
    mock_gray = [
        [100, 200],
        [50, 150]
    ]
    try:
        binary_out = module.threshold_filter(mock_gray, 120)
        # Values > 120 -> 255, <= 120 -> 0
        expected = [
            [0, 255],
            [0, 255]
        ]
        if binary_out != expected:
            print(f"Error: threshold_filter failed. Got {binary_out}, expected {expected}")
            sys.exit(1)
        print("Binary threshold classification: OK")
    except Exception as e:
        print(f"Error in threshold_filter: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 1 tests passed! Library OCR parser active.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_1()
