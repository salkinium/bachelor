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


    def _simulate_link(self, link, payload, error_tables):
        for ii in range(len(payload)):
            link.tx['data'][10 + 12 + ii] = payload[ii]
        new_link = Link(link.tx)

        corrupted_payload = self._corrupt_payload(payload, error_tables)

        for rx in link.valid_rx:
            # print "origi:", "".join(map((lambda d: bin(d)[2:].zfill(8)), rx['xor'])), rx['bit_errors']
            for ii in range(len(corrupted_payload)):
                rx['data'][10 + 12 + ii] = corrupted_payload[ii]
            new_link.add_rx(rx)
        for rx in link.timeout_rx:
            new_link.add_rx(rx)
        for rx in link.invalid_rx:
            new_link.add_rx(rx)

        return new_link

    def _corrupt_payload(self, payload, error_tables):
        corruption = []

        for byte in payload:
            upper_nibble = self._get_corruption_for_symbol((byte & 0xf0) >> 4, error_tables)
            lower_nibble = self._get_corruption_for_symbol(byte & 0x0f, error_tables)
            corruption.append((upper_nibble << 4 | lower_nibble))

        # cor_string = "".join(map((lambda d: bin(d)[2:].zfill(8)), corruption))
        # print "before:", cor_string, cor_string.count("1")
        corruption = self._add_corruption_for_burst_error(corruption, error_tables)
        corruption = self._add_corruption_for_burst_error(corruption, error_tables)
        # corruption = self._add_corruption_for_burst_error(corruption, error_tables)
        # cor_string = "".join(map((lambda d: bin(d)[2:].zfill(8)), corruption))
        # print "after: ", cor_string, cor_string.count("1")

        return map(lambda l, r: l ^ r, payload, corruption)

    def _add_corruption_for_burst_error(self, corruption, error_tables):
        bit_errors = sum(map(lambda b: bin(b).count("1"), corruption))

        corruption_bits = []
        for byte in corruption:
            for ii in reversed(range(8)):
                corruption_bits.append(1 if ((byte & (1 << ii)) > 0) else 0)

        position = 0
        burst_length = 0
        while(position < len(corruption_bits)):
            if corruption_bits[position] == 0:
                # remove single bit error
                if position > 1 and corruption_bits[position-1] == 1 and corruption_bits[position-2] == 0:
                    if random.random() < 0.25:
                        corruption_bits[position - 1] = 0

                position += 1
                continue

            burst_length = self._random_burst_length(error_tables['burst'])
            for ii in range(position, min(len(corruption_bits), position+burst_length)):
                corruption_bits[ii] = 1
            position += burst_length

        for byte in range(len(corruption)):
            cor_byte = 0
            for bit in reversed(range(8)):
                cor_byte |= (corruption_bits[byte*8 + (7 - bit)] << bit)
            corruption[byte] = cor_byte

        return corruption

    def _random_burst_length(self, burst_error_table):
        rands = random.random()
        current_prop = 0

        for length in reversed(range(1, len(burst_error_table))):
            if rands < current_prop:
                return length
            current_prop += burst_error_table[length]

        return 1

    def _get_corruption_for_symbol(self, symbol, error_tables):
        bit_errors = error_tables['symbol'][symbol]
        corruption = 0

        for ii in range(4):
            # ordered from LSB (0) to MSB (3)
            if random.random() < bit_errors[ii]:
                corruption |= (1 << ii)

        return corruption

    def _calculate_error_tables(self, start, window):
        links = self.links[start:start+window]

        symbol_errors = [ [0.0] * 4 for _ in range(16) ]
        burst_errors = [0] * (16+1)
        messages = 0

        for link in links:
            for rx in link.valid_rx:
                messages += 1
                for symbol in range(16):
                    for bit in range(4):
                        symbol_errors[symbol][bit] += rx['symbol_errors'][symbol][bit]
                for burst_length in range(16+1):
                    burst_errors[burst_length] += rx['burst_errors'][burst_length]

        # average over window
        if messages >= 2:
            for symbol in range(16):
                for bit in range(4):
                    symbol_errors[symbol][bit] /= messages
            for burst_length in range(16 + 1):
                burst_errors[burst_length] /= messages

        symbols = [0.0] * 4
        for symbol in symbol_errors:
            for bit in range(4):
                symbols[bit] += symbol[bit]
        for bit in range(4):
            symbols[bit] /= 16

        for ii in range(16):
            burst_errors[ii +1] *= (1+symbols[ii%4])

        # relative bit errors
        total_burst_errors = sum(burst_errors)
        if total_burst_errors > 0:
            total_lengths = 1.0 / sum(map(lambda b: 1 if b > 0 else 0, burst_errors))
            for burst_length in range(1, 16 + 1):
                burst_errors[burst_length] = float(burst_errors[burst_length]) / total_burst_errors

        return {'symbol': symbol_errors, 'burst': burst_errors}

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
                error_tables = self._calculate_error_tables(link, self.window_size)
                simulated_link = self._simulate_link(self.links[link], payload.data, error_tables)
                self._write_link_to_log(simulated_link, payload.properties)
            except:
                print link+1,
            if (link + 1) % 100 == 0:
                print link + 1
            else:
                sys.stdout.write('.')

    def __hash__(self):
        return str(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("LinkFile( {} )\n".format(self.filename))
