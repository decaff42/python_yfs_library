#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""
  
"""
VERSION HISTORY:
20181205 - Original release
20210129 - Re-formatting IAW PEPs.
"""
  
  
def assign_kills_deaths(airplanes, ground, kill_credits):
    """Associate the kill credits with the killer and killed airplanes."""
    flight_ids = list()
    
    # Gather the flight ids of each airplane class
    for i in airplanes:
        flight_ids.append(i.ysf_id)
        
    for kill in kill_credits:
        data = kill.split()  # Split by whitespace
        killer = data[1]
        killed = data[2]

        killer_type = killer[0]
        killed_type = killed[0]
        killer_id = int(killer[1:])
        killed_id = int(killed[1:])

        # Assign the kill
        if killer_type == "A":
            for plane in airplanes:
                if plane.ysf_id == killer_id:
                    plane.assign_kill(kill)
        elif killer_type == "G":
            for gnd in ground:
                if gnd.id == killer_id:
                    gnd.assign_kill(kill)

        # Assign the death
        if killed_type == "A":
            for plane in airplanes:
                if plane.ysf_id == killed_id:
                    plane.assign_death_report(kill)
        elif killed_type == "G":
            for gnd in ground:
                if gnd.id == killed_id:
                    gnd.assign_death(kill)            

    return airplanes, ground
