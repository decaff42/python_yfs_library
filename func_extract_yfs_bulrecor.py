#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181129 - Original release
20210129 - Re-formatting IAW PEPs. 
"""

from python_ysf_lib.class_bullet_record_event import BulletRecord


def extract_raw_bullet_record(raw):
    """Extract the raw bullet record from the .yfs file."""
    try:
        start = raw.index("BULRECOR")
    except ValueError:
        # No bullet record  can be found
        return []
    
    raw = raw[start:]
    bullets = list()
    record = False
    num_bullets = 0

    for ind, line in enumerate(raw):
        if line.startswith("NUMRECO"):
            num_bullets = line.split()[-1]
            record = True
        elif line.startswith("ENDRECO") or line.startswith("KILLCREDIT") or ind == len(raw):
            record = False
            break
        elif record is True:
            bullets.append(line)
            
    bullet_records = process_bullet_records(bullets, num_bullets)

    return bullet_records


def process_bullet_records(bullets,num_bullets):
    """Parse the raw bullet record into actuall bullet records"""
    
    bullet_classes = list()
    next_start = 0
    # weapon_types = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12]
    # weapon_names = ["Gun", "AIM9", "AGM", "B500", "RKT", "FLR", "AIM120", "B250", "B500HD", "AIM9X", "FUEL"]
    
    for ind, line in enumerate(bullets):
        if next_start == ind:
            # This should be the start of the next bullet record. Get the
            # weapon type number to determine if this record has 2 or 3 lines.
            if '.' in line.split(" ")[1]:
                print(line)
                raise Exception("Error with processing weapon record line.")
            wpn_type = int(line.split(" ")[1])
            if wpn_type in [1, 2, 4, 6, 10]:
                # This is a missile or rocket, so it will have 3 lines.
                next_start = ind + 3
                raw_lines = bullets[ind:next_start]
                bullet_classes.append(BulletRecord(raw_lines))
            elif wpn_type not in [1, 2, 4, 6, 10]:
                # This is a non missile/rocket weapon and will have 2 lines.
                next_start = ind + 2
                raw_lines = bullets[ind:next_start]
                bullet_classes.append(BulletRecord(raw_lines))

    if int(num_bullets) != len(bullet_classes):
        print("An error occurred with the weapon extraction.")
        print("{} Bullet Classes".format(len(bullet_classes)))
        print("{} Bullet Records".format(num_bullets))
        raise()
    
    return bullet_classes
