import os
import sys

def test_chapter_0():
    print("Testing Chapter 0 Outpost Boot Setup...")
    solution_path = "/workspace/ch0_cli.sh"
    if not os.path.exists(solution_path):
        # Local fallback path check
        solution_path = "save_data/relic_save/ch0_cli.sh"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch0_cli.sh' not found in workspace.")
            sys.exit(1)
            
    with open(solution_path, "r") as f:
        content = f.read().strip()
        
    print(f"Loaded solution scripts:\n---\n{content}\n---")
    
    # We assert that the player's script configures PATH or sets system environment keys
    if "PATH=" in content or "export " in content or "echo" in content:
        print("Success: Environment configuration parameters verified.")
        print("Citadel Core Gates: ACCESS GRANTED.")
        sys.exit(0)
    else:
        print("Error: Missing environment export mappings. Check PATH exports.")
        sys.exit(1)

if __name__ == "__main__":
    test_chapter_0()
