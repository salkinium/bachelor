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

import matplotlib.pyplot as plt
import pylab as P
import logging

class Analyzer(object):

    def __init__(self, links=None):
        self.links = links if links else []

        self.logger = logging.getLogger('LinkAnalyzer')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s: %(message)s')
        # console logging
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_array_of_property(self, key):
        return [p[key] for p in self.links]

    def create_rssi_plot(self):
        rssi = self.get_array_of_property('rssi')
        self.logger.debug("RSSI in range [{}, {}]".format(min(rssi), max(rssi)))

        P.figure()
        n, bins, patches = P.hist(rssi, range(-100, -65), normed=True, histtype='stepfilled', rwidth=0.8)
        P.setp(patches, 'facecolor', 'r', 'alpha', 0.75)
        P.ylabel("occurances")
        P.xlabel("RSSI")
        return P

    def create_lqi_plot(self):
        lqi = self.get_array_of_property('lqi')
        self.logger.debug("LQI in range [{}, {}]".format(min(lqi), max(lqi)))

        P.figure()
        n, bins, patches = P.hist(lqi, range(20, 110), normed=True, histtype='stepfilled', rwidth=0.8)
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
        P.ylabel("occurances")
        P.xlabel("LQI")
        return P

    def create_power_plot(self):
        power = self.get_array_of_property('power')
        self.logger.debug("Power in range [{}, {}]".format(min(power), max(power)))

        P.figure()
        n, bins, patches = P.hist(power, range(0, 30), normed=True, histtype='stepfilled', rwidth=0.8)
        P.setp(patches, 'facecolor', 'b', 'alpha', 0.75)
        P.ylabel("occurances")
        P.xlabel("Power")
        return P

    def create_errors_plot(self):
        errors = self.get_array_of_property('errors')
        self.logger.debug("Errors in range [{}, {}]".format(min(errors), max(errors)))

        P.figure()
        n, bins, patches = P.hist(errors, range(0, 100), normed=True, histtype='stepfilled', rwidth=0.8)
        P.setp(patches, 'facecolor', 'y', 'alpha', 0.75)
        P.ylabel("occurances")
        P.xlabel("Errors")
        return P

    def save_plot_to_file(self, plot, filename):
        self.logger.debug("Saving Plot to file: '{}'".format(filename))
        plot.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots', filename))
        pass
