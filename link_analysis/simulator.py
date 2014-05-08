# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from string_message import StringMessage
from link import Link
from link_analyzer import Analyzer
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'experiment_control', 'commands'))
from payload import Payload

class Simulator:

    def __init__(self, links, log_file, window=1):
        self.links = links
        self.window_size = min(window, len(links))
        self.current_link = 0
        self.log_file_name = log_file
        self.log_file = open(log_file, 'a')
        random.seed(os.urandom(1))


    def _simulate_link(self, link, payload, symbol_errors):
        for ii in range(len(payload)):
            link.tx['data'][10 + 12 + ii] = payload[ii]
        new_link = Link(link.tx)

        corrupted_payload = self._corrupt_payload(payload, symbol_errors)

        for rx in link.valid_rx:
            for ii in range(len(corrupted_payload)):
                rx['data'][10 + 12 + ii] = corrupted_payload[ii]
            new_link.add_rx(rx)
        for rx in link.timeout_rx:
            new_link.add_rx(rx)
        for rx in link.invalid_rx:
            new_link.add_rx(rx)

        return new_link

    def _corrupt_payload(self, payload, symbol_errors):
        corrupted_payload = []

        for byte in payload:
            upper_nibble = self._corrupt_symbol((byte & 0xf0) >> 4, symbol_errors)
            lower_nibble = self._corrupt_symbol(byte & 0x0f, symbol_errors)
            corrupted_payload.append((upper_nibble << 4 | lower_nibble))

        # print map(lambda b1, b2: b1 ^ b2, payload, corrupted_payload)
        # print symbol_errors
        return corrupted_payload

    def _corrupt_symbol(self, symbol, symbol_errors):
        bit_errors = symbol_errors[symbol]
        corruption = 0

        for ii in range(4):
            # ordered from LSB (0) to MSB (3)
            if random.random() <= bit_errors[ii]:
            # if bit_errors[ii] != 0:
                corruption |= (1 << ii)

        return (symbol ^ corruption)

    def _calculate_symbol_errors(self, start, window):
        links = self.links[start:start+window]

        symbol_errors = []
        for _ in range(16):
            symbol_errors.append([0.0] * 4)
        messages = 0

        for link in links:
            for rx in link.valid_rx:
                messages += 1
                for symbol in range(16):
                    for bit in range(4):
                        symbol_errors[symbol][bit] += rx['symbol_errors'][symbol][bit]

        if messages >= 2:
            for symbol in range(16):
                for bit in range(4):
                    symbol_errors[symbol][bit] /= messages

        return symbol_errors

    def _write_link_to_log(self, link, properties):
        lines = [link.tx.format_for_log(properties)]
        for rx in link.rx:
            lines.append(rx.format_for_log())

        self.log_file.writelines(lines)

    def simulate(self, payload_string, number_of_link=None):
        payload = Payload(payload_string)
        self.simulate_payload(payload, number_of_link if number_of_link else len(self.links))

    def simulate_payload(self, payload, links):
        number_of_links = min(len(self.links)-self.window_size-2, links)
        if number_of_links <= 0:
            return

        for link in range(number_of_links):
            try:
                if link % 100 == 0:
                    print link
                else:
                    sys.stdout.write('.')
                symbol_error = self._calculate_symbol_errors(link, self.window_size)
                simulated_link = self._simulate_link(self.links[link], payload.data, symbol_error)
                self._write_link_to_log(simulated_link, payload.properties)
            except:
                print link,

    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("LinkFile( {} )\n".format(self.filename))
