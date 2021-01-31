#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181127 - Original release
20210129 - Re-formatting IAW PEPs. Updated code to run faster by looking for indexes of segments.
"""

from python_ysf_lib.class_yfs_ground_object import GroundObject


def extract_yfs_ground_objects(raw):
    """Extract the ground object data."""

    # Define variables
    ground_objects = list()
    ground_object_classes = list()
    ground_object_count = 0
    ground_object_start_index = list()
    bad_ground_object_counter = 0

    # Identify the number of ground objects in the replay file
    for idx, line in enumerate(raw):
        if line.startswith("GROUNDOB"):
            ground_object_count += 1
            ground_object_start_index.append(idx)
        elif line.startswith("BULRECOR") or line.startswith("KILLCREDIT") or line.startswith("EXPRECOR"):
            ground_object_start_index.append(idx)
            break

    # Extract data from the raw yfs file and separate into chunks for the ground objects
    for i in range(ground_object_count):
        start_row = ground_object_start_index[i]
        end_row = ground_object_start_index[i + 1]

        ground_object_rows = raw[start_row:end_row]
        ground_objects.append(ground_object_rows)

    # Identify ground objects that have errors in them and do not save them.
    if len(ground_objects) > 0:
        for ysfid, lines in enumerate(ground_objects):
            try:
                ground_object_classes.append(GroundObject(lines, ysfid))
            except:
                bad_ground_object_counter += 1

    if bad_ground_object_counter > 0:
        print("   Could not process {} of {} Ground Objects".format(bad_ground_object_counter, ground_object_count))

    return ground_object_classes


def extract_yfs_ground_objects2(raw):
    # Initialize variables
    gnd_obj = list()
    gnd_obj_classes = list()
    num_lines = len(raw)
    ground_object_count = 0

    for ind, line in enumerate(raw):
        if line.startswith("GROUNDOB"):
            ground_object_count += 1
            record = True
            temp = list()
            i = 0
            while record is True:
                if ind + i < num_lines:
                    if ((raw[ind + i].startswith("GROUNDOB") and i > 0) or
                            raw[ind + i].startswith("BULRECOR") or
                            raw[ind + i].startswith("AIRPLANE") or
                            ind + i >= num_lines):
                        record = False
                        gnd_obj.append(temp)
                    else:
                        temp.append(raw[ind + i])
                        i += 1
                else:
                    record = False

            gnd_obj.append(temp)

    print("        Found {} Ground Objects".format(ground_object_count))

    bad_gnd_obj_counter = 0
    if len(gnd_obj) > 0:
        for ysfid, i in enumerate(gnd_obj):
            try:
                gnd_obj_classes.append(GroundObject(i, ysfid))
            except:
                bad_gnd_obj_counter += 1

    if bad_gnd_obj_counter > 0:
        print("   Could not process {} Ground Objects".format(bad_gnd_obj_counter))

    return gnd_obj_classes
