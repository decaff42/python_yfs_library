#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181129 - Original release
20210129 - Re-formatting IAW PEPs. 
"""


def extract_kill_credits(raw):
    """Extract the raw bullet record from the .yfs file."""
    start = -1
    kill_credit = list()
    for i in raw:
        if i.startswith("KILLCREDIT"):
            start = raw.index(i)
            break

    if start == -1:
        # There are no kill credits!
        return kill_credit

    raw = raw[start:]
    record = False
    
    for ind, line in enumerate(raw):
        if line.startswith("KILLCREDIT"):
            num_kills = int(line.split(" ")[-1])
            record = True
        elif line.startswith("ENDRECO"):
            record = False
            break
        elif record is True:
            kill_credit.append(line)
            
    kill_credit = remove_dup_kills(kill_credit)            
        
    return kill_credit


def remove_dup_kills(kill_credits):
    """Sometimes duplicate kills are recorded, determined by having the same
    killer and killed entities, within 3 seconds of eachother.
    """

    clean_kills = kill_credits  # Assume all good to start with.
    bad_kills = list()
    
    data_kills = list()
    for kill in kill_credits:
        temp = kill.split(" ")
        temp[-1] = float(temp[-1])
        data_kills.append(temp)
    
    for ind, line in enumerate(data_kills):
        if ind < len(data_kills)-1:
            if line[:3] == data_kills[ind+1][:3]:
                # if the weapon, killer and killed match test to see if the
                # times between these kills is too short (w/in 3 seconds)
                if line[-1] + 3 >= data_kills[ind+1][-1]:
                    bad_kills.append(ind+1)
                    
    for ind in reversed(bad_kills):
        print("  Deleting Duplicate Kill Credit: {}".format(clean_kills[ind]))
        del clean_kills[ind]

    return clean_kills
