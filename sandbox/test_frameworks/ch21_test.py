# Program: ult - ch21_test.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Automated check for chapter 21 (Altar of TempleOS (Bare-Metal HolyC)): inspects the player's saved solution and exits 0 on pass or 1 on failure.

import os
import sys

def test_chapter_21():
    """Locate the chapter 21 solution (sandbox workspace first, local save folder as fallback), run the checks, print the result and exit with a status code."""
    print("Testing Chapter 21: Altar of TempleOS (Bare-Metal HolyC)...")
    # Inside the sandbox the player's file lives under /workspace.
    solution_path = "/workspace/ch21_altar.py"
    if not os.path.exists(solution_path):
        # Not found there, so fall back to the local save folder (running outside the sandbox).
        solution_path = "save_data/relic_save/ch21_altar.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch21_altar.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "validate_holyc_syntax") or not hasattr(module, "get_templeos_serial_command"):
        print("Error: Solution must define 'validate_holyc_syntax' and 'get_templeos_serial_command' functions.")
        sys.exit(1)

    # 1. Test HolyC Syntax Checker
    try:
        valid_holyc = """
        U0 ComputeChecksum() {
            Print("Computing Relic Checksums...\n");
            I64 sum = 0;
            for (I64 i = 0; i < 100; i++) {
                sum += i;
            }
            Print("Checksum: %d\n", sum);
        }
        ComputeChecksum();
        """
        
        invalid_holyc = """
        def compute_checksum():
            print("python syntax not allowed in TempleOS!")
        """

        if not module.validate_holyc_syntax(valid_holyc):
            print("Error: validate_holyc_syntax rejected a valid HolyC function template.")
            sys.exit(1)
            
        if module.validate_holyc_syntax(invalid_holyc):
            print("Error: validate_holyc_syntax accepted python code inside HolyC compiler.")
            sys.exit(1)
            
        print("HolyC syntax validation check: PASS")
    except Exception as e:
        print(f"Error testing validate_holyc_syntax: {e}")
        sys.exit(1)

    # 2. Test serial connection commands
    try:
        cmd = module.get_templeos_serial_command()
        
        # Ensure it launches telnet or serial bridge redirection on local port 4444
        if "4444" not in cmd and "localhost" not in cmd and "127.0.0.1" not in cmd:
            print(f"Error: Invalid QEMU serial parameters. Expected local loopback port binding (e.g. 4444 telnet redirection). Got: {cmd}")
            sys.exit(1)
            
        print("QEMU serial terminal command configuration: PASS")
    except Exception as e:
        print(f"Error testing get_templeos_serial_command: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 21 tests passed! Divine Compiler HolyC checksum initialized.")
    sys.exit(0)

# Run the check only when executed as a script, not when imported.
if __name__ == "__main__":
    test_chapter_21()
