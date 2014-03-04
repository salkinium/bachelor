# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))

from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *

from messages import *

class Evaluator(object):
    def __init__(self):
        super(Evaluator, self).__init__()

        self.logger = logging.getLogger('Evaluator')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # console logging
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)

    @staticmethod
    def format_values(values):

        result_string = ""
        if 'power' in values:
            result_string += "power={}\t".format(values['power'])
        if 'rssi' in values:
            result_string += "rssi={}\t".format(values['rssi'])
        if 'lqi' in values:
            result_string += "lqi={}\t".format(values['lqi'])
        if 'crc' in values:
            result_string += "crc={}\t".format(values['crc'])
        if 'errors' in values:
            result_string += "errors={}\t".format(values['errors'])
        if 'from' in values:
            result_string += "from={}\t".format(values['from'])
        if 'to' in values:
            result_string += "to={}\t".format(values['to'])
        if 'temperatureFrom' in values:
            result_string += "fromT={:.1f}\t".format(values['temperatureFrom'])
        if 'temperatureTo' in values:
            result_string += "toT={:.1f}\t".format(values['temperatureTo'])
        if 'data' in values:
            values['data'] = ["0x%x" % b for b in values['data']]
            result_string += "data={}\t".format(" ".join(values['data']))
        if 'xor' in values:
            values['xor'] = ["0x%x" % b for b in values['xor']]
            result_string += "xor={}\t".format(" ".join(values['xor']))

        return result_string

    @staticmethod
    def evaluate_messages(tx, rx):
        # man are these numbers arbitrary
        tx_length = tx.get_header_len()
        rx_length = rx.get_header_len()
        tx_data = tx.data[22:-(100 - tx_length)]
        rx_data = rx.data[22:-(100 - rx_length)]
        rx_metadata = [rx.getElement_header_metadata(0), rx.getElement_header_metadata(1)]

        data = map(ord, tx_data)
        xor = [ord(tx_data[ii]) ^ ord(rx_data[ii]) for ii in range(min(len(tx_data), len(rx_data)))]
        xor_bits = map((lambda d: bin(d).count("1")), xor)
        errors = sum(xor_bits)

        crc = rx_metadata[1] >> 7
        lqi = rx_metadata[1] & 0x7f
        rssi = struct.unpack('>b', chr(rx_metadata[0]))[0] - 45
        power = tx.get_header_power()
        from_id = tx.get_header_nodeid()
        to_id = rx.get_header_nodeid()

        results = {'data': data,
                   'xor': xor,
                   'errors': errors,
                   'crc': crc,
                   'lqi': lqi,
                   'rssi': rssi,
                   'from': from_id,
                   'to': to_id,
                   'power': power}

        return results

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Evaluator"
