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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'link_analysis'))
from logger import Logger
import time

from daemonize import Daemonize
from box import TemperatureBox

if __name__ == "__main__":

    level = 'debug'
    logger = Logger(level)

    box1 = Box("Box1", "/dev/ttyUSB0:telos", "/dev/ttyUSB1", logger)
    box2 = Box("Box2", "/dev/ttyUSB2:telos", "/dev/ttyUSB3", logger)

    original_sigint = signal.getsignal(signal.SIGINT)

    def exit_gracefully(signum, frame):
        # restore the original signal handler as otherwise evil things will happen
        # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
        signal.signal(signal.SIGINT, original_sigint)
    
        print 'closing all ports...'
        control.port.close()
        mote.tos_source.close()
        print
        sys.exit(1)
    
    signal.signal(signal.SIGINT, exit_gracefully)
    
    while(True):
        pass
    