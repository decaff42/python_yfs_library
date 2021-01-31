#!/usr/bin/env python

__version__ = "20190202"
__author__ = "Decaff_42"
__copyright__ = "2019 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""


import datetime


from python_ysf_lib.func_extract_yfs_txt_evt import extract_yfs_event_block
from python_ysf_lib.func_extract_yfs_ground_objects import extract_yfs_ground_objects
from python_ysf_lib.func_extract_yfs_aircraft import extract_aircraft_blocks
from python_ysf_lib.func_extract_yfs_bulrecor import extract_raw_bullet_record
from python_ysf_lib.func_extract_yfs_killcredit import extract_kill_credits
from python_ysf_lib.func_extract_yfs_explosions import extract_explosions


def print_break():
    """Put a separation in the output window"""
    print("----------------------------------------------------")


def process_yfs_file(raw_yfs):
    """Process a YFS file's data and extract the important parts of the file."""

    # Perform extraction of raw data:
    # Some functions like the bullet record and kill credit ones will do some
    # parsing of the raw data to prepare the data for easier association with
    # airplane classes later.

    text_events = list()
    wpn_cnfgs = list()
    player_ids = list()
    airplanes = list()
    ground_objects = list()
    bullet_records = list()
    kill_credits = list()
    explosions = list()

    # Extract event block of the YFS file
    try:
        text_events, wpn_cnfgs, player_ids = extract_yfs_event_block(raw_yfs)
    except:
        print("      An Error was found while trying to extract header event blocks")
    print("{} - Extracted Event Blocks".format(datetime.datetime.now().time()))
    print("                - Found {} Chat Messages".format(len(text_events)))
        
    # Extract the aircraft blocks of the YFS file
    try:
        airplanes = extract_aircraft_blocks(raw_yfs)
    except:
        print("      An Error was found while trying to extract aircraft event blocks")
    print("{} - Extracted Airplane Blocks".format(datetime.datetime.now().time()))
    print("                - Found {} Airplane Blocks".format(len(airplanes)))       
    
    # Extract the ground object blocks of the YFS file.
    try:
        ground_objects = extract_yfs_ground_objects(raw_yfs)
    except:
        print("      An Error was found while trying to extract ground object event blocks")
    print("{} - Extracted Ground Objects".format(datetime.datetime.now().time()))
    print("                - Found {} Ground Objects".format(len(ground_objects))) 
    
    # Extract Bullet Records
    try:
        bullet_records = extract_raw_bullet_record(raw_yfs)
    except:
        print("      An Error was found while trying to extract bullet record events")
    print("{} - Extracted Bullet Records".format(datetime.datetime.now().time()))
    print("                - Found {} Weapon Events".format(len(bullet_records))) 
    
    # Extract Kill Credits
    try:
        kill_credits = extract_kill_credits(raw_yfs)
    except:
        print("      An Error was found while trying to extract kill credit events")
    print("{} - Extracted Kill Credits".format(datetime.datetime.now().time()))
    
    # Extract Explosion Record
    try:
        explosions = extract_explosions(raw_yfs)
    except:
        print("      An Error was found while trying to extract explosion events")
    print("{} - Extracted Explosion Records".format(datetime.datetime.now().time()))
    print("                - Found {} Explosions".format(len(explosions))) 
    
    # Print Summary of YFS extracted data
    print_break()
    print("Raw YFS Summary:")
    print("  {} Airplane Event Blocks".format(len(airplanes)))
    print("  {} Text Event Blocks".format(len(text_events)))
    print("  {} Ground Objects".format(len(ground_objects)))
    print("  {} Bullet Records".format(len(bullet_records)))
    print("  {} Kills Recorded".format(len(kill_credits)))
    print("  {} Explosions Recorded".format(len(explosions)))
    print_break()

    return airplanes, text_events, wpn_cnfgs, player_ids, ground_objects, bullet_records, kill_credits, explosions
