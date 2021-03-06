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


class MoteControl(object):
    """ MoteControl
    Enables communication with the WSN mote in the box.
    """

    def __init__(self, device=None, logfile=None):
        super(MoteControl, self).__init__()

        self.logger = logging.getLogger('MoteControl.({})'.format(device))
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # console logging
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARN if logfile else logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # file logging
        if logfile:
            fh = logging.FileHandler(logfile)
            fh.setLevel(logging.WARN)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        self.mif = MoteIF.MoteIF()
        self.device = device
        self.tos_source = self.mif.addSource("serial@" + device)
        self.mif.addListener(self, SerialMessage)
        self.mif.addListener(self, RadioMessage)
        self.mif.addListener(self, SensorMessage)
        self.logger.info("listening")

        self._temperature = 0
        self.humidity = 0
        self.received_serial_messages = []
        self.temperature_correction = 0

    @property
    def temperature(self):
        return self._temperature + self.temperature_correction

    def purge_receive_buffer(self):
        self.received_serial_messages = []

    def receive_buffer_empty(self):
        return len(self.received_serial_messages) == 0

    def get_received_message(self):
        if not self.receive_buffer_empty():
            return self.received_serial_messages[0]
        else:
            return None

    def receive(self, src, msg):
        if msg.get_amType() == SensorMessage.get_amType():
            m = SensorMessage(msg.dataGet())
            self._temperature = m.get_temperature() * 0.01 - 40.1
            linear_humidity = -2.0468 + 0.0367 * m.get_humidity() + (-1.5955e-6 * m.get_humidity()) ** 2
            self.humidity = (self.temperature - 25) * (0.01 + 0.00008 * m.get_humidity()) + linear_humidity

            self.logger.debug("SensorMessage: NodeId={}, Temp={:.1f}C, Hum={:.1f}%"
                              .format(m.get_nodeid(), self.temperature, self.humidity))

        elif msg.get_amType() == SerialMessage.get_amType():
            m = SerialMessage(msg.dataGet())
            self.logger.info("SerialMessage: {}".format(str(m)))
            self.received_serial_messages.append(m)

        else:
            self.logger.warn("Unknown Message: {}".format(str(m)))

    def broadcast(self, msg):
        self.logger.info("Transmitting: {}".format(msg))
        self.mif.sendMsg(self.tos_source, 0, msg.get_amType(), 0, msg)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "MoteControl( %s )\n" % self.device
