# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import dateutil.parser


class StringMessage(object):
    """ StringMessage
    Parses a string and generates a link class
    """

    def __init__(self, string=None):
        self.properties = {}

        if string:
            string = string.replace('\n', '')
            for item in string.split('\t'):
                items = item.split('=')
                if len(items) >= 2:
                    self.properties[items[0]] = items[1]

        for p in self.properties:
            if p in ['power', 'lqi', 'rssi', 'errors', 'id', 'seqnum', 'length', 'timeout', 'crc']:
                self[p] = int(self[p])
            elif p in ['temperature']:
                self[p] = float(self[p])
            elif p in ['timestamp']:
                self[p] = dateutil.parser.parse(self[p].replace(',', '.'))
            elif p in ['data']:
                self[p] = [int(ii, 16) for ii in self[p].split(' ')]

    @property
    def is_transmission(self):
        return self['mode'] == 'tx'

    @property
    def is_reception(self):
        return self['mode'] == 'rx'

    def __iter__(self):
        for key in self.properties:
            yield key

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __getitem__(self, key):
        return self.properties[key]

    def __len__(self):
        return len(self.properties)

    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("Message(\t{} )\n".format(",\n".join(["'%s': '%s'" % (p, self.properties[p]) for p in self.properties]))
                .replace("\n", "\n\t"))
