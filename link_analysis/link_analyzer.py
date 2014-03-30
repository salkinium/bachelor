#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import os
import pylab
import logging


class Analyzer(object):

    def __init__(self, links=None):
        self.links = [] if not links else [link for link in links if link.is_valid]

        self.logger = logging.getLogger('LinkAnalyzer')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)s: %(message)s')
        # console logging
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(ch)

    def get_array_of_property(self, key):
        results = []
        for link in self.links:
            for rx in link.get_messages_with_errors():
                if key in rx:
                    results.append(rx[key])
        return results


    def create_rssi_plot(self):
        rssi = self.get_array_of_property('rssi')
        self.logger.debug("RSSI in range [{}, {}]".format(min(rssi), max(rssi)))

        pylab.figure()
        n, bins, patches = pylab.hist(rssi, range(-100, -65), normed=True, histtype='stepfilled', rwidth=0.8)
        pylab.setp(patches, facecolor='r', alpha=0.75)
        pylab.ylabel("occurances")
        pylab.xlabel("RSSI")
        return pylab

    def create_rssi_plot(self):
        rssi = self.get_array_of_property('rssi')
        self.logger.debug("RSSI in range [{}, {}]".format(min(rssi), max(rssi)))

        pylab.figure()
        n, bins, patches = pylab.hist(rssi, range(-100, -65), normed=True, histtype='stepfilled', rwidth=0.8)
        pylab.setp(patches, facecolor='r', alpha=0.75)
        pylab.ylabel("occurances")
        pylab.xlabel("RSSI")
        return pylab

    def create_lqi_plot(self):
        lqi = self.get_array_of_property('lqi')
        self.logger.debug("LQI in range [{}, {}]".format(min(lqi), max(lqi)))

        pylab.figure()
        n, bins, patches = pylab.hist(lqi, range(20, 110), normed=True, histtype='stepfilled', rwidth=0.8)
        pylab.setp(patches, facecolor='g', alpha=0.75)
        pylab.ylabel("occurances")
        pylab.xlabel("LQI")
        return pylab

    def create_power_plot(self):
        power = self.get_array_of_property('power')
        self.logger.debug("Power in range [{}, {}]".format(min(power), max(power)))

        pylab.figure()
        n, bins, patches = pylab.hist(power, range(0, 30), normed=True, histtype='stepfilled', rwidth=0.8)
        pylab.setp(patches, facecolor='b', alpha=0.75)
        pylab.ylabel("occurances")
        pylab.xlabel("Power")
        return pylab

    def create_errors_plot(self):
        errors = self.get_array_of_property('errors')
        self.logger.debug("Errors in range [{}, {}]".format(min(errors), max(errors)))

        pylab.figure()
        n, bins, patches = pylab.hist(errors, range(0, 100), normed=True, histtype='stepfilled', rwidth=0.8)
        pylab.setp(patches, facecolor='y', alpha=0.75)
        pylab.ylabel("occurances")
        pylab.xlabel("Errors")
        return pylab

    def create_xor_plot(self):
        xors = self.get_array_of_property('xor')
        max_length = max(map(len, xors))
        bits_array = [0] * max_length * 8

        for xor in xors:
            for ii in range(len(xor)):
                for jj in range(8):
                    bits_array[ii*8 + jj] += 1 if xor[ii] & (1 << (7 - jj)) else 0

        pylab.figure()
        lines = pylab.plot(range(len(bits_array)), bits_array)
        pylab.setp(lines, color='b', alpha=0.75, linewidth=0.2)
        pylab.ylabel("occurances")
        pylab.xlabel("bit position")
        return pylab

    def save_plot_to_file(self, plot, filename):
        self.logger.debug("Saving Plot to file: '{}'".format(filename))
        plot.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots', filename))
        pass
