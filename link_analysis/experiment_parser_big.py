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
    link = None
    new_link = False
    files = [range(8), range(8), range(8), range(8)]

    for tx in range(4):
        for rx in range(8):
            if tx == rx:
                continue
            files[tx][rx] = open('../../hauser_data/big/{}_to_{}.txt'.format(tx, rx), 'w')

    for arg in sys.argv[1:]:
        with open(arg, 'r') as linkfile:
            for line in linkfile:
                try:
                    if 'errors=0' not in line:
                        message = StringMessage(line)

                        if message.is_transmission:
                            if new_link:
                                new_link = False

                                tx_id = link.tx['id']
                                for rx in link.get_messages_with_errors():
                                    rx_id = rx['id']

                                    results = []
                                    results.append("xor={}".format(" ".join(["0x%x" % b for b in rx['xor']])))
                                    results.append("rssi={}".format(rx['rssi']))
                                    results.append("lqi={}".format(rx['lqi']))

                                    # print tx_id, rx_id, files[tx_id][rx_id].name
                                    files[tx_id][rx_id].write("\t".join(results) + "\n")

                            link = Link(message)
                        elif message.is_reception:
                            link.add_rx(message)
                            new_link = True
                except:
                    print line
