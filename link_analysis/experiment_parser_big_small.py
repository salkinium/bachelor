#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import sys, os
from string_message import StringMessage
from link_analyzer import Analyzer
from link import Link
import glob
import pylab


if __name__ == "__main__":

    for arg in sys.argv[1:]:
        files = glob.glob(arg + "/[0-9]_to_[0-9].txt")

        for file in files:

            xors = []
            lqi = []
            rssi = []

            with open(file, 'r') as xorfile:
                for line in xorfile:
                    p = {}
                    line = line.replace('\n', '')
                    for item in line.split('\t'):
                        items = item.split('=')
                        if len(items) >= 2:
                            p[items[0]] = items[1]
                    # p['xor'] = [int(ii, 16) for ii in p['xor'].split(' ')]
                    # xors.append(p['xor'])
                    rssi.append(int(p['rssi']))
                    lqi.append(int(p['lqi']))

            # max_length = max(map(len, xors))
            # bits_array = [0] * max_length * 8

            # for xor in xors:
            #     for ii in range(len(xor)):
            #         for jj in range(8):
            #             bits_array[ii * 8 + jj] += 1 if xor[ii] & (1 << (7 - jj)) else 0
            #
            # pylab.figure()
            # lines = pylab.plot(range(len(bits_array)), bits_array)
            # pylab.setp(lines, color='b', alpha=0.75, linewidth=0.2)
            # pylab.ylabel("occurances")
            # pylab.xlabel("bit position")
            # pylab.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots', os.path.basename(xorfile.name)).replace(".txt", ".pdf"))
            # pylab.close()

            pylab.figure()
            n, bins, patches = pylab.hist(rssi, range(-100, -65), normed=True, histtype='stepfilled', rwidth=0.8)
            pylab.setp(patches, facecolor='r', alpha=0.75)
            pylab.ylabel("occurances")
            pylab.xlabel("RSSI")
            pylab.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots',
                                       "rssi_"+os.path.basename(xorfile.name)).replace(".txt",".pdf"))
            pylab.close()

            pylab.figure()
            n, bins, patches = pylab.hist(lqi, range(20, 110), normed=True, histtype='stepfilled', rwidth=0.8)
            pylab.setp(patches, facecolor='g', alpha=0.75)
            pylab.ylabel("occurances")
            pylab.xlabel("LQI")
            pylab.savefig(os.path.join(os.path.dirname(__file__), '..', 'plots',
                                       "lqi_" + os.path.basename(xorfile.name)).replace(".txt", ".pdf"))
            pylab.close()

