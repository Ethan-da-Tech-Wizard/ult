import os
import re
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

    # Strip comments so example lines in the skeleton can't pass for the player
    active_lines = [
        line for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    active = "\n".join(active_lines)

    # The player must write a real export that extends PATH (not replace it)
    export_match = re.search(r"export\s+PATH\s*=\s*(\S+)", active)
    if not export_match:
        print("Error: No `export PATH=...` statement found.")
        print("Hint: append the toolchain directory, e.g. export PATH=$PATH:/usr/local/bin")
        sys.exit(1)

    path_value = export_match.group(1)
    if "$PATH" not in path_value and "${PATH}" not in path_value:
        print("Error: Your export REPLACES the existing PATH instead of extending it.")
        print("Hint: keep the old entries by referencing $PATH, e.g. export PATH=$PATH:/usr/local/bin")
        sys.exit(1)

    if not re.search(r"\$\{?PATH\}?:[^\s]+|[^\s]+:\$\{?PATH\}?", path_value):
        print("Error: PATH was referenced but no new directory was appended to it.")
        print("Hint: add a directory after a colon, e.g. export PATH=$PATH:/usr/local/bin")
        sys.exit(1)

    print("Success: PATH extended without clobbering the existing entries.")
    print("Citadel Core Gates: ACCESS GRANTED.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_0()
