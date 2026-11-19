# ==============================================================================
# Program: ch0_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating POSIX shell PATH environment configuration. Asserts that the solution extends the existing PATH search hierarchy without clobbering baseline system binary directories.
# ==============================================================================

# How this file fits the app: the validator for chapter 0. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/ch0_cli.sh.
# What it checks: reads the file as text, drops comment lines so the starter's example line cannot pass, and
# requires an `export PATH=...` that references $PATH and appends a directory (so the old PATH is extended,
# not replaced). Never executes the script.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch0_test.py
# The solution file is read as plain text and never executed.
import os
import re
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_0():
    print("Testing Chapter 0 Outpost Boot Setup...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
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

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_0()
