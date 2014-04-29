# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import os
import sys
import time
import random
from threading import Timer
from multiprocessing import Value
import itertools

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))

from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *

from base import BaseCommand
from payload import Payload
from formatter import MessageFormatter
from messages import *


class MessageCommand(BaseCommand):

    def __init__(self, arguments, result_logger):
        super(MessageCommand, self).__init__(arguments)
        self.results = result_logger
        self.sending_timeout_timer = None
        self.sending_timeout_expired = Value('b', False)
        self.sending_period_timer = None
        self.sending_period_expired = Value('b', False)

        # we cannot add an item to a dict while iterating over it
        self.arguments['randomize'] = False
        for key in self.arguments:
            if key in ['power', 'repeat', 'bursts']:
                try:
                    self.arguments[key] = int(self.arguments[key])
                except ValueError:
                    self.logger.error("MessageCommand failed on parsing argument '{}'={} as integer"
                                      .format(key, self.arguments[key]))
            elif key in ['from']:
                if self.arguments[key].startswith("cycle"):
                    self.arguments[key] = []
                else:
                    try:
                        id_list = self.arguments[key].split(',')
                        self.arguments[key] = map(int, id_list)
                    except ValueError:
                        self.logger.error("MessageCommand failed on parsing argument '{}'={} as list of integers"
                                          .format(key, self.arguments[key]))
            elif key in ['period', 'timeout']:
                try:
                    self.arguments[key] = float(self.arguments[key])
                except ValueError:
                    self.logger.error("MessageCommand failed on parsing argument '{}'={} as float"
                                      .format(key, self.arguments[key]))
            elif key in ['data']:
                data = Payload(self.arguments[key])
                if not data.valid:
                    self.logger.error("MessageCommand failed miserably on parsing the payload.")
                self.arguments[key] = data

        args = {'timeout': 1, 'power': 7, 'data': Payload(), 'repeat': 1, 'period': 0, 'bursts': 1, 'randomize': False}
        args.update(self.arguments)
        if not all(key in args for key in ['from', 'power', 'data', 'repeat', 'period', 'timeout', 'bursts']):
            self.logger.error("MessageCommand has incomplete arguments: '{}'".format(args))
            self.arguments = None
        else:
            self.arguments = args

    def execute(self, boxmanager):
        if not self.arguments:
            return False

        tx = SerialMessage()
        tx.set_header_channel(26)
        tx.set_header_type(SerialMessage.get_amType())
        tx.set_header_power(self.arguments['power'])
        tx.set_header_len(len(self.arguments['data']))
        tx.set_data(self.arguments['data'].data)
        self.logger.debug("Created message: {}".format(tx))

        bursts = self.arguments['bursts'] - 1 if self.arguments['bursts'] > 0 else 0
        repeats = self.arguments['repeat']
        if len(self.arguments['from']) > 0:
            if not all(box_id in boxmanager for box_id in self.arguments['from']):
                self.logger.error("MessageCommand cannot find all boxes in BoxManager. Available boxes are: '{}'".format(boxmanager.identifiers))
                return False
            all_boxes = [boxmanager.get_box(box_id) for box_id in self.arguments['from']]
        else:
            all_boxes = boxmanager.boxes
        if not len(all_boxes):
            self.logger.error("MessageCommand found no boxes to send with.")
            return False

        senders = itertools.cycle(all_boxes)
        sender = next(senders)

        while repeats:
            if bursts > 0:
                bursts -= 1
            else:
                bursts = self.arguments['bursts'] - 1 if self.arguments['bursts'] > 0 else 0
                sender = next(senders)

            # clear all previous receive buffers
            map(lambda box: box.mote_control.purge_receive_buffer(), boxmanager.boxes)

            # broadcast the message
            tx.set_header_nodeid(sender.id)
            tx.set_header_seqnum((self.arguments['repeat'] - repeats) & 0xffff)
            sender.broadcast(tx)

            # start the sender period timer
            if self.sending_period_timer:
                self.sending_period_timer.cancel()
            self.sending_period_expired.value = False
            self.sending_period_timer = Timer(self.arguments['period'], self._sending_period_expired)
            self.sending_period_timer.start()

            # start the receive timeout timer
            if self.sending_timeout_timer:
                self.sending_timeout_timer.cancel()
            self.sending_timeout_expired.value = False
            self.sending_timeout_timer = Timer(self.arguments['timeout'], self._sending_timeout_expired)
            self.sending_timeout_timer.start()

            # wait until all boxes received something or reception timed out
            while not self.sending_timeout_expired.value and \
                    any(box.mote_control.receive_buffer_empty() for box in boxmanager.boxes):
                time.sleep(0)

            # the sender received the local loop-back message
            tx_loopback = sender.mote_control.get_received_message()
            if not tx_loopback:
                self.logger.error("MessageCommand did not receive the loopback message from box '{}'".format(sender.id))
                continue

            # write this message to the logs
            tx_string = MessageFormatter.format_tx_message(tx_loopback, sender.mote_temperature)
            self.results.info(tx_string)

            # all other motes might have received the message
            for receiver in boxmanager.boxes_without(sender):
                # the receiver might have received a message
                rx = receiver.mote_control.get_received_message()
                # write this message to the logs
                rx_string = MessageFormatter.format_rx_message(rx, receiver.id, tx_loopback.get_header_seqnum(), receiver.mote_temperature)
                self.results.info(rx_string)

            if repeats > 0:
                repeats -= 1
                tx.set_data(self.arguments['data'].data)
                # wait to send again
                while not self.sending_period_expired.value:
                    time.sleep(0)

        return True


    def _sending_timeout_expired(self):
        self.sending_timeout_expired.value = True

    def _sending_period_expired(self):
        self.sending_period_expired.value = True

    def __str__(self):
        return "MessageCommand()"
