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

from temperature_control import TemperatureControl
from mote_control import MoteControl

if __name__ == "__main__":
    """
    Some test code
    """
    level = 'debug'
    logger = Logger(level)
    
    control = TemperatureControl('/dev/ttyUSB0', logger)
    mote = MoteControl("/dev/ttyUSB1:telos", logger)
    
    while(True):
        pass
    