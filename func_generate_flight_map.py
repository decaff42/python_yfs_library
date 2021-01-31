#!/usr/bin/env python

__version__ = "20210129"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__date__ = "29 January 2021"
__license__ = """Only non-commercial use with attribution is allowed without prior written permission from Decaff_42."""

"""
VERSION HISTORY:
20200306 - Updated release to fix map generation issues
20210129 - Re-formatting IAW PEPs. 
"""

# Import standard python modules
import matplotlib.pyplot as plt
import os
import sys
from tkinter import filedialog, messagebox

# Import custom modules from python_ysf_lib
from python_ysf_lib.func_import_file import import_any_file
from python_ysf_lib.func_process_yfs import process_yfs_file
from python_ysf_lib.func_yfs_header_extract import extract_yfs_header


# Define custom functions
def get_map_data(scenery_name):
    """Get the map information from the map_data.cfg file"""
    map_data_path = os.path.join(os.getcwd(), "Reference_Maps", "map_data.cfg")
    map_data = import_any_file(map_data_path, 'txt')
    map_data = map_data[1:]  # Strip the header information.

    data = list()
    for row in map_data:
        if row.startswith(scenery_name):
            data = row.split(",")

            # Format the pixel centers, scaling, and image sizes to appropriate data types
            data[2] = int(data[2])
            data[3] = int(data[3])
            data[4] = float(data[4])
            data[5] = int(data[5])
            data[6] = int(data[6])

    return data


def scale_map_for_report(scenery_name, image_output_path):
    map_data = get_map_data(scenery_name)
    if len(map_data) < 1:
        print("ERRROR: YFS Map is not loaded. Add Map to code!")
        print("Missing Map {}".format(scenery_name))
        return

    # Get information from map_data
    plotting_scale = map_data[4]  # how many meters each pixel represents
    map_image_width = map_data[5]
    map_image_height = map_data[6]
    map_x_pos = map_image_width - map_data[2]  # Pixels are taken from the left
    map_y_pos = map_data[3]  # Pixels are taken from the top
    image_path = os.path.join(os.getcwd(), "Reference_Maps", map_data[1])
    legend_location = map_data[7]
    plot_name = "Scaled_{}".format(map_data[1])

    # Replace / in scenery names
    if "/" in scenery_name:
        scenery_name = scenery_name.replace("/", "_")
    if "\\" in scenery_name:
        scenery_name = scenery_name.replace("\\", "_")

    # Prepare image information for plotting
    map_out_put_pixel_width = 1000
    map_out_put_pixel_height = (map_out_put_pixel_width / map_image_width) * map_image_height
    map_dpi = 96

    im_x_min = map_x_pos - map_image_width
    im_x_max = map_image_width - abs(im_x_min)
    im_y_min = map_y_pos - map_image_height
    im_y_max = map_image_height - abs(im_y_min)

    plt.figure(figsize=(map_out_put_pixel_width / map_dpi, map_out_put_pixel_height / map_dpi), dpi=map_dpi)
    plt.axis('equal')
    plt.axis([im_x_min, im_x_max, im_y_min, im_y_max])
    plt.axis('off')  # hides the tic marks and axis lines
    plt.margins(0, 0)
    im = plt.imread(image_path)
    implot = plt.imshow(im, extent=[im_x_min, im_x_max, im_y_min, im_y_max])
    plt.tight_layout()
    plt.savefig(os.path.join(image_output_path, plot_name), transparent=True)


