# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


from link import Link
import dateutil.parser


class StringLink(Link):
    """ NewStringLink
    Parses a string and generates a link class
    """

    def __init__(self, string=None):
        Link.__init__(self, None)

        if string:
            string = string.replace('\n', '')
            for item in string.split('\t'):
                items = item.split('=')
                if len(items) >= 2:
                    self.properties[items[0]] = items[1]

        for p in self.properties:
            if p in ['power', 'lqi', 'rssi', 'errors', 'from', 'to']:
                self[p] = int(self[p])
            elif p in ['crc']:
                self[p] = self[p]
            elif p in ['fromT', 'toT']:
                self[p] = float(self[p])
            elif p in ['timestamp']:
                self[p] = dateutil.parser.parse(self[p].replace(',', '.'))
            elif p in ['data', 'xor']:
                self[p] = [int(ii, 16) for ii in self[p].split(' ')]


    def __str__(self):
        return "NewString" + Link.__str__(self)
