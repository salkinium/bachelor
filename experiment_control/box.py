# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

import logging
import os

from periodic_timer import PeriodicTimer
from temperature_control import TemperatureControl
from mote_control import MoteControl


class Box(object):
    """ TemperatureBox
    Allows access to the controller and node in the styrofoam box.
    """

    def __init__(self, identifier, mote, temperature, log_path=''):
        super(Box, self).__init__()

        self.logger = logging.getLogger('Box.({})'.format(identifier))
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # console logging
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # file logging
        fh = logging.FileHandler(os.path.join(log_path, 'box-{}.log'.format(identifier)))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.id = int(identifier)
        self.mote_control = MoteControl(mote, os.path.join(log_path, 'box_raw-{}.log'.format(identifier)))

        if temperature:
            self.temperature_control = TemperatureControl(temperature, os.path.join(log_path, 'box_raw-{}.log'
                                                                                .format(identifier)))
        else:
            self.temperature_control = None

        self.environment_timer = PeriodicTimer(10, self._report_environment)
        self.environment_timer.start()

    @property
    def air_temperature(self):
        if self.temperature_control:
            return self.temperature_control.temperature
        else:
            return self.mote_temperature

    @property
    def mote_temperature(self):
        return self.mote_control.temperature

    @property
    def mote_humidity(self):
        return self.mote_control.humidity

    def temperature_target_reached(self):
        if self.temperature_control:
            return (self.temperature_control.target_reached(self.mote_temperature))
        else:
            return True

    def set_air_temperature(self, value):
        if not self.temperature_control:
            return
        self.logger.info("Setting air temperature to {}C".format(value))
        self.temperature_control.temperature = value

    def broadcast(self, msg):
        self.mote_control.broadcast(msg)

    def _report_environment(self):
        if self.temperature_control:
            power = self.temperature_control.power
        else:
            power = -1
        self.logger.info("Environment: Tair={:.1f}C Tmote={:.1f}C Hmote={:.1f}% Tpower={}%"
                             .format(self.air_temperature, self.mote_temperature,
                                     self.mote_humidity, power))
        return True

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box( {} )".format(self.id)
