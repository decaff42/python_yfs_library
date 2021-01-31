#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181128 - Original Code
20210129 - Re-formatting IAW PEPs. 
"""

import os


def break_line():
    """Put a separation in the output window"""
    print("----------------------------------------------------")


def check_input(min_num, max_num, number_input):
    """Make sure input is in-range and is the proper type."""
    try:
        number_input = int(number_input)
    except ValueError:
        return False

    if min_num <= number_input <= max_num:
        return input
    else:
        return False


def select_file(folder_path):
    """Find all files in a directory and ask the user to select a file."""
    files = os.listdir(folder_path)
    yfs = list()
    for file in files:
        if file.lower().endswith(".yfs"):
            yfs.append(file)
    
    if len(yfs) == 0:
        print("No YFS Files Found!")
        return False
    else:
        print("Select a YFS File!")
        for ind, file in enumerate(yfs):
            print("({}) {}".format(ind, file))

        selected = False
        while selected is False:
            user = input("Please enter the number of the YFS file you wish to select:  \n")
            selected = check_input(0, len(yfs), user)

    return os.path.join(folder_path, yfs[selected])
