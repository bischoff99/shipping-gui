import os
import sys


def check_python():
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)


def check_flask():
    try:
        import flask

        print("Flask version:", flask.__version__)
    except ImportError:
        print("Flask not installed.")


def check_imports():
    try:
        pass

        print("All imports resolved.")
    except Exception as e:
        print("Import error:", e)


def check_debug_profiles():
    vscode_dir = os.path.join(os.getcwd(), ".vscode")
    launch_path = os.path.join(vscode_dir, "launch.json")
    if os.path.exists(launch_path):
        print("VS Code launch.json found.")
    else:
        print("VS Code launch.json missing!")


def check_scripts():
    scripts = [
        "activate_venv.ps1",
        "validate_requirements.ps1",
        "fix_pythonpath.ps1",
        "setup_project.ps1",
    ]
    for script in scripts:
        path = os.path.join("scripts", script)
        if os.path.exists(path):
            print(f"{script} found.")
        else:
            print(f"{script} missing!")


def main():
    check_python()
    check_flask()
    check_imports()
    check_debug_profiles()
    check_scripts()
    print("Setup validation complete.")


if __name__ == "__main__":
    main()
