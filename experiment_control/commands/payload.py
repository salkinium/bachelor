# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rs'))

from rs import RSCoder


class Payload(object):

    def __init__(self, string=''):
        super(Payload, self).__init__()

        self.properties = {'type': None}
        self.valid = False

        if string.startswith("random("):
            try:
                length = int(string[7:-1])
                self.properties.update({'type': 'random', 'length': length})
                self.valid = True
            except Exception as e:
                print e
        elif string.startswith("rs("):
            try:
                n, k, data = string[3:-1].replace(" ", "").split(",")
                n = int(n); k = int(k)
                coder = RSCoder(n, k)
                if data.startswith("random"):
                    data = "random({})".format(k)
                data = Payload(data)
                assert len(data) == k
                self.properties.update({'type': 'reed-solomon', 'coder': coder, 'payload': data})
                self.valid = True
            except Exception as e:
                print e
        elif string != '':
            data = Payload.decode_hex_string(string)
            if data:
                self.properties.update({'type': 'static', 'data': data})
                self.valid = True

    @staticmethod
    def decode_hex_string(string):
        try:
            return map(ord, string.decode("hex"))
        except ValueError as e:
            print e
            return None

    def __len__(self):
        return len(self.data)

    @property
    def type(self):
        return self.properties['type']

    @property
    def data(self):
        if not self.valid:
            return []

        if self.properties['type'] == 'static':
            return self.properties['data']

        elif self.properties['type'] == 'random':
            length = self.properties['length']
            return [random.randint(0, 255) for _ in xrange(length)]

        elif self.properties['type'] == 'reed-solomon':
            coder = self.properties['coder']
            payload = self.properties['payload']
            return map(ord, coder.encode(map(chr, payload.data)))

        return []

    def __str__(self):
        return "Payload( {} )".format(self.properties)
