import os
import shutil
import re

# Move test_*.py and run_tests.py to tests/
project_root = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(project_root)
tests_dir = os.path.join(root, "tests")
services_dir = os.path.join(root, "services")

# Backup original structure
backup_dir = os.path.join(root, "backup_original_structure")
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)
    for fname in os.listdir(root):
        if fname.endswith(".py") and fname not in ["move_files.py"]:
            shutil.copy2(os.path.join(root, fname), backup_dir)

# Move test_*.py and run_tests.py
for fname in os.listdir(root):
    if re.match(r"test_.*\.py", fname) or fname == "run_tests.py":
        shutil.move(os.path.join(root, fname), os.path.join(tests_dir, fname))

# Move inventory_monitor.py to services/
if os.path.exists(os.path.join(root, "inventory_monitor.py")):
    shutil.move(
        os.path.join(root, "inventory_monitor.py"),
        os.path.join(services_dir, "inventory_monitor.py"),
    )

# Update imports in all .py files
for folder in [root, tests_dir, services_dir]:
    for fname in os.listdir(folder):
        if fname.endswith(".py"):
            fpath = os.path.join(folder, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            # Update imports for moved files
            content = re.sub(
                r"from (inventory_monitor|run_tests|test_\w+)",
                r"from services.\1",
                content,
            )
            content = re.sub(
                r"import (inventory_monitor|run_tests|test_\w+)",
                r"from services import \1",
                content,
            )
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
print("File organization complete. Backups in backup_original_structure/.")
