import os
import sys

def test_chapter_21():
    print("Testing Chapter 21: Altar of TempleOS (Bare-Metal HolyC)...")
    solution_path = "/workspace/ch21_altar.py"
    if not os.path.exists(solution_path):
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

if __name__ == "__main__":
    test_chapter_21()
