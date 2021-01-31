#!/usr/bin/env python

__version__ = "20181130"
__author__ = "Decaff_42"
__copyright__ = "2018 by Decaff_42"
__license__ = """Only non-comercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181130 - Original release
20210129 - Re-formatting IAW PEPs. 
"""


def extract_explosions(raw):
    """Extract the raw bullet record from the .yfs file."""

    # Get the index of the explosion record
    try:
        start = raw.index("EXPRECOR")
    except ValueError:
        # No Explosion Records in this replay
        return []
    
    explosions = list()
    raw = raw[start:]
    record = False
    num_lines = len(raw)
    num_exp = 0

    for ind, line in enumerate(raw):
        if line.startswith("NUMRECO"):
            num_exp = int(line.split(" ")[-1])
            record = True
        elif line.startswith("ENDRECO") or ind == num_lines:
            record = False
            break
        elif record is True:
            explosions.append(line)
        
    return explosions
