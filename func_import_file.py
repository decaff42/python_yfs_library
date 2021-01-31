#!/usr/bin/env python

__version__ = "20181125_2202"
__author__ = "Decaff_42"
__copyright__ = "2018 by Decaff_42"
__license__ = """Only non-comercial use with attribution is allowed without
prior written permission from Decaff_42."""


import csv


def import_any_file(filepath, file_type):
    """Import and handle any filetype as needed by various scripts."""
    data = list()               # Initialize here
    file_type = file_type.upper()   # Will be needed in multiple places.

    if filepath.endswith(".csv") or file_type is "CSV":
        # This is a csv file and should be read using the csv module.
        with open(filepath, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                data.append(row)
    else:
        # This is a text-based filetype
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as txt_file:
            data = txt_file.readlines()

        for ind, row in enumerate(data):
            if row.endswith("\n"):
                # The readlines method in line 22 leaves the new line character
                # in the string it imports. This will strip it away.
                data[ind] = row.strip('\n')
            if file_type == "LST":
                # It is useful to split the various elements of the .lst line
                data[ind] = data[ind].split()   # Whitespace split
            if file_type == "CFG":
                # Settings file needs to be put into dictionary.
                output = {}
                for i in data:
                    d = i.split(" -- ")
                    output[str(d[0])] = d[1]
                data = output

    return data
