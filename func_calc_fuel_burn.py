#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20190114 - Original Release
20210129 - Re-formatting IAW PEPs. Breaks interactions with legacy code.
"""

import re


def get_fuel_burn_total(dat, avg_fuel):
    """
    Estimate the fuel burned by the aircraft.
    """
    # Get dat file values for burn rates.
    fuel_mil = ""
    fuel_afterburner = ""
    for line in dat:
        if line.startswith("FUELMILI"):
            fuel_mil = determine_fuel_rate(line)
        elif line.startswith("FUELABRN"):
            fab = determine_fuel_rate(line)

        if fuel_mil != "" and fuel_afterburner != "":
            break

    if fuel_mil == "":
        fuel_mil = 0
    if fuel_afterburner == "":
        fuel_afterburner = 0
            
    avg_thr = avg_fuel[0]/99
    mil_time = avg_fuel[1]
    ab_time = avg_fuel[2]

    # Calculate total fuel burn.
    fuel = 0
    fuel += float(fuel_mil) * float(avg_thr) * float(mil_time)
    fuel += float(fuel_afterburner) * float(ab_time)
    fuel = int(fuel)

    return fuel


def determine_fuel_rate(line):
    """find what units are in the burn rate strings."""
    units = ["t", "lb", "kg"]
    line = line.split()
    unit = ""
    chars = "abcdefghijklmnopqrstuvwxyz"

    # Get units.
    for i in units:
        if i in line[1]:
            unit = i
            break

    # Get burn rate as float
    rate = line[1]
    rate = re.sub('[^.0-9]', '', rate)
    rate = float(rate)
        
    # Convert burn rate to kg.
    if unit == "t":
        rate = rate * 2000
    elif unit == "lb":
        rate = rate * 0.453592
    else:
        rate = rate

    return rate

