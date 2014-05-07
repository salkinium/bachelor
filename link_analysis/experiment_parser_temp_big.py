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
    tx_id = 0

    for tx in range(4):
        for rx in range(8):
            if tx == rx:
                continue
            files[tx][rx] = open('../../hauser_data/big2/{}_to_{}.txt'.format(tx, rx), 'w')

    for arg in sys.argv[1:]:
        with open(arg, 'r') as linkfile:
            for line in linkfile:
                try:
                    message = StringMessage(line)

                    if message.is_transmission:
                        tx_id = message['id']
                        for rx_id in xrange(4,8):
                            files[tx_id][rx_id].write(line)

                    elif message.is_reception:
                        files[tx_id][message['id']].write(line)
                except:
                    print line
