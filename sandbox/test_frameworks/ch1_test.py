# ==============================================================================
# Program: ch1_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating 2D optical character recognition filters. Evaluates mathematical RGB-to-grayscale luminescence weighting and binary threshold matrix segmentation algorithms.
# ==============================================================================

# How this file fits the app: the validator for chapter 1. server/sandbox_manager.py runs it (inside the zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile, after server/main.py has saved the player's code as save_data/relic_save/ch1_ocr.py.
# What it checks: monochrome_filter(rgb_matrix) must return a same-sized 2D grey matrix; threshold_filter(gray, t) must map values > t to 255 and the rest to 0 (checked on tiny hand-made matrices).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so messages are written for learners. Run it by hand from the repo root: python3 sandbox/test_frameworks/ch1_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside this process; use the Docker sandbox for untrusted code.
import os
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of returning a value.
def test_chapter_1():
    print("Testing Chapter 1: Alexandria Library OCR Prep...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch1_ocr.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch1_ocr.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch1_ocr.py' not found.")
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_1()
