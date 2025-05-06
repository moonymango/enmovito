"""
Utility functions for the Enmovito application.

This module contains utility functions that are used throughout the application.
"""

import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path (str): Path relative to the application root
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(f"Running from PyInstaller bundle. MEIPASS: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        print(f"Running from source. Base path: {base_path}")

    return os.path.join(base_path, relative_path)
