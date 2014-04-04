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

class MessageFormatter(object):

    _visualizer = None

    @staticmethod
    def add_visualizer(visualizer):
        MessageFormatter._visualizer = visualizer

    @staticmethod
    def disable_visualizer():
        MessageFormatter._visualizer = None

    @staticmethod
    def format_dictionary(values):
        result_list = []
        result_list.append(MessageFormatter._format_item(values, 'mode'))
        result_list.append(MessageFormatter._format_item(values, 'id'))
        result_list.append(MessageFormatter._format_item(values, 'seqnum'))
        if 'temperature' in values:
            result_list.append("temperature={:.1f}".format(values['temperature']))

        if 'timeout' in values and values['timeout']:
            result_list.append("timeout=1")
        else:
            result_list.append(MessageFormatter._format_item(values, 'timeout'))
            result_list.append(MessageFormatter._format_item(values, 'length'))
            if 'data' in values:
                values['data'] = ["0x%x" % b for b in values['data']]
                result_list.append("data={}".format(" ".join(values['data'])))
            result_list.append(MessageFormatter._format_item(values, 'power'))
            result_list.append(MessageFormatter._format_item(values, 'rssi'))
            result_list.append(MessageFormatter._format_item(values, 'lqi'))
            result_list.append(MessageFormatter._format_item(values, 'crc'))

        # filter out the None values
        result_list = [result for result in result_list if result]
        return "\t".join(result_list)

    @staticmethod
    def _format_item(values, key):
        if key in values:
            return "{}={}".format(key, values[key])
        else:
            return None

    @staticmethod
    def decode_message(msg):
        if msg is None:
            return {}

        length = ord(msg.data[10])
        data = msg.data[:-(100 - length)]
        metadata = [msg.getElement_header_metadata(0), msg.getElement_header_metadata(1)]
        data = map(ord, data)
        channel = msg.get_header_channel()
        seqnum = msg.get_header_seqnum()

        crc = metadata[1] >> 7
        lqi = metadata[1] & 0x7f
        rssi = struct.unpack('>b', chr(metadata[0]))[0] - 45
        power = msg.get_header_power()
        node_id = msg.get_header_nodeid()

        results = {'data': data,
                   'length': length,
                   'channel': channel,
                   'seqnum': seqnum,
                   'crc': crc,
                   'lqi': lqi,
                   'rssi': rssi,
                   'id': node_id,
                   'power': power}

        return results

    @staticmethod
    def format_tx_message(msg, temperature):
        values = {'temperature': temperature, 'mode': 'tx'}
        values.update(MessageFormatter.decode_message(msg))

        # only some keys make sense for a transmitted message
        filtered_keys = ['mode', 'id', 'temperature', 'length', 'data', 'power', 'seqnum']
        filtered_values = {key:value for key, value in values.items() if key in filtered_keys}

        string_message = MessageFormatter.format_dictionary(filtered_values)
        if MessageFormatter._visualizer:
            MessageFormatter._visualizer.add_tx_message(string_message)

        return string_message

    @staticmethod
    def format_rx_message(msg, identifier, seqnum, temperature):
        mvalues = {'id': identifier, 'temperature': temperature, 'mode': 'rx', 'timeout': 0, 'seqnum': seqnum}
        if msg is None:
            mvalues.update({'timeout': 1})
            return MessageFormatter.format_dictionary(mvalues)
        else:
            values = MessageFormatter.decode_message(msg)
            values.update(mvalues)

        # only some keys make sense for a received message
        filtered_keys = ['mode', 'id', 'timeout', 'temperature', 'seqnum', 'length', 'data', 'lqi', 'rssi', 'crc']
        filtered_values = {key: value for key, value in values.items() if key in filtered_keys}

        string_message = MessageFormatter.format_dictionary(filtered_values)
        if MessageFormatter._visualizer:
            MessageFormatter._visualizer.add_rx_message(string_message)

        return string_message

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "MessageFormatter({})".format(MessageFormatter._visualizer)
