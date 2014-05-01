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

    # visualizer = MessageVisualizer(2, 200)
    # MessageFormatter.add_visualizer(visualizer)

    boxmanager = BoxManager()

    # Current setup for power 3.
    # From the top, door is left, windows on the right
    # |        0  |
    # |
    # \           |
    #
    # /           |
    # |
    # |        1  |

    # Transmitters
    # ID | Type               | UUID     | Current Port | Angle
    #  0 | FTDI MTM-CM5000MSP | MFUD5PNI | /dev/ttyUSB0 | 315 @ 30C
    #  1 | FTDI MTM-CM5000MSP | MFUBFEOE | /dev/ttyUSB2 | 355 @ 65C

    # Temperature
    # ID | UUID     | Current Port
    #  0 | A7027DQP | /dev/ttyUSB1
    #  1 | A7027DJS | /dev/ttyUSB3

    boxmanager.add_box(0, "/dev/ttyUSB0:telos", "/dev/ttyUSB1", -1)
    boxmanager.add_box(1, "/dev/ttyUSB2:telos", "/dev/ttyUSB3", -1)

    scriptmanager = ScriptManager(boxmanager)
    for arg in sys.argv[1:]:
        scriptmanager.add_script(arg)

    while True:
        scriptmanager.run()
        if scriptmanager.is_idle():
            # turn off all the heating elements
            for box in boxmanager.boxes:
                box.set_air_temperature(0)
            # force quit of all threads
            print "Terminating..."
            os._exit(1)
