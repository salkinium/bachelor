#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import os, sys, signal
import glob
import time

from box_manager import BoxManager

if __name__ == "__main__":

    manager = BoxManager()
    manager.addBox(0, "/dev/ttyUSB2:telos", "/dev/ttyUSB0", -2)
    manager.addBox(1, "/dev/ttyUSB1:telos", "/dev/ttyUSB3", -2)
    for arg in sys.argv[1:]:
        manager.addScript(arg)
    
    while(1):
    	manager.run()
        if manager.isIdle():
        	# turn off all the heating elements
        	for box in manager.boxes:
        		box.setAirTemperature(0)
        	# force quit of all threads
        	print "Terminating..."
        	os._exit(1)
