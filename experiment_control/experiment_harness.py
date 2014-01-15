#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
# 
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import os, sys
import glob

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'link_analysis'))
from logger import Logger
import time

from temperature_controller import TemperatureControl

if __name__ == "__main__":
    """
    Some test code
    """
    level = 'debug'
    logger = Logger(level)
    
    control = TemperatureControl('/dev/ttyUSB0', logger)
    
    while(True):
        time.sleep(5)
        control.setTemperature(0)
        time.sleep(15)
        control.setTemperature(30)
        time.sleep(15)
        control.setTemperature(50)
        pass
    