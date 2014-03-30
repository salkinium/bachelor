# -*- coding: utf-8 -*-
# Copyright (c) 2014, Niklas Hauser
# All rights reserved.
#
# The file is part of my bachelor thesis and is released under the 3-clause BSD
# license. See the file `LICENSE` for the full license governing this code.
# -----------------------------------------------------------------------------

from base import BaseCommand


class TemperatureCommand(BaseCommand):

    def __init__(self, arguments=None):
        super(TemperatureCommand, self).__init__(arguments)

        for key in self.arguments:
            if key in ['temperature', 'box']:
                try:
                    self.arguments[key] = int(self.arguments[key])
                except ValueError:
                    self.logger.error("TemperatureCommand failed on parsing argument '{}'={} as integer"
                                      .format(key, self.arguments[key]))

        args = {'timeout': None}
        args.update(self.arguments)

        if not all(key in args for key in ['box', 'temperature']):
            self.logger.error("TemperatureCommand has incomplete arguments: '{}'".format(args))
            self.arguments = None
        else:
            self.arguments = args

    def execute(self, boxmanager):
        if not self.arguments:
            return False

        box = boxmanager.get_box(self.arguments['box'])
        if not box:
            self.logger.error("Box '{}' not found!".format(self.arguments['box']))
            return False

        box.set_air_temperature(self.arguments['temperature'])
        return True

    def __str__(self):
        return "TemperatureCommand()"
