#!/usr/bin/env python

__version__     = "20200229"
__author__      = "Decaff_42"
__copyright__   = "2020 by Decaff_42"
__license__     = """Only non-comercial use with attribution is allowed without
prior written permission from Decaff_42."""


import os
import csv



def write_csv(path, data):
    """Write a csv file to the specified path with list of list data"""
    with open(path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


def write_txt(path, data):
    """write a plain text file to the specified path with list of list data"""
    with open(path, 'w') as txt_file:
        for row in data:
            try:
                if row.endswith("\n") == False:
                    txt_file.write('{}\n'.format(row))
                else:
                    txt_file.write(row)
            except:
                print(row)
