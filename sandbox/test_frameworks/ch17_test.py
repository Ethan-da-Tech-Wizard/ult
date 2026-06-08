import os
import sys
import json

def test_chapter_17():
    print("Testing Chapter 17: Agentic Skyway (Tool-Calling Schema & Loops)...")
    solution_path = "/workspace/ch17_agent.py"
    if not os.path.exists(solution_path):
        solution_path = "save_data/relic_save/ch17_agent.py"
        if not os.path.exists(solution_path):
            print("Error: Solution file 'ch17_agent.py' not found.")
            sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("student_solution", solution_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error: Solution script failed to compile: {e}")
        sys.exit(1)

    if not hasattr(module, "generate_tool_schema") or not hasattr(module, "execute_tool_call"):
        print("Error: Solution must define 'generate_tool_schema' and 'execute_tool_call' functions.")
        sys.exit(1)

    # 1. Test generate_tool_schema
    # Let's define a target function
    def cast_fireball(target: str, power: int):
        """Casts a fireball at a specified JRPG monster target."""
        return f"Fireball cast at {target} with power {power}!"

    try:
        schema = module.generate_tool_schema(cast_fireball)
        
        # Verify schema elements
        if schema.get("name") != "cast_fireball":
            print(f"Error: Schema name mismatch. Got {schema.get('name')}, expected 'cast_fireball'")
            sys.exit(1)
            
        desc = schema.get("description", "")
        if "Casts a fireball" not in desc:
            print("Error: Function docstring description missing or incorrect in schema.")
            sys.exit(1)
            
        params = schema.get("parameters", {})
        if params.get("type") != "object":
            print("Error: Parameters schema type must be 'object'.")
            sys.exit(1)
            
        props = params.get("properties", {})
        if "target" not in props or "power" not in props:
            print("Error: Function arguments are missing from schema properties.")
            sys.exit(1)
            
        # Optional validation of types if supported
        print("JSON Tool Schema Generation: PASS")
    except Exception as e:
        print(f"Error testing generate_tool_schema: {e}")
        sys.exit(1)

    # 2. Test execute_tool_call
    try:
        tools_map = {"cast_fireball": cast_fireball}
        tool_call_dict = {
            "name": "cast_fireball",
            "arguments": {"target": "Syntax Goblin", "power": 85}
        }
        tool_call_str = json.dumps(tool_call_dict)
        
        # Run execution
        res = module.execute_tool_call(tool_call_str, tools_map)
        expected = "Fireball cast at Syntax Goblin with power 85!"
        
        if res != expected:
            print(f"Error: Tool execution failed. Got '{res}', expected '{expected}'")
            sys.exit(1)
            
        print("Dynamic Tool Call Parse & Run Loop: PASS")
    except Exception as e:
        print(f"Error testing execute_tool_call: {e}")
        sys.exit(1)

    print("\n>>> All Chapter 17 tests passed! Tool-calling agents operational.")
    sys.exit(0)

if __name__ == "__main__":
    test_chapter_17()
