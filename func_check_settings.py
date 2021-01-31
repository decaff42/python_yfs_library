#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181125_2222 - Original release
20210129 - Re-formatting IAW PEPs.
"""

import os
from pathlib import Path
from python_ysf_lib.func_import_file import import_any_file


def get_settings(filepath=False):
    """Check for and import settings file if it exists."""
    if filepath is False:
        # Assign the default location for the settings file.
        print("Looking for settings file in the default location:")
        fpath = os.path.join(os.getcwd(), "settings.cfg")
        print(fpath)
        
    if Path(filepath).is_file():
        # Import the file.
        data = import_any_file(fpath, "CFG")
    else:
        # The provided path cannot find a file.
        print("Cannot identify a settings file at specified location.")
        return False
    
    return data
