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
    manager.addBox(0, "/dev/ttyUSB0:telos", "/dev/ttyUSB1")
    manager.addBox(1, "/dev/ttyUSB2:telos", "/dev/ttyUSB3")
    if len(sys.argv) > 1:
        manager.addScript(sys.argv[1])
    
    while(1):
    	manager.run()
        pass
