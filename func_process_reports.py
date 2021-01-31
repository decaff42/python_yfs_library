#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20200306 - Updated release to fix map generation issues
20210129 - Re-formatting IAW PEPs. 
"""

# Import standard python modules
import os
from datetime import datetime
import base64

# Import modules from python_ysf_lib
from python_ysf_lib.func_assign_kd import assign_kills_deaths
from python_ysf_lib.func_assign_wep import assign_bullet_record
from python_ysf_lib.func_get_dats import get_dats
from python_ysf_lib.func_calc_fuel_burn import get_fuel_burn_total
from python_ysf_lib.class_kill_record import KILL
from python_ysf_lib.func_generate_flight_map import get_map_data, scale_map_for_report, run_html_mapping_code
from python_ysf_lib.func_export_file import write_txt


def get_report(report, mode, ysf_path, airplanes, ground_objects, kill_credits, bullet_records, explosions):
    """Run the correct report"""
    if mode == "MIL":
        report = generate_military_report(report, airplanes, ground_objects, kill_credits, bullet_records, explosions)
    elif mode == "CIV":
        report = generate_civilian_report(report, airplanes, ysf_path)

    return report


def generate_civilian_html_report(airplanes, yfs_path, scenery_name, plot_names, plot_folder, ysf_version, flight_date,
                                  csv_report):
    """Extract civilian data and export to html file."""
    print("Generating HTML Report...")
    yfs_filename = os.path.basename(yfs_path)
    report_date = datetime.today().strftime('%d-%b-%Y')
    report_title = "{} Civilian Flight Log Map Report".format(scenery_name)
    report_path = os.path.join(os.getcwd(), "HTML Reports")
    report_filename = "{}_-_{}_-_{}.html".format(yfs_filename, scenery_name, report_date)

    # Replace / in report filename
    if "/" in report_filename:
        report_filename = report_filename.replace("/", "_")
    if "\\" in report_filename:
        report_filename = report_filename.replace("\\", "_")

    map_data = get_map_data(scenery_name)
    if len(map_data) < 1:
        print("Ending HTML Creation - Map not in Database")
        return []

    # Start the HTML file
    html = ["<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>{}</title>".format(report_title),
            "<style>",
            "td {padding:2px 10;}",
            "img {position:absolute; left:0%; top: 0em; height:50em; width: auto;}.details {position:absolute; top:50em;}.container{position: relative;}",
            "</style>",
            "</head>",
            "<body>",
            '<div class="header">',
            "<h3><center>YSF Flight Log Report</center></h3>",
            "<table>",
            "<tr>",
            '<th align="left">Map: </th>',
            "<td>{}</td>".format(scenery_name),
            "</tr>",
            "<tr>",
            '<th align="left">YSF Version: </th>',
            "<td>{}</td>".format(ysf_version),
            "</tr>",
            "<tr>",
            '<th align="left">Flown On:</th>',
            "<td>{}</td>".format(flight_date),
            "</tr>",
            "<tr>",
            '<th align="left">Report Date:</th>',
            "<td>{}</td>".format(report_date),
            "</tr>",
            "</table>",
            "</div>"]

    # Determine how many sorties each player flew
    usernames = list()
    list_of_users = dict()
    image_order = list()
    username_order = list()
    sortie_order = list()
    pilot_order = list()
    for airplane in airplanes:
        user = airplane.username
        sorties = airplane.sortie_class_instances_sorted()
        if user not in usernames:
            usernames.append(user)

        for sortie in sorties:
            sortie_order.append(sortie)
            pilot_order.append(user)

        if len(sorties) > 0:
            if user not in username_order:
                username_order.append(user)
            try:
                list_of_users[user] += len(sorties)
            except KeyError:
                list_of_users[user] = len(sorties)

    # Sort the sorties and pilots
    final_sortie_order = list()
    final_pilot_order = list()
    max_num_sorties = 0
    for user in username_order:
        for sortie, pilot in zip(sortie_order, pilot_order):
            if pilot == user and sortie.flight_time > 0.016:  # Greater than 1 minute of flight time required.
                final_sortie_order.append(sortie)
                final_pilot_order.append(user)
        # Update the list_of_user dictionary
        list_of_users[user] = final_pilot_order.count(user)
        if list_of_users[user] > max_num_sorties:
            max_num_sorties = list_of_users[user]

    # Create Plots
    image_order = run_html_mapping_code(final_sortie_order, final_pilot_order, scenery_name, yfs_filename)

    # Generate checkboxes for each user
    script_check_vars = list()
    script_img_vars = list()

    html.append("<hr>")
    html.append("<table>")
    total_check_boxes = 0
    # Write header row
    html.append('<tr style="border-bottom:1px solid black">')
    html.append("<th>Pilot</th>")
    for i in range(max_num_sorties):
        html.append("<th>{}</th>".format(i + 1))
    html.append("</tr>")
    for user in username_order:
        html.append("<tr>")
        html.append("<th>{}</th>".format(user))
        check_string = ""
        for sortie in range(list_of_users[user]):
            total_check_boxes += 1
            html.append('<td><input type="checkbox" id="chk{}" onclick="showFlight()"></td>'.format(total_check_boxes))
            script_check_vars.append(
                '  var checkBox{} = document.getElementById("chk{}");'.format(total_check_boxes, total_check_boxes))
            script_img_vars.append(
                '  var img{} = document.getElementById("img{}");'.format(total_check_boxes, total_check_boxes))
        html.append("</tr>")
    html.append("</table>")

    # Add show/hide all button
    html.append('<button type="button" onclick="showHideAll()">Show All / Hide All Toggle</button>')
    html.append("<hr>")

    # Encode the images
    encoded_images = list()
    scale_map_for_report(scenery_name, plot_folder)
    scale_plot_name = "Scaled_{}".format(map_data[1])
    image_order.insert(0, scale_plot_name)

    # Replace / in scenery names
    if "/" in scenery_name:
        scenery_name = scenery_name.replace("/", "_")
    if "\\" in scenery_name:
        scenery_name = scenery_name.replace("\\", "_")

    for image in image_order:
        # Define plot filepath
        plot_path = os.path.join(plot_folder, image)
        if plot_path.endswith(".png") is False:
            plot_path = plot_path + ".png"

        # Encode and store images for insertion into HTML file
        image_data = base64.b64encode(open(plot_path, 'rb').read()).decode('utf-8')
        image_tag = '<img src="data:image/png;base64,{0}"></img>'.format(image_data)
        encoded_images.append(image_tag)

    # Write the maps
    print("Encoded Images: ", len(encoded_images))
    html.append('<div class="container">')
    html.append('{}'.format(encoded_images[0]))

    for ind, image in enumerate(encoded_images[1:]):
        html.append('<p id="img{}" style="display:none">{}</p>'.format(ind + 1, image))

    # Write the report section
    html.append('<div class="details">')
    csv_report = csv_report[5:]
    html.append('<table border="1">')
    for row_num, row in enumerate(csv_report):
        html.append('<tr>')
        for col in row:
            if row_num == 0:
                html.append('<th>{}</th>'.format(col))
            else:
                html.append('<td>{}</td>'.format(col))
        html.append('</tr>')
    html.append('</table>')

    # Finish off HTML file with copyright
    html.append("<hr>")
    html.append("<center>")
    html.append("YSF Flight Log Version 2.2 copyright 2021 by Decaff_42")
    html.append("</center>")
    html.append("</div>")
    html.append("</div>")

    # Write the showFlight function
    html.append("<script>function showFlight() {")
    for i in script_check_vars:
        html.append(i)
    for i in script_img_vars:
        html.append(i)
    for i in range(total_check_boxes):
        html.append('  if (checkBox{}.checked == true){{'.format(i + 1))
        html.append('    img{}.style.display = "block";'.format(i + 1))
        html.append('  } else {')
        html.append('    img{}.style.display = "none";'.format(i + 1))
        html.append('  }')
    html.append('}')

    # Write showHideAll function
    html.append("function showHideAll() {")
    for i in script_check_vars:
        html.append(i)
    for i in script_img_vars:
        html.append(i)
    html.append('')
    html.append('  if (checkBox1.checked == true){')
    for ind in range(total_check_boxes):
        html.append('    img{}.style.display = "none";'.format(ind + 1))
    for ind in range(total_check_boxes):
        html.append('    checkBox{}.checked = false;'.format(ind + 1))
    html.append('  } else {')
    for ind in range(total_check_boxes):
        html.append('    img{}.style.display = "block";'.format(ind + 1))
    for ind in range(total_check_boxes):
        html.append('    checkBox{}.checked = true;'.format(ind + 1))
    html.append('  }')
    html.append('}')
    html.append('</script>')
    html.append('</body>')
    html.append("</html>")

    # Write the HTML report to file
    write_txt(os.path.join(report_path, report_filename), html)

    print("HTML Report Written")
    return image_order


def generate_civilian_report(report, airplanes, ysf_path):
    """Extract Civilian Data from the AIRCRAFT classes and compile a report."""
    header = ["AIRCRAFT", "USERNAME", "TAKEOFF TIME", "FLIGHT TIME (HR)",
              "FLIGHT DISTANCE (KM)", "FLIGHT DISTANCE (NM)",
              "MAX_ALTITUDE (FT)", "AVG SPEED (KT)",
              "FUEL BURNED (KG)", "FUEL BURNED (LB)", "DIRECT FLIGHT DISTANCE (NM)"]

    report.append(header)

    # Get aircraft DAT files.
    aircraft_dats = get_dats(ysf_path, airplanes)
    output_data = []

    # Write output data.
    for plane in airplanes:
        data = plane.sortie_class_instances_sorted()
        identify = plane.aircraft_name
        pilot = plane.username

        for sortie in data:
            # only count sorties that last more than 1 minute
            if sortie.flight_time > 0.016:
                # Get Fuel Burn numbers for as many aircraft as possible.
                if identify in list(aircraft_dats.keys()):
                    # This has a data file.
                    dat = aircraft_dats[identify]
                    fuel = get_fuel_burn_total(dat, sortie.throttle_settings)
                    fuel1 = int(fuel * 2.20462)
                else:
                    fuel = "N/A"
                    fuel1 = "N/A"

                line = [identify, pilot]
                sortie_output_data = sortie.output()

                line.extend(sortie_output_data[:-2])
                line.append(fuel)
                line.append(fuel1)
                line.append(sortie_output_data[-2])
                output_data.append(line)

    output_data.sort(key=lambda x: x[2])
    report.extend(output_data)

    return report


def generate_military_report(report, airplanes, ground_objects, kill_credits, bullet_records, explosions):
    """Generate military combat report"""

    # Assign Kill Credits to airplane and ground classes
    airplanes, ground_objects = assign_kills_deaths(airplanes, ground_objects, kill_credits)
    print(" Kill and Death data assigned to airplanes.")

    # Assign bullet records to airplane classes
    airplanes, ground_objects = assign_bullet_record(airplanes, ground_objects, bullet_records)
    print(" Bullet Records assigned to Airplanes and Ground Objects")

    # Insert YFS Summary
    report.extend(yfs_summary(airplanes, ground_objects, kill_credits, bullet_records, explosions))

    # Insert Combat Summary
    report.extend(combat_summary(airplanes))

    # Insert Kill Details
    report.extend(kill_details(airplanes, ground_objects, kill_credits))

    # Insert Sortie Summaries
    report.extend(sortie_stats(airplanes))

    return report


def sortie_stats(airplanes):
    """Write a sortie stat section showing weapons fired."""
    header = [["----------", "----------"],
              ["SORTIE STATS"],
              ["LAUNCH TIME", "USERNAME", "AIRCRAFT", "KILLS", "RESULT",
               "GUNS", "AIM9", "AIM9X", "AGM65", "B500", "RKT", "FLR", "AIM120",
               "B250", "B500HD", "TANK"]
              ]
    weapon_order = ["GUNS", "AIM9", "AIM9X", "AGM65", "B500", "RKT", "FLR", "AIM120",
                    "B250", "B500HD", "TANK"]

    output = list()
    output.append(" ")
    output.extend(header)
    for plane in airplanes:
        launch = plane.start_time()
        user = plane.username
        air = plane.aircraft_name
        kills = len(plane.i_killed_list)
        death = plane.result()

        line = [launch, user, air, kills, death]
        stats = plane.weapon_stats()

        for i in weapon_order:
            if stats[i] == 0:
                line.append("-")
            else:
                line.append(stats[i])

        output.append(line)

    return output


def kill_details(airplanes, ground_objects, kill_credits):
    """Provide a list of each kill with who killed whom."""
    output = list()
    output.append([" "])
    header = [["----------", "----------"],
              ["KILL LOG"],
              ["TIME", "KILLER NAME", "KILLER VEHICLE", "KILLED NAME",
               "KILLED VEHICLE", "WEAPON"]
              ]
    output.extend(header)

    # Iterate through kills and get names for killed and killer.
    for kill in kill_credits:
        kill = KILL(kill)
        killer_id = kill.killer
        killed_id = kill.killed
        kill_time = kill.event_time
        kill_wpn = kill.weapon_name
        kill_id = int(killer_id[1:])
        dead_id = int(killed_id[1:])

        # Need default names and ids. Match the vehicle names with unknowns from below.
        killer_name = "-"
        killer_user = "Unknown"
        killed_name = "-"
        killed_user = "Unknown"

        # lookup killer names & aircraft/gnd objects
        if killer_id.startswith("A"):
            for plane in airplanes:
                if plane.ysf_id == kill_id:
                    killer_name = plane.aircraft_name
                    killer_user = plane.username
        elif killer_id.startswith("G"):
            for gnd in ground_objects:
                if kill_id == gnd.id:
                    killer_user = gnd.gnd_type
                    killer_name = "-"

                    # Lookup killed names & aircraft /gnd objects
        if killed_id.startswith("A"):
            for plane in airplanes:
                if plane.ysf_id == dead_id:
                    killed_name = plane.aircraft_name
                    killed_user = plane.username
        elif killed_id.startswith("G"):
            for gnd in ground_objects:
                if dead_id == gnd.id:
                    killed_user = gnd.gnd_type
                    killed_name = "-"

        line = [kill_time, killer_user, killer_name, killed_user,
                killed_name, kill_wpn]
        output.append(line)

    return output


def combat_summary(airplanes):
    """Report the number of kills, deaths and sorties for each user."""
    output = list()
    output.append("  ")
    output.append(["----------", "----------"])
    output.append(["USER SUMMARY"])
    output.append(["USERNAME", "KILLS", "DEATHS", "SORTIES"])

    # Get list of users
    user_list = list()
    users = dict()
    for plane in airplanes:
        user = plane.username
        if user not in user_list:
            user_list.append(user)
            users[user] = [0, 0, 0]  # Kills/deaths/sorties

    # Find the number of deaths and kills they have.
    for plane in airplanes:
        data = users[plane.username]
        data[0] = data[0] + len(plane.i_killed_list)
        if plane.result == "KILLED":
            data[1] = data[1] + 1
        data[2] = data[2] + 1
        users[plane.username] = data

    for key in users:
        line = [key]
        line.extend(users[key])
        output.append(line)

    return output


def yfs_summary(airplanes, ground_objects, kill_credits, bullet_records, explosions):
    """Create a stats of the YFS file"""
    output = list()
    output.append(["YFS SUMMARY"])
    output.append(["SORTIES", len(airplanes)])
    output.append(["GROUND OBJECTS", len(ground_objects)])
    output.append(["BULLET RECORDS", len(bullet_records)])
    output.append(["KILLS RECORDED", len(kill_credits)])
    output.append(["EXPLOSIONS RECORDED", len(explosions)])

    return output
