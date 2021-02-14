#!/usr/bin/env python

__version__ = "20210213"
__author__ = "Decaff_42"
__copyright__ = "2021 by Decaff_42"
__license__ = """Only non-comercial use with attribution is allowed for any part of this code without prior written 
permission from Decaff_42. This code carries no guarantee or guarentee of any sort. Use at own risk"""


def decode_misc_parameter(misc):
    """The Misc parameter holds information about several aircraft details. If
    any of the conditions are active in the list below their value is summed up
    to form the value of the misc parameter.

    128 - Landing Lights On
    64  - Strobe Lights On
    32  - Navigation Lights On
    16  - Beacon Lights On
    8   - Overrun
    4   - Velocity Vector Indicator On
    1   - Afterburner On
    """

    output = [False, False, False, False, False, False, False]
    values = [128, 64, 32, 16, 8, 4, 1]

    for idx, i in enumerate(values):
        if misc - i >= 0:
            misc -= i
            output[idx] = True

        if misc == 0:
            # Found all the true values no need to proceed.
            break

    return output

            
