import os
import sys
import subprocess
import shutil

def main():
    print("====================================================")
    print("Building The Sacred Tech JRPG Desktop Assistant...")
    print("====================================================")
    
    # 1. Paths configuration
    server_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(server_dir, ".."))
    export_dir = os.path.join(project_root, "save_data", "export")
    
    os.makedirs(export_dir, exist_ok=True)
    
    # 2. Add-data separator based on OS
    sep = ";" if sys.platform.startswith("win") else ":"
    
    # Define files/directories to bundle
    # Format: src_path + separator + dest_relative_path
    client_bundle = f"{os.path.join(project_root, 'client')}{sep}client"
    sandbox_bundle = f"{os.path.join(project_root, 'sandbox')}{sep}sandbox"
    
    # 3. Setup PyInstaller arguments
    exe_name = "Zeus_Assistant"
    pyinstaller_args = [
        "pyinstaller",
        "--onefile",
        f"--name={exe_name}",
        f"--add-data={client_bundle}",
        f"--add-data={sandbox_bundle}",
        "--clean",
        os.path.join(server_dir, "main.py")
    ]
    
    print(f"Project root: {project_root}")
    print(f"Export directory: {export_dir}")
    print(f"Executing: {' '.join(pyinstaller_args)}")
    
    # 4. Invoke pyinstaller
    # We run it using uv run to ensure dependencies are automatically resolved
    try:
        # Check if uv is available
        uv_check = subprocess.run(["uv", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if uv_check.returncode == 0:
            print("Invoking PyInstaller via UV...")
            # We bundle PyInstaller and other required packages into uv runtime
            cmd = [
                "uv", "run",
                "--with", "pyinstaller",
                "--with", "fastapi",
                "--with", "uvicorn",
                "--with", "pydantic",
                "--with", "jinja2"
            ] + pyinstaller_args
            subprocess.run(cmd, check=True)
        else:
            print("UV not detected. Running standard PyInstaller...")
            subprocess.run(pyinstaller_args, check=True)
            
        # 5. Move output to save_data/export/
        dist_dir = os.path.join(project_root, "dist")
        built_file = os.path.join(dist_dir, exe_name + (".exe" if sys.platform.startswith("win") else ""))
        target_file = os.path.join(export_dir, exe_name + (".exe" if sys.platform.startswith("win") else ""))
        
        if os.path.exists(built_file):
            shutil.move(built_file, target_file)
            print(f"\nSUCCESS! Desktop app packaged at: {target_file}")
        else:
            print(f"\nError: Built binary not found at expected location: {built_file}")
            
    except subprocess.CalledProcessError as e:
        print(f"\nError: Build command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError occurred during package run: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
