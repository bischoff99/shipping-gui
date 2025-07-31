# Utils package initialization
# Import functions from the root utils.py for backward compatibility
import importlib.util
import sys
import os

# Add the parent directory to sys.path to access root utils.py
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from root level utils module

spec = importlib.util.spec_from_file_location(
    "root_utils", os.path.join(parent_dir, "utils.py")
)
root_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_utils)

# Re-export the functions
parse_customer_input = root_utils.parse_customer_input
normalize_customer_data = root_utils.normalize_customer_data

__all__ = ["parse_customer_input", "normalize_customer_data"]
