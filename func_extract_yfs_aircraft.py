#!/usr/bin/env python

__version__ = "20201213"
__author__ = "Decaff_42"
__copyright__ = "2020 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20201213 - Original release
20210129 - Re-formatting IAW PEPs. Updated code to run faster by looking for indexes of segments.
"""

import datetime


from python_ysf_lib.class_aircraft import Aircraft


def extract_aircraft_blocks(data):
    """Extract the data blocks for the airplanes and create class instances
    data: list of strings from the imported yfs file.
    """
    print("{} - Extracting Aircraft data from YFS File...".format(datetime.datetime.now().time()))

    # Define variables
    airplane_class_instances = list()
    airplane_text_blocks = list()

    # Start by identifying the start and stop indices for the
    aircraft_start_indexes = list()
    airplane_counter = 0
    for idx, line in enumerate(data):
        if line.startswith("AIRPLANE "):
            airplane_counter += 1
            aircraft_start_indexes.append(idx)
        elif (line.startswith("GROUNDOB") or line.startswith("BULRECOR") or
              line.startswith("KILLCREDIT") or line.startswith("EXPRECOR")):
            # Found the end of the aircraft definition block, just add a final entry into the index list to finish the
            # last aircraft data block off.
            aircraft_start_indexes.append(idx)
            break

    # Extract data from the raw yfs file and separate into chunks for the airplane class instances
    for i in range(airplane_counter):
        start_row = aircraft_start_indexes[i]
        end_row = aircraft_start_indexes[i + 1]

        airplane_rows = data[start_row:end_row]
        airplane_text_blocks.append(airplane_rows)

    # Create aircraft class instances if there are airplanes identified
    bad_airplane_counter = 0
    if airplane_counter > 0:
        for ysfid, lines in enumerate(airplane_text_blocks):
            # The YSF ID is the index of the airplane event block. The index starts at zero, which works well with the
            # python enumerate which also starts at zero.
            try:
                airplane_class_instances.append(Aircraft(lines, ysfid))
            except:
                bad_airplane_counter += 1

            if ysfid % 50 == 0 and ysfid > 9:
                print("{} - Processed {} of {} Airplane Event Blocks".format(datetime.datetime.now().time(),
                                                                             ysfid,
                                                                             airplane_counter)
                      )

    if bad_airplane_counter > 0:
        print("   Could not process {} of {} Airplanes".format(bad_airplane_counter, airplane_counter))

    return airplane_class_instances
