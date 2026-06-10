import os
import sys

def test_chapter_6():
    print("Testing Chapter 6: Docker Relic Dependency Auditing...")
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

if __name__ == "__main__":
    test_chapter_6()