def run_html_mapping_code(sortie_list, pilot_list, scenery_name, yfs_file_name):
    """Runs the transparent (mode 2) plotting routine given a sorted list of flights

    Updated in 2.1.0 so that colors and linestyles are based on user rather than
    the flight.
    
    """
    image_output_path = os.path.join(os.getcwd(), "Flight Maps")

    # Extract information that will be used for plotting
    map_data = get_map_data(scenery_name)

    if len(map_data) < 1:
        print("Map could not be found")
        print("YFS MAP: {}".format(scenery_name))
        return
    plotting_scale = map_data[4]  # how many meters each pixel represents
    map_image_width = map_data[5]
    map_image_height = map_data[6]
    map_x_pos = map_image_width - map_data[2]  # Pixels are taken from the left
    map_y_pos = map_data[3]  # Pixels are taken from the top

    # Prepare image information for plotting
    map_out_put_pixel_width = 1000
    map_out_put_pixel_height = (map_out_put_pixel_width / map_image_width) * map_image_height
    map_dpi = 96

    im_x_min = map_x_pos - map_image_width
    im_x_max = map_image_width - abs(im_x_min)
    im_y_min = map_y_pos - map_image_height
    im_y_max = map_image_height - abs(im_y_min)

    # Set the plot line options for multiple paths.
    plot_colors = ['yellow', 'magenta', 'cyan', 'red', 'darkorange', 'springgreen', 'silver', 'darkviolet', 'gold',
                   'lightskyblue']
    plot_options = ['solid', 'dashed', 'dashdot', 'dotted']

    # Generate the combinations of color and line styles.
    line_options = list()
    for option in plot_options:
        for color in plot_colors:
            line_options.append([color, option])

    # Assign colors and linestyles to users
    user_color_linestyle = {}
    unique_users = list(set(pilot_list))
    for username, line in zip(unique_users, line_options):
        user_color_linestyle[username] = line

    # Replace / in scenery names
    if "/" in scenery_name:
        scenery_name = scenery_name.replace("/", "_")
    if "\\" in scenery_name:
        scenery_name = scenery_name.replace("\\", "_")

    # Plot
    plotting_order = list()
    plot_counter = 0
    for ind, (sortie, pilot) in enumerate(zip(sortie_list, pilot_list)):
        pilot_sortie_number = pilot_list[:ind].count(pilot)
        fname = "{}_{}_{}_{}.png".format(yfs_file_name, scenery_name, pilot, pilot_sortie_number)
        print(fname)
        plotting_order.append(fname)

        # Get the sortie class information.
        x = sortie.x
        y = sortie.z

        # Format x,y data to match the image scale
        plot_x = list()
        plot_y = list()
        for xpos, ypos in zip(x, y):
            plot_x.append(xpos / plotting_scale)
            plot_y.append(-1 * ypos / plotting_scale)

            # Use the pilot name to determine line color and style
        plot_color, plot_linestyle = user_color_linestyle[pilot]

        # Generate figure
        plt.figure(figsize=(map_out_put_pixel_width / map_dpi, map_out_put_pixel_height / map_dpi), dpi=map_dpi)

        # Keep the axes equal so that they don't scale weirdly
        plt.axis('equal')
        plt.axis([im_x_min, im_x_max, im_y_min, im_y_max])
        plt.axis('off')  # hides the tic marks and axis lines

        # Plot the data
        plt.plot(plot_x, plot_y, color=plot_color, linewidth=2, linestyle=plot_linestyle)

        # Minimize white-space around map
        plt.margins(0, 0)

        # Save the figures
        plt.tight_layout()
        plt.savefig(os.path.join(image_output_path, fname), transparent=True)
        plt.close()

        plot_counter += 1

    return plotting_order


