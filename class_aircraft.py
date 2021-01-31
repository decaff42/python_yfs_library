#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""


"""
VERSION HISTORY:
20200229 - Adds outputs from the aircraft and sortie classes for flight maps
20210129 - Re-formatting IAW PEPs. Breaks interactions with legacy code.
"""


class Aircraft:
    def __init__(self, data, ysf_id):
        self.raw = data
        self.ysf_id = int(ysf_id)  # Should be int, but be sure.

        # Define parameters
        self.block_plane = False  # Assume False unless otherwise told.

        # Initialize values
        self.iff = -1
        self.max_altitude = 0
        self.id = -1
        self.max_speed = 0
        self.average_speed = 0
        self.max_mach = 0
        self.a2a_kills = 0
        self.a2g_kills = 0
        self.start_speed = 0
        self.start_throttle = 0
        self.NUMRECOR = 0
        self.start = 0
        self.avg_speed = 0
        self.flight_time = 0
        self.throttle_setting = [0, 0, 0]
        self.flight_distance = 0
        self.taxi_distance = 0
        self.flight_distance_nm = 0

        # Initialize lists and dictionaries
        self.times = list()
        self.flight_state = list()
        self.t = list()
        self.x = list()
        self.y = list()
        self.z = list()
        self.g = list()
        self.sortie_class_instances = list()
        self.i_killed_list = list()
        self.was_killed_list = list()
        self.bullet_record = list()
        self.parsed_data = list()
        self.velocity = list()
        self.weapon_count = dict()
        self.sorties = list()

        # Initialize strings
        self.aircraft_name = ""
        self.start_position = ""
        self.username = ""
        self.id_and_tag = ""

        # Call functions to work raw data.
        self.extract_header_info()
        self.parse_data()
        self.get_sorties()

    def extract_header_info(self):
        """Get vital info from the header."""
        for ind, row in enumerate(self.raw):
            if row.startswith("AIRPLANE"):
                self.aircraft_name = row.split()[1]
                subst = row.split()[2]
                if subst is "FALSE":
                    self.block_plane = True
            elif row.startswith("STARTPOS"):
                self.start_position = row[12:]
            elif row.startswith("AIRSPEED"):
                self.start_speed = float(row.split()[-1][:-3])
            elif row.startswith("THROTTLE"):
                self.start_throttle = float(row.split()[-1])
            elif row.startswith("IDANDTAG"):
                self.id = int(row.split(" ")[1])
                self.id_and_tag = " ".join(row.split(" ")[1:])
                self.username = row.split('"')[1]   # Trim away the " in the usernames
            elif row.startswith("IDENTIFY"):
                self.iff = int(row.split(" ")[1]) + 1
            elif row.startswith("NUMRECOR"):
                self.NUMRECOR = int(row.split()[1])
                self.start = ind
                break
                # Stop the for loop here as there is no need to cycle through
                # rest of the raw data.

    def parse_data(self):
        """Parse the raw data into flight data"""
        self.parsed_data = list()
        data = self.raw
        row_num = -1

        # Find the start of the flight data
        for i in data:
            row_num += 1
            if i.startswith("NUMRECOR"):
                row_num += 1
                break

        slices = 0
        while slices < self.NUMRECOR:
            line = self.raw[row_num].split()
            line.extend(self.raw[row_num + 1].split())
            line.extend(self.raw[row_num + 2].split())
            line.extend(self.raw[row_num + 3].split())

            self.parsed_data.append(line)
            row_num += 4
            slices += 1

            # Extract useful parameters for later
            self.times.append(float(line[0]))
            self.flight_state.append(int(line[8]))
            self.t.append(float(line[0]))
            self.x.append(float(line[1]))
            self.y.append(float(line[2]))
            self.z.append(float(line[3]))

    def calculate_max_altitude(self):
        """Determine peak altitude in feet"""
        self.max_altitude = int(max(self.y) * 3.28084)

    def calculate_average_speed(self):
        """Determine average speed from the flight time and flight distance.
        For cases when the flight time is not present, return zero.
        """
        if self.flight_time > 0:
            self.avg_speed = int(self.flight_distance_nm / self.flight_time)
        else:
            self.avg_speed = 0

    def calc_average_throttle(self):
        """Determine average throttle setting to get estimate of fuel
        burned when combined with dat file data.
        List is:
          - Throttle average
          - Throttle time
          - AB Time
        """
        afterburner_time = 0
        throttle = list()
        for ind, row in enumerate(self.parsed_data[:-1]):
            t = float(row[0])
            t_next = float(self.parsed_data[ind+1][0])
            if int(row[16]) % 2 == 1:
                # Is odd, AB is on
                afterburner_time += t_next - t
            else:
                throttle.append(int(row[18]))

        # Total length of data segment
        times = float(self.parsed_data[-1][0]) - float(self.parsed_data[0][0])

        # Total time - AB_Time is the non-AB time.
        try:
            avg_thr = float(sum(throttle)/len(throttle))
        except:
            avg_thr = 0
        self.throttle_setting = [avg_thr, times - afterburner_time, afterburner_time]

    def calculate_flight_time(self):
        """Calculate the total time in the sky"""
        # Flight State breakdown:
        # 0 = Flying
        # 1 = Rolling
        # 2 = Stall
        # 3 = Left the airplane
        # 4 = Dead
        # 5 = Unknown
        # 6 = Stopped

        time_hacks = [self.times[0]]
        fs_hacks = [self.flight_state[0]]
        flying_flight_states = [0, 2]

        for t, fs in zip(self.times, self.flight_state):
            if fs != fs_hacks[-1]:
                fs_hacks.append(fs)
                time_hacks.append(t)

        start_time = False
        self.flight_time = 0
        for index, fs in enumerate(fs_hacks):
            if fs in flying_flight_states and start_time is False:
                start_time = time_hacks[index]
            elif fs not in flying_flight_states and start_time is not False:
                sortie = time_hacks[index] - start_time
                self.flight_time += sortie
                start_time = False

        self.flight_time = round(self.flight_time/3600, 3)

    def calculate_flight_distance(self):
        """Determine how far the player has flown."""

        self.flight_distance = 0
        self.taxi_distance = 0
        flying_flight_states = [0, 2]
        non_flying_flight_states = [1, 4, 5, 6]
        for ind, (fs, x, z) in enumerate(zip(self.flight_state, self.x, self.z)):
            if ind == 0 and fs in flying_flight_states:
                # Aircraft is airborne and we need to skip this slice.
                pass
            elif ind > 0 and fs in flying_flight_states:
                x_old = self.x[ind - 1]
                z_old = self.z[ind - 1]

                self.flight_distance += ((x - x_old)**2 + (z - z_old)**2)**0.5
            elif ind > 0 and fs in non_flying_flight_states:
                x_old = self.x[ind - 1]
                z_old = self.z[ind - 1]
                self.taxi_distance += ((x-x_old)**2 + (z-z_old)**2)**0.5

        # Calculate Distances in various units of measurement.
        self.flight_distance = round(self.flight_distance/1000, 1)
        self.taxi_distance = round(self.taxi_distance/1000, 1)
        self.flight_distance_nm = round(self.flight_distance * 0.539957, 1)

    def calculate_speed(self):
        """Record speed profile"""
        distance = 0  # pre-define for unusual case
        for ind, (t, x, y, z) in enumerate(zip(self.times, self.x, self.y, self.z)):
            if ind == 0:
                dt = 0
            else:
                x_old = self.x[ind - 1]
                y_old = self.y[ind - 1]
                z_old = self.z[ind - 1]
                t_old = self.times[ind - 1]

                distance = ((x - x_old)**2 + (y - y_old)**2 + (z - z_old)**2)**0.5
                dt = t - t_old

            # Do not put this inside the previous if/else to capture unexpected
            # cases of dt = 0.
            if dt > 0:
                self.velocity.append(distance / dt)
            else:
                self.velocity.append(0)

        self.max_speed = round(max(self.velocity) * 1.94384, 0)

    def count_weapons(self):
        """Counts the number of each kind of bullet record."""
        # weapons and weapon_ids match the BULLET_RECORD class lists.
        weapons = ["GUNS", "AIM9", "AGM65", "B500", "RKT", "FLR", "AIM120", "B250", "B500HD", "AIM9X", "TANK"]
        # weapon_ids = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 12]  # Kept here for reference

        # Initialize dict.
        for i in weapons:
            self.weapon_count[i] = 0

        # Iterate Bullet Records
        for rec in self.bullet_record:
            wpn = rec.weapon_name
            self.weapon_count[wpn] = self.weapon_count[wpn] + 1

    def get_sorties(self):
        """Create Sortie classes for the aircraft and get the output."""
        sorties = list()
        sortie_start = [self.aircraft_name, self.username]
        sortie_starts = list()
        sortie_ends = list()
        flying = False
        for ind, fs in enumerate(self.flight_state):
            if fs == 0 and flying is False:
                flying = True
                sortie_starts.append(ind)
            elif fs == 2 and flying is True:
                # Stall in flight
                pass
            elif fs not in [0, 2] and flying is True:
                flying = False
                sortie_ends.append(ind)

        if len(sortie_ends) == len(sortie_starts) - 1:
            # aircraft left while flying.
            sortie_ends.append(len(self.flight_state) - 1)

        for start, end in zip(sortie_starts, sortie_ends):
            data = self.parsed_data[start:end]
            if end - start > 1:
                sortie = Sortie(data)
                self.sortie_class_instances.append(sortie)
                output = sortie.output()
                if output[3] > 30 and sortie.alt_run() > 20:
                    sorties.append(sortie_start + output)

        self.sorties = sorties

    # Take optional data from outside the class and process.
    def assign_kill(self, kill):
        """Associate a kill with this aircraft. The report will want to know
        who/what the player killed and with what weapon and when.
        kill: raw string of kill credit from yfs file.
        """
        self.i_killed_list.append(kill)

        if kill.split()[2].startswith("G"):
            self.a2g_kills += 1
        elif kill.split()[2].startswith("A"):
            self.a2a_kills += 1

    def assign_death_report(self, death):
        """Associate the player's death with this aircraft. The report will
        show who/what killed the player and with what weapon.
        """
        self.was_killed_list.append(death)

    def assign_bullet(self, record):
        """Associate a bullet record event with this aircraft."""
        self.bullet_record.append(record)

    # Functions to extract information from the class
    def civilian_report(self):
        """Output data needed for a civilian report."""
        output = [self.aircraft_name,
                  self.username,
                  self.flight_time,
                  self.flight_distance,
                  self.flight_distance_nm,
                  self.max_altitude,
                  self.avg_speed,
                  self.taxi_distance,
                  self.throttle_setting]
        return output

    def inverted_z(self):
        """Invert the Z axis position data."""
        zz = list()
        for i in self.z:
            zz.append(-1 * i)
        return zz

    def start_time(self):
        """Determine the takeoff time."""
        return round(float(self.parsed_data[0][0]), 3)

    def weapon_stats(self):
        """Determine the current weapon count."""
        self.count_weapons()
        return self.weapon_count

    def has_death(self):
        """Determine if the aircraft class instance has been killed by anyone."""
        if len(self.was_killed_list) == 0:
            # Check the flight state record
            if len(self.flight_state) >= 10:
                if 4 in self.flight_state[-10:] or 5 in self.flight_state[-10:]:
                    return [1]
        else:
            return self.was_killed_list

    def sortie_class_instances_sorted(self):
        """Sort a list of the aircraft class instances and sort by takeoff time."""
        self.sortie_class_instances.sort(key=lambda x: x.takeoff_time)
        return self.sortie_class_instances

    def last_10_flight_states(self):
        if len(self.flight_state) >= 10:
            return self.flight_state[-10:]
        else:
            return self.flight_state

    def result(self):
        if len(self.was_killed_list) > 0 or any(x in [4, 5] for x in self.flight_state):
            return "KILLED"
        if len(self.flight_state) >= 2:
            if self.flight_state[-2] in [1, 6]:
                return "LEFT AIRPLANE - ON GROUND"
            else:
                return "LEFT AIRPLANE - IN AIR"
        elif self.flight_state[-1] in [1, 6]:
            return "LEFT AIRPLANE - ON GROUND"
        else:
            return "LEFT AIRPLANE - IN AIR"

    # def YSFID(self):
    #     return self.yfs_id
    # def USERNAME(self):
    #     return self.username
    # def ID(self):
    #     return self.id
    # def IDANDTAG(self):
    #     return self.id_and_tag
    # def AIRCRAFT(self):
    #     return self.aircraft_name
    # def STARTPOS(self):
    #     return self.start_position

    # def T(self):
    #     return self.t
    # def X(self):
    #     return self.x
    # def Y(self):
    #     return self.y

    # def Z1(self):
    #     return self.z

    # def has_kill(self):
    #     return self.i_killed_list
    # def bullet_record(self):
    #     return self.bullet_record
    # def block(self):
    #     return self.block_plane

    # def SORTIELIST(self):
    #     return self.sorties


