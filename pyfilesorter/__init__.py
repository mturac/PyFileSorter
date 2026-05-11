"""
PyFileSorter - Automatic file organizer by type and month with duplicate detection.
"""

__version__ = "0.1.0"
from .sorter import organize_folder, save_report
from .cli import main

__all__ = ["organize_folder", "save_report", "main"]