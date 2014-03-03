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


if __name__ == "__main__":

    manager = BoxManager()
    manager.add_box(0, "/dev/ttyUSB2:telos", "/dev/ttyUSB0", -2)
    manager.add_box(1, "/dev/ttyUSB1:telos", "/dev/ttyUSB3", -2)
    for arg in sys.argv[1:]:
        manager.add_script(arg)

    while True:
        manager.run()
        if manager.is_idle():
            # turn off all the heating elements
            for box in manager.boxes:
                box.set_air_temperature(0)
            # force quit of all threads
            print "Terminating..."
            os._exit(1)
