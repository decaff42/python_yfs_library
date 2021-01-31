#!/usr/bin/env python

__version__ = "20201213"
__author__ = "Decaff_42"
__copyright__ = "2020 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""


"""
VERSION HISTORY:
20201213 - Updated for Red vs Blue Combat Scoring
20210129 - Re-formatting IAW PEPs. Breaks interactions with legacy code.
"""


class GroundObject:
    def __init__(self, data, ysf_id):
        self.raw = data
        self.ysf_id = ysf_id  # The nth ground object defined in the .yfs file

        # Define variables
        self.ground_id = ""
        self.id = -1
        self.tag = ""
        self.gnd_type = "UNKNOWN"
        self.name = ""
        self.iff = -1
        self.start_pos = [0, 0, 0]
        self.pos_data = list()
        self.bullet_record = list()
        self.kill_record = list()
        self.death_record = list()
        self.ground_position = list()
        self.ground_attitude = list()
        self.ground_flags = list()
        self.number_data_frames = -1

        # Run initial functions
        self.parse()

    def parse(self):
        """Extract information from raw data"""
        # Get information from the first row
        first_row = self.raw[0].split()
        self.gnd_type = first_row[1]

        # Get information from the second row
        second_row = self.raw[1].split()
        self.iff = int(second_row[1]) + 1  # YSF has IFF enumerations start at zero

        # Get information from the 3rd row
        third_row = self.raw[2].split()
        self.id = int(third_row[1])
        self.tag = third_row[2].split('"')[1]  # Expect a "tag" format

        # If there is a tag, use that as the name, otherwise use the ground type
        if len(self.tag) > 1:
            self.name = self.tag
        else:
            self.name = self.gnd_type

        # Determine the ground ID for this object.
        self.ground_id = "G{}".format(self.id)

        # After the 3rd row, then data can vary. Known line prefixes are:
        # GRNDCMND MAXSPEED ###kt
        # GRNDCMND MAXROTAT ###deg
        # GNDPOSIT ###m ###m ###m
        # GNDATTIT ###rad ###rad ###rad
        # GNDFLAGS ###

        # Find the the start of ground object position/animation data
        ground_data_start_index = -1
        for idx, line in enumerate(self.raw):
            if line.startswith("NUMGDREC"):
                ground_data_start_index = idx + 1  # Data actually starts on the next row
                self.number_data_frames = int(line.split()[1])

        # Only import the ground object data if it exists
        if ground_data_start_index > 0 and self.number_data_frames > 0:
            # Each frame of data will have 6 rows
            # time
            # x, y, z, r, p, y
            # Unknown
            # Unknown
            # Unknown

            reference_line_index = ground_data_start_index  # initialize value with the found start index
            temp = list()
            for i in range(6):
                parts = self.raw[reference_line_index + i].split()
                temp.extend(parts)

            self.pos_data.append(temp)

            # Extract the start Position
            self.start_pos = [float(self.pos_data[0][1]),
                              float(self.pos_data[0][2]),
                              float(self.pos_data[0][3])]

    def assign_bullet(self, record):
        """Associate a bullet record event with this ground object."""
        self.bullet_record.append(record)

    def assign_kill(self, kill):
        """Associate a kill report with this ground object."""
        self.kill_record.append(kill)

    def assign_death(self, death):
        """Associate a death report with this ground object."""
        self.death_record.append(death)

    # Pass information out of the class
    # def ID(self):
    #     return self.id
    # def YSFID(self):
    #     return self.ysfid
    # def NAME(self):
    #     return self.name
    # def GND_TYPE(self):
    #     return self.gnd_type
    # def IFF(self):
    #     return self.iff
    
    