class Sortie:
    def __init__(self, data):
        self.data = data

        # Initialize Parameters
        self.direct_flight_distance = 0
        self.flight_time = 0
        self.max_speed = 0
        self.avg_speed = 0
        self.flight_distance = 0
        self.flight_distance_nm = 0
        self.throttle_settings = [0, 0, 0]
        self.start = [0, 0]
        self.end = [0, 0]

        # Initialize Lists
        self.t = list()
        self.x = list()
        self.y = list()
        self.z = list()
        self.th = list()
        self.misc = list()
        self.velocity = list()

        # Initialize strings
        self.takeoff_time = ""

        # Call functions to process data in the class
        self.parse()
        self.calc_flight_time()
        self.calculate_flight_distance()
        self.calculate_speed()
        self.calc_throttle()
        self.calculate_average_speed()
        self.calc_takeoff_time()
        self.calc_direct_flight_distance()

    def parse(self):
        """Parse the data provided by the aircraft class instance."""

        for line in self.data:
            self.t.append(float(line[0]))
            self.x.append(float(line[1]))
            self.y.append(float(line[2]))
            self.z.append(-1 * float(line[3]))
            self.th.append(int(line[18]))
            self.misc.append(int(line[16]))

    def calc_direct_flight_distance(self):
        """Calculate the direct distance between takeoff and landing positions. Report in NM"""
        x_start = self.x[0]
        z_start = self.z[0]

        x_end = self.x[-1]
        z_end = self.z[-1]

        # Convert meters to nautical miles
        self.direct_flight_distance = round((((x_end-x_start)**2 + (z_end-z_start)**2)**0.5) / 1852, 1)

    def calc_flight_time(self):
        """Incoming data should be from takeoff to landing so the
        time between the first and last time stamp is the flight time.
        """
        if len(self.t) > 1:
            self.flight_time = self.t[-1] - self.t[0]
            self.flight_time = round(self.flight_time / 3600, 3)
        else:
            self.flight_time = 0

    def calculate_speed(self):
        """Record speed profile"""
        distance = 0  # Initialize for the code to use in an odd event
        for ind, (t, x, y, z) in enumerate(zip(self.t, self.x, self.y, self.z)):
            if ind == 0:
                dt = 0
            else:
                x_old = self.x[ind-1]
                y_old = self.y[ind-1]
                z_old = self.z[ind-1]
                t_old = self.t[ind-1]

                distance = ((x-x_old)**2 + (y-y_old)**2 + (z-z_old)**2)**0.5
                dt = t - t_old

            # Do not put this inside the previous if/else to capture unexpected
            # cases of dt = 0, along with the first time slice.
            if dt > 0:
                self.velocity.append(distance / dt)
            else:
                self.velocity.append(0)

        if len(self.velocity) > 0:
            self.max_speed = round(max(self.velocity) * 1.94384, 0)
            self.avg_speed = sum(self.velocity) / len(self.velocity)  # m/s
        else:
            self.max_speed = 0
            self.avg_speed = 0

    def calculate_average_speed(self):
        """Determine average speed from the flight time and flight distance.
        For cases when the flight time is not present, return zero.
        """
        if self.flight_time > 0:
            self.avg_speed = int(self.flight_distance_nm / self.flight_time)
        else:
            self.avg_speed = 0

    def calculate_flight_distance(self):
        """Determine how far the player has flown."""

        self.flight_distance = 0
        # Aircraft is always airborne in the data provided.
        for ind, (x, z) in enumerate(zip(self.x, self.z)):
            if ind == 0:
                pass
            elif ind > 0:
                x_old = self.x[ind-1]
                z_old = self.z[ind-1]
                self.flight_distance += ((x-x_old)**2 + (z-z_old)**2)**0.5

        # Calculate Distances in various units of measurement.
        self.flight_distance = round(self.flight_distance/1000, 1)
        self.flight_distance_nm = round(self.flight_distance * 0.539957, 1)

    def calc_throttle(self):
        """Determine average throttle value and times."""
        afterburner_time = 0
        throttle = list()
        for ind, (t, th, misc) in enumerate(zip(self.t[:-1], self.th[:-1], self.misc[:-1])):
            t_next = self.t[ind+1]

            if misc % 2 == 1:
                # AB is on
                afterburner_time += t_next - t
            else:
                throttle.append(th)
        mil_time = self.t[-1] - self.t[0] - afterburner_time
        try:
            avg_thr = float(sum(throttle)/len(throttle))
        except:
            avg_thr = 0
        self.throttle_settings = [avg_thr, mil_time, afterburner_time]

    def calc_takeoff_time(self):
        """Convert seconds to hour min"""
        seconds = int(self.t[0])
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        h = str(h).zfill(2)
        m = str(m).zfill(2)
        s = str(s).zfill(2)

        self.takeoff_time = "{}:{}:{}".format(h, m, s)

    # Pass information from the class.
    def max_altitude(self):
        """Return the maximum altitude of the sortie."""
        return int(max(self.y))

    def get_start_end(self):
        """Store the start and end position"""
        self.start = [self.x[0].self.y[0], self.z[0]]
        self.end = [self.x[-1].self.y[-1], self.z[-1]]
        return self.start, self.end

    def output(self):
        """Combine the output into a single list"""
        return [self.takeoff_time,
                self.flight_time,
                self.flight_distance,
                self.flight_distance_nm,
                int(max(self.y)*3.28084),  # Max altitude in feet
                int(self.avg_speed),       # Average speed rounded off to nearest whole number
                self.direct_flight_distance,
                self.throttle_settings]

    def takeoff_time(self):
        """Determine takeoff time"""
        return self.t[0]

    def alt_run(self):
        """Determine the difference between minimum and maximum altitudes for validity testing."""
        return int(max(self.y) - min(self.y))

    # def X(self):
    #     return self.x
    # def T(self):
    #     return self.t
    # def Y(self):
    #     return self.y
    # def Z(self):
    #     return self.z
    # def FH(self):
    #     return self.flight_time
    # def AVGSPD(self):
    #     return self.avg_speed
    #
    # def FDKM(self):
    #     return self.flight_distance
    # def FDNM(self):
    #     return self.flight_distance_nm
    #
    # def FUEL(self):
    #     return self.throttle_setting
    #
    # def THROTTLESETTINGS(self):
    #     return self.throttle_settings


# Define Static functions for Aircraft and Sortie classes
def calc_mach(alt):
    """Calculate the speed of sound in KTAS at given altitude"""
    if alt > 12000:
        return 573
    else:
        return alt * (-85/12000) + 660
