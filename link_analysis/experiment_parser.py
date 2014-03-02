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
from string_link import StringLink
from link_analyzer import Analyzer

if __name__ == "__main__":
    links = []

    for arg in sys.argv[1:]:
        with open(arg, 'r') as linkfile:
            for line in linkfile:
                if 'crc=0' in line:
                    link = StringLink(line)
                    links.append(link)

    analyzer = Analyzer(links)

    rssi_plot = analyzer.create_rssi_plot()
    analyzer.save_plot_to_file(rssi_plot, 'rssi_plot.pdf')

    error_plot = analyzer.create_errors_plot()
    analyzer.save_plot_to_file(error_plot, 'error_plot.pdf')

    lqi_plot = analyzer.create_lqi_plot()
    analyzer.save_plot_to_file(lqi_plot, 'lqi_plot.pdf')
