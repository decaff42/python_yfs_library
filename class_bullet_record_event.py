#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-comercial use with attribution is allowed without
prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20210129 - Re-formatting IAW PEPs. Breaks interactions with legacy code.
"""


class BulletRecord:
    """This class is intended to store all information about a weapon event
    form the bullet record in a .yfs replay file.
    """
    def __init__(self, lines):
        self.raw_data = lines
        self.launch_time = float(lines[0].split(" ")[0])

        # Initialize Variables
        self.weapon_names = ["GUNS", "AIM9", "AGM65", "B500", "RKT", "FLR", "AIM120", "B250", "B500HD", "AIM9X", "TANK"]
        self.weapon_types = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12]
        self.weapon_type = -1
        self.weapon_name = "unknown"
        self.launcher = -1
        self.launcher_type = "U"
        self.launch_position = list()
        self.target = -1
        self.target_type = "U"
        self.launcher_id = ""

        # Run functions on provided data.
        self.get_weapon_type()
        self.get_launch_entity()
        self.get_launch_position()

    def get_launch_position(self):
        """Use the first line data to determine position"""
        line = self.raw_data[0]
        parts = line.split()  # white space delimiter by default
        self.launch_position = [float(parts[2]), float(parts[3]), float(parts[4])]

    def get_weapon_type(self):
        """Determine what kind of weapon this is."""
        self.weapon_type = int(self.raw_data[0].split(" ")[1])
        self.weapon_name = self.weapon_names[self.weapon_types.index(self.weapon_type)]

    def get_launch_entity(self):
        """Determine who/what launched the weapon."""
        data = self.raw_data[1].split(" ")
        
        if data[-2] == "N":
            # Don't know who launched the weapon
            self.launcher = "Unknown"
            self.launcher_type = "N"
            
        elif data[-2].startswith("A"):
            self.launcher_id = data[-2]
            self.launcher = int(data[-2][1:])
            self.launcher_type = "A"
            
        elif data[-2].startswith("G"):
            # A ground object launched the weapon
            self.launcher_id = data[-2]
            self.launcher = int(data[-2][1:])
            self.launcher_type = "G"
        
    # Pass information from the class
    def raw_id(self):
        """Return the raw id of this weapon"""
        return self.raw_data[1].split()[-2]

    # def WEAPONTYPE(self):
    #     return self.weapon_type
    # def WEAPONNAME(self):
    #     return self.weapon_name
    # def LAUNCHER(self):
    #     return self.launcher
    # def LAUNCHERTYPE(self):
    #     return self.launcher_type
    # def RAW(self):
    #     return self.raw_data
