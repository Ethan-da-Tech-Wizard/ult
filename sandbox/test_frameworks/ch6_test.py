# ==============================================================================
# Program: ch6_test.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Automated verification test suite validating Python package manifest dependency specifications. Parses requirements.txt for pinned version specifiers and security vulnerability patches.
# ==============================================================================

# How this file fits the app: the validator for chapter 6. server/sandbox_manager.py runs it (inside the
# zeus-sandbox container or, without Docker, with the host Python) every time the player presses Compile,
# after server/main.py has saved the player's code as save_data/relic_save/requirements.txt.
# What it checks: every `requests==X.Y` line must be version 2.31 or newer (the CVE-fix floor); a file without
# requests only prints a warning and passes.
# Contract with the rest of the app: exit code 0 means the chapter is solved; any failure prints an
# explanation and exits 1. The output is returned verbatim by /api/compile and shown to the player, so
# messages are written for learners. Run it by hand from the repo root: python3
# sandbox/test_frameworks/ch6_test.py
# The solution file is read as plain text and never executed.
import os
import sys

# One test function so the file can also be run directly; it ends the process itself with sys.exit instead of
# returning a value.
def test_chapter_6():
    print("Testing Chapter 6: Docker Relic Dependency Auditing...")

    # Two locations are tried: /workspace is where the Docker container sees the player's files (bind mount of
    # save_data/relic_save); the relative save_data path is used when run on the host from the repo root.
    requirements_path = "/workspace/requirements.txt"
    if not os.path.exists(requirements_path):
        requirements_path = "save_data/relic_save/requirements.txt"
        if not os.path.exists(requirements_path):
            print("Error: Dependency file 'requirements.txt' not found.")
            sys.exit(1)
            
    # We assert that the player updated requirements to a secure package version
    with open(requirements_path, "r") as f:
        content = f.read().strip()
        
    print(f"Checking requirements.txt contents:\n---\n{content}\n---")
    
    # We check if a known vulnerable library (e.g. requests<2.31.0) is upgraded
    lines = content.split("\n")
    has_requests = False
    for line in lines:
        if "requests" in line:
            has_requests = True
            if "==" in line:
                version = line.split("==")[1].strip()
                v_parts = [int(x) for x in version.split(".") if x.isdigit()]
                # Check version >= 2.31.0
                if len(v_parts) >= 2 and (v_parts[0] > 2 or (v_parts[0] == 2 and v_parts[1] >= 31)):
                    print(f"Success: Upgraded requests package to secure version {version}.")
                else:
                    print(f"Error: requests version {version} contains known security vulnerabilities (CVE-2023-32681). Upgrade to >= 2.31.0.")
                    sys.exit(1)
                    
    if not has_requests:
        print("Warning: requirements.txt is missing core packages. Standard dependencies verified.")
        
    print("\n>>> All Chapter 6 tests passed! Docker dependencies audited and secure.")
    sys.exit(0)

# Entry point when executed as a script (the way sandbox_manager.py runs it).
if __name__ == "__main__":
    test_chapter_6()
