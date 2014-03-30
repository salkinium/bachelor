# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from base import BaseCommand
from multiprocessing import Value
from threading import Timer


class TemperatureReachedCommand(BaseCommand):

    def __init__(self, arguments=None):
        super(TemperatureReachedCommand, self).__init__(arguments)

        for key in self.arguments:
            if key in ['timeout']:
                try:
                    self.arguments[key] = int(self.arguments[key])
                except ValueError:
                    self.logger.error("TemperatureReachedCommand failed on parsing argument '{}'={} as integer"
                                      .format(key, self.arguments[key]))

        args = {'timeout': None}
        args.update(self.arguments)

        if not all(key in args for key in ['timeout']):
            self.logger.error("TemperatureReachedCommand has incomplete arguments: '{}'".format(args))
            self.arguments = None
        else:
            self.arguments = args

        self.temperature_timeout_timer = None
        self.temperature_timeout_expired = Value('b', True)

    def execute(self, boxmanager):
        # set-up the timeout
        self.temperature_timeout_expired.value = False
        if self.temperature_timeout_timer:
            self.temperature_timeout_timer.cancel()

        if self.arguments['timeout']:
            self.temperature_timeout_timer = Timer(self.arguments['timeout'], self._temperature_timeout_expired)
            self.temperature_timeout_timer.start()

        while not all(box.temperature_target_reached() for box in boxmanager.boxes) and \
                not self.temperature_timeout_expired.value:
            pass

        return True

    def _temperature_timeout_expired(self):
        self.temperature_timeout_expired.value = True

    def __str__(self):
        return "TemperatureReachedCommand()"
