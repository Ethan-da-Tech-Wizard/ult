# ==============================================================================
# Program: ch9_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating Layer Normalization and SGD backpropagation weight updates. Evaluates row-wise statistical mean/variance calculation and mean squared error gradient descent.
# ==============================================================================

# How this file fits the app: the validator for chapter 9. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch9_forge.py.
# What it checks: layernorm_forward(x,gamma,beta) must give rows with mean 0 and std 1;
# training_step(weights,inputs,targets,lr) must return weights that differ from the input (a gradient step
# happened).
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch9_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside
# this process; use the Docker sandbox for untrusted code.
import os
import sys
import numpy as np

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_9():
    print("Testing Chapter 9: Forge of Zeus LayerNorm & Residual Skips...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch9_forge.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch9_forge.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch9_forge.py' not found.")
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

    if not hasattr(module, "layernorm_forward") or not hasattr(module, "training_step"):
        print("Error: Solution must define 'layernorm_forward' and 'training_step' functions.")
        sys.exit(1)

    # Test LayerNorm forward calculations
    x = np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]])
    gamma = np.array([1.0, 1.0, 1.0])
    beta = np.array([0.0, 0.0, 0.0])
    
    try:
        out = module.layernorm_forward(x, gamma, beta)
        
        # Expected properties of layer normalization:
        # Each row should have mean ~ 0 and standard deviation ~ 1
        for row in out:
            mean = np.mean(row)
            std = np.std(row)
            if not np.isclose(mean, 0.0, atol=1e-4):
                print(f"Error: Normalized row mean is not zero: {mean}")
                sys.exit(1)
            if not np.isclose(std, 1.0, atol=1e-4):
                print(f"Error: Normalized row standard deviation is not one: {std}")
                sys.exit(1)
                
        print("LayerNorm calculations: OK")
    except Exception as e:
        print(f"Error testing layernorm_forward: {e}")
        sys.exit(1)

    # Test PyTorch Backprop Training iteration
    try:
        # Mock weights update check
        # training_step(weights, inputs, targets, lr) returns updated weights
        w_init = np.array([0.5, 0.5])
        inputs = np.array([1.0, 2.0])
        targets = 5.0
        w_new = module.training_step(w_init, inputs, targets, lr=0.1)
        
        if np.allclose(w_new, w_init):
            print("Error: Backpropagation step did not modify model weights. Check gradient descent updates.")
            sys.exit(1)
            
        print("Backpropagation gradient update: OK")
    except Exception as e:
        print(f"Error testing training_step: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 9 tests passed! Forge of Zeus compiler online.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_9()
