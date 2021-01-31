#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-comercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20181205 - Original release
20210129 - Re-formatting IAW PEPs. Breaks interactions with legacy code.
"""


class KILL():
    def __init__(self,raw):
        self.data = raw.split()
        self.weapon_type = int(self.data[0])
        self.killer = self.data[1]
        self.killed = self.data[2]
        self.x = float(self.data[4])
        self.y = float(self.data[5])
        self.z = float(self.data[6])
        self.event_time = round(float(self.data[7]), 3)
        self.weapon_name = ""
        
        self.assign_weapon_name()
        
    def assign_weapon_name(self):
        """Determine the name of the weapon"""
        weapon_types = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12]
        weapon_names = ["GUNS", "AIM9", "AGM65", "B500", "RKT", "FLR", "AIM120", "B250", "B500HD", "AIM9X", "TANK"]
        ind = weapon_types.index(self.weapon_type)
        self.weapon_name = weapon_names[ind]

    # def KILLER(self):
    #     return self.killer
    # def KILLED(self):
    #     return self.killed
    # def TIME(self):
    #     return self.event_time
    # def WEAPON(self):
    #     return self.weapon_name
