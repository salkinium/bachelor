# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import sys
import os

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', 'experiment_control', 'rs'))
from rs import RSCoder


class Link:
    """ Link
    Represents a link in a non-platform specific format.
    Contains a transmitted message and all received messages.
    Does validation, error detection and evaluation of links.
    """

    def __init__(self, tx, coder=None):
        assert tx.is_transmission
        self.tx = tx
        self.valid_rx = []
        self.invalid_rx = []
        self.timeout_rx = []
        self.coder = None
        if 'coder' in self.tx:
            self.coder = coder
            coder_info = self.tx['coder'].split(",")
            if coder_info[0] == "rs":
                n, k = int(coder_info[1]), int(coder_info[2])
                self.tx['coded_payload'] = self.tx['data'][10 + 12:10 + 12 + self.coder.k]
                if self.coder == None or self.coder.n != n or self.coder.k != k:
                    # really inefficient, don't do that
                    self.coder = RSCoder(n, k)


    def add_rx(self, rx):
        assert rx.is_reception

        if not rx['timeout'] and \
                len(rx['data']) >= len(self.tx['data']) and \
                rx['data'][10] == self.tx['data'][10] and \
                rx['seqnum'] == self.tx['seqnum']:
            self.valid_rx.append(rx)

            # bit errors
            xor = [rx['data'][ii] ^ self.tx['data'][ii] for ii in range(10, len(self.tx['data']))][:-1]
            xor_string = "".join(map((lambda d: bin(d)[2:].zfill(8)), xor))
            xor_bits = map((lambda d: bin(d).count("1")), xor)
            bit_errors = xor_string.count("1")

            # byte errors
            xor_bytes = map((lambda d: 1 if d != 0 else 0), xor)
            byte_errors = sum(xor_bytes)

            # burst bit errors
            burst_errors = [0] * (16+1)
            for burst in reversed(range(1, 16+1)):
                burst_errors[burst] = xor_string.count("1" * burst)
                xor_string = xor_string.replace("1" * burst, "0" * burst)

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

            # normalize for symbol occurance
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

            rx['xor'] = xor
            rx['bit_errors'] = bit_errors
            rx['byte_errors'] = byte_errors
            rx['burst_errors'] = burst_errors
            rx['symbol_errors'] = symbol_errors

            if self.coder != None:
                rx_coded_payload_with_parity = rx['data'][10+12:-1]
                tx_coded_payload = self.tx['coded_payload']

                rx_decoded_payload = map(ord, self.coder.decode(map(chr, rx_coded_payload_with_parity), nostrip=True))
                rx['decoded_payload'] = rx_decoded_payload

                # these are all the bit errors that RS missed!
                decoded_bit_errors = map(lambda l, r: bin(l ^ r).count("1"), tx_coded_payload, rx_decoded_payload)

                rx['decoded_bit_errors'] = sum(decoded_bit_errors)
                if rx['decoded_bit_errors'] != 0:
                    sys.stdout.write(':{}'.format(rx['decoded_bit_errors']))

                rx_coded_payload = rx['coded_payload'] = rx_coded_payload_with_parity[:self.coder.k]
                # these are all the bit errors, that RS was able to correct
                corrected_bit_errors = map(lambda l, r: bin(l ^ r).count("1"), rx_coded_payload, rx_decoded_payload)
                rx['coded_bit_errors'] = sum(map(lambda b: bin(b).count("1"), xor[12:12+self.coder.k]))
                rx['corrected_bit_errors'] = sum(corrected_bit_errors)
                # print rx['coded_bit_errors'], rx['corrected_bit_errors'], rx['decoded_bit_errors']

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
