#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20210105 - Update to text event extraction
20210129 - Re-formatting IAW PEPs.
"""


def extract_yfs_event_block2(raw):
    """Get information from the event block of the yfs file. This function will
    not use slicing because the header block of .yfs files are relatively small
    and the added complication is not necessary as a time saving measure. It
    will, however send the end of the events line to the next function because
    this section of the .yfs file can be quite long.
    """

    # Pre-allocate the pieces to extract
    text_events = list()
    weapon_configs = list()
    player_air_id = list()
    visibility_changes = list()
    air_commands = list()

    # Parse the events
    event_starts = ["TXTEVT", "WPNCFG", "PLRAIR", "VISCHG", "AIRCMD"]
    text_start_indexes = list()
    for idx, line in enumerate(raw):
        parts = line.split()
        if parts[0] in event_starts:
            text_start_indexes.append(idx)
        if line.startswith("EDEVTBLK"):
            text_start_indexes.append(idx)
            break

    # Put into lists
    for idx in text_start_indexes:
        if raw[idx].startswith("TXTEVT"):
            text_events.append(1)


def extract_yfs_event_block(raw):
    """Get information from the event block of the yfs file. This function will
    not use slicing because the header block of .yfs files are relatively small
    and the added complication is not necessary as a time saving measure. It
    will, however send the end of the events line to the next function because
    this section of the .yfs file can be quite long.
    """

    # Get things to extract
    text_events = list()
    weapon_config = list()
    player_air_id = list()
    vis_changes = list()
    air_commands = list()

    for ind, line in enumerate(raw):
        if line.startswith("TXTEVT"):
            text_events.append([line.split(" ")[1], raw[ind+1][4:]])
        elif line.startswith("WPNCFG"):
            temp = []
            record = True
            i = 0
            while record is True:
                if raw[ind+i].startswith("ENDEVT"):
                    record = False
                else:
                    temp.append(raw[ind+i])
                    i += 1
            weapon_config.append(temp)
        elif line.startswith("PLRAIR"):
            player_air_id.append([raw[ind:ind+1]])
            
        elif line.startswith("VISCHG"):
            vis_changes.append(raw[ind:ind+2])
            
        elif line.startswith("AIRCMD"):
            # AIR Commands are currently not used for anything in analysis.
            pass
        
        if line.startswith("EDEVTBLK"):
            break
        
    return text_events, weapon_config, player_air_id
