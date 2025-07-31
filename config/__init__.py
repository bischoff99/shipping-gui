"""
Configuration package for the Shipping GUI application.

This package contains configuration modules for logging, Celery, and other
application settings.
"""

# Re-export Config from the root config.py
import os
import sys
from pathlib import Path

# Add parent directory to path to import config.py
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import Config class from root config.py module
import importlib.util
spec = importlib.util.spec_from_file_location("root_config", parent_dir / "config.py")
root_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_config)

Config = root_config.Config

__all__ = ['Config']