def run_mapping_code(yfs_data, scenery_name, yfs_file_name, image_output_path, plotting_mode):
    """Runs the mapping process for a flight.
    plotting_mode == 0 >> Stand-alone plots of each flight
    plotting_mode == 1 >> All flights on single plot
    plotting_mode == 2 >> Transparent background plots."""

    # yfs_data has the following pieces to the list of data:
    # 1 - airplane class instances
    # 2 - text_events
    # 3 - wpn_cnfgs
    # 4 - player_ids
    # 5 - ground_objects
    # 6 - bullet_records
    # 7 - kill_credits
    # 8 - explosions

    # Replace / in scenery names
    if "/" in scenery_name:
        scenery_name.replace("/", "_")
    if "\\" in scenery_name:
        scenery_name.replace("\\", "_")

    # Make sure that the map flown is in the list of maps for plotting
    map_data = get_map_data(scenery_name)
    if len(map_data) < 1:
        return

    # Extract information that will be used for plotting
    flights = yfs_data[0]

    # Determine the pilots (users)
    usernames = list()
    for airplane in flights:
        user = airplane.username
        if user not in usernames:
            usernames.append(user)

    unique_users = list(set(usernames))

    # Get information from map_data
    plotting_scale = map_data[4]  # how many meters each pixel represents
    map_image_width = map_data[5]
    map_image_height = map_data[6]
    map_x_pos = map_image_width - map_data[2]  # Pixels are taken from the left
    map_y_pos = map_data[3]  # Pixels are taken from the top
    image_path = os.path.join(os.getcwd(), "Reference_Maps", map_data[1])
    legend_location = map_data[7]

    # Prepare image information for plotting
    map_out_put_pixel_width = 1920
    map_out_put_pixel_height = (map_out_put_pixel_width / map_image_width) * map_image_height
    map_dpi = 96

    im_x_min = map_x_pos - map_image_width
    im_x_max = map_image_width - abs(im_x_min)
    im_y_min = map_y_pos - map_image_height
    im_y_max = map_image_height - abs(im_y_min)

    # Set the plot line options for multiple paths.
    plot_colors = ['yellow', 'magenta', 'cyan', 'red', 'darkorange', 'springgreen', 'silver', 'darkviolet', 'gold',
                   'lightskyblue']
    plot_options = ['solid', 'dashed', 'dashdot', 'dotted']

    # Generate the combinations of color and line styles.
    line_options = list()
    for option in plot_options:
        for color in plot_colors:
            line_options.append([color, option])

    # Assign colors and linestyles to users
    user_color_linestyle = {}
    for username, line in zip(unique_users, line_options):
        user_color_linestyle[username] = line

    plot_names = list()
    # Create stand-alone plots
    plot_counter = 0
    if plotting_mode == 0 or plotting_mode == 2:
        for flight_num, flight in enumerate(flights):
            # Catch flights that don't takeoff.
            if len(flight.sorties) < 1:
                continue

            # Get information that won't change based on sortie
            pilot = flight.username
            aircraft = flight.aircraft_name

            # Process each sortie as a separate plot.
            sorties = flight.sortie_class_instances_sorted()
            for sortie_num, sortie in enumerate(sorties):
                # Skip if the flight time is too short
                if sortie.flight_time > 0.032:
                    # Get the sortie class information.
                    x = sortie.x
                    y = sortie.z

                    # Generate plot name
                    plot_name = "{}_{}_{}_{}.png".format(yfs_file_name, scenery_name, pilot, sortie_num + 1)
                    plot_names.append(plot_name)

                    # Format x,y data to match the image scale
                    plot_x = list()
                    plot_y = list()
                    for xpos, ypos in zip(x, y):
                        plot_x.append(xpos / plotting_scale)
                        plot_y.append(-1 * ypos / plotting_scale)

                    # Use the pilot name to determine line color and style
                    plot_color, plot_linestyle = user_color_linestyle[pilot]

                    # Generate figure
                    plt.figure(figsize=(map_out_put_pixel_width / map_dpi, map_out_put_pixel_height / map_dpi),
                               dpi=map_dpi)

                    # Keep the axes equal so that they don't scale weirdly
                    plt.axis('equal')
                    plt.axis([im_x_min, im_x_max, im_y_min, im_y_max])
                    plt.axis('off')  # hides the tic marks and axis lines

                    # Plot the data
                    plt.plot(plot_x, plot_y, color=plot_color, linewidth=2, linestyle=plot_linestyle)

                    # Minimize white-space around map
                    plt.margins(0, 0)

                    # Handle difference between plotting mode 0 and 2.
                    # 0 is for transparent background
                    # 2 is for the map background
                    if plotting_mode == 2:
                        im = plt.imread(image_path)
                        implot = plt.imshow(im, extent=[im_x_min, im_x_max, im_y_min, im_y_max])

                    # Save the figures
                    plt.tight_layout()
                    plt.savefig(os.path.join(image_output_path, plot_name), transparent=True)
                    plt.close()

                    # Incriment the plot_counter for the next iteration. This should only increase
                    # when there is actually a plot produced.
                    plot_counter += 1

    elif plotting_mode == 1:
        # Put all flights on a single plot
        # Replace / in scenery names
        if "/" in scenery_name:
            scenery_name = scenery_name.replace("/", "_")
        if "\\" in scenery_name:
            scenery_name = scenery_name.replace("\\", "_")

        print(scenery_name)

        # Generate the output filename
        plot_name = "{} - {}.png".format(yfs_file_name, scenery_name)
        plot_names.append(plot_name)

        plt.figure(figsize=(map_out_put_pixel_width / map_dpi, map_out_put_pixel_height / map_dpi), dpi=map_dpi)
        plt.axis('equal')
        plt.axis([im_x_min, im_x_max, im_y_min, im_y_max])
        plt.axis('off')  # Hides the axis and tick marks

        for flight_num, flight in enumerate(flights):
            # Catch flights that don't takeoff.
            if len(flight.sorties) < 1:
                continue
            # Get information that won't change based on sortie
            pilot = flight.username
            aircraft = flight.aircraft_name

            # Process each sortie as a separate plot.
            sorties = flight.sortie_class_instances_sorted()
            for sortie_num, sortie in enumerate(sorties):
                if sortie.flight_time > 0.032:
                    # Get the sortie class information.
                    x = sortie.x
                    y = sortie.z

                    # Generate map legend name for this plot
                    legend_name = "{}_Flight#{}_{}".format(pilot, sortie_num + 1, aircraft)

                    # Format x,y data to match the image scale
                    plot_x = list()
                    plot_y = list()
                    for xpos, ypos in zip(x, y):
                        plot_x.append(xpos / plotting_scale)
                        plot_y.append(-1 * ypos / plotting_scale)

                    # Use the plot counter to determine what color and style type the plot should use
                    plot_color, plot_linestyle = user_color_linestyle[pilot]

                    # Plot the data
                    plt.plot(plot_x, plot_y, color=plot_color, linewidth=2, linestyle=plot_linestyle, label=legend_name)

                    # Increment the plot_counter for the next iteration. This should only increase
                    # when there is actually a plot produced.
                    plot_counter += 1

        plt.margins(0, 0)
        im = plt.imread(image_path)
        implot = plt.imshow(im, extent=[im_x_min, im_x_max, im_y_min, im_y_max])
        plt.tight_layout()
        plt.legend(loc=legend_location, facecolor="white", fancybox=False, framealpha=0.8)
        plt.savefig(os.path.join(image_output_path, plot_name), transparent=True)

    return plot_names
