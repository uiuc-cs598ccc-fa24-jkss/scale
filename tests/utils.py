import sys
import os

def add_to_sys_path(root_dir):
    """Recursively add directories to sys.path, excluding virtual environments and cache directories."""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip unnecessary directories
        if "venv" in dirnames:
            dirnames.remove("venv")  # Do not descend into 'venv'
        if ".venv" in dirnames:
            dirnames.remove(".venv")  # Do not descend into 'venv'
        if "__pycache__" in dirnames:
            dirnames.remove("__pycache__")  # Skip __pycache__ directories
        if "pip" in dirpath or "_vendor" in dirpath:
            continue  # Skip pip or vendorized paths
            
        sys.path.insert(0, dirpath)