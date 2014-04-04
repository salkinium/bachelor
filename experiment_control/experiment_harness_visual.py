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
import time

from box_manager import BoxManager
from script_manager import ScriptManager
from visualizer import MessageVisualizer
from formatter import MessageFormatter


if __name__ == "__main__":

    visualizer = MessageVisualizer(2, 200)
    MessageFormatter.add_visualizer(visualizer)

    boxmanager = BoxManager()

    # Current setup:
    # From the top, wall is left
    # |
    # |   0
    # |
    # |
    # |   4
    # |

    # Transmitters
    # ID | Type               | UUID     | Current Port
    #  0 | FTDI MTM-CM5000MSP | MFUBFEOE | /dev/ttyUSB0
    #  4 | FTDI MTM-CM5000MSP | MFUCIY5N | /dev/ttyUSB1

    boxmanager.add_box(0, "/dev/ttyUSB0:telos", None, -2)
    boxmanager.add_box(1, "/dev/ttyUSB1:telos", None, -2)

    scriptmanager = ScriptManager(boxmanager)
    for arg in sys.argv[1:]:
        scriptmanager.add_script(arg)

    while True:
        # time.sleep(1)
        scriptmanager.run()
        if scriptmanager.is_idle():
            # turn off all the heating elements
            for box in boxmanager.boxes:
                box.set_air_temperature(0)
            # force quit of all threads
            print "Terminating..."
            os._exit(1)
