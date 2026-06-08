import os
import sys

def test_chapter_11():
    print("Testing Chapter 11: API Archipelago Loopback Binding Security...")
    solution_path = "/workspace/ch11_api.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch11_api.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch11_api.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "get_launch_config"):
        print("Error: Solution must define the 'get_launch_config' configuration function.")
        sys.exit(1)

    # Verify launch parameters bound strictly to local loopback (127.0.0.1)
    try:
        config = module.get_launch_config()
        host = config.get("host", "")
        port = config.get("port", 0)
        
        print(f"Server configuration detected: {host}:{port}")
        
        if host == "0.0.0.0":
            print("Error: Port exposure vulnerability detected! Binding to '0.0.0.0' exposes your local API to anyone on your network. Correct to '127.0.0.1' to secure it.")
            sys.exit(1)
            
        if host not in ["127.0.0.1", "localhost"]:
            print(f"Error: Invalid binding host '{host}'. Server must bind strictly to local loopback interface.")
            sys.exit(1)
            
        print("Local port binding security check: PASS")
    except Exception as e:
        print(f"Error testing get_launch_config: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 11 tests passed! FastAPI local routing secure.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_11()
