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
        self.valid_rx = []
        self.invalid_rx = []
        self.timeout_rx = []

    def add_rx(self, rx):
        assert rx.is_reception

        if not rx['timeout'] and \
                len(rx['data']) >= len(self.tx['data']) and \
                rx['data'][10] == self.tx['data'][10] and \
                rx['seqnum'] == self.tx['seqnum']:
            self.valid_rx.append(rx)

            # bit errors

            xor = [rx['data'][ii] ^ self.tx['data'][ii] for ii in range(10, len(self.tx['data']))][:-1]
            xor_bytes = map((lambda d: 1 if d != 0 else 0), xor)
            xor_bits = map((lambda d: bin(d).count("1")), xor)
            bit_errors = sum(xor_bits)
            byte_errors = sum(xor_bytes)

            rx['xor'] = xor
            rx['bit_errors'] = bit_errors
            rx['byte_errors'] = byte_errors

            # bit errors per symbol
            symbol_errors = []
            for _ in range(16):
                symbol_errors.append([0.0] * 4)

            for ii in range(len(xor)):
                td = self.tx['data'][10+ii]
                xd = xor[ii]
                for symbol in [[(td & 0xf0) >> 4, (xd & 0xf0) >> 4], [td & 0x0f, xd & 0x0f]]:
                    for jj in range(4):
                        if ((symbol[1] >> jj) & 0x01) == 1:
                            # ordered from LSB (0) to MSB (3)
                            symbol_errors[symbol[0]][jj] += 1

            for symbol in range(16):
                occurance = 0
                for td in self.tx['data'][10:-1]:
                    if ((td & 0xf0) == (symbol << 4)):
                        occurance += 1
                    if ((td & 0x0f) == symbol):
                        occurance += 1

                if occurance >= 2:
                    for bit in range(4):
                        symbol_errors[symbol][bit] /= occurance

            rx['symbol_errors'] = symbol_errors

        else:
            if rx['timeout'] == 1:
                self.timeout_rx.append(rx)
            else:
                self.invalid_rx.append(rx)


    @property
    def is_valid(self):
        return (len(self.valid_rx) + len(self.timeout_rx) > 0)

    @property
    def has_error(self):
        return any(rx['errors'] for rx in self.valid_rx)

    def get_messages_with_errors(self):
        return [rx for rx in self.valid_rx if rx['errors'] > 0]

    @property
    def rx(self):
        rx = []
        rx.extend(self.valid_rx)
        rx.extend(self.invalid_rx)
        rx.extend(self.timeout_rx)

        return rx

    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("Link(\t[1, {}] )\n".format(len(self.rx)))
