#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


import sys
from string_message import StringMessage
from link_analyzer import Analyzer
from link import Link


if __name__ == "__main__":
    messages = []

    for arg in sys.argv[1:]:
        with open(arg, 'r') as linkfile:
            for line in linkfile:
                if 'errors=0' not in line:
                    message = StringMessage(line)
                    messages.append(message)

    links = []
    link = None

    for msg in messages:
        if msg.is_transmission:
            link = Link(msg)
            links.append(link)
        elif msg.is_reception:
            link.add_rx(msg)

    # length_rx = [rx['length'] for rx in link.invalid_rx if 'length' in rx for link in links]
    # print list(set(length_rx))

    links_rx_lower = []
    links_rx_upper = []

    for link in links:
        if link.tx['id'] == 0:
            # transmitting from 0 to 1
            links_rx_lower.append(link)
        else:
            links_rx_upper.append(link)

    print "len rx_30={}".format(len(["" for link in links_rx_lower if link.is_valid]))
    print "len rx_50={}".format(len(["" for link in links_rx_upper if link.is_valid]))
    print "timeouts rx_30={}".format(len(["" for link in links_rx_lower if len(link.timeout_rx)]))
    print "timeouts rx_50={}".format(len(["" for link in links_rx_upper if len(link.timeout_rx)]))

    analyzerLower = Analyzer(links_rx_lower)

    rssi_plot = analyzerLower.create_rssi_plot()
    analyzerLower.save_plot_to_file(rssi_plot, 'r_rssi_plot_30_0_to_1.pdf')

    error_plot = analyzerLower.create_errors_plot()
    analyzerLower.save_plot_to_file(error_plot, 'r_error_plot_30_0_to_1.pdf')

    lqi_plot = analyzerLower.create_lqi_plot()
    analyzerLower.save_plot_to_file(lqi_plot, 'r_lqi_plot_30_0_to_1.pdf')

    xor_plot = analyzerLower.create_xor_plot()
    analyzerLower.save_plot_to_file(xor_plot, 'r_xor_plot_30_0_to_1.pdf')


    analyzerUpper = Analyzer(links_rx_upper)

    rssi_plot = analyzerUpper.create_rssi_plot()
    analyzerUpper.save_plot_to_file(rssi_plot, 'r_rssi_plot_30_1_to_0.pdf')

    error_plot = analyzerUpper.create_errors_plot()
    analyzerUpper.save_plot_to_file(error_plot, 'r_error_plot_30_1_to_0.pdf')

    lqi_plot = analyzerUpper.create_lqi_plot()
    analyzerUpper.save_plot_to_file(lqi_plot, 'r_lqi_plot_30_1_to_0.pdf')

    xor_plot = analyzerUpper.create_xor_plot()
    analyzerUpper.save_plot_to_file(xor_plot, 'r_xor_plot_30_1_to_0.pdf')
