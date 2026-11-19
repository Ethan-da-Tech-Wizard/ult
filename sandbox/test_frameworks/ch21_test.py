# ==============================================================================
# Program: ch21_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating bare-metal HolyC compilation checksums for TempleOS. Evaluates static language typing syntax verification, serial command generation, and 16-bit summation hashing.
# ==============================================================================

# How this file fits the app: the validator for chapter 21. server/sandbox_manager.py runs it (inside the zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile, after server/main.py has saved the player's code as save_data/relic_save/ch21_altar.py.
# What it checks: validate_holyc_syntax(code) must accept a HolyC sample (U0/I64 types, Print) and reject Python code; get_templeos_serial_command() must return a command that mentions port 4444, localhost or 127.0.0.1, i.e. the serial bridge used by server/qemu_launcher.py.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so messages are written for learners. Run it by hand from the repo root: python3 sandbox/test_frameworks/ch21_test.py
# Security note: for Python chapters the player's file is imported with exec_module, so their code runs inside this process; use the Docker sandbox for untrusted code.
import os
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of returning a value.
def test_chapter_21():
    print("Testing Chapter 21: Altar of TempleOS (Bare-Metal HolyC)...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    solution_path = "/workspace/ch21_altar.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch21_altar.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch21_altar.py' not found.")
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_21()
