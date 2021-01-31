#!/usr/bin/env python

__version__ = "20190114"
__author__ = "Decaff_42"
__copyright__ = "2019 by Decaff_42"
__license__ = """Only non-comercial use with attribution is allowed without
prior written permission from Decaff_42."""


import os
import re


def get_dats(ysfpath, airplanes):
    """Get the DAT contents for each of the aircraft."""
    print("Looking for DAT files for all aircraft")

    # Get the unique identify names
    aircraft_idents = list()
    for plane in airplanes:
        name = plane.aircraft_name
        name = name.replace(" ", "_")
        name = name.strip("\n")
        if name not in aircraft_idents:
            aircraft_idents.append(name)
    temp_aircraft_idents = aircraft_idents

    # Get all .dat files
    files_to_test = list()
    ignore_dir_list = ["ground", "misc", "mission", "scenery", "sound", "weapons"]
    for root, dirs, files in os.walk(ysfpath):
        if root in ignore_dir_list:
            break
        for file in files:
            if file.lower().endswith(".dat"):
                files_to_test.append(os.path.join(root,file))
        
    # Get DAT Files for these unique IDENTIFY lines.
    aircraft_dats = dict()
    identify_lines = list()
    for file in files_to_test:
        if len(temp_aircraft_idents) == 0:
            # All files have been found
            break
        with open(file, mode='r', errors='ignore') as f:
            dat_lines = f.readlines()
        for line in dat_lines:
            if line.startswith("IDENTIFY"):
                identify_lines.append(line)
                # Search this line for all idents.
                name = line.strip("\n").upper().replace(" ", "_")
                for ind, ident in enumerate(temp_aircraft_idents):
                    if ident in name:
                        # Found the file!
                        aircraft_dats[ident] = dat_lines
                        print("    - Found DAT File for {}".format(ident))
                        del temp_aircraft_idents[ind]  # Don't re-find identify line
                        break
                else:
                    continue
                break

    if len(temp_aircraft_idents) > 0:
        print("Could not find DAT File(s) for these aircraft:")
        for i in temp_aircraft_idents:
            print("  {}".format(i))
        print(" ")
    else:
        print("Found DAT files for all aircraft!.")

    return aircraft_dats

