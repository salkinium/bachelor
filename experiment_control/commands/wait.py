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
import time


class WaitCommand(BaseCommand):

    def __init__(self, arguments=None):
        super(WaitCommand, self).__init__(arguments)

        for key in self.arguments:
            if key in ['timeout']:
                try:
                    self.arguments[key] = int(self.arguments[key])
                except ValueError:
                    self.logger.error("WaitCommand failed on parsing argument '{}'={} as integer"
                                      .format(key, self.arguments[key]))

        args = {'timeout': None}
        args.update(self.arguments)

        if not all(key in args for key in ['timeout']):
            self.logger.error("WaitCommand has incomplete arguments: '{}'".format(args))
            self.arguments = None
        else:
            self.arguments = args

        self.wait_timeout_timer = None
        self.wait_timeout_expired = Value('b', True)

    def execute(self, boxmanager):
        # set-up the timeout
        self.wait_timeout_expired.value = False
        if self.wait_timeout_timer:
            self.wait_timeout_timer.cancel()

        if self.arguments['timeout']:
            self.wait_timeout_timer = Timer(self.arguments['timeout'], self._wait_timeout_expired)
            self.wait_timeout_timer.start()

        while not self.wait_timeout_expired.value:
            time.sleep(0)

        return True

    def _wait_timeout_expired(self):
        self.wait_timeout_expired.value = True

    def __str__(self):
        return "WaitCommand()"
