#!/usr/bin/env python

__version__ = "20181127"
__author__ = "Decaff_42"
__copyright__ = "2018 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""


import os


def check_folder_structure(folder_path, names):
    """Check the provided directory for the files and folders provided. If any
    folder does not exist, create it and report that information.
    """
    files = os.listdir(folder_path)
    all_present = True
    
    for name in names:
        if name not in files:
            # Create the folder.
            path = os.path.join(folder_path, name)
            os.mkdir(path)
            print("Created missing folder:  {}".format(name))
            all_present = False
    
    if all_present is True:
        print("All Folders Present!")
