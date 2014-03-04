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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tinyos', 'support', 'sdk', 'python'))

from tinyos.message import *
from tinyos.message.Message import *
from tinyos.message.SerialPacket import *

from base import BaseCommand
from evaluator import Evaluator
from messages import *


class MessageCommand(BaseCommand):

    def __init__(self, arguments, result_logger):
        super(MessageCommand, self).__init__(arguments)
        self.results = result_logger
        self.sending_timeout_timer = None
        self.sending_timeout_expired = Value('b', False)

        self.arguments['randomize'] = False
        for key in self.arguments:
            if key in ['power', 'timeout', 'repeat', 'from', 'to', 'bursts']:
                try:
                    self.arguments[key] = int(self.arguments[key])
                except ValueError:
                    self.logger.error("MessageCommand failed on parsing argument '{}'={} as integer"
                                      .format(key, self.arguments[key]))
            if key in ['period']:
                try:
                    self.arguments[key] = float(self.arguments[key])
                except ValueError:
                    self.logger.error("MessageCommand failed on parsing argument '{}'={} as float"
                                      .format(key, self.arguments[key]))
            if key in ['data']:
                if self.arguments[key].startswith("random("):
                    try:
                        number = int(self.arguments[key][7:-1])
                        self.arguments[key] = [random.randint(0, 255) for _ in xrange(number)]
                        self.arguments['randomize'] = True
                    except ValueError:
                        self.logger.error("MessageCommand failed on parsing the length of random data '{}' as integer"
                                          .format(self.arguments[key][7:-1]))
                    except:
                        self.logger.error("MessageCommand failed miserably on parsing the random data.")
                else:
                    try:
                        string = self.arguments[key].decode("hex")
                        self.arguments[key] = map(ord, string)
                    except ValueError:
                        self.logger.error("MessageCommand failed on decoding the hexadecimal data.")

        args = {'timeout': 1, 'power': 7, 'data': [], 'repeat': 1, 'period': 1, 'bursts': None, 'randomize': False}
        args.update(self.arguments)
        if not all(key in args for key in ('from', 'to', 'power', 'data', 'repeat', 'period', 'timeout', 'bursts')):
            self.logger.error("MessageCommand has incomplete arguments: '{}'".format(args))
            self.arguments = None
        else:
            self.arguments = args

    def execute(self, boxmanager):
        if not self.arguments:
            return False

        from_id = self.arguments['from']
        to_id = self.arguments['to']

        sender = sender_orig = boxmanager.get_box(from_id)
        if not sender:
            self.logger.error("Sender '{}' not found!".format(from_id))
            return False

        receiver = receiver_orig = boxmanager.get_box(to_id)
        if not receiver:
            self.logger.error("Receiver '{}' not found!".format(to_id))
            return False

        tx = SerialMessage()
        tx.set_header_channel(26)
        tx.set_header_type(SerialMessage.get_amType())
        tx.set_header_power(self.arguments['power'])
        tx.set_header_len(len(self.arguments['data']))
        tx.set_data(self.arguments['data'])
        self.logger.debug("Created message: {}".format(tx))

        reversed_message_flow = False
        bursts = self.arguments['bursts']
        bursts = bursts - 1 if (bursts and bursts > 0) else None
        repeats = self.arguments['repeat']

        while repeats:

            if self.arguments['bursts'] and reversed_message_flow:
                sender = receiver_orig
                receiver = sender_orig
            else:
                sender = sender_orig
                receiver = receiver_orig

            sender.mote_control.purge_receive_buffer()
            receiver.mote_control.purge_receive_buffer()

            tx.set_header_nodeid(sender.id)
            #self.logger.debug("Sending message from '{}' to '{}'.".format(sender.id, receiver.id))
            sender.transmit(receiver.id, tx)

            if self.sending_timeout_timer:
                self.sending_timeout_timer.cancel()
            self.sending_timeout_expired.value = False
            self.sending_timeout_timer = Timer(self.arguments['timeout'], self._sending_timeout_expired)
            self.sending_timeout_timer.start()

            while not self.sending_timeout_expired.value and \
                    (sender.mote_control.receive_buffer_empty() or receiver.mote_control.receive_buffer_empty()):
                pass

            tx_confirmation = sender.mote_control.get_received_message()
            rx = receiver.mote_control.get_received_message()

            if self.sending_timeout_expired.value or not rx or not tx_confirmation:
                self.logger.warning("Message reception timed out on repeat {}".format(args['repeat'] - repeats))
            else:
                values = Evaluator.evaluate_messages(tx_confirmation, rx)
                values.update({'temperatureFrom': sender.mote_temperature,
                               'temperatureTo': receiver.mote_temperature})

                result_string = Evaluator.format_values(values)
                self.results.info(result_string)

            if self.arguments['bursts']:
                if bursts > 0:
                    bursts -= 1
                else:
                    reversed_message_flow = not reversed_message_flow
                    bursts = self.arguments['bursts'] - 1

            if repeats > 0:
                repeats -= 1
                if self.arguments['randomize']:
                    # randomize payload
                    tx.set_data([random.randint(0, 255) for _ in xrange(len(self.arguments['data']))])
                # wait to send again
                time.sleep(self.arguments['period'])

        return True


    def _sending_timeout_expired(self):
        self.sending_timeout_expired.value = True

    def __str__(self):
        return "MessageCommand()"
