#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181127 - Original Code
20210129 - Re-formatting IAW PEPs. 
"""


def break_line():
    print("----------------------------------------------------")


def extract_yfs_header(data):
    """Extract key information from the YFS header"""
    ysf_version = ""
    scenery_name = ""
    event_block_start_line = 0

    for ind, line in enumerate(data):
        if line.startswith("YFSVERSI"):
            ysf_version = line.split(" ")[-1]
        elif line.startswith("FIELDNAM"):
            scenery_name = line.split(" ")[1]
        elif line.startswith("EVTBLOCK"):
            event_block_start_line = ind
            break

    print("YSF Version:  {}".format(ysf_version))
    print("Map:          {}".format(scenery_name))
    break_line()

    return ysf_version, scenery_name
