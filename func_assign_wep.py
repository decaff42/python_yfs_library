#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2018 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without
prior written permission from Decaff_42."""


"""
VERSION HISTORY:
20190113 - Update.
20210129 - Re-formatting IAW PEPs.
"""


def assign_bullet_record(airplanes, ground_objects, bullet_records):
    """This function assigns bullet record class instances to airplane and ground object class instances.
    airplanes: list of airplane class instances
    ground_objects: list of ground object class instances
    bullet_records: list of bullet record class instances.
    """
    unknown_launcher_count = 0
    un_assignable_bullet_record_count = 0
    aircraft_launch_counter = 0
    ground_launch_counter = 0

    for bullet in bullet_records:
        # Extract information from the bullet record class
        launch_type = bullet.launcher_type
        launch_id = bullet.launcher_id  # e.g. G124 or A0
        launcher = bullet.launcher  # The ysf id of the airplane or ground object.

        # Identify the launching aircraft or ground object.
        record_assigned = False

        if launch_type == "U":
            # The bullet record class instance could not determine the launching entity
            unknown_launcher_count += 1
        elif launch_type == "A":
            # This weapon was launched by an aircraft
            for airplane in airplanes:
                # Iterate through the airplane class instances
                if airplane.ysf_id == launcher:
                    # Found a match!
                    aircraft_launch_counter += 1
                    record_assigned = True
                    airplane.assign_bullet(bullet)
                    break
        elif launch_type == "G":
            # This weapon was launched by a ground object
            for ground_object in ground_objects:
                # Iterate through the ground object class instances
                if ground_object.ysf_id == launcher:
                    # Found a match!
                    ground_launch_counter += 1
                    record_assigned = True
                    ground_object.assign_bullet(bullet)
                    break  # no need to keep iterating at this point

        if record_assigned is False:
            un_assignable_bullet_record_count += 1

    print("  {} Bullet Records could not be assigned.".format(un_assignable_bullet_record_count))
    print("  {} Bullet Records assigned to aircraft.".format(aircraft_launch_counter))
    print("  {} Bullet Records assigned to ground objects.".format(ground_launch_counter))
    print("  {} Bullet Records not assigned due to unknown launching aircraft.".format(unknown_launcher_count))

    return airplanes, ground_objects


def assign_bullet_record2(airplanes, grounds, record):
    """Assign bullet records to the airplanes."""
    unknown_ground_ids = []
    unassigned_records = []
    unassigned_launcher = []
    for bullet in record:
        launcher = bullet.LAUNCHER()
        launch_type = bullet.LAUNCHERTYPE()
        launch_raw = bullet.RAWID()
        
        assigned = False
        if launch_type == "U":
            pass

        elif launch_type is "A":
            # Launched by an Aircraft.
            for air in airplanes:
                if air.YSFID() is launcher:
                    air.assign_bullet(bullet)
                    assigned = True
                    break

        elif launch_type is "G":
            # Launched by a Ground Object.
            for gnd in grounds:
                if gnd.ID() is launcher:
                    gnd.assign_bullet(bullet)
                    assigned = True
                    break

        if assigned is False and launch_type == "G":
            if launch_raw not in unknown_ground_ids:
                unknown_ground_ids.append(launch_raw)
            unassigned_records.append(bullet)
            unassigned_launcher.append(launch_raw)

    print("  {} Bullet Records could not be assigned.".format(len(unassigned_records)))

    return airplanes, grounds
