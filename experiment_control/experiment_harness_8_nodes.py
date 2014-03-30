#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import os
import sys

from box_manager import BoxManager
from script_manager import ScriptManager


if __name__ == "__main__":

    boxmanager = BoxManager()

    # Current setup:
    # From the top, wall is left
    # |
    # |   4 5 6 7
    # |
    # |
    # |   0 1 2 3
    # |

    # Transmitters
    # ID | Type               | UUID     | Current Port
    #  0 | FTDI MTM-CM5000MSP | MFUBFEOE | /dev/ttyUSB6
    #  1 | FTDI MTM-CM5000MSP | MFUCIY5N | /dev/ttyUSB7
    #  2 | Moteiv tmote sky   | M4A9K6N6 | /dev/ttyUSB0
    #  3 | Moteiv tmote sky   | M4A9K6NA | /dev/ttyUSB1

    boxmanager.add_box(0, "/dev/ttyUSB6:telos", None, -2)
    boxmanager.add_box(1, "/dev/ttyUSB8:telos", None, -2)
    boxmanager.add_box(2, "/dev/ttyUSB0:telos", None, -2)
    boxmanager.add_box(3, "/dev/ttyUSB1:telos", None, -2)

    # Receivers
    # ID | Type               | UUID     | Current Port
    #  4 | FTDI MTM-CM5000MSP | MFUD5QHV | /dev/ttyUSB4
    #  5 | Moteiv tmote sky   | M4A9K6O0 | /dev/ttyUSB3
    #  6 | FTDI MTM-CM5000MSP | MFUD5PNI | /dev/ttyUSB2
    #  7 | Moteiv tmote sky   | M4A9K6M5 | /dev/ttyUSB5

    boxmanager.add_box(4, "/dev/ttyUSB4:telos", None, -2)
    boxmanager.add_box(5, "/dev/ttyUSB3:telos", None, -2)
    boxmanager.add_box(6, "/dev/ttyUSB2:telos", None, -2)
    boxmanager.add_box(7, "/dev/ttyUSB5:telos", None, -2)

    scriptmanager = ScriptManager(boxmanager)
    for arg in sys.argv[1:]:
        scriptmanager.add_script(arg)

    while True:
        scriptmanager.run()
        if scriptmanager.is_idle():
            # force quit of all threads
            print "Terminating..."
            os._exit(1)
