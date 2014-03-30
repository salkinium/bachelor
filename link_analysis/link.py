# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------


class Link:
    """ Link
    Represents a link in a non-platform specific format.
    Contains a transmitted message and all received messages.
    Does validation, error detection and evaluation of links.
    """

    def __init__(self, tx):
        assert tx.is_transmission
        self.tx = tx
        self.rx = []
        self.invalid_rx = []
        self.timeout_rx = []

    def add_rx(self, rx):
        assert rx.is_reception

        if not rx['timeout'] and \
                len(rx['data']) >= len(self.tx['data']) and \
                rx['data'][10] == self.tx['data'][10] and \
                rx['seqnum'] == self.tx['seqnum']:
            self.rx.append(rx)

            xor = [rx['data'][ii] ^ self.tx['data'][ii] for ii in range(10, len(self.tx['data']))][:-1]
            xor_bits = map((lambda d: bin(d).count("1")), xor)
            errors = sum(xor_bits)
            rx['xor'] = xor
            rx['errors'] = errors

        else:
            if rx['timeout']:
                self.invalid_rx.append(rx)
            else:
                self.timeout_rx.append(rx)

    @property
    def is_valid(self):
        return len(self.rx)

    @property
    def has_error(self):
        return any(rx['errors'] for rx in self.rx)

    def get_messages_with_errors(self):
        return [rx for rx in self.rx if rx['errors'] > 0]

    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("Message(\t{} )\n".format(",\n".join(["'%s': '%s'" % (p, self.properties[p]) for p in self.properties]))
                .replace("\n", "\n\t"))